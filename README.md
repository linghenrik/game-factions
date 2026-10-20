# game-factions

Faction packs: heroes, minions, abilities, items and towers.

A content repo for the game: packs of JSON definitions and art, one folder per pack (the folder name is the pack id). The game copies these packs in, and **merging to `main` ships to ranked**, so the owner approves every pull request.

- How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md).
- With an AI agent: the `add-content` skill (`.claude/skills/add-content/`) walks it through adding a hero, tower, item, monster or camp.
- Before you push: `uv run pack-tools/check_repo.py` (see [pack-tools](pack-tools/README.md)).

## Licence

This repository is public so that anyone can read it, but its licence is not decided yet. Until it is, all rights are reserved: apart from what GitHub's Terms of Service allow (viewing and forking on GitHub), nothing here may be copied or reused. Third-party assets keep their own licences, listed in [CREDITS.md](CREDITS.md) and in each pack's `CREDITS.md`.

For now, only collaborators can open issues and pull requests. To take part, ask the owner.
