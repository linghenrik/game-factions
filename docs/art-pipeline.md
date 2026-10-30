# Art guide: models, icons, textures and sounds

This guide is for you if you want to add art or sound to a pack in this repo. You do not need the game, and you do not need to know much about git. You need a GitHub account, the steps in [CONTRIBUTING.md](../CONTRIBUTING.md), and one tool that makes a 3D model, an icon or a sound.

There are three ways to get a file:

1. **Download** it from a free library.
2. **Make it by hand** (Blender, Inkscape, a microphone).
3. **Generate it** with an AI tool.

All three routes face the same check. The check does not care how you made a file. It cares that the file is small enough, has the right clips, and has an honest row in the pack's `CREDITS.md`.

Prices and terms change, so this guide gives none. Each tool has a pricing page and a terms page. **Read the terms on the day you use the tool, and take a screenshot of them.** Keep the screenshot. If anyone asks later what you agreed to, you can show it.

## 1. What you can add, and where it goes

Art files sit under the pack's `assets/` folder, in a subfolder by type. Do not put anything else there.

| Subfolder | Extension | A def uses it as | Limits |
|---|---|---|---|
| `assets/models/` | `.glb` | `assets.model_3d`, `assets.model_fallback` | 5 MB, 10,000 triangles |
| `assets/icons/` | `.svg` | `assets.icon` | 256 KB, 1024 px |
| `assets/textures/` | `.png` | a map's `ground.texture` | 8 MB, 4096 px |
| `assets/audio/` | `.ogg`, `.wav` | `sfx` and `voice` blocks, the pack theme | no size limit, but a credit row |

Three naming rules:

- **Prefix.** Every file in a pack other than `base` starts with the pack id and `_`. In the `swarm` pack: `swarm/assets/models/swarm_clerk.glb`.
- **Key.** A def names a file by its key: the file name without folder or extension. `"model_3d": "swarm_clerk"` means `assets/models/swarm_clerk.glb`.
- **Fallback.** Until your model is ready, set `"model_fallback"` to a model that already exists, such as `"base_bruiser"`, and the game shows that one. A def with no model and no fallback should not be merged.

The full rules for defs, ids and keys are in [the add-content skill](../.claude/skills/add-content/SKILL.md), sections 1, 2 and 4. Read them first. They also cover Git LFS: `.glb`, `.png`, `.ogg` and `.wav` files go through it, so run `git lfs install` once on your machine before your first commit that adds one.

## 2. The look

The factions are cartoonish, dark and heavy, but not gory. Think of *Valiant Hearts*, *Darkest Dungeon* and *Hades*. The mood is old generals and corporations sending young people to war. Each faction has its own flavour: Swarm is corporate greed, Elite is agricultural, Utility is tech.

Weight comes from four things:

- **Palette.** Mud, khaki, gas-green and a bruised sky, plus one accent colour per faction.
- **Lighting.** Low sun, long shadows, haze. The game does the lighting, so you only choose colours that will look good under it.
- **Animation.** Slow collapses. Bodies that linger for a moment.
- **Sound.** Distant artillery, whistles, and silence after a wave dies.

The hard rules of the look:

- **No blood.** Deaths are collapses.
- **Every unit is a person**, including the jungle monsters (think deserters and stragglers). They share one skeleton and one set of clips, so give them near-standard human proportions. Get the cartoon look from the silhouette, the costume and the palette, not from extreme proportions.
- **Weapons are holstered or slung**, not fused to the hands.
- **Readable first.** The camera looks down from above, so a unit is only 40 to 80 pixels tall on screen. If you cannot tell what it is at that size, it needs a clearer silhouette, not more detail.
- **Fictional companies only.** If you make fun of a corporation, invent it.

## 3. The rules the check enforces

You run the check yourself (section 6), and the pull request runs it again. Each problem prints on one line with its fix.

### Models (`.glb`)

- **Budgets.** At most 5 MB and 10,000 triangles. The count is per node, as the game's engine adds it up: a mesh used by two nodes counts twice.
- **No Draco compression.** The game's engine cannot load it. Export without mesh compression.
- **Clips.** An animation clip is a named movement. The game only plays these names: `idle`, `run`, `attack`, `hit`, `death`, `stun`. A clip with any other name is refused, so rename it.
  - A model used by a **hero**, a **minion** or a **monster** must have `idle`, `run` and `attack`.
  - `hit`, `death` and `stun` are optional but make the unit feel alive. `death` is where the slow collapse goes.
  - A **prop** (a tower, a wall, a tree) may have no clips at all.

### Icons (`.svg`) and textures (`.png`)

- Icons: at most 256 KB, and at most 1024 px in the `width`, `height` or `viewBox` of the `<svg>` tag.
- Textures: at most 8 MB and 4096 px on the longer side.

### Credit rows

Every model, icon and texture needs one row in the `## Art` table of the pack's `CREDITS.md`. Every sound needs one row in the `## Audio` table of the same file. The header is always the same:

```markdown
## Art

| File | Licence | Source | Author | Edits |
|---|---|---|---|---|
```

A cell never contains the `|` character. There is one row per file, and no row for a file that is not there. If the pack already has a `CREDITS.md`, keep its rows and add yours.

The **Source** cell takes one of three forms. Here is one example row of each:

```markdown
| assets/models/swarm_clerk.glb | CC0-1.0 | https://quaternius.com/ | Quaternius | decimated to 6,000 triangles, recoloured |
| assets/icons/swarm_stapler.svg | LicenseRef-Contributor | generated: FLUX.2 klein 4B [local] 2026-11-02; prompt "stapler, flat icon", seed 1234 | Your Name | traced with potrace, optimised with svgo |
| assets/models/swarm_cubicle.glb | LicenseRef-Contributor | made: modelled and rigged by hand in Blender 4.2 | Your Name | none |
```

- **An https link** is for art someone else made. The licence must be `CC0-1.0`, `PDM-1.0`, `CC-BY-3.0` or `CC-BY-4.0`.
- **`generated: <tool> <version> [<plan>] <YYYY-MM-DD>; <prompt, seed, inputs>`** is for art you generated.
  - The plan goes in square brackets. It is the paid tier you used, or `local` if you ran the model on your own computer. A free tier is refused.
  - After the semicolon, write what someone would need to repeat it: the prompt, the seed, the input images.
  - The licence is `LicenseRef-Contributor`.
- **`made: <who, how>`** is for art you made by hand. The licence is `LicenseRef-Contributor`.

Sounds work the same way, with two differences:

- The only licences are `CC0-1.0` and `PDM-1.0`.
- A sound you generated or recorded yourself is released as `CC0-1.0` (not `LicenseRef-Contributor`). Its source reads `generated: <model> <version>, prompt "...", seed N` or `recorded: <who, where, how>`.

```markdown
## Audio

| File | Licence | Source | Author | Edits |
|---|---|---|---|---|
| assets/audio/swarm_stapler_hit.ogg | CC0-1.0 | https://freesound.org/s/123456/ | Some Person | trimmed, mono |
| assets/audio/swarm_whistle.ogg | CC0-1.0 | recorded: my own whistle, living room, phone microphone | Your Name | noise removed |
| assets/audio/swarm_rumble.ogg | CC0-1.0 | generated: Stable Audio 3 Small-SFX 1.0, prompt "distant artillery rumble", seed 77 | Your Name | none |
```

### The licences, in plain words

- **`CC0-1.0` and `PDM-1.0`** mean the maker gave the work to everyone (CC0), or it is old enough to belong to everyone (public domain). No credit is needed, but we give it anyway.
- **`CC-BY-3.0` and `CC-BY-4.0`** mean anyone may use the work if they credit the maker. The game credits them from your row.
- **`LicenseRef-Contributor`** means **you made it or generated it**, and:
  - the copyright stays yours, and so does the credit;
  - once the owner merges your pull request, the game may use it as [LICENSE.md](../LICENSE.md) section 3 says. In short: in the game, and on physical goods such as prints, figures and clothing, where the owner has the sole right to make them;
  - you can ask for removal at any time, as section 4 says. Within 30 days the owner takes it out of `main` and out of every build made after your request. What already exists keeps it: builds already released or shared, recorded matches and their replays, the git history, and physical goods already made.

The **Author** column always names the person who really made the work. For a download, that is the creator (not the website, and not you). For something you made or generated, that is you. Two reasons:

- CC BY says the maker must be credited. A missing or wrong name breaks the licence.
- Nobody should be credited for someone else's work.

The `generated:` row matters for a second reason. Game stores ask for a note when a game contains AI-generated art, and your rows are the record that note is written from. Raw AI output may also have little or no copyright in some countries, so the row is how we show what was done, and by whom.

### Banned names

The check reads the **Source** and **Edits** cells of every table row in `CREDITS.md`, and refuses a row that names a tool from section 5's table. It matches whole words, so "Stable Audio 3" is fine. Do not name a banned tool even to say you did not use it, because the check cannot tell the difference.

## 4. Three routes

### Download

- **Models and animations:** Quaternius (CC0), Poly Pizza (each model shows its own licence: take CC0 or CC BY only), Kenney (CC0).
- **Textures:** ambientCG (CC0).
- **Icons:** game-icons.net (CC BY: the Author is the icon's artist, shown on its page).
- **Sounds:** Kenney (CC0), and Freesound **filtered to CC0 only**. Freesound's CC BY, BY-NC and Sampling+ sounds are all refused. Recordings from 1914 to 1925 in public archives (the Great 78 Project, the National Jukebox) are `PDM-1.0` and fit the mood well.

For each file, put the page's address in the **Source** cell, the licence the page shows, and the maker's name as **Author**. In **Edits** write what you changed, for example "decimated" or "renamed clips". Quaternius also has a CC0 set of human animations you can use as a start for a rig.

### Make it by hand

- **Models: Blender.**
  - Start from a human in an **A-pose** (arms slightly down and out), with the weapon holstered.
  - Name your actions `idle`, `run` and `attack` (and `hit`, `death`, `stun` if you make them). Blender uses the action's name as the clip name.
  - To see the triangle count, turn on **Overlays, Statistics** in the 3D viewport and read the **Triangles** number with the whole model visible. Stay well under 10,000. If it is over, add a **Decimate** modifier.
  - Export with **File, Export, glTF 2.0** and choose the format **glTF Binary (.glb)**. In the **Mesh** section, leave **Compression** (Draco) switched off. In the **Animation** section, keep the animations on.
- **Icons: Inkscape.** Draw on a page of 1024 px or less. Save as **Plain SVG** so the file stays small.
- **Sounds: your own recordings.** Record, trim and export to `.ogg`. In the credit row use a `recorded:` source and release the sound as `CC0-1.0`.

In the credit row use `made:` for models and icons, with `LicenseRef-Contributor`.

### Generate it

Use a **paid plan** of a hosted tool, or a **model you run on your own computer** (local). Never a free tier: free tiers often let the vendor keep rights or make your output public.

- **Icons and images:** FLUX.2 klein 4B (Apache 2.0 licence, runs locally, for example in Draw Things or mflux). Turn the image into a vector with `potrace`, then shrink it with `svgo`.
- **Sounds and music:** Stable Audio 3, run locally. Its terms ask commercial users to register, so read them first.
- **Models from an image:** make a front, side and back picture of your character in an A-pose, then turn it into a mesh with Tripo on a **paid** plan. Aim for 4,000 to 8,000 triangles. Expect to try about three times. Read Tripo's current terms and pricing pages and screenshot them. Meshy meshes are allowed on a paid plan, but not its rigs or animations.
- **Rig and clips:** upload the mesh to Mesh2Motion in your browser. It rigs the model and gives you CC0 animation clips. Its clip names may not match ours: rename them in Blender to `idle`, `run` and `attack`. Export without Draco compression.

Fill in the `generated:` row **as you go**, not afterwards. Write down the tool, its version, the plan, the date, the prompt and the seed every time. A model that went through several tools gets one row with every step in it: each tool, version and plan, and the images used as input. If you cannot say how a file was made, we cannot take it.

## 5. Do not use

These tools have terms that clash with a public repo and with licensed art. A pull request that uses them is refused.

| Do not use | Why | Does the check refuse the name? |
|---|---|---|
| Mixamo | Its licence is personal and cannot be passed on, and redistribution is banned. | Yes |
| ActorCore (also "actor core"), AccuRIG | Its licence bars publishing. | Yes |
| Meshy rigs and animations | They are "service assets" that stay Meshy's. Use Meshy meshes only. | No |
| Free tiers of Meshy, Tripo, Rodin, Recraft and Scenario, and Midjourney without a plan that keeps your output private | The vendor keeps rights, or the output is public. | A plan with "free" in it |
| FLUX.1 or FLUX.2 dev (also Kontext and Krea dev), FLUX.2 klein 9B, Qwen-Image (file names such as `flux1_dev` too) | Non-commercial weights. A style model trained on them cannot ship either. | Yes |
| Hunyuan3D (also "Hunyuan 3D") | It has no licence in the EU, UK or South Korea. | Yes |
| Udio, Suno | Ownership limits, or games are excluded. | Yes |
| ElevenLabs Music | The same kind of limits. | No |
| MusicGen, AudioGen | Non-commercial weights. | Yes |
| Sonniss GDC bundles | Redistributing them "as sound effects" is banned. | Yes |
| Freesound BY-NC or Sampling+ sounds, OpenGameArt GPL audio | Non-commercial or copyleft terms. | No, but the licence check refuses it |

"No" means the check cannot see it, not that it is allowed. The owner reads every pull request.

## 6. Check and open the pull request

1. Commit your work, then run the check from the top folder of your clone:

   ```bash
   git fetch
   uv run pack-tools/check_repo.py
   ```

   It runs the pack lint, the budget and clip checks on your files, the credit checks for art and sound, and the Git LFS rules. Fix every line it prints, commit, and run it again until the last line says `check_repo: OK`.
2. Push your branch and open the pull request. One pack per pull request.
3. The pull request runs **Content checks**, which is the same command.
4. Once the owner has switched it on for your repo, **game-validate** also runs. It loads your pack in the real game engine: references, stats and sizes, plus short test matches. Passing the lint does not mean it passes.

**Never commit `.import` files.** Godot makes them when you open a model in its editor, and they stay out of git. The game needs small placeholder files next to each model so that builds ship it; the owner writes those when your pack is brought into the game. That step is not yours.

If a tool or a licence confuses you, ask the owner before you spend time on a file. [pack-tools/README.md](../pack-tools/README.md) lists every checker.

## 7. How the official factions were made

How the pilot's heroes were made, step by step. Every step is in the record (docs/art/pilot/record.jsonl); the picked style images are on the public style board: https://github.com/linghenrik/game-arena/tree/main/docs/style-board

### The Yoke (elite_breaker)

- **sheet** (sheet-elite_breaker-006): Nano Banana 2.1 gemini-nano-banana-2.1, Gemini API paid, seed 999097730, 2026-10-28, $0.05
  Prompt: "A character design sheet for The Yoke, a hero of a top-down strategy game, on a plain light background. A huge ploughman who leans forward and drags an old wooden ard behind him with one hand: he grips the crossbar at the front end of its long beam in his right hand, and his left hand is free. An iron-shod share sits at the back end. It is pulled, not pushed, so it has no handles at the back. He carries no other weapon. An ox jawbone (the lower jaw, with its teeth) bound to his belt as a bloodline bone; no skulls. Seen from above, the shape is the long beam trailing straight behind him. Show: (1) the full figure large, dragging the ard with his right hand; (2) a smaller view swinging the ard one-handed by its crossbar, the same ard with only its share at the end, no axe blade; (3) a smaller view standing at rest, the beam in his right hand and the share on the ground; (4) a view from directly above while he walks forward dragging the ard: his head and shoulders, with the beam running from his right hand straight back behind him; (5) the ard alone, from the side; (6) a close-up of the ox jawbone. Keep the ard clearly separate from his body and hands in every view. Dark, semi-realistic painted concept art: muted earthy colour, soft painterly rendering, dramatic rim light against a dark background, figures standing in churned mud and straw. Heavy, weathered, hand-made materials. Near-standard human proportions. One bone and linen accent. A clan of farming families proud of their bloodlines, their strength and their legacy: broad, muscular, well-fed people. Each wears bloodline bones, heirloom bones of the family's champion animals, carved with one notch per generation and bound with linen. No rosettes or ribbons. Ploughs, sacking, rope, straw, worn wool and leather: people who work the land and now fight for it. No blood, no gore. Must read from a top-down camera, so the head, shoulders and whatever is carried or worn on the back carry the shape. Match the attached pictures' style, and take his design from the Breaker in them."
- **turnaround body** (turnaround-elite_breaker-003): Nano Banana 2.1 gemini-nano-banana-2.1, Gemini API paid, seed 2073493243, 2026-10-28, $0.05
  Prompt: "A turnaround of The Yoke: front, side and back views side by side on one sheet, in an A-pose with the arms slightly down and out, on a plain light background with even, flat lighting, no cast shadows and no ground. Near-standard human proportions. The figure holds and carries nothing; both hands are empty and open. A huge, broad, muscular ploughman with a deep hood, worn leather and wool, rope bindings and wrapped forearms. An ox jawbone (the lower jaw, with its teeth) bound to his belt as a bloodline bone, carved with notches and bound with linen. Paint the team parts (a cloth band around the hood, and an armband on the left arm) in flat magenta #FF00FF, and make nothing else magenta. Semi-realistic painted concept art, muted earthy colour, heavy, weathered, hand-made materials, one bone and linen accent. No blood. Match the person and outfit in the attached character sheet."
- **turnaround prop** (turnaround-elite_breaker_prop-001): Nano Banana 2.1 gemini-nano-banana-2.1, Gemini API paid, seed 460349422, 2026-10-28, $0.05
  Prompt: "The Yoke's ard on its own, a separate object: an old wooden ard, a long beam about as long as a man is tall, with a crossbar grip at the front end and a single iron-shod share at the back end; it has no handles at the back. Side view, top view and a view along the beam from the front end, side by side on one sheet, on a plain light background with even, flat lighting and no cast shadows. No figure and no hands. Semi-realistic painted concept art, worn wood, rope bindings and dark iron. Match the ard in the attached character sheet."
- **mesh body** (mesh-elite_breaker-002): Tripo P2.0, Pro, task https://studio.tripo3d.ai/workspace/texture/d7b81408-49af-468a-b82c-920d0eb58ade, image to 3D with smart mesh (quad topology), auto rig with the UE5 skeleton, preset animations kept in place; the 300 credits cover the model, rig and animation tries together, 2026-10-28, $0.00 (300 Tripo credits)
- **mesh prop** (mesh-elite_breaker_prop-001): Tripo v3.1, Pro, task https://studio.tripo3d.ai/workspace/texture/d4e15dcf-e809-462c-8257-628aa9fdd9c6, image to 3D, single image cut from the kept turnaround; polycount about 50k, generate in parts off, AI complete on, smart mesh off, detailed texture, remove lighting on, 2K texture, 2026-10-28, $0.00 (40 Tripo credits)
- **rig** (rig-elite_breaker-003): Tripo P2.0, Pro, 2026-10-28, $0.00
- **finish** (finish-elite_breaker-004): Blender 5.2.3 LTS, local, 2026-10-28, $0.00

### The Auditor (swarm_ranger)

- **sheet** (sheet-swarm_ranger-002): Nano Banana 2.1 gemini-nano-banana-2.1, Gemini API paid, seed 747770025, 2026-10-29, $0.05
  Prompt: "A character design sheet for The Auditor, a hero of a top-down strategy game, on a plain light background. A portly company marksman in a bowler hat and a tailored three-piece suit with long coat tails lined in plum, a plum tie and a watch chain, with a thick ledger strapped to his left hip. He carries a scoped bolt-action rifle in both hands. Seen from above, the shape is the bowler's round crown and the coat tails. Show: (1) the full figure large, holding the rifle across his body; (2) a smaller view aiming the rifle from the shoulder; (3) a smaller view standing at rest, the rifle in his right hand pointing at the ground; (4) a view from directly above while he walks forward: the round bowler crown, the shoulders and the coat tails; (5) the rifle alone, from the side; (6) a close-up of the ledger. Keep the rifle clearly separate from his body and hands in every view. Bold graphic-novel ink: heavy black outlines, flat colour and heavy black shadows; muted charcoal, grey and brown on a muddy ground, with plum as the only bright accent. Near-standard human proportions, the heroes a little portly. One plum accent, the colour of company ink. Corporate greed and old generals sending young men to war. Well kept and well fed, the opposite of the rough, hard-working Elite: the heroes are a little portly and neatly groomed, and everyone wears a tailored suit, with waistcoats, watch chains, bowler hats, polished shoes and pressed creases. Ledgers, stamped forms, brass and rubber stamps. No blood, no gore. Must read from a top-down camera, so the head, shoulders and whatever is carried or worn on the back carry the shape. Match the attached picture's style, and take his design from the Ranger in it."
- **turnaround body** (turnaround-swarm_ranger-001): Nano Banana 2.1 gemini-nano-banana-2.1, Gemini API paid, seed 2112740311, 2026-10-29, $0.05
  Prompt: "A turnaround of The Auditor: front, left side, right side and back views side by side, in that order, on one sheet, the left side view showing the figure's own left side, in a T-pose with the arms straight out to the sides, on a plain light background with even, flat lighting, no cast shadows and no ground. Near-standard human proportions. The figure holds and carries nothing; both hands are empty and open. A portly company marksman in a bowler hat and a tailored three-piece suit with long coat tails lined in plum, a plum tie, a plum pocket square and a watch chain, with a thick ledger strapped to his left hip. Polished shoes. Paint the team parts (the hat band, and an armband on the left arm) in flat magenta #FF00FF, and make nothing else magenta. Bold graphic-novel ink: heavy black outlines and flat colour; muted charcoal, grey and brown, with plum as the only bright accent. No blood. Match the person and outfit in the attached character sheet."
- **mesh body** (mesh-swarm_ranger-002): Tripo P2.0, Pro, task https://studio.tripo3d.ai/workspace/animate/a-portly-company-marksman-in-a-bowler-hat-and-a-tailored-three-piece-s-5bbd09b6-b17d-4a66-a549-924376fda8e6, multi-view image to 3D from the four views of the kept T-pose turnaround (magenta hat band and armband), smart mesh (quad topology), 5,284 triangles straight from Tripo; auto rig with the UE5 skeleton, preset animations kept in place; the 50 credits cover the model, rig and animation, 2026-10-29, $0.00 (50 Tripo credits)
- **mesh prop** (mesh-swarm_ranger_prop-001): Tripo P2.0, Pro, task https://studio.tripo3d.ai/workspace/texture/014f96ce-e465-4448-9760-4635c256a926, image to 3D from the rifle's side view cropped from the kept sheet, smart mesh (quad topology), 1,362 triangles straight from Tripo, 2026-10-29, $0.00 (40 Tripo credits)
- **rig** (rig-swarm_ranger-002): Tripo P2.0, Pro, 2026-10-29, $0.00
- **finish** (finish-swarm_ranger-001): Blender 5.2.3 LTS, local, 2026-10-29, $0.00

### The Coil Engineer (utility_conduit)

- **turnaround body** (turnaround-utility_conduit-003): Nano Banana 2.1 gemini-nano-banana-2.1, Gemini API paid, seed 51713515, 2026-10-29, $0.05
  Prompt: "A turnaround of The Coil Engineer: front, left side, right side and back views side by side, in that order, on one sheet, the left side view showing the figure's own left side, in an A-pose with the arms slightly down and out, the same pose in every view: in the side views the arms hang down beside the body and never reach toward the viewer, on a plain light background with even, flat lighting, no cast shadows and no ground. Near-standard human proportions. The left hand is empty and open. The right hand holds a small pistol-grip trigger with a thumb button. A lean, wiry signals engineer with a thin face and slicked-back hair, in a stained canvas work suit with a high collar, a leather harness across the chest holding a small brass meter panel with two dials, a belt with pouches, thick black rubber gloves to the elbow and rubber boots, and round goggles with green lenses. A big round copper coil with verdigris patches is strapped flat against his back by the harness, with two short ribbed ceramic insulator bushings standing up from its top edge. One thick black rubber cable runs from the coil over his right shoulder and down the outside of his right arm, held tight to the sleeve by straps, into the trigger grip; no other cable hangs loose. Paint the team parts (the goggle strap, and an armband on the left arm) in flat magenta #FF00FF, and make nothing else magenta. Vintage technical-manual engraving: fine cross-hatched black linework with flat, muted colour washes, and one verdigris accent. No blood. Match the person, outfit and coil of the Conduit in the attached picture."
- **mesh body** (mesh-utility_conduit-001): Tripo P2.0, Pro, task https://studio.tripo3d.ai/workspace/animate/gas-suit-soldier-with-steampunk-gear-beige-flight-suit-pink-armband-37d9256f-f839-48db-af68-2b26b8158fc8, multi-view image to 3D from the four views of the kept A-pose turnaround 003 (magenta goggle strap and armband; the coil, bushings, cable and trigger modelled as part of the body), smart mesh (quad topology), 8,196 triangles straight from Tripo; auto rig with the UE5 skeleton, preset animations kept in place; the 140 credits cover the model, rig and animation, 2026-10-29, $0.00 (140 Tripo credits)
- **rig** (rig-utility_conduit-001): Tripo P2.0, Pro, 2026-10-29, $0.00
- **finish** (finish-utility_conduit-001): Blender 5.2.3 LTS, local, 2026-10-29, $0.00

Pilot total: $23.85, bible and key art included.
