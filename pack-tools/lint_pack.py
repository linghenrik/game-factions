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
import struct
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

# Budgets and clips. Pinned to client/assets_3d.gd (TRI_BUDGET, SIZE_BUDGET, ICON_*,
# TEXTURE_*, REQUIRED_ANIMS) by test_budget_constants_match_assets_3d; keep them equal.
MODEL_TRI_BUDGET = 10000
MODEL_SIZE_BUDGET = 5 * 1024 * 1024  # bytes
ICON_SIZE_BUDGET = 256 * 1024  # bytes
ICON_MAX_DIM = 1024  # px, declared width/height/viewBox
TEXTURE_SIZE_BUDGET = 8 * 1024 * 1024  # bytes
TEXTURE_MAX_DIM = 4096  # px
_ANIMS = ("idle", "run", "attack")
REQUIRED_CLIPS = {"hero": _ANIMS, "minion": _ANIMS, "monster": _ANIMS, "worker": ("idle", "run")}
# The clip names the renderer plays (client/anim_state.gd, client/entity_view_3d.gd).
KNOWN_CLIPS = ("idle", "run", "attack", "hit", "death", "stun")
_GLB_MAGIC = b"glTF"
_GLB_JSON_CHUNK = 0x4E4F534A  # "JSON", little-endian
_DRACO = "KHR_draco_mesh_compression"
_BARE_NAME = re.compile(r"^[A-Za-z0-9_.\-]+$")


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


def _defs(
    pack_dir: Path, cats: dict, manifest: dict | None, items: list[dict]
) -> list[tuple[str, list[str]]]:
    """Lint the defs; return (kind, model keys) for every def that names a model."""
    uses: list[tuple[str, list[str]]] = []
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
        art = d.get("assets")
        if isinstance(art, dict) and isinstance(kind, str):
            keys = [art.get("model_3d"), art.get("model_fallback")]
            uses.append((kind, [k for k in keys if isinstance(k, str) and _BARE_NAME.match(k)]))
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
    return uses


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


def _lfs_size(data: bytes) -> int | None:
    """The byte size a Git LFS pointer's `size <n>` line declares, or None if it isn't a pointer."""
    if len(data) >= LFS_MAX or not data.startswith(LFS_HEADER):
        return None
    m = re.search(rb"^size (\d+)$", data, re.MULTILINE)
    return int(m.group(1)) if m else 0


def glb_info(data: bytes) -> dict | str:
    """Triangles, animation clip names and extensionsRequired of a binary glTF 2.0 file.

    Returns a message instead when the bytes are not one. Reads only the JSON chunk: an
    accessor's `count` is all the triangle count needs, so no buffer is decoded.
    """
    if len(data) < 20:
        return "too short to be a .glb"
    magic, version, total = struct.unpack_from("<4sII", data, 0)
    if magic != _GLB_MAGIC:
        return "does not start with the 'glTF' magic bytes"
    if version != 2:
        return f"is glTF version {version}, not 2"
    if total > len(data):
        return f"is truncated (header says {total} bytes, file has {len(data)})"
    length, ctype = struct.unpack_from("<II", data, 12)
    if ctype != _GLB_JSON_CHUNK:
        return "has no JSON chunk first"
    if 20 + length > len(data):
        return "has a JSON chunk longer than the file"
    try:
        gltf = json.loads(data[20 : 20 + length].decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as e:
        return f"has a JSON chunk that does not parse: {e}"
    if not isinstance(gltf, dict):
        return "has a JSON chunk that is not an object"
    try:
        tris = _gltf_tris(gltf)
        clips = [
            str(a.get("name", "")) if isinstance(a, dict) else ""
            for a in gltf.get("animations", [])
        ]
        required = [str(e) for e in gltf.get("extensionsRequired", [])]
    except (TypeError, ValueError, KeyError, IndexError, AttributeError):
        return "has glTF JSON with a malformed mesh, accessor, node or animation list"
    return {"tris": tris, "clips": clips, "required": required}


def _gltf_tris(gltf: dict) -> int:
    """Triangles summed per node that has a mesh, as Godot sums per MeshInstance3D."""
    accessors = gltf.get("accessors", [])
    per_mesh = []
    for mesh in gltf.get("meshes", []):
        n = 0
        for prim in mesh.get("primitives", []):
            mode = prim.get("mode", 4)
            if "indices" in prim:
                count = int(accessors[prim["indices"]]["count"])
            else:
                count = int(accessors[prim["attributes"]["POSITION"]]["count"])
            if mode == 4:
                n += count // 3
            elif mode in (5, 6):
                n += max(count - 2, 0)
        per_mesh.append(n)
    return sum(per_mesh[node["mesh"]] for node in gltf.get("nodes", []) if "mesh" in node)


def _to_float(text: str) -> float:
    """Godot's String.to_float: the number the text starts with, else 0."""
    m = re.match(r"\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)", text)
    return float(m.group(1)) if m else 0.0


def svg_declared_dim(text: str) -> float:
    """Largest of the root <svg> tag's width/height and viewBox extent (0 if none).

    Mirrors Assets3D._svg_declared_dim (client/assets_3d.gd), quirks included: `\\b` also
    matches inside `stroke-width`.
    """
    start = text.find("<svg")
    if start < 0:
        return 0.0
    end = text.find(">", start)
    tag = text[start:] if end < 0 else text[start:end]
    dim = 0.0
    for m in re.finditer(r"\b(?:width|height)\s*=\s*[\"']\s*([0-9.]+)", tag):
        dim = max(dim, _to_float(m.group(1)))
    vb = re.search(r"\bviewBox\s*=\s*[\"']([^\"']*)", tag)
    if vb is not None:
        parts = [p for p in vb.group(1).replace(",", " ").split(" ") if p]
        if len(parts) == 4:
            dim = max(dim, _to_float(parts[2]), _to_float(parts[3]))
    return dim


def _png_dim(head: bytes) -> int:
    """The larger of the IHDR width and height (big-endian u32 at byte 16); 0 if too short."""
    if len(head) < 24:
        return 0
    return max(struct.unpack_from(">II", head, 16))


def _size_item(rel: str, size: int, budget: int, pointer: bool) -> dict:
    where = "its LFS pointer says" if pointer else "is"
    return _item(
        rel,
        "budget",
        f"{where} {size:,} bytes, over the {budget:,}-byte budget: shrink or compress the file",
    )


def _budgets(
    pack_dir: Path,
    manifest: dict | None,
    items: list[dict],
    allow_lfs_pointers: bool,
    uses: list[tuple[str, list[str]]] | None = None,
) -> None:
    """Size, triangle, pixel and clip checks on the pack's own models, icons and textures.

    `uses` is what _defs collected: (kind, model keys) per def. Only keys whose file is in
    this pack are checked; a key that names a model in another pack is skipped.
    """
    assets = pack_dir / "assets"
    if not assets.is_dir():
        return
    need: dict[str, set[str]] = {}  # model key -> clips its kinds need
    kinds: dict[str, set[str]] = {}
    for kind, keys in uses or []:
        for key in keys if kind in REQUIRED_CLIPS else []:
            need.setdefault(key, set()).update(REQUIRED_CLIPS[kind])
            kinds.setdefault(key, set()).add(kind)
    if isinstance(manifest, dict) and manifest.get("category") == "core":
        need.setdefault("worker", set()).update(REQUIRED_CLIPS["worker"])
        kinds.setdefault("worker", set()).add("worker")
    for path in sorted(assets.rglob("*")):
        rel = path.relative_to(pack_dir).as_posix()
        parts = rel.split("/")
        if not path.is_file() or any(p.startswith(".") for p in parts) or len(parts) != 3:
            continue
        ext = parts[2].rsplit(".", 1)[-1] if "." in parts[2] else ""
        folder = parts[1]
        if (folder, ext) not in (("models", "glb"), ("icons", "svg"), ("textures", "png")):
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        pointer = _lfs_size(data)
        if pointer is not None:
            if allow_lfs_pointers:  # the real file isn't here: only its declared size is known
                budget = {"models": MODEL_SIZE_BUDGET, "icons": ICON_SIZE_BUDGET}.get(
                    folder, TEXTURE_SIZE_BUDGET
                )
                if pointer > budget:
                    items.append(_size_item(rel, pointer, budget, True))
            continue  # not allowed: _lfs_pointers already reports it
        if folder == "models":
            _check_model(rel, data, parts[2][: -len(".glb")], need, kinds, items)
        elif folder == "icons":
            _check_pixels(rel, data, ICON_SIZE_BUDGET, ICON_MAX_DIM, items)
        else:
            _check_pixels(rel, data, TEXTURE_SIZE_BUDGET, TEXTURE_MAX_DIM, items)


def _check_pixels(rel: str, data: bytes, size_budget: int, max_dim: int, items: list[dict]) -> None:
    if len(data) > size_budget:
        items.append(_size_item(rel, len(data), size_budget, False))
        return
    if rel.endswith(".svg"):
        dim = svg_declared_dim(data.decode("utf-8", errors="replace"))
    else:
        dim = _png_dim(data[:24])
    if dim > max_dim:
        items.append(
            _item(
                rel,
                "budget",
                f"declares {int(dim)} px, over the {max_dim} px budget: "
                f"resize it to {max_dim} px or less",
            )
        )


def _check_model(
    rel: str,
    data: bytes,
    key: str,
    need: dict[str, set[str]],
    kinds: dict[str, set[str]],
    items: list[dict],
) -> None:
    if len(data) > MODEL_SIZE_BUDGET:  # the game refuses to load it, so nothing else to check
        items.append(_size_item(rel, len(data), MODEL_SIZE_BUDGET, False))
        return
    info = glb_info(data)
    if isinstance(info, str):
        items.append(_item(rel, "model", f"is not a valid binary glTF 2.0 file: it {info}"))
        return
    if _DRACO in info["required"]:
        items.append(
            _item(
                rel,
                "model",
                "Godot can't load Draco-compressed models: export without mesh compression",
            )
        )
    if info["tris"] > MODEL_TRI_BUDGET:
        items.append(
            _item(
                rel,
                "budget",
                f"{info['tris']:,} triangles, over the {MODEL_TRI_BUDGET:,} budget: "
                "decimate it (Blender: Decimate modifier)",
            )
        )
    clips = info["clips"]
    unknown = [c for c in clips if c not in KNOWN_CLIPS]
    if unknown:
        names = ", ".join(f"'{c}'" for c in unknown)
        items.append(
            _item(
                rel,
                "clips",
                f"clip {names} is not one the game plays ({', '.join(KNOWN_CLIPS)}): "
                "rename the clips",
            )
        )
    missing = [c for c in KNOWN_CLIPS if c in need.get(key, ()) and c not in clips]
    if missing:
        names = " and ".join(f"'{c}'" for c in missing)
        who = "/".join(sorted(kinds[key]))
        items.append(
            _item(
                rel,
                "clips",
                f"has no {names} clip, which a {who} model needs: add "
                f"{'it' if len(missing) == 1 else 'them'} (needs {', '.join(sorted(need[key]))})",
            )
        )


def lint(pack_dir: Path, cats: dict, allow_lfs_pointers: bool = False) -> list[dict]:
    pack_dir = Path(pack_dir)
    items: list[dict] = []
    manifest = _manifest(pack_dir, cats, items)
    uses = _defs(pack_dir, cats, manifest, items)
    _assets(pack_dir, cats, manifest, items)
    _budgets(pack_dir, manifest, items, allow_lfs_pointers, uses)
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
