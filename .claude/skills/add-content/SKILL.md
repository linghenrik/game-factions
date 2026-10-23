---
name: add-content
description: Use when adding or changing game content (a hero, tower, shop item, minion, monster, camp, ability, augment, map or whole pack), its lore slots or its art files; when editing a content pack (a folder with a pack.json) in a content repo clone such as game-arena or game-factions; or when a pack lint error, a change summary, or a failed game-validate check needs explaining.
---

# Adding content

Written for a clone of a **content repo** (`game-arena` or `game-factions`), with no game repo next to it. Sections 1 to 7 are the whole route. Section 8 is only for the owner, who also has the game repo.

Content is data: JSON defs plus asset files, grouped in packs. You never write game code. The game loads a pack by reading its `pack.json` and the JSON files in its folders.

## 1. Where content lives

One top-level folder per pack, and the folder name is the pack id.

- **game-arena:** `base/` (the core pack), `map_<slug>/` (one map each) and `jungle_<slug>/` (monsters, camps, camp items).
- **game-factions:** `swarm/`, `elite/`, `utility/` (one faction each).

**Branches and `main`.** Work on a branch, never on `main`. **Merging to `main` ships to ranked**, and once the owner switches on branch previews every pushed branch is playable too. So the owner approves every PR, and a PR merges as one squashed commit. Keep PRs small, and put nothing half-done on `main`.

**Rules for the files.**
- A def is one JSON object in one file, exactly one folder deep: `<pack>/<folder>/<name>.json`. Nothing deeper.
- Def ids are `<pack>.<kind>.<name>`, for example `base.tower.silo`. The middle word is `hero`, `tower`, `shop_item`, `monster`, `camp`, `ability`, `augment`, and `unit` for a minion (`swarm.unit.swarmling`). The file name is `<name>.json`. A `<name>` is lowercase letters, digits and `_`. The lint only enforces the `<pack>.` start; keep to the rest so ids match their neighbours.
- Files are UTF-8 with LF line endings. Git stores them byte for byte, so a stray CRLF changes the pack.
- Start from a real def of the same kind (section 2): copy it, rename it, change the numbers.
- If the pack has no folder for that kind yet (for example `swarm/towers/`), create it. A pack's folders hold only the kinds its category allows.

**Pack ids and manifests.** A new pack needs a `pack.json` next to its folders. Start it from a template: copy `pack-tools/templates/<category>.pack.json` (`faction`, `map` or `jungle`) to `<id>/pack.json`, then set `id` (the same as the folder name) and `name`. A finished one looks like this:

```json
{ "id": "swarm", "version": "0.2.0", "category": "faction", "name": "Swarm", "order": 10, "dependencies": ["base"], "lore": {"summary": ""} }
```

- The id matches `^[a-z][a-z0-9_]{1,31}$`, equals the folder name, and is not one of `core engine game main test tests exp` or anything starting with `sample`.
- `version` is `X.Y.Z`. `category` is one of the rows below. Only `base` is category `core`.
- A new faction also needs a house def in `base` (the owner adds it), because every minion's `house_tag` must name a house. Ask the owner before starting a new faction.

**Which category may hold which folder.** The table is `pack-tools/pack_categories.json`, and the lint reads it by itself. Written out:

| Category | Folders it may have | `dependencies` | Notes |
|---|---|---|---|
| `core` | any (only `base`) | `[]` | owner only |
| `faction` | `abilities`, `augments`, `heroes`, `units`, `shop_items`, `towers`, `sound_themes` | exactly `["base"]` | no `houses`, `classes`, `maps`, camps or monsters; every minion's `house_tag` is the pack id |
| `map` | `maps` | exactly `["base"]` | |
| `jungle` | `monsters`, `camps`, `camp_items` | exactly `["base"]` | |
| `mod` | any | any | the only category that may override another pack's defs (`overrides`); owner only |
| `skin`, `sound` | none (client-only) | | not wired yet; do not add |

Folder to kind: `abilities` ability, `augments` augment, `heroes` hero, `houses` house, `classes` hero_class, `units` minion, `monsters` monster, `towers` tower, `shop_items` and `camp_items` shop_item, `camps` camp, `maps` map, `rulesets` ruleset, `ai` ai_profile, `commander_ai`, `hero_ai`, `sound_themes` sound_theme. A def's `kind` must match its folder.

## 2. Per kind

Template paths are inside a pack: `swarm/...` is in game-factions, `base/...` in game-arena. If the template lives in the other repo, open it on GitHub, or ask the owner for the file.

Every def has `id`, `kind` and a `lore` block (section 3). These kinds also need non-empty `name` and `description` strings: tower, shop item, minion, monster, camp, ability, augment. Heroes don't.

### Hero

- **Folder and id:** `heroes/<name>.json`, `<pack>.hero.<name>`. Category: faction (or core).
- **Template:** `swarm/heroes/ranger.json` (a full faction hero), or `base/heroes/lance.json` (the smallest).
- **Also add elsewhere:**
  - `abilities`: a list of ability ids that exist (your own in `abilities/`, or a base one such as `base.ability.piercing_shot`). At least one must hit enemies and have a `range` above 0, or the hero bot has no engage distance and the pack is refused.
  - `signature_ability`, if you set it, must also be in `abilities`.
  - `hero_class` must be an existing class tag: `breaker`, `conduit` or `ranger`.
  - Set `house_tag` to your pack id, as `swarm/heroes/ranger.json` does.
  - `hp` and `speed` are required numbers.
  - A new ability is its own def in `abilities/` (template: `swarm/abilities/basic_ranger_auto.json`, or `base/abilities/piercing_shot.json`). Its `on_cast` and `on_hit` ops are limited to the game's verbs, so copy a working ability and change numbers rather than invent ops.
- **Model:** `assets.model_3d`. The `.glb` needs the animation clips `idle`, `run` and `attack`, or the game shows a placeholder and warns.

### Tower

- **Folder and id:** `towers/<name>.json`, `<pack>.tower.<name>`. Category: faction (or core). Towers are not gated by faction; every loaded tower can be built.
- **Template:** `base/towers/arrow.json` (no skills). With skills: `base/towers/silo.json`. A faction pack has no tower yet, and game-factions has no `base/`, so start from this one (a file in `swarm/towers/`, say), then change the id, name and numbers:

  ```json
  {
    "id": "swarm.tower.cubicle_turret", "kind": "tower",
    "name": "Cubicle Turret", "description": "A stapler on a swivel chair.",
    "levels": [
      {"cost": 60.0, "hp": 400.0, "attack_damage": 18.0, "attack_range": 150.0, "attack_cooldown": 1.0}
    ],
    "assets": {"model_3d": "swarm_cubicle_turret", "model_fallback": "tower_arrow", "icon": "crosshair"},
    "lore": {"flavor": ""}
  }
  ```
- **Required:** `name`, `description`, and a non-empty `levels` array. Each level needs `cost`, `hp`, `attack_damage`, `attack_range`, `attack_cooldown`, all numbers, none negative, `hp` above 0.
- **Skills (optional):** `skill_point_costs` plus `skills`, each pointing at an existing stat augment or tower ability. If you add them, add those defs to `augments/` and `abilities/` too.
- **Art:** `assets.model_3d` is required, but the file may not exist yet. Set `"model_fallback": "tower_arrow"` and the game uses base's model until yours arrives. `assets.icon` can be any base icon name.

### Shop item

- **Folder and id:** `shop_items/<name>.json` (`channel` is `hero` or `commander`), or `camp_items/<name>.json` (`channel` is `camp`). Id `<pack>.shop_item.<name>`. A camp-channel item outside `camp_items/`, or any other channel inside it, is an error. Category: faction for `shop_items/`, jungle for `camp_items/`.
- **Template:** `swarm/shop_items/pink_slip.json` with its augment `swarm/augments/pink_slip.json`. A camp item: `base/camp_items/camp_overtime_pay.json`.
- **Also add elsewhere:**
  - A hero or commander item grants an ability or augment: `grant_kind` is `ability` or `augment`, and `grants` is the id of a def that exists. So a new item usually comes with a new def in `augments/` or `abilities/` of the same pack (the shop item and its augment share a name).
  - `price` is a number.
  - A camp item uses `grant_kind: "team_modifier"` and a `modifiers` object (keys: `minion_hp_pct`, `minion_sight_add`, `worker_income_add`, `tower_hp_pct`, `camp_respawn_add`).
  - Put `unlock` on the granted ability or augment, never on the item.
  - A commander item that upgrades a hero's signature ability also needs `signature_rank`: integers 0, 1, 2 and so on, one each per signature. Copy the three `swarm/shop_items/signature_ranger_*.json` items if you add one.

### Minion (units)

- **Folder and id:** `units/<name>.json`, `<pack>.unit.<name>`. Category: faction.
- **Template:** `swarm/units/swarmling.json`.
- **Also:** `house_tag` must be the pack id (the lint and the game both check it). Required numbers: `cost`, `hp`, `speed`, `attack_damage`, `attack_range`, `attack_cooldown`, `aggro_radius`. A minion needs `assets.model_3d` with the `idle`, `run` and `attack` clips.

### Monster

- **Folder and id:** `monsters/<name>.json`, `<pack>.monster.<name>`. Category: jungle (or core).
- **Template:** `base/monsters/pest.json`.
- **Required numbers:** `hp`, `speed`, `attack_damage`, `attack_range`, `attack_cooldown`, `bounty`, `xp_value`. Keep `kill_category` as in the template. Set `model_fallback` to a base model key such as `base_swarmling` until your model exists.
- **Model:** `assets.model_3d`, with `idle`, `run` and `attack` clips.

### Camp

- **Folder and id:** `camps/<name>.json`, `<pack>.camp.<name>`. Category: jungle (or core).
- **Template:** `base/camps/jungle_lodge.json` for a fighting camp, `base/camps/old_mill.json` for a shop camp (`"shop": true`).
- **Also add elsewhere:**
  - `monsters` is a non-empty list of `{"unit": <monster id>, "count": n}`; each unit must be a monster that exists. Add the monster def first.
  - `respawn` and `leash` above 0; `aggro_radius` is 0 or more, and `aggro_radius + 28` must not exceed `leash`.
  - `catalog` (what a shop camp sells) lists camp items by id: `{"item": "<pack>.shop_item.<name>"}`, each a camp-channel item. Leave `catalog` as `[]` unless you need it. An `unlock` on a catalog entry may only use `team_camp_clears` in a jungle pack: the plot-named keys in `base/camps/jungle_lodge.json` work only in the pack that owns the map's plots.
  - Keep `theme` and `shop` as in the template.
  - **A camp does nothing until a map has a plot for it.** A map's `plots` list has entries like `{"id": "A1", "team": 0, "pos": [348, 345], "camp": "base.camp.recruiting_office"}` (see `base/maps/standard.json`). A map pack depends on `base` only, so it can place base camps. A `jungle_<slug>` camp stays unplaced until the owner adds a layout for it; say so in your PR.
  - A proximity-aggro camp (aggro_radius above 0) must have its plot farther from every hero spawn than its `leash`.

### Map

Rare. A map pack is `map_<slug>/` with `maps/<name>.json` (template: `base/maps/standard.json`). Ask the owner first; the validator also plays two short test matches on every map.

## 3. Lore

Every def carries a `lore` block of empty strings, which the owner or a writer fills later. The game never reads it. To add one: **copy the `lore` block from the template def and empty its strings.** The keys per kind:

| Kind | Keys |
|---|---|
| hero | `title`, `bio`, `quote` |
| house | `summary`, `history` |
| hero_class, map, camp | `summary` |
| minion, monster, tower, ability, augment, shop_item | `flavor` |
| `pack.json` (kind "pack") | `summary` |

- Always list every key of the kind, even when empty (`"lore": {"flavor": ""}`). The game's own check wants all of them.
- A key from another kind, a non-string value or a kind with no lore is an error.
- Length limits: `title` 60, `quote` 200, `flavor` 300, `summary` 600, `bio` 4000, `history` 4000.
- Other kinds (ruleset, ai_profile, commander_ai and the rest) take no lore.

## 4. Assets

Asset files sit under the pack's `assets/` folder, in a subfolder by type:

| Subfolder | Extensions | Used by | Limits |
|---|---|---|---|
| `assets/models/` | `.glb` | `assets.model_3d`, `model_fallback` | 5 MB, 10,000 triangles |
| `assets/icons/` | `.svg` | `assets.icon` | 256 KB, 1024 px |
| `assets/textures/` | `.png` | a map's `ground.texture` | 8 MB, 4096 px |
| `assets/audio/` | `.ogg`, `.wav` | `sfx` and `voice` blocks, the pack theme | |

- **Names.** Every file in a non-core pack starts with `<pack>_`, for example `swarm/assets/models/swarm_tower_silo.glb`. Base files are not prefixed. This keeps two packs from shipping the same name.
- **Keys.** A def names a file by its bare key: the file name without folder or extension, only `a-z 0-9 _ -`. So `"model_3d": "swarm_tower_silo"` means `assets/models/swarm_tower_silo.glb`. The game looks in your pack first, then in `base`, so a def can use a base icon (`"icon": "crosshair"`) without copying it.
- **Git LFS.** The repo's `.gitattributes` sends `.glb`, `.png`, `.ogg` and `.wav` through Git LFS automatically; `.svg` stays in plain git. Run `git lfs install` **once per machine** (macOS: `brew install git-lfs` first), before your first commit that adds a binary. Check `git lfs version` works **before** your first binary commit. Without git-lfs, git ignores the LFS rule and stores the raw binary as a plain file. `check_repo` (section 5) refuses such a binary and prints the fix: run `git lfs install`, then `git rm --cached "<file>"`, `git add "<file>"` and commit. Because PRs are squash-merged, fixing it in a new commit is enough; the raw copy never reaches `main`, so no history rewrite is needed. After you commit, `git lfs ls-files` must list the file. A checkout made without git-lfs leaves small pointer text files where the binaries should be, and the lint reports each one (run `git lfs install` and `git lfs pull`).
- **Never commit `.import` files.** Godot makes them when you open a model in the editor; they are gitignored in a content repo. The game's own copy gets its small keep-stubs when the owner bumps your pack. Textures Godot extracts next to a `.glb` (`assets/models/*.png`) are also ignored, so don't add them.
- **Sounds must be free to share.** Every file under `assets/audio/` is CC0-1.0 or public domain (PDM-1.0), and each needs a row in the pack's `CREDITS.md` under a `## Audio` heading, in a table with the header `| File | Licence | Source | Author | Edits |`. Source is an https URL, or `generated: <model> <version>, prompt "...", seed N` for a sound you made yourself. `check_repo` (section 5) refuses an uncredited sound or any other licence.
- **No JSON under `assets/`**, no other subfolders, no other extensions.

## 5. Check

Before you push, **commit your work**, then run one command from the top folder of your clone (from a pack folder, use `../pack-tools/check_repo.py`; it finds the clone itself). Use `uv` (it fetches Python 3.12 for you; nothing to install):

```bash
git fetch
uv run pack-tools/check_repo.py
```

- **What it runs.**
  - The repo rules, on what you committed: no binary committed without Git LFS, no `.import` files, no `.lfsconfig`, and `.gitattributes` unchanged.
  - The lint of every pack (it reads the files as they are now).
  - The audio licence check: every sound under `assets/audio/` is credited in `CREDITS.md` as CC0-1.0 or public domain.
  - A summary of what your *committed* changes do against `origin/main`. So `git fetch` first, and commit first: uncommitted edits are not in it. A new pack with no defs yet has nothing to list.
- **What it prints.** One line per problem, `<file>: [rule] message`, with the fix spelled out. The last line is `check_repo: OK (<n> packs)`, or `check_repo: <n> problems` and exit code 1. Fix every problem, commit, and run it again. Paste the `## Change summary` part into the PR.
- **The single tools** are still there:
  - `uv run pack-tools/lint_pack.py <pack>` lints one pack. It finds `pack_categories.json` by itself. It takes a few seconds and needs no game. It checks the manifest, the folder and kind rules, ids, camp-item placement, minion `house_tag`, asset folders, extensions and name prefix, and files that are Git LFS pointers instead of real binaries. It cannot see missing references (an `abilities` entry naming nothing), lore shape or stats; the real validator does.
  - `uv run pack-tools/change_summary.py <old> <new>` prints a Markdown summary of what changed between two copies of a pack, one line per def: `added`, `removed` or `changed`. A changed def says `presentation-only` when only assets, vfx, sfx, voice, lore, name or description changed, and otherwise names the gameplay fields that changed (for example `hp`).
- **On the PR**, two checks must pass. **Content checks** runs the same command; read it, fix what it names and push again. **game-validate** (the real validator, run by the game repo) then runs the pack against the game: references, ability programs, stats, lore, asset budgets and short test matches. The lint passing does not mean that check passes. Its verdict is the comment from `linghenrik-content-bot`, updated on every push: read it for the errors. A `game-validate` check with no matching bot comment for the PR's latest commit is not the game's verdict.

## 6. Versions

Don't touch `version` in `pack.json`. A pack is identified by its commit, not its version. The owner bumps `version` only when another pack needs to declare a `requires` range on the new one.

## 7. Rules that keep your content working later

The game will get an FPS client one day, with a faster tick and 3D aiming. These rules make sure your content still means the same thing then:

- Positions in ability and bot programs are always 2D `[x, y]`. Height only ever arrives as new optional fields (`body.height`, terrain height).
- Every distance to a unit measures to the edge of its body (`body.radius`).
- Durations are in seconds, never ticks. The tick rate will change.
- An ability's `on_tick` runs at most once every `ability_tick_period` seconds (0.05 in the standard ruleset), whatever the tick rate. A `wait` inside it still works as before.
- Some names are reserved, and the game refuses them: the terrain fields `height` and `blocks_sight`, and `cast_target` `unit` and `self`.
- `cast_target: "direction"` is a 2D direction in programs, even when an FPS client later aims in 3D.

## 8. Don'ts

- No overrides: only a `mod` pack may replace another pack's def, and friends don't make mods.
- No `house` defs (or `classes`, `rulesets`) in a faction pack. Houses belong to `base`.
- No `.import` files, no extracted `assets/models/*.png`.
- No edits to another pack's folder in the same PR. One PR, one pack.
- Don't edit `pack-tools/`, `.github/`, `.claude/`, `.gitattributes`, `.gitignore`, `AGENTS.md` or `CLAUDE.md`. The owner updates them; a PR that touches them will be asked to undo it.
- Don't rename or delete an id other defs point at (a hero's ability, a camp's monster, a map plot's camp) without changing every reference in the same PR.
- Don't leave half-done content on `main`: a def with no model should still say `model_fallback`, and a camp nobody placed should say so in the PR.

## 9. If you have the game repo (the owner)

Everything above still applies. The game repo adds these routes. Run them from the repo root (your worktree); every `content.py` command takes `--help`.

**Where to edit.** The game keeps a vendored copy of each pack: `data/base` for base, `mods/<id>` for the rest, listed in `content.lock.json`. **Never edit `content.lock.json` by hand**; `content.py` writes it.

The packs are published: `base` in [game-arena](https://github.com/linghenrik/game-arena), and `elite`, `swarm` and `utility` in [game-factions](https://github.com/linghenrik/game-factions). Editing a vendored copy in the game makes `content.py status` say `modified`. Then either export it or edit in the content repo:
  1. Edit in the content repo, then check it against the game with `godot --headless -s tools/validate_packs.gd -- --overlay=<dir>` (the pack folder in your clone; repeat `--overlay` for several packs). When the PR merges, the relay starts `content-bump` in the game: it opens `bot/bump-<repo>` with the change summary. A bump that changes packs waits for you to merge it; a lock-only bump (`Lock only: yes`) merges itself after game CI. `content.py bump <pack>` by hand still works.
  2. Edit in the game. When that change merges to `main`, `content-export` opens the content repo's `export/<pack>-<hash8>` PR as content-bot (`uv run tools/content/content.py export <pack>` does the same by hand). After that PR merges, the bump is lock-only and merges itself. `bump` refuses a game-side edit that was never exported (it names the file); `--force` discards it.
- **A pack that is not locked yet:** `content.py add <repo> <pack>`. A new content repo: `content.py init-repo <repo>`. It seeds the repo from the vendored packs and writes the kit; the url comes from `tools/content/repos.json` unless you pass `--url`.
- **Keep a content repo's kit current:** `content.py kit <repo> [--check]`. `--check` lists what differs and changes nothing; without it, the command opens a PR on the content repo that brings its `pack-tools/`, workflows, CODEOWNERS and so on up to date. You merge that PR yourself, through the admin bypass. The daily `content-sweep` opens kit PRs by itself, except for a change under `.github/workflows/`: content-bot can't push workflow files, so run `content.py kit <repo>` yourself.
- **The daily sweep** (`content-sweep`, 04:17 UTC) dispatches what the event-driven workflows missed: a bump that never ran, an unexported game-side edit, kit drift, a PR with no `game-validate` verdict. It exits 1 on what only you can fix: a failed bridge run in the last day, a stuck `bot/bump-*` PR, an `export/` or `kit/` branch with no PR. `gh workflow run content-sweep.yml -f stuck_hours=0` re-dispatches every PR without a verdict now.
- **Before approving a content PR**, read content-bot's `game-validate` comment for the latest commit. GitHub accepts a `game-validate` check of the same name from any source (step 21's F1 case), so the check alone can be forged by a PR workflow; the comment can't.
- **Repo settings** (who may merge, which checks must pass): `content.py repo-settings [<repo>...]` compares GitHub with `rules` in `tools/content/repos.json` and lists every difference (it changes nothing). `content.py repo-settings --apply <repo>` changes GitHub to match. `--apply` with no repo names covers the content repos only; the game repo is applied only when you name it (`--apply game`).
- `content.py status [--fetch]` shows each pack against the lock and (with `--fetch`) how far upstream `main` moved. `content.py verify` checks the lock against the tree.

**Lore slots.** `godot --headless -s tools/lore_scaffold.gd [-- --dry-run]` adds empty `lore` blocks to every vendored def and `pack.json` that has none (idempotent; it only works on `data/base` and `mods/*`). `tests/test_lore_coverage.gd` fails until every shipped def has all its keys.

**Keep-stubs.** After adding a raw asset to the game copy, `uv run tools/content/content.py stubs` writes the `importer="keep"` `.import` files (`stubs --check` only checks). Commit them in the game repo. Without a stub a Godot export (a game build) ships only Godot's imported copy and the model renders invisible.

**Tests.** `tools/test.sh <fragment>` while iterating. When engine-facing defs changed (abilities, rulesets, anything the sim reads), run `tools/verify.sh` before the PR (the `verify-ci` skill). It runs the validator on all vendored packs too.

**Game-repo PRs** also update TODO.md and README.md (see AGENTS.md).
