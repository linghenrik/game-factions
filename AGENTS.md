# Rules for AI agents (and people) in this content repo

- To add or change content, follow the `add-content` skill: `.claude/skills/add-content/SKILL.md`.
- Work on a branch. Never push to `main`: merging to `main` ships to ranked, and the owner approves every pull request.
- One pack per pull request. Don't change `version` in `pack.json`.
- Before you push, run `uv run pack-tools/check_repo.py` and fix everything it reports. Paste its change summary into the pull request.
- Big files (`.glb`, `.png`, `.ogg`, `.wav`) go through Git LFS: run `git lfs install` once per machine, before your first commit.
- Don't edit `pack-tools/`, `.github/`, `.claude/`, `.gitattributes`, `.gitignore`, this file or `CLAUDE.md`. The owner updates them from the game repo.
