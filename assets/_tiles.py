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
"""
import os
from _core import ZONE_TILE, Img, write_png

ATLAS_COLS = 12   # atlas width in tiles; keeps the sheet roughly square

_EMPTY = None     # upper-grid marker for "no tile here"


def slice_atlas(img, tiles=None, seen=None, skip_empty=False):
    """Cut img on the ZONE_TILE grid, dedupe cells -> (tiles, grid).

    tiles/seen thread through repeat calls so several canvases (lower +
    upper) share one atlas. With skip_empty, fully transparent cells become
    None in the grid instead of atlas entries (the upper layer is sparse).
    """
    t = ZONE_TILE
    assert img.w % t == 0 and img.h % t == 0, "composition not tile-aligned"
    cols, rows = img.w // t, img.h // t
    tiles = [] if tiles is None else tiles
    seen = {} if seen is None else seen
    grid = []
    for ty in range(rows):
        row = []
        for tx in range(cols):
            cell = bytearray()
            for y in range(ty * t, ty * t + t):
                o = (y * img.w + tx * t) * 4
                cell += img.buf[o:o + t * 4]
            key = bytes(cell)
            if skip_empty and not any(key[3::4]):
                row.append(_EMPTY)
                continue
            if key not in seen:
                seen[key] = len(tiles)
                tiles.append(key)
            row.append(seen[key])
        grid.append(row)
    return tiles, grid


def write_atlas(path, tiles):
    """Pack deduped tiles into an ATLAS_COLS-wide sheet PNG."""
    t = ZONE_TILE
    rows = (len(tiles) + ATLAS_COLS - 1) // ATLAS_COLS
    sheet = Img(ATLAS_COLS * t, rows * t)
    for i, cell in enumerate(tiles):
        ox, oy = (i % ATLAS_COLS) * t, (i // ATLAS_COLS) * t
        for y in range(t):
            o = ((oy + y) * sheet.w + ox) * 4
            sheet.buf[o:o + t * 4] = cell[y * t * 4:(y + 1) * t * 4]
    write_png(path, sheet.w, sheet.h, sheet.buf)


def write_tileset_tres(path, png_res_path, n_tiles):
    """TileSet .tres declaring every atlas tile. Visuals only: no physics
    (collision is the shared invisible collision_tileset.tres layer)."""
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
    for i in range(n_tiles):
        lines.append(f'{i % ATLAS_COLS}:{i // ATLAS_COLS}/0 = 0')
    lines += [
        '',
        '[resource]',
        f'tile_size = Vector2i({t}, {t})',
        'sources/0 = SubResource("atlas_0")',
        '',
    ]
    open(path, "w").write("\n".join(lines))
    print(f"wrote {os.path.basename(path)} ({n_tiles} tiles)")


def write_layout(path, grids, header=""):
    """Named layer sections of per-cell atlas coords, one map row per line
    ('cx,cy' tokens; '-' = empty cell). grids: {"lower": grid, "upper": grid}.
    Parsed by scene/tiled_map.gd — keep formats in sync."""
    out = [f"; generated{' — ' + header if header else ''}; do not hand-edit"]
    for name, grid in grids.items():
        out.append(f"layer {name}")
        for row in grid:
            out.append(" ".join(
                "-" if i is _EMPTY else f"{i % ATLAS_COLS},{i // ATLAS_COLS}"
                for i in row))
    open(path, "w").write("\n".join(out) + "\n")
    print(f"wrote {os.path.basename(path)} "
          f"({'+'.join(grids)}: {len(grid[0])}x{len(grid)} cells)")
