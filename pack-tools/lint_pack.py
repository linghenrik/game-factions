# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Fast standalone pack linter (content repos v2 spec C2).

Standard library only and no sibling imports: step 18 copies this file into each
content repo's kit. The authority stays tools/validate_packs.gd; this catches the
common mistakes in seconds, without Godot.

    uv run lint_pack.py [--categories <path>] [--allow-lfs-pointers] [--json] <pack_dir>...
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Same table as stubs.ASSET_EXTS (and tools/import_stubs_lib.gd); pinned by a test.
ASSET_EXTS = {
    "models": ["glb"],
    "icons": ["svg"],
    "textures": ["png"],
    "audio": ["ogg", "wav"],
}
_VERSION = re.compile(r"^\d+\.\d+\.\d+$")
# A Git LFS pointer file: under LFS_MAX bytes and starting with LFS_HEADER. Inlined on
# purpose (this file imports nothing from its siblings); packfiles.py has the same test.
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1\n"
LFS_MAX = 1024


def _item(file: str, rule: str, message: str) -> dict:
    return {"file": file, "rule": rule, "message": message}


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, ValueError) as e:
        return None, str(e)


def _is_extracted_texture(rel: str) -> bool:
    # Textures an editor import extracts from a .glb; gitignored, not pack assets.
    parts = rel.split("/")
    return (
        len(parts) == 3
        and parts[:2] == ["assets", "models"]
        and (parts[2].endswith(".png") or parts[2].endswith(".png.import"))
    )


def _manifest(pack_dir: Path, cats: dict, items: list[dict]):
    data, err = None, None
    path = pack_dir / "pack.json"
    if not path.is_file():
        items.append(_item("pack.json", "manifest", "pack.json is missing"))
        return None
    data, err = _load_json(path)
    if err or not isinstance(data, dict):
        items.append(_item("pack.json", "manifest", f"pack.json is not a JSON object: {err or ''}"))
        return None
    pid = data.get("id")
    if not isinstance(pid, str):
        items.append(_item("pack.json", "manifest", "id must be a string"))
        return data
    if re.search(cats["pack_id_pattern"], pid) is None:
        items.append(
            _item("pack.json", "manifest", f"id '{pid}' must match {cats['pack_id_pattern']}")
        )
    if pid in cats["reserved_ids"]:
        items.append(_item("pack.json", "manifest", f"id '{pid}' is reserved"))
    for prefix in cats["reserved_prefixes"]:
        if pid.startswith(prefix):
            items.append(
                _item("pack.json", "manifest", f"id '{pid}' is reserved (prefix '{prefix}')")
            )
    if pack_dir.name != pid:
        items.append(
            _item(
                "pack.json", "manifest", f"folder '{pack_dir.name}' must be named after id '{pid}'"
            )
        )
    ver = data.get("version")
    if not isinstance(ver, str) or _VERSION.match(ver) is None:
        items.append(_item("pack.json", "manifest", "version must be X.Y.Z"))
    cat = data.get("category")
    rule = cats["categories"].get(cat) if isinstance(cat, str) else None
    if rule is None:
        known = ", ".join(cats["categories"])
        items.append(_item("pack.json", "manifest", f"category must be one of {known}"))
        return data
    core_id = cats["core_id"]
    if (cat == "core") != (pid == core_id):
        items.append(
            _item(
                "pack.json",
                "manifest",
                f"only '{core_id}' is the core pack, and it is category core",
            )
        )
    deps = data.get("dependencies", [])
    if not isinstance(deps, list):
        items.append(_item("pack.json", "manifest", "dependencies must be an Array"))
        deps = []
    mode = rule.get("deps")
    if mode == "none" and deps:
        items.append(_item("pack.json", "manifest", "the core pack has no dependencies"))
    elif mode == "base" and deps != [core_id]:
        items.append(
            _item("pack.json", "manifest", f'a {cat} pack depends on exactly ["{core_id}"]')
        )
    overrides = data.get("overrides", [])
    if overrides and not rule.get("overrides", False):
        items.append(_item("pack.json", "manifest", "only a mod pack may declare overrides"))
    return data


def _allowed(rule: dict, folder: str) -> bool:
    folders = rule.get("folders", [])
    return folders == "*" or folder in folders


def _defs(pack_dir: Path, cats: dict, manifest: dict | None, items: list[dict]) -> None:
    cat = manifest.get("category") if manifest else None
    rule = cats["categories"].get(cat) if isinstance(cat, str) else None
    pack_id = manifest.get("id") if manifest else pack_dir.name
    seen: dict[str, str] = {}
    for path in sorted(pack_dir.rglob("*.json")):
        rel = path.relative_to(pack_dir).as_posix()
        parts = rel.split("/")
        if rel == "pack.json" or any(p.startswith(".") for p in parts):
            continue
        if parts[0] == "assets":
            items.append(_item(rel, "layout", "JSON does not belong under assets/"))
            continue
        if len(parts) != 2:
            items.append(
                _item(rel, "layout", "defs sit exactly one folder deep: <folder>/<name>.json")
            )
            continue
        folder = parts[0]
        if rule is not None and rule.get("client_only"):
            items.append(_item(rel, "layout", f"a {cat} pack has no defs"))
            continue
        if folder not in cats["folders"]:
            items.append(_item(rel, "layout", f"'{folder}/' is not a def folder"))
            continue
        if rule is not None and not _allowed(rule, folder):
            items.append(_item(rel, "layout", f"a {cat} pack may not have {folder}/"))
        d, err = _load_json(path)
        if err or not isinstance(d, dict):
            items.append(_item(rel, "def", f"does not parse as a JSON object: {err or ''}"))
            continue
        kind = d.get("kind")
        want = cats["folders"][folder]
        if kind != want:
            items.append(
                _item(rel, "def", f"a {kind} def does not belong in {folder}/ (it holds {want})")
            )
        did = d.get("id")
        if not isinstance(did, str) or not did.startswith(f"{pack_id}."):
            items.append(_item(rel, "def", f"id must start with '{pack_id}.'"))
        elif did in seen:
            items.append(_item(rel, "def", f"duplicate id '{did}' (also in {seen[did]})"))
        else:
            seen[did] = rel
        if kind == "shop_item":
            camp = d.get("channel") == "camp"
            camp_folder = cats["camp_items_folder"]
            if camp and folder != camp_folder:
                items.append(_item(rel, "def", f"camp-channel shop items go in {camp_folder}/"))
            elif not camp and folder == camp_folder:
                items.append(
                    _item(rel, "def", f"{camp_folder}/ holds only camp-channel shop items")
                )
        if (
            kind == "minion"
            and rule is not None
            and rule.get("minion_house_is_pack")
            and d.get("house_tag") != pack_id
        ):
            items.append(
                _item(rel, "def", f"a {cat} minion's house_tag must be its pack id '{pack_id}'")
            )


def _assets(pack_dir: Path, cats: dict, manifest: dict | None, items: list[dict]) -> None:
    assets = pack_dir / "assets"
    if not assets.is_dir():
        return
    pack_id = manifest.get("id") if manifest else pack_dir.name
    is_core = pack_id == cats["core_id"]
    for path in sorted(assets.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(pack_dir).as_posix()
        parts = rel.split("/")
        if any(p.startswith(".") for p in parts) or rel.endswith(".json"):
            continue
        if _is_extracted_texture(rel):
            continue
        if len(parts) < 3 or parts[1] not in ASSET_EXTS:
            items.append(_item(rel, "asset", f"belongs in assets/<{'|'.join(ASSET_EXTS)}>/"))
            continue
        name = parts[-1]
        ext = name.rsplit(".", 1)[-1] if "." in name else ""
        if ext != "import" and ext not in ASSET_EXTS[parts[1]]:
            allowed = ", ".join(ASSET_EXTS[parts[1]])
            items.append(_item(rel, "asset", f"assets/{parts[1]}/ takes .{allowed} files"))
        if not is_core and not name.startswith(f"{pack_id}_"):
            items.append(_item(rel, "asset", f"name must start with '{pack_id}_'"))


def _lfs_pointers(pack_dir: Path, items: list[dict]) -> None:
    """A file that is a Git LFS pointer: a checkout without git-lfs left it instead of the binary."""
    for path in sorted(pack_dir.rglob("*")):
        if path.is_symlink() or not path.is_file() or path.stat().st_size >= LFS_MAX:
            continue
        try:
            head = path.read_bytes()
        except OSError:
            continue
        if head.startswith(LFS_HEADER):
            items.append(
                _item(
                    path.relative_to(pack_dir).as_posix(),
                    "lfs",
                    "is a Git LFS pointer, not the real file: install git-lfs "
                    "(git lfs install) and run `git lfs pull`",
                )
            )


def lint(pack_dir: Path, cats: dict, allow_lfs_pointers: bool = False) -> list[dict]:
    pack_dir = Path(pack_dir)
    items: list[dict] = []
    manifest = _manifest(pack_dir, cats, items)
    _defs(pack_dir, cats, manifest, items)
    _assets(pack_dir, cats, manifest, items)
    if not allow_lfs_pointers:
        _lfs_pointers(pack_dir, items)
    return items


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Lint content packs without Godot.")
    ap.add_argument(
        "--categories",
        help="pack_categories.json (default: next to this script, else sim/ in the game repo)",
    )
    ap.add_argument(
        "--allow-lfs-pointers",
        action="store_true",
        help="for CI checkouts without LFS files; check_repo.py checks pointers itself",
    )
    ap.add_argument("--json", action="store_true", help="print findings as JSON")
    ap.add_argument("packs", nargs="+")
    args = ap.parse_args(argv)
    here = Path(__file__).resolve().parent
    beside = here / "pack_categories.json"
    cats_path = args.categories or str(
        beside if beside.is_file() else here.parents[1] / "sim" / "pack_categories.json"
    )
    try:
        cats = json.loads(Path(cats_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"lint_pack: cannot read {cats_path}: {e}", file=sys.stderr)
        return 1
    found: list[dict] = []
    for p in args.packs:
        path = Path(p)
        if not path.is_dir():
            print(f"lint_pack: {p} is not a directory", file=sys.stderr)
            return 1
        for it in lint(path, cats, args.allow_lfs_pointers):
            found.append({**it, "file": f"{p.rstrip('/')}/{it['file']}"})
    if args.json:
        print(json.dumps(found, indent=2))
    else:
        for it in found:
            print(f"{it['file']}: [{it['rule']}] {it['message']}")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
