# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Art licence gate: every model, icon and texture in a pack is free to share (TODO step 24).

Standard library only and no sibling imports: the content-repo kit copies this file
into each content repo (pack-tools/), so friends' art passes the same gate.

A pack that ships files under assets/models/, assets/icons/ or assets/textures/
lists every one of them in the pack's CREDITS.md, in the table under a "## Art" heading:

    | File | Licence | Source | Author | Edits |
    |---|---|---|---|---|
    | assets/models/crab.glb | CC0-1.0 | https://quaternius.com/ | name | decimated |

Source is one of:
  - an https URL (third-party art); Licence is CC0-1.0, PDM-1.0, CC-BY-3.0 or CC-BY-4.0;
  - "generated: <tool> <version> [<plan>] <YYYY-MM-DD>; <prompt, seed, inputs>" for art
    a contributor generated; Licence is LicenseRef-Contributor and Author is that person.
    The plan is a paid tier or "local" (a free tier is refused);
  - "made: <who, how>" for art made by hand (Blender, Inkscape, ...); Licence is
    LicenseRef-Contributor and Author is the person who made it.
Cells never contain "|".

Every table row in CREDITS.md (Audio too) is also scanned for tools whose licence bars
shipping their output (see BANNED).

    uv run art_credits.py <pack_dir>...      exit 1 and one line per problem
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ART_DIRS = {"models": (".glb",), "icons": (".svg",), "textures": (".png",)}
THIRD_PARTY_LICENCES = ("CC0-1.0", "PDM-1.0", "CC-BY-3.0", "CC-BY-4.0")
CONTRIBUTOR_LICENCE = "LicenseRef-Contributor"
HEADER = ["File", "Licence", "Source", "Author", "Edits"]
GENERATED = "generated: "
MADE = "made: "
GENERATED_RE = re.compile(
    r"^generated: \S.*? \[(?P<plan>[^\]]+)\] (?P<date>\d{4}-\d{2}-\d{2})(;|$)"
)
# A separator between the parts of a name: space, dot, underscore, dash, square brackets.
_S = r"[\s._\-\[\]]*"
BANNED = (
    (r"mixamo", "personal licence, no redistribution"),
    (rf"actor{_S}core", "the licence bars publishing"),
    (r"accurig", "the licence bars publishing"),
    (rf"flux{_S}[12]{_S}(?:kontext{_S}|krea{_S})?dev", "non-commercial weights"),
    (rf"klein{_S}9b", "non-commercial weights"),
    (rf"qwen{_S}image", "non-commercial weights"),
    (rf"hunyuan{_S}3d", "no licence in the EU, UK or KR"),
    (r"udio", "ownership limits, or games excluded"),
    (r"suno", "ownership limits, or games excluded"),
    (r"musicgen", "non-commercial"),
    (r"audiogen", "non-commercial"),
    (r"sonniss", 'redistribution "as sound effects" is banned'),
)
# Letters and digits only bound a name, so "flux1_dev" and "FLUX.1 [dev]" match but "audiogenic" does not.
_BANNED_RES = tuple(
    (re.compile(rf"(?<![a-z0-9]){p}(?![a-z0-9])", re.IGNORECASE), why) for p, why in BANNED
)


def _is_extracted_texture(rel: str) -> bool:
    # Textures an editor import extracts from a .glb; gitignored, not pack assets.
    parts = rel.split("/")
    return len(parts) == 3 and parts[:2] == ["assets", "models"] and parts[2].endswith(".png")


def art_files(pack_dir: Path) -> list[str]:
    found: list[str] = []
    for sub, exts in ART_DIRS.items():
        root = pack_dir / "assets" / sub
        if not root.is_dir():
            continue
        for p in root.rglob("*"):
            rel = p.relative_to(pack_dir).as_posix()
            if p.is_file() and p.suffix in exts and not _is_extracted_texture(rel):
                found.append(rel)
    return sorted(found)


def _split(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def credit_rows(text: str, section: str = "Art") -> tuple[list[dict[str, str]], list[str]]:
    """The rows of the table under '## <section>', and any problems reading it."""
    rows: list[dict[str, str]] = []
    problems: list[str] = []
    in_section = False
    seen_header = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            in_section = line.strip() == f"## {section}"
            continue
        if not in_section or not line.startswith("|"):
            continue
        cells = _split(line)
        if not seen_header:
            if cells != HEADER:
                problems.append(
                    f"CREDITS.md:{n}: the {section} table header must be | {' | '.join(HEADER)} |"
                )
                return rows, problems
            seen_header = True
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue  # the |---| separator
        if len(cells) != len(HEADER):
            problems.append(f"CREDITS.md:{n}: a row needs {len(HEADER)} cells")
            continue
        rows.append(dict(zip(HEADER, cells, strict=True)) | {"line": str(n)})
    return rows, problems


def banned_problems(name: str, text: str) -> list[str]:
    """Banned tools named in the Source or Edits cell of any table row, under any heading."""
    problems: list[str] = []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.startswith("|"):
            continue
        cells = _split(line)
        if len(cells) != len(HEADER) or cells == HEADER:
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        scanned = f"{cells[2]} {cells[4]}"
        for rx, why in _BANNED_RES:
            m = rx.search(scanned)
            if m:
                problems.append(
                    f"{name}/CREDITS.md:{n}: {m.group(0)} may not be used: {why} "
                    f'(docs/art-pipeline.md, "Do not use")'
                )
    return problems


def _check_row(where: str, r: dict[str, str]) -> list[str]:
    src, lic = r["Source"], r["Licence"]
    if src.startswith("https://") and src[len("https://") :].strip():
        if lic not in THIRD_PARTY_LICENCES:
            allowed = ", ".join(THIRD_PARTY_LICENCES)
            return [f"{where}: licence '{lic}' is not one of {allowed} (third-party art)"]
        return []
    if src.startswith(GENERATED):
        m = GENERATED_RE.match(src)
        if not m:
            fmt = f"'{GENERATED}<tool> <version> [<plan>] <YYYY-MM-DD>; <prompt, seed, inputs>'"
            return [f"{where}: a generated source reads {fmt}"]
        out = []
        if re.search(r"free", m.group("plan"), re.IGNORECASE):
            out.append(
                f"{where}: plan '{m.group('plan')}' is a free tier; use a paid plan "
                "or a local tool ([local])"
            )
        if lic != CONTRIBUTOR_LICENCE:
            out.append(f"{where}: a generated file is licensed {CONTRIBUTOR_LICENCE}, not '{lic}'")
        return out
    if src.startswith(MADE) and src[len(MADE) :].strip():
        if lic != CONTRIBUTOR_LICENCE:
            return [f"{where}: a hand-made file is licensed {CONTRIBUTOR_LICENCE}, not '{lic}'"]
        return []
    return [f"{where}: source must be an https URL, '{GENERATED}...' or '{MADE}...'"]


def check_pack(pack_dir: Path) -> list[str]:
    name = pack_dir.name
    if not pack_dir.is_dir():
        return [f"{name}: not a pack directory"]
    files = art_files(pack_dir)
    credits = pack_dir / "CREDITS.md"
    if not credits.is_file():
        return [f"{name}: has art but no CREDITS.md"] if files else []
    try:
        text = credits.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"{name}: CREDITS.md is not valid UTF-8"]
    problems = banned_problems(name, text)
    rows, read_problems = credit_rows(text)
    problems += [f"{name}/{p}" for p in read_problems]
    by_file: dict[str, dict[str, str]] = {}
    for r in rows:
        where = f"{name}/CREDITS.md:{r['line']}"
        if r["File"] in by_file:
            problems.append(f"{where}: {r['File']} is listed twice")
        by_file[r["File"]] = r
        problems += _check_row(where, r)
        if not r["Author"]:
            problems.append(f"{where}: author is empty")
        if r["File"] not in files:
            problems.append(f"{where}: {r['File']} is not in the pack")
    for f in files:
        if f not in by_file:
            problems.append(f"{name}: {f} has no row in CREDITS.md")
    return problems


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: art_credits.py <pack_dir>...")
        return 2
    problems = [p for d in argv for p in check_pack(Path(d))]
    for p in problems:
        print(p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
