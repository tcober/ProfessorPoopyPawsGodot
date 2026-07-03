# Basil — Sprite Sheet Prompt (for Gemini / image gen)

The current `assets/basil.png` is a great character design but a **non-uniform pose
sheet** — the figures are different sizes and nearly touch, so it can't be sliced into
even animation cells. The game's `player_frames.tres` expects a **uniform grid**. Use the
prompt below to regenerate it in a clean, sliceable layout, then drop it in (see
"After you get the sheet").

## The prompt to paste into Gemini

> A 2D top-down character sprite sheet for a retro 16-bit action-RPG, in the style of
> The Legend of Zelda: A Link to the Past. Character: "Basil", a black cat scientist with
> green eyes wearing a white lab coat, holding a sci-fi **laser gun** (green/purple
> energy). Keep his design, colors, and proportions identical in every frame.
>
> Output ONE image laid out as a strict, evenly-spaced **grid of 6 columns by 7 rows**,
> each cell the **same square size**, character centered in every cell, with a fully
> **transparent background** and a small consistent gap between cells. No drop shadows, no
> text, no labels, no extra decorations. Pixel-art style, crisp edges (no anti-aliasing /
> no blur), consistent lighting and scale across all cells.
>
> Row by row (left to right):
> 1. Walk DOWN (facing the camera) — 6 frames of a walk cycle.
> 2. Walk UP (facing away) — 6 frames.
> 3. Walk RIGHT (facing right, profile) — 6 frames.
> 4. Shoot DOWN — 4 frames aiming/firing the laser gun toward the camera, then 2 empty cells.
> 5. Shoot UP — 4 frames firing upward/away, then 2 empty cells.
> 6. Shoot RIGHT — 4 frames firing to the right, then 2 empty cells.
> 7. Hurt/recoil — 2 frames flinching, then 4 empty cells.
>
> Every character must sit at the same position and size within its cell so the grid
> slices cleanly. Front view = facing down; back view = facing up.

## Tips for a cleaner result
- Generate a couple of times and keep the most grid-aligned one; image models drift.
- If it won't hold a perfect grid, ask it to "increase the spacing between cells and keep
  every cat the exact same size and centered."
- A **drink/refill** pose (cat raising a beaker) is a nice extra — add an 8th row of 4
  frames if you want a refill animation later.

## Target spec the engine assumes
- Final sheet sliced as **48×48 px cells, 6 columns × 7 rows → 288×336 px**, transparent,
  nearest-neighbor (no smoothing).
- Row order and frame counts exactly as listed above (this matches
  `entities/player/player_frames.tres`).
- If the grid ends up a different cell size, that's fine — we just update the `region`
  rectangles in `player_frames.tres` to match.

## After you get the sheet
1. Save it as `assets/basil_sheet.png` (keep the original `basil.png`).
2. In Godot, open `player_frames.tres` and either re-point the AtlasTexture `atlas` to the
   new PNG, or use the SpriteFrames editor's "Add frames from sprite sheet" with 6×7.
3. No code changes needed — `player.gd` plays animations by name
   (`walk_*`, `idle_*`, `shoot_*`, `hurt`).
