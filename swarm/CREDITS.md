# Swarm credits

## Audio

Every sound in this pack is CC0-1.0 or public domain (PDM-1.0); sounds we generated are released as CC0-1.0. CI checks this table (tools/content/audio_credits.py). Built by tools/audio/sound.py build.

| File | Licence | Source | Author | Edits |
|---|---|---|---|---|
| assets/audio/swarm_ability_cast.ogg | CC0-1.0 | https://freesound.org/s/590612/ | MrFossy | copy of base assets/audio/ability_cast.ogg; mono, +1.1 dB to -18 LUFS, Ogg Vorbis q3, from the Freesound HQ preview |

## Art

Every model, icon and texture in this pack is CC0, public domain or CC BY (credited here), or made by the contributor named in its row, who keeps the copyright; the game uses it under LICENSE.md. CI checks this table (pack-tools/art_credits.py; the guide is docs/art-pipeline.md).

| File | Licence | Source | Author | Edits |
|---|---|---|---|---|
| assets/models/swarm_breaker.glb | CC0-1.0 | https://quaternius.com/packs/cutemonsters.html | Quaternius | clips renamed to idle/run/attack/hit/death, unused clips dropped (tools/remap_glb_anims.gd) |
| assets/models/swarm_conduit.glb | CC0-1.0 | https://quaternius.com/packs/cutemonsters.html | Quaternius | clips renamed to idle/run/attack/hit/death, unused clips dropped (tools/remap_glb_anims.gd) |
| assets/models/swarm_ranger.glb | LicenseRef-Contributor | generated: Nano Banana 2.1 gemini-nano-banana-2.1 [Gemini API paid] 2026-10-29; sheet sheet-swarm_ranger-002 'A character design sheet for The Auditor, a hero of a top-down strategy game, on a plain light background. A portly company marksman in a bowler hat and a tailored three-piece suit with long coat tails lined in plum, a plum tie and a watch chain, with a thick ledger strapped to his left hip. He carries a scoped bolt-action rifle in both hands. Seen from above, the shape is the bowler's round crown and the coat tails. Show: (1) the full figure large, holding the rifle across his body; (2) a smaller view aiming the rifle from the shoulder; (3) a smaller view standing at rest, the rifle in his right hand pointing at the ground; (4) a view from directly above while he walks forward: the round bowler crown, the shoulders and the coat tails; (5) the rifle alone, from the side; (6) a close-up of the ledger. Keep the rifle clearly separate from his body and hands in every view. Bold graphic-novel ink: heavy black outlines, flat colour and heavy black shadows; muted charcoal, grey and brown on a muddy ground, with plum as the only bright accent. Near-standard human proportions, the heroes a little portly. One plum accent, the colour of company ink. Corporate greed and old generals sending young men to war. Well kept and well fed, the opposite of the rough, hard-working Elite: the heroes are a little portly and neatly groomed, and everyone wears a tailored suit, with waistcoats, watch chains, bowler hats, polished shoes and pressed creases. Ledgers, stamped forms, brass and rubber stamps. No blood, no gore. Must read from a top-down camera, so the head, shoulders and whatever is carried or worn on the back carry the shape. Match the attached picture's style, and take his design from the Ranger in it.', seed 747770025, refs bible-swarm-003; turnarounds turnaround-swarm_ranger-001; Tripo P2.0 [Pro] 2026-10-29, task https://studio.tripo3d.ai/workspace/animate/a-portly-company-marksman-in-a-bowler-hat-and-a-tailored-three-piece-s-5bbd09b6-b17d-4a66-a549-924376fda8e6, multi-view image to 3D from the four views of the kept T-pose turnaround (magenta hat band and armband), smart mesh (quad topology), 5,284 triangles straight from Tripo; auto rig with the UE5 skeleton, preset animations kept in place; the 50 credits cover the model, rig and animation; prop Tripo P2.0 [Pro] 2026-10-29, task https://studio.tripo3d.ai/workspace/texture/014f96ce-e465-4448-9760-4635c256a926, image to 3D from the rifle's side view cropped from the kept sheet, smart mesh (quad topology), 1,362 triangles straight from Tripo; Tripo P2.0 [Pro] auto rig and preset animations; Blender 5.2.3 LTS [local] | Henrik Ling | decimated to 8008 triangles, prop fixed to hand_r when drawn and to spine_03 when stowed, team material, clips renamed (tools/art finish) |
| assets/models/swarm_swarmling.glb | CC0-1.0 | https://quaternius.com/packs/cutemonsters.html | Quaternius | clips renamed to idle/run/attack/hit/death, unused clips dropped (tools/remap_glb_anims.gd) |

## How this pack was made

Made by the art pilot (tools/art, docs/art-pipeline.md). Each model came from generated images (a character sheet and turnarounds), a Tripo mesh, a rig and a Blender finish, all steps recorded; the prompts and seeds are in the Source cell of the Art table.

| Stage | Tool | Version | Plan | Date | Cost |
|---|---|---|---|---|---|
| swarm_ranger sheet | Nano Banana 2.1 | gemini-nano-banana-2.1 | Gemini API paid | 2026-10-29 | $0.05 |
| swarm_ranger turnaround body | Nano Banana 2.1 | gemini-nano-banana-2.1 | Gemini API paid | 2026-10-29 | $0.05 |
| swarm_ranger mesh body | Tripo | P2.0 | Pro | 2026-10-29 | $0.00 (50 Tripo credits) |
| swarm_ranger mesh prop | Tripo | P2.0 | Pro | 2026-10-29 | $0.00 (40 Tripo credits) |
| swarm_ranger rig | Tripo | P2.0 | Pro | 2026-10-29 | $0.00 |
| swarm_ranger finish | Blender | 5.2.3 LTS | local | 2026-10-29 | $0.00 |
