# Contributing

## What this repo is

This repo holds packs: JSON definitions and art, one folder per pack (every top-level folder except `pack-tools` and `docs` counts as a pack). **Merging to `main` ships to ranked**, so the owner approves every pull request. Pull requests are merged as one squashed commit.

The repo is public: everyone can read it, but only collaborators can open pull requests and issues. The licence isn't decided yet; see README.md.

## One-time setup

1. Install git, git-lfs (`brew install git-lfs`, or https://git-lfs.com) and [uv](https://docs.astral.sh/uv/). On Windows: `winget install Git.Git GitHub.GitLFS astral-sh.uv`.
2. Turn on Git LFS once per machine: `git lfs install`
3. Clone this repo and open the folder.

## The loop

1. Make a branch: `git switch -c <your-name>/<what>`
2. Edit one pack, and only one.
3. Commit: `git add <pack folder>` then `git commit -m "<what you did>"`
4. Check your work: `git fetch` then `uv run pack-tools/check_repo.py`
5. If it reports anything, fix it, commit again and repeat step 4.
6. Push: `git push -u origin HEAD`
7. Open the pull request on GitHub and fill in the template.
8. Wait for **Content checks** to pass and for the owner's review.
9. If GitHub says the branch is out of date, press **Update branch**.

## With an AI agent

Claude Code finds the `add-content` skill (`.claude/skills/add-content/`) by itself. For other agents, point them at `AGENTS.md`.

## The rules

- One pack per pull request.
- Don't change `version` in `pack.json`. The owner does that.
- No `.import` files. Godot makes them; they stay out of git.
- Binary files (`.glb`, `.png`, `.ogg`, `.wav`) go through Git LFS. If you committed one without LFS, fix it in a new commit; no history rewrite is needed.
- `pack-tools/`, `.github/`, `.claude/`, `.gitattributes`, `.gitignore`, `CREDITS.md`, `AGENTS.md` and `CLAUDE.md` are the owner's. The owner updates them from the game repo.

## Getting help

Ask the owner.
