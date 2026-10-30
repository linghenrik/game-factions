# Elite credits

## Audio

Every sound in this pack is CC0-1.0 or public domain (PDM-1.0); sounds we generated are released as CC0-1.0. CI checks this table (tools/content/audio_credits.py). Built by tools/audio/sound.py build.

| File | Licence | Source | Author | Edits |
|---|---|---|---|---|
| assets/audio/elite_ability_cast.ogg | CC0-1.0 | https://freesound.org/s/590612/ | MrFossy | copy of base assets/audio/ability_cast.ogg; mono, +1.1 dB to -18 LUFS, Ogg Vorbis q3, from the Freesound HQ preview |

## Art

Every model, icon and texture in this pack is CC0, public domain or CC BY (credited here), or made by the contributor named in its row, who keeps the copyright; the game uses it under LICENSE.md. CI checks this table (pack-tools/art_credits.py; the guide is docs/art-pipeline.md).

| File | Licence | Source | Author | Edits |
|---|---|---|---|---|
| assets/models/elite_breaker.glb | LicenseRef-Contributor | generated: Nano Banana 2.1 gemini-nano-banana-2.1 [Gemini API paid] 2026-10-28; sheet sheet-elite_breaker-006 'A character design sheet for The Yoke, a hero of a top-down strategy game, on a plain light background. A huge ploughman who leans forward and drags an old wooden ard behind him with one hand: he grips the crossbar at the front end of its long beam in his right hand, and his left hand is free. An iron-shod share sits at the back end. It is pulled, not pushed, so it has no handles at the back. He carries no other weapon. An ox jawbone (the lower jaw, with its teeth) bound to his belt as a bloodline bone; no skulls. Seen from above, the shape is the long beam trailing straight behind him. Show: (1) the full figure large, dragging the ard with his right hand; (2) a smaller view swinging the ard one-handed by its crossbar, the same ard with only its share at the end, no axe blade; (3) a smaller view standing at rest, the beam in his right hand and the share on the ground; (4) a view from directly above while he walks forward dragging the ard: his head and shoulders, with the beam running from his right hand straight back behind him; (5) the ard alone, from the side; (6) a close-up of the ox jawbone. Keep the ard clearly separate from his body and hands in every view. Dark, semi-realistic painted concept art: muted earthy colour, soft painterly rendering, dramatic rim light against a dark background, figures standing in churned mud and straw. Heavy, weathered, hand-made materials. Near-standard human proportions. One bone and linen accent. A clan of farming families proud of their bloodlines, their strength and their legacy: broad, muscular, well-fed people. Each wears bloodline bones, heirloom bones of the family's champion animals, carved with one notch per generation and bound with linen. No rosettes or ribbons. Ploughs, sacking, rope, straw, worn wool and leather: people who work the land and now fight for it. No blood, no gore. Must read from a top-down camera, so the head, shoulders and whatever is carried or worn on the back carry the shape. Match the attached pictures' style, and take his design from the Breaker in them.', seed 999097730, refs bible-elite-020, bible-elite-021; turnarounds turnaround-elite_breaker-003, turnaround-elite_breaker_prop-001; Tripo P2.0 [Pro] 2026-10-28, task https://studio.tripo3d.ai/workspace/texture/d7b81408-49af-468a-b82c-920d0eb58ade, image to 3D with smart mesh (quad topology), auto rig with the UE5 skeleton, preset animations kept in place; the 300 credits cover the model, rig and animation tries together; prop Tripo v3.1 [Pro] 2026-10-28, task https://studio.tripo3d.ai/workspace/texture/d4e15dcf-e809-462c-8257-628aa9fdd9c6, image to 3D, single image cut from the kept turnaround; polycount about 50k, generate in parts off, AI complete on, smart mesh off, detailed texture, remove lighting on, 2K texture; Tripo P2.0 [Pro] auto rig and preset animations; Blender 5.2.3 LTS [local] | Henrik Ling | decimated to 9800 triangles, prop fixed to hand_r, team material, clips renamed (tools/art finish) |
| assets/models/elite_bruiser.glb | CC0-1.0 | https://quaternius.com/packs/ultimatedanimatedcharacter.html | Quaternius | clips renamed to idle/run/attack/hit/death, unused clips dropped (tools/remap_glb_anims.gd) |
| assets/models/elite_conduit.glb | CC0-1.0 | https://quaternius.com/packs/ultimatedanimatedcharacter.html | Quaternius | clips renamed to idle/run/attack/hit/death, unused clips dropped (tools/remap_glb_anims.gd) |
| assets/models/elite_ranger.glb | CC0-1.0 | https://quaternius.com/packs/ultimatedanimatedcharacter.html | Quaternius | clips renamed to idle/run/attack/hit/death, unused clips dropped (tools/remap_glb_anims.gd) |

## How this pack was made

Made by the art pilot (tools/art, docs/art-pipeline.md). Each model came from generated images (a character sheet and turnarounds), a Tripo mesh, a rig and a Blender finish, all steps recorded; the prompts and seeds are in the Source cell of the Art table.

| Stage | Tool | Version | Plan | Date | Cost |
|---|---|---|---|---|---|
| elite_breaker sheet | Nano Banana 2.1 | gemini-nano-banana-2.1 | Gemini API paid | 2026-10-28 | $0.05 |
| elite_breaker turnaround body | Nano Banana 2.1 | gemini-nano-banana-2.1 | Gemini API paid | 2026-10-28 | $0.05 |
| elite_breaker turnaround prop | Nano Banana 2.1 | gemini-nano-banana-2.1 | Gemini API paid | 2026-10-28 | $0.05 |
| elite_breaker mesh body | Tripo | P2.0 | Pro | 2026-10-28 | $0.00 (300 Tripo credits) |
| elite_breaker mesh prop | Tripo | v3.1 | Pro | 2026-10-28 | $0.00 (40 Tripo credits) |
| elite_breaker rig | Tripo | P2.0 | Pro | 2026-10-28 | $0.00 |
| elite_breaker finish | Blender | 5.2.3 LTS | local | 2026-10-28 | $0.00 |
