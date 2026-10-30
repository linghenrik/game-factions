# Asset Credits

Most shipped 3D models and textures are **CC0 1.0 Universal / public domain** —
no attribution required, but the creators absolutely deserve it (and a coffee:
[patreon.com/quaternius](https://www.patreon.com/quaternius)). UI icons are
**CC BY 3.0** (<https://creativecommons.org/licenses/by/3.0/>) — attribution required; each pack's `CREDITS.md` credits them.

The shipped `.glb` files in each pack's `assets/models/` are converted from the
original downloads by the game's own build tools (animation clips renamed to
the canonical `idle`/`run`/`attack`/`hit`/`death` set, unused clips dropped).

Each pack's `CREDITS.md` lists its art (models, icons, textures) and its sounds, with
source, licence and edits; `tools/content/art_credits.py` and `audio_credits.py` check them.

Thank you to [Quaternius](https://quaternius.com) for the CC0 models.

## Audio

Every shipped sound is CC0 or public domain; each pack's `CREDITS.md` lists its
files, sources and edits (checked by `tools/content/audio_credits.py`).

## Main screen

The picture behind the front door and its title font. The picture is generated art, kept
in `docs/art/pilot/record.jsonl` under its id.

| File | Licence | Source | Author | Edits |
|---|---|---|---|---|
| client/art/main_screen.jpg | LicenseRef-Contributor | generated: Nano Banana 2.1 gemini-nano-banana-2.1 [Gemini API paid (prepay)] 2026-10-30; keyart keyart-main_screen-009, seed 1484156990, refs turnaround-elite_breaker-003, sheet-elite_breaker-006, turnaround-swarm_ranger-001, sheet-swarm_ranger-002, turnaround-utility_conduit-003 | Henrik Ling | converted to a 3840 px JPEG |
| client/fonts/IMFellEnglishSC-Regular.ttf | OFL-1.1 | https://fonts.google.com/specimen/IM+Fell+English+SC | Igino Marini | none |
