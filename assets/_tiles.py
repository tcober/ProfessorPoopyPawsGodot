#!/usr/bin/env python3
"""Tileset kit: turn full-room compositions into a real two-layer Godot tileset.

The SNES workflow, automated — a generator paints the room on a LOWER Img
(drawn under entities) and an UPPER Img (transparent; drawn over entities so
bodies can pass behind railings, furniture tops, doorway lintels), then
slice_atlas() cuts both on the ZONE_TILE grid and dedupes identical cells into
ONE shared atlas, exactly like a tile editor squeezing a mockup into VRAM.
Repeated art (floor, wall field, tile-quantized light) collapses to shared
tiles; one-off art (window, furniture) keeps unique tiles. Output per room:

    <name>_tiles.png    the packed atlas (both layers share it)
    <name>_tiles.tres   TileSet (visuals only — collision stays on the
                        invisible collision_tileset.tres layer)
    <name>_layout.txt   per-cell atlas coords, one `layer` section each for
                        lower and upper; scene/tiled_map.gd stamps them

Generators that want the tiled READ must keep repeating art a function of
tile-local coordinates + per-cell variant hashes, and quantize light/shade
per tile — per-pixel gradients make every tile unique and kill the rhythm.

ANIMATED TILES (the SNES water cycle): a scene may hand slice_atlas a LIST of
N lower-canvas frames. A cell whose N frames are byte-identical dedupes to a
plain static tile; a cell that differs across frames becomes ONE animated
tile whose frames pack_tiles() lays out as N contiguous same-row atlas cells
(base cell leftmost — Godot's TileSetAtlasSource reads frames rightward).
The .tres declares animation_frames_count + per-frame durations on the base
cell ONLY — frame/padding cells must never get their own `x:y/0 = 0` line
(create_tile inside a reserved animation span poisons the whole TileSet).
"""
import os
from _core import ZONE_TILE, Img, write_png

ATLAS_COLS = 12   # atlas width in tiles; keeps the sheet roughly square

WATER_FRAME_DUR = 0.30   # sec/frame for animated tiles (SNES-slow 1.2s loop)

_EMPTY = None     # upper-grid marker for "no tile here"


def slice_atlas(imgs, tiles=None, seen=None, skip_empty=False):
    """Cut imgs on the ZONE_TILE grid, dedupe cells -> (tiles, grid).

    imgs: one Img or a list of N animation-frame Imgs (same dims). Each
    tile is the TUPLE of its per-frame cell bytes — all-identical frames
    collapse to the 1-frame static case, so single-Img callers behave
    exactly as before. tiles/seen thread through repeat calls so several
    canvases (lower + upper) share one atlas. With skip_empty, cells whose
    frame-0 is fully transparent become None in the grid instead of atlas
    entries (the upper layer is sparse).
    """
    if isinstance(imgs, Img):
        imgs = [imgs]
    t = ZONE_TILE
    for img in imgs:
        assert img.w == imgs[0].w and img.h == imgs[0].h, "frame dims differ"
    assert imgs[0].w % t == 0 and imgs[0].h % t == 0, "composition not tile-aligned"
    cols, rows = imgs[0].w // t, imgs[0].h // t
    tiles = [] if tiles is None else tiles
    seen = {} if seen is None else seen
    grid = []
    for ty in range(rows):
        row = []
        for tx in range(cols):
            frames = []
            for img in imgs:
                cell = bytearray()
                for y in range(ty * t, ty * t + t):
                    o = (y * img.w + tx * t) * 4
                    cell += img.buf[o:o + t * 4]
                frames.append(bytes(cell))
            if all(f == frames[0] for f in frames[1:]):
                frames = frames[:1]                    # static: dedupe as 1-frame
            key = tuple(frames)
            if skip_empty and not any(key[0][3::4]):
                row.append(_EMPTY)
                continue
            if key not in seen:
                seen[key] = len(tiles)
                tiles.append(key)
            row.append(seen[key])
        grid.append(row)
    return tiles, grid


def pack_tiles(tiles):
    """Lay out deduped frame-tuples -> (cells, coords).

    Statics (1-frame tuples) pack first in reading order — an all-static
    scene reproduces today's atlas byte-for-byte. Then the cell list pads
    with transparent tiles to a row boundary and each animated tile takes
    nf CONTIGUOUS same-row cells, base cell leftmost (ATLAS_COLS must
    divide evenly into nf-wide groups so no group straddles a row).
    Returns the flat atlas cell list (for write_atlas) and, per tile,
    coords[i] = (cx, cy, nframes) of its base cell.
    """
    t = ZONE_TILE
    blank = bytes(t * t * 4)
    cells, coords = [], [None] * len(tiles)
    for i, frames in enumerate(tiles):
        if len(frames) == 1:
            coords[i] = (len(cells) % ATLAS_COLS, len(cells) // ATLAS_COLS, 1)
            cells.append(frames[0])
    anim = [i for i, frames in enumerate(tiles) if len(frames) > 1]
    if anim:
        nf = len(tiles[anim[0]])
        assert all(len(tiles[i]) == nf for i in anim), "mixed frame counts"
        assert ATLAS_COLS % nf == 0, f"ATLAS_COLS={ATLAS_COLS} not divisible by {nf} frames"
        while len(cells) % ATLAS_COLS:
            cells.append(blank)                        # pad to a fresh row
        base_row, per_row = len(cells) // ATLAS_COLS, ATLAS_COLS // nf
        for j, i in enumerate(anim):
            coords[i] = ((j % per_row) * nf, base_row + j // per_row, nf)
            cells.extend(tiles[i])
    return cells, coords


def write_atlas(path, cells):
    """Pack the flat cell list into an ATLAS_COLS-wide sheet PNG."""
    t = ZONE_TILE
    rows = (len(cells) + ATLAS_COLS - 1) // ATLAS_COLS
    sheet = Img(ATLAS_COLS * t, rows * t)
    for i, cell in enumerate(cells):
        ox, oy = (i % ATLAS_COLS) * t, (i // ATLAS_COLS) * t
        for y in range(t):
            o = ((oy + y) * sheet.w + ox) * 4
            sheet.buf[o:o + t * 4] = cell[y * t * 4:(y + 1) * t * 4]
    write_png(path, sheet.w, sheet.h, sheet.buf)


def write_tileset_tres(path, png_res_path, coords, frame_dur=WATER_FRAME_DUR):
    """TileSet .tres declaring every atlas tile. Visuals only: no physics
    (collision is the shared invisible collision_tileset.tres layer).
    Animated tiles declare frame count + durations on the base cell; the
    frame cells to its right are reserved by Godot and get NO tile line."""
    t = ZONE_TILE
    lines = [
        '[gd_resource type="TileSet" load_steps=2 format=3]',
        '',
        f'[ext_resource type="Texture2D" path="{png_res_path}" id="1_tex"]',
        '',
        '[sub_resource type="TileSetAtlasSource" id="atlas_0"]',
        'texture = ExtResource("1_tex")',
        f'texture_region_size = Vector2i({t}, {t})',
    ]
    n_anim = 0
    for cx, cy, nf in coords:
        if nf > 1:
            n_anim += 1
            lines.append(f'{cx}:{cy}/animation_frames_count = {nf}')
            for f in range(nf):
                lines.append(f'{cx}:{cy}/animation_frame_{f}/duration = {frame_dur}')
        lines.append(f'{cx}:{cy}/0 = 0')
    lines += [
        '',
        '[resource]',
        f'tile_size = Vector2i({t}, {t})',
        'sources/0 = SubResource("atlas_0")',
        '',
    ]
    open(path, "w").write("\n".join(lines))
    anim_note = f", {n_anim} animated" if n_anim else ""
    print(f"wrote {os.path.basename(path)} ({len(coords)} tiles{anim_note})")


def write_layout(path, grids, coords, header=""):
    """Named layer sections of per-cell atlas coords, one map row per line
    ('cx,cy' tokens; '-' = empty cell). grids: {"lower": grid, "upper": grid}.
    Animated cells reference their BASE atlas cell. Parsed by
    scene/tiled_map.gd — keep formats in sync."""
    out = [f"; generated{' — ' + header if header else ''}; do not hand-edit"]
    for name, grid in grids.items():
        out.append(f"layer {name}")
        for row in grid:
            out.append(" ".join(
                "-" if i is _EMPTY else f"{coords[i][0]},{coords[i][1]}"
                for i in row))
    open(path, "w").write("\n".join(out) + "\n")
    print(f"wrote {os.path.basename(path)} "
          f"({'+'.join(grids)}: {len(grid[0])}x{len(grid)} cells)")
