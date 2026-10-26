# pack-tools

Tools for checking packs. They come from the game repo, so **don't edit them here**: the owner updates this folder (and `.github/`, `.claude/`, `.gitattributes`, `.gitignore`) with a pull request.

| File | What it does |
|---|---|
| `check_repo.py` | The one check: the repo rules (Git LFS, no `.import` files), the lint of every pack, the audio licence check, and a summary of your committed changes against `origin/main`. The pull request's **Content checks** run the same thing. `uv run pack-tools/check_repo.py` |
| `lint_pack.py` | Fast pack lint, no game needed: `uv run pack-tools/lint_pack.py <pack folder>` |
| `change_summary.py` | What changed between two copies of a pack, as Markdown: `uv run pack-tools/change_summary.py <old> <new>` |
| `art_credits.py` | The art licence gate: every model, icon and texture under `assets/` needs a row in the `## Art` table of the pack's `CREDITS.md`, with an allowed licence, and no credit may name a banned generator. `check_repo.py` runs it. `uv run pack-tools/art_credits.py <pack folder>` |
| `audio_credits.py` | The audio licence gate: every sound under `assets/audio/` needs a row in the pack's `CREDITS.md`, and only CC0 or public-domain sounds pass. `check_repo.py` runs it. `uv run pack-tools/audio_credits.py <pack folder>` |
| `pack_categories.json` | Which folders and kinds each pack category may hold (the game's own table) |
| `templates/` | A `pack.json` to start a new faction, map or jungle pack (ask the owner first) |

Install [uv](https://docs.astral.sh/uv/) once; it fetches the right Python by itself.
