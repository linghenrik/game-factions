# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Audio licence gate: every sound in a pack is free to share (TODO step 29).

Standard library only and no sibling imports: the content-repo kit copies this file
into each content repo (pack-tools/), so friends' sounds pass the same gate.

A pack that ships files under assets/audio/ lists every one of them in the
pack's CREDITS.md, in the table under a "## Audio" heading:

    | File | Licence | Source | Author | Edits |
    |---|---|---|---|---|
    | assets/audio/hit.ogg | CC0-1.0 | https://freesound.org/s/123/ | name | trimmed, mono |

Licence is CC0-1.0, or PDM-1.0 for public-domain recordings. Source is an https
URL, or "generated: <model> <version>, prompt "...", seed N" for a sound we made
ourselves, which we release as CC0-1.0. Cells never contain "|".

    uv run audio_credits.py <pack_dir>...      exit 1 and one line per problem
"""

from __future__ import annotations

import sys
from pathlib import Path

ALLOWED_LICENCES = ("CC0-1.0", "PDM-1.0")
AUDIO_EXTS = (".ogg", ".wav")
HEADER = ["File", "Licence", "Source", "Author", "Edits"]
GENERATED = "generated: "


def audio_files(pack_dir: Path) -> list[str]:
    root = pack_dir / "assets" / "audio"
    if not root.is_dir():
        return []
    # Only assets/audio/*.ogg|.wav: lint_pack rejects audio anywhere else, and any other extension.
    return sorted(
        p.relative_to(pack_dir).as_posix()
        for p in root.rglob("*")
        if p.is_file() and p.suffix in AUDIO_EXTS
    )


def credit_rows(text: str) -> tuple[list[dict[str, str]], list[str]]:
    """The rows of the table under '## Audio', and any problems reading it."""
    rows: list[dict[str, str]] = []
    problems: list[str] = []
    in_section = False
    seen_header = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            in_section = line.strip() == "## Audio"
            continue
        if not in_section or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not seen_header:
            if cells != HEADER:
                problems.append(
                    f"CREDITS.md:{n}: the Audio table header must be | {' | '.join(HEADER)} |"
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


def _has_source(src: str) -> bool:
    """An https URL or a 'generated: ...' note, with something after the prefix."""
    return any(src.startswith(p) and src[len(p) :].strip() for p in ("https://", GENERATED))


def check_pack(pack_dir: Path) -> list[str]:
    name = pack_dir.name
    if not pack_dir.is_dir():
        return [f"{name}: not a pack directory"]
    files = audio_files(pack_dir)
    if not files:
        return []
    credits = pack_dir / "CREDITS.md"
    if not credits.is_file():
        return [f"{name}: has audio but no CREDITS.md"]
    try:
        text = credits.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"{name}: CREDITS.md is not valid UTF-8"]
    rows, read_problems = credit_rows(text)
    problems = [f"{name}/{p}" for p in read_problems]
    by_file: dict[str, dict[str, str]] = {}
    for r in rows:
        where = f"{name}/CREDITS.md:{r['line']}"
        if r["File"] in by_file:
            problems.append(f"{where}: {r['File']} is listed twice")
        by_file[r["File"]] = r
        if r["Licence"] not in ALLOWED_LICENCES:
            allowed = ", ".join(ALLOWED_LICENCES)
            problems.append(f"{where}: licence '{r['Licence']}' is not one of {allowed}")
        src = r["Source"]
        if not _has_source(src):
            problems.append(f"{where}: source must be an https URL or '{GENERATED}...'")
        if src.startswith(GENERATED) and r["Licence"] != "CC0-1.0":
            problems.append(f"{where}: a generated sound is released as CC0-1.0")
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
        print("usage: audio_credits.py <pack_dir>...")
        return 2
    problems = [p for d in argv for p in check_pack(Path(d))]
    for p in problems:
        print(p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
