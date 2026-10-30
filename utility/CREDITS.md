# Utility credits

## Audio

Every sound in this pack is CC0-1.0 or public domain (PDM-1.0); sounds we generated are released as CC0-1.0. CI checks this table (tools/content/audio_credits.py). Built by tools/audio/sound.py build.

| File | Licence | Source | Author | Edits |
|---|---|---|---|---|
| assets/audio/utility_ability_cast.ogg | CC0-1.0 | https://freesound.org/s/590612/ | MrFossy | copy of base assets/audio/ability_cast.ogg; mono, +1.1 dB to -18 LUFS, Ogg Vorbis q3, from the Freesound HQ preview |

## Art

Every model, icon and texture in this pack is CC0, public domain or CC BY (credited here), or made by the contributor named in its row, who keeps the copyright; the game uses it under LICENSE.md. CI checks this table (pack-tools/art_credits.py; the guide is docs/art-pipeline.md).

| File | Licence | Source | Author | Edits |
|---|---|---|---|---|
| assets/models/utility_archer.glb | CC0-1.0 | https://quaternius.com/packs/animatedmech.html | Quaternius | clips renamed to idle/run/attack/hit/death, unused clips dropped (tools/remap_glb_anims.gd) |
| assets/models/utility_breaker.glb | CC0-1.0 | https://quaternius.com/packs/animatedmech.html | Quaternius | clips renamed to idle/run/attack/hit/death, unused clips dropped (tools/remap_glb_anims.gd) |
| assets/models/utility_conduit.glb | LicenseRef-Contributor | generated: Nano Banana 2.1 gemini-nano-banana-2.1 [Gemini API paid] 2026-10-29; turnaround turnaround-utility_conduit-003 'A turnaround of The Coil Engineer: front, left side, right side and back views side by side, in that order, on one sheet, the left side view showing the figure's own left side, in an A-pose with the arms slightly down and out, the same pose in every view: in the side views the arms hang down beside the body and never reach toward the viewer, on a plain light background with even, flat lighting, no cast shadows and no ground. Near-standard human proportions. The left hand is empty and open. The right hand holds a small pistol-grip trigger with a thumb button. A lean, wiry signals engineer with a thin face and slicked-back hair, in a stained canvas work suit with a high collar, a leather harness across the chest holding a small brass meter panel with two dials, a belt with pouches, thick black rubber gloves to the elbow and rubber boots, and round goggles with green lenses. A big round copper coil with verdigris patches is strapped flat against his back by the harness, with two short ribbed ceramic insulator bushings standing up from its top edge. One thick black rubber cable runs from the coil over his right shoulder and down the outside of his right arm, held tight to the sleeve by straps, into the trigger grip; no other cable hangs loose. Paint the team parts (the goggle strap, and an armband on the left arm) in flat magenta #FF00FF, and make nothing else magenta. Vintage technical-manual engraving: fine cross-hatched black linework with flat, muted colour washes, and one verdigris accent. No blood. Match the person, outfit and coil of the Conduit in the attached picture.', seed 51713515, refs bible-utility-003; Tripo P2.0 [Pro] 2026-10-29, task https://studio.tripo3d.ai/workspace/animate/gas-suit-soldier-with-steampunk-gear-beige-flight-suit-pink-armband-37d9256f-f839-48db-af68-2b26b8158fc8, multi-view image to 3D from the four views of the kept A-pose turnaround 003 (magenta goggle strap and armband; the coil, bushings, cable and trigger modelled as part of the body), smart mesh (quad topology), 8,196 triangles straight from Tripo; auto rig with the UE5 skeleton, preset animations kept in place; the 140 credits cover the model, rig and animation; Tripo P2.0 [Pro] auto rig and preset animations; Blender 5.2.3 LTS [local] | Henrik Ling | decimated to 8196 triangles, no separate prop, team material, clips renamed (tools/art finish) |
| assets/models/utility_ranger.glb | CC0-1.0 | https://quaternius.com/packs/animatedmech.html | Quaternius | clips renamed to idle/run/attack/hit/death, unused clips dropped (tools/remap_glb_anims.gd) |

## How this pack was made

Made by the art pilot (tools/art, docs/art-pipeline.md). Each model came from generated images (a character sheet and turnarounds), a Tripo mesh, a rig and a Blender finish, all steps recorded; the prompts and seeds are in the Source cell of the Art table.

| Stage | Tool | Version | Plan | Date | Cost |
|---|---|---|---|---|---|
| utility_conduit turnaround body | Nano Banana 2.1 | gemini-nano-banana-2.1 | Gemini API paid | 2026-10-29 | $0.05 |
| utility_conduit mesh body | Tripo | P2.0 | Pro | 2026-10-29 | $0.00 (140 Tripo credits) |
| utility_conduit rig | Tripo | P2.0 | Pro | 2026-10-29 | $0.00 |
| utility_conduit finish | Blender | 5.2.3 LTS | local | 2026-10-29 | $0.00 |
