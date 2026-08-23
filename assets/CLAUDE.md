# assets/ — the procedural art pipeline

**Load the `art-pipeline` skill before editing anything here.** For map txt files, prop
placement, cliffs and z-order, load **`map-authoring`** as well.

All art is drawn by stdlib-only Python. Never hand-edit a generated PNG — edit the
generator and re-run it. `docs/reference/` is concept art only, parked behind a
`.gdignore`.

The same doctrine covers audio: `_gen_music.py` synthesizes the four looping
tracks in `assets/audio/` from hand-written note tables, and `_gen_sfx.py` the
one-shot menu/dialogue set — mono, non-looping, including the three Star-Fox
talk-blip voice timbres that `scene/sfx.gd` pitches per speaker (see DESIGN.md →
"Music"). Edit the generator, never a WAV, and `--headless --import` after
regenerating.

The three rules that break things most often:

1. **Regenerate → lint → import**, always in that order:
   `python3 assets/_gen_*.py` → `python3 assets/_check_art.py` →
   `godot --headless --import`. Game runs never re-import, so a regenerated atlas renders
   scrambled until you do.
2. **Dedupe is the point.** Cells must be byte-identical by construction — fabric texture
   is tile-local (`_grain_dither` / `_hatch`) and **never keyed on absolute position**.
   Watch the tile count out of `finish()`; a jump means something broke it.
3. **Keep `_maps.py` and `scene/map_data.gd` parsers in sync** — the same map txt drives
   both paint and collision, and that is the only reason they can't drift.

Byte-locked twins must move together: `maps/town.txt` ↔ `maps/town_fest.txt`,
`maps/overworld.txt` ↔ `maps/overworld_bright.txt`, and `maps/downstairs.txt` ↔
`maps/downstairs_bare.txt` (same grid + anchors; only the east lab corner and
the mom door's walk bit differ — scene/downstairs_fever.gd swaps between them
on a story flag).
