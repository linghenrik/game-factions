# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Markdown summary of what changed between two pack trees (content repos v2 C3).

Standard library only and no sibling imports: step 18 copies this file into each
content repo's kit.

    uv run change_summary.py <old> <new>

Either side is a pack folder (it has pack.json) or a root whose child folders are
packs, paired by folder name. A missing side or pack means added or removed.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

PRESENTATION = {"assets", "vfx", "sfx", "voice", "lore", "name", "description"}
MAP_PRESENTATION = PRESENTATION | {"ground"}


def _skip(rel: str) -> bool:
    return rel.endswith(".import") or any(p.startswith(".") for p in rel.split("/"))


def _packs(side: Path | None) -> dict[str, Path]:
    if side is None or not Path(side).is_dir():
        return {}
    side = Path(side)
    if (side / "pack.json").is_file():
        return {side.name: side}
    return {
        d.name: d
        for d in sorted(side.iterdir())
        if d.is_dir() and not d.name.startswith(".") and (d / "pack.json").is_file()
    }


def _json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _defs(pack: Path | None) -> dict[str, tuple[str, dict]]:
    out: dict[str, tuple[str, dict]] = {}
    if pack is None:
        return out
    for path in sorted(pack.glob("*/*.json")):
        rel = path.relative_to(pack).as_posix()
        if rel.startswith("assets/") or _skip(rel):
            continue
        d = _json(path)
        if isinstance(d, dict) and isinstance(d.get("id"), str):
            out[d["id"]] = (rel, d)
    return out


def _assets(pack: Path | None) -> dict[str, str]:
    """relpath -> sha256 hex of the bytes, so big binaries are not held in memory."""
    out: dict[str, str] = {}
    if pack is None or not (pack / "assets").is_dir():
        return out
    for path in sorted((pack / "assets").rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(pack).as_posix()
        if not _skip(rel):
            out[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


def _terrain_model_only(a, b) -> bool:
    if not isinstance(a, list) or not isinstance(b, list) or len(a) != len(b):
        return False

    def strip(e):
        return {k: v for k, v in e.items() if k != "model_3d"} if isinstance(e, dict) else e

    return all(strip(x) == strip(y) for x, y in zip(a, b, strict=True))


def _changed_keys(old: dict, new: dict) -> list[str]:
    return sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))


def _is_presentation(key: str, old: dict, new: dict) -> bool:
    kind = new.get("kind", old.get("kind"))
    if key in PRESENTATION:
        return True
    if kind == "map":
        if key == "ground":
            return True
        if key == "terrain":
            return _terrain_model_only(old.get("terrain"), new.get("terrain"))
    return False


def _ticks(names: list[str]) -> str:
    return ", ".join(f"`{n}`" for n in names)


def _pack_section(name: str, old: Path | None, new: Path | None) -> str | None:
    old_m = (_json(old / "pack.json") if old else None) or {}
    new_m = (_json(new / "pack.json") if new else None) or {}
    old_defs, new_defs = _defs(old), _defs(new)
    lines: list[str] = []
    changed_lines: list[str] = []
    all_presentation = True
    any_changed = False
    for did in sorted(set(old_defs) & set(new_defs)):
        (_, od), (nrel, nd) = old_defs[did], new_defs[did]
        keys = _changed_keys(od, nd)
        if not keys:
            continue
        any_changed = True
        pres = all(_is_presentation(k, od, nd) for k in keys)
        all_presentation = all_presentation and pres
        label = "presentation-only (" if pres else ""
        tail = f"{label}{_ticks(keys)}{')' if pres else ''}"
        changed_lines.append(f"- changed `{did}` (`{nrel}`): {tail}")
    lines += changed_lines
    moved = sorted(
        did for did in set(old_defs) & set(new_defs) if old_defs[did][0] != new_defs[did][0]
    )
    for did in moved:
        lines.append(f"- moved `{did}` (`{old_defs[did][0]}` → `{new_defs[did][0]}`)")
    for did in sorted(set(new_defs) - set(old_defs)):
        lines.append(f"- added `{did}` (`{new_defs[did][0]}`)")
    for did in sorted(set(old_defs) - set(new_defs)):
        lines.append(f"- removed `{did}` (`{old_defs[did][0]}`)")
    manifest_gameplay = False
    if old and new:
        keys = [k for k in _changed_keys(old_m, new_m) if k != "version"]
        if keys:
            lines.append(f"- manifest: changed {_ticks(keys)}")
            manifest_gameplay = any(k not in PRESENTATION for k in keys)
    old_a, new_a = _assets(old), _assets(new)
    parts = []
    added = sorted(set(new_a) - set(old_a))
    removed = sorted(set(old_a) - set(new_a))
    changed = sorted(r for r in set(old_a) & set(new_a) if old_a[r] != new_a[r])
    if added:
        parts.append(f"added {_ticks(added)}")
    if changed:
        parts.append(f"changed {_ticks(changed)}")
    if removed:
        parts.append(f"removed {_ticks(removed)}")
    if parts:
        lines.append("- assets: " + "; ".join(parts))
    ov, nv = old_m.get("version"), new_m.get("version")
    version_changed = old is not None and new is not None and ov != nv
    if not lines and not version_changed:
        return None
    header = f"### {name}"
    if version_changed:
        header += f" {ov} → {nv}"
    # Asset changes are presentation by nature; a manifest key (dependencies,
    # overrides, ...) or a moved def is not.
    same_defs = set(new_defs) == set(old_defs) and not moved
    if any_changed and all_presentation and same_defs and not manifest_gameplay:
        header += " (presentation-only)"
    if old is None:
        header += " (new pack)"
    elif new is None:
        header += " (removed pack)"
    return "\n".join([header, *lines])


def summarize(old: Path | None, new: Path | None) -> str:
    old_p, new_p = _packs(old), _packs(new)
    # A pair of single pack folders with different folder names is one pack.
    single = (
        old is not None
        and new is not None
        and (Path(old) / "pack.json").is_file()
        and (Path(new) / "pack.json").is_file()
    )
    if single:
        old_p = {next(iter(new_p)): next(iter(old_p.values()))}
    sections = []
    for name in sorted(set(old_p) | set(new_p)):
        sec = _pack_section(name, old_p.get(name), new_p.get(name))
        if sec:
            sections.append(sec)
    if not sections:
        return "No pack changes.\n"
    return "\n\n".join(sections) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("usage: change_summary.py <old> <new>", file=sys.stderr)
        return 2
    old = Path(args[0]) if args[0] else None
    new = Path(args[1]) if args[1] else None
    for p in (old, new):
        if p is not None and not p.exists():
            print(f"change_summary: {p} does not exist", file=sys.stderr)
            return 1
    sys.stdout.write(summarize(old, new))
    return 0


if __name__ == "__main__":
    sys.exit(main())
