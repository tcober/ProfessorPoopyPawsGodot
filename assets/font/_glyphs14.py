"""Native high-res pixel font glyphs: 10x16 cells, baseline after row 13.

Caps, digits and punctuation are derived from the legacy 5x7 set (_pixfont) via
Scale2x — the corner-rounding upscale — so they keep their proportions but lose
the doubled-pixel staircase. Lowercase a–z are hand-drawn natives (x-height rows
5–13, ascenders from row 1, descenders to row 15) — real lowercase is what makes
dialog read like an SNES RPG instead of a marquee.

Rendered by assets/font/_gen_font.py at BMFont size=16 → Labels with
font_size=16 draw 1:1 (metrics footprint identical to the old doubled font:
advance 12, line height 18).
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _pixfont import GLYPHS as _SRC

CHAR_W, CHAR_H = 10, 16
ADVANCE = 12
BASE = 14            # px from line top to baseline

_BLANK = "." * CHAR_W


def _scale2x(rows):
    """Scale2x: 2x upscale that rounds staircase corners on 1-bit art."""
    h, w = len(rows), len(rows[0])

    def at(x, y):
        if 0 <= x < w and 0 <= y < h:
            return rows[y][x]
        return "."

    out = [["."] * (w * 2) for _ in range(h * 2)]
    for y in range(h):
        for x in range(w):
            p = at(x, y)
            a, b = at(x, y - 1), at(x + 1, y)
            c, d = at(x - 1, y), at(x, y + 1)
            e0 = a if (c == a and c != d and a != b) else p
            e1 = b if (a == b and a != c and b != d) else p
            e2 = c if (d == c and d != b and c != a) else p
            e3 = d if (b == d and b != a and d != c) else p
            out[y * 2][x * 2] = e0
            out[y * 2][x * 2 + 1] = e1
            out[y * 2 + 1][x * 2] = e2
            out[y * 2 + 1][x * 2 + 1] = e3
    return ["".join(r) for r in out]


def _cell(rows, start=0):
    """Pad rows into a full 10x16 cell starting at `start`."""
    assert all(len(r) == CHAR_W for r in rows), rows
    out = [_BLANK] * start + list(rows) + [_BLANK] * (CHAR_H - start - len(rows))
    assert len(out) == CHAR_H
    return out


# ---- caps / digits / punctuation: Scale2x of the 5x7 set (rows 0-13) ---------------
GLYPHS16 = {}
for _ch, _rows in _SRC.items():
    _start = 2 if _ch in (",", ";") else 0     # commas dip below the baseline
    GLYPHS16[_ch] = _cell(_scale2x(_rows), start=_start)

# ---- hand-drawn lowercase (2px strokes; x-height rows 5-13) --------------------------
_LOWER = {
    "a": _cell([
        "..XXXXX...",
        ".XXXXXXX..",
        "......XX..",
        ".XXXXXXX..",
        "XX....XX..",
        "XX....XX..",
        "XX...XXX..",
        ".XXXXXXX..",
        "..XXX.XX..",
    ], 5),
    "b": _cell([
        "XX........",
        "XX........",
        "XX........",
        "XX........",
        "XX.XXXX...",
        "XXXXXXXX..",
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
        "XXXXXXXX..",
        "XX.XXXX...",
        "..........",
    ], 1),
    "c": _cell([
        "..XXXXX...",
        ".XXXXXXX..",
        "XX....XX..",
        "XX........",
        "XX........",
        "XX........",
        "XX....XX..",
        ".XXXXXXX..",
        "..XXXXX...",
    ], 5),
    "d": _cell([
        "......XX..",
        "......XX..",
        "......XX..",
        "......XX..",
        "..XXXX.XX.",
        ".XXXXXXXX.",
        "XX.....XX.",
        "XX.....XX.",
        "XX.....XX.",
        "XX.....XX.",
        ".XXXXXXXX.",
        "..XXXX.XX.",
        "..........",
    ], 1),
    "e": _cell([
        "..XXXXX...",
        ".XXXXXXX..",
        "XX....XX..",
        "XXXXXXXX..",
        "XXXXXXXX..",
        "XX........",
        "XX....XX..",
        ".XXXXXXX..",
        "..XXXXX...",
    ], 5),
    "f": _cell([
        "...XXXX...",
        "..XXXXXX..",
        "..XX..XX..",
        "..XX......",
        "XXXXXX....",
        "XXXXXX....",
        "..XX......",
        "..XX......",
        "..XX......",
        "..XX......",
        "..XX......",
        "..XX......",
        "..........",
    ], 1),
    "g": _cell([
        "..XXXX.XX.",
        ".XXXXXXXX.",
        "XX.....XX.",
        "XX.....XX.",
        "XX.....XX.",
        "XX.....XX.",
        ".XXXXXXXX.",
        "..XXXX.XX.",
        ".......XX.",
        "XX....XX..",
        ".XXXXXX...",
    ], 5),
    "h": _cell([
        "XX........",
        "XX........",
        "XX........",
        "XX........",
        "XX.XXXX...",
        "XXXXXXXX..",
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
        "..........",
    ], 1),
    "i": _cell([
        "...XX.....",
        "...XX.....",
        "..........",
        "..XXX.....",
        "..XXX.....",
        "...XX.....",
        "...XX.....",
        "...XX.....",
        "...XX.....",
        "...XX.....",
        "..XXXX....",
        "..XXXX....",
        "..........",
    ], 1),
    "j": _cell([
        ".....XX...",
        ".....XX...",
        "..........",
        "....XXX...",
        "....XXX...",
        ".....XX...",
        ".....XX...",
        ".....XX...",
        ".....XX...",
        ".....XX...",
        ".....XX...",
        ".....XX...",
        "..XX.XX...",
        "..XXXXX...",
        "...XXX....",
    ], 1),
    "k": _cell([
        "XX........",
        "XX........",
        "XX........",
        "XX........",
        "XX...XXX..",
        "XX..XXX...",
        "XX.XXX....",
        "XXXXX.....",
        "XXXXX.....",
        "XX.XXX....",
        "XX..XXX...",
        "XX...XXX..",
        "..........",
    ], 1),
    "l": _cell([
        "..XXX.....",
        "..XXX.....",
        "...XX.....",
        "...XX.....",
        "...XX.....",
        "...XX.....",
        "...XX.....",
        "...XX.....",
        "...XX.....",
        "...XX.....",
        "..XXXX....",
        "..XXXX....",
        "..........",
    ], 1),
    "m": _cell([
        "XXXXX.XX..",
        "XXXXXXXXX.",
        "XX..XX..XX",
        "XX..XX..XX",
        "XX..XX..XX",
        "XX..XX..XX",
        "XX..XX..XX",
        "XX..XX..XX",
        "XX..XX..XX",
    ], 5),
    "n": _cell([
        "XX.XXXX...",
        "XXXXXXXX..",
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
    ], 5),
    "o": _cell([
        "..XXXXX...",
        ".XXXXXXX..",
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
        ".XXXXXXX..",
        "..XXXXX...",
    ], 5),
    "p": _cell([
        "XX.XXXX...",
        "XXXXXXXX..",
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
        "XXXXXXXX..",
        "XX.XXXX...",
        "XX........",
        "XX........",
        "XX........",
    ], 5),
    "q": _cell([
        "..XXXX.XX.",
        ".XXXXXXXX.",
        "XX.....XX.",
        "XX.....XX.",
        "XX.....XX.",
        "XX.....XX.",
        ".XXXXXXXX.",
        "..XXXX.XX.",
        ".......XX.",
        ".......XX.",
        ".......XX.",
    ], 5),
    "r": _cell([
        "XX.XXXX...",
        "XXXXXXXX..",
        "XXX...XX..",
        "XX........",
        "XX........",
        "XX........",
        "XX........",
        "XX........",
        "XX........",
    ], 5),
    "s": _cell([
        ".XXXXXX...",
        "XXXXXXXX..",
        "XX........",
        ".XXXXX....",
        "..XXXXX...",
        "......XX..",
        "......XX..",
        "XXXXXXXX..",
        ".XXXXXX...",
    ], 5),
    "t": _cell([
        "..XX......",
        "..XX......",
        "..XX......",
        "..XX......",
        "XXXXXX....",
        "XXXXXX....",
        "..XX......",
        "..XX......",
        "..XX......",
        "..XX......",
        "..XX..XX..",
        "..XXXXXX..",
        "...XXXX...",
    ], 1),
    "u": _cell([
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
        "XX....XX..",
        "XX...XXX..",
        ".XXXXXXX..",
        "..XXX.XX..",
    ], 5),
    "v": _cell([
        "XX.....XX.",
        "XX.....XX.",
        "XX.....XX.",
        ".XX...XX..",
        ".XX...XX..",
        ".XX...XX..",
        "..XX.XX...",
        "..XXXXX...",
        "...XXX....",
    ], 5),
    "w": _cell([
        "XX..XX..XX",
        "XX..XX..XX",
        "XX..XX..XX",
        "XX..XX..XX",
        "XX..XX..XX",
        "XX..XX..XX",
        "XX..XX..XX",
        "XXXXXXXXX.",
        ".XX.XXXX..",
    ], 5),
    "x": _cell([
        "XX....XX..",
        "XXX..XXX..",
        ".XX..XX...",
        "..XXXX....",
        "...XX.....",
        "..XXXX....",
        ".XX..XX...",
        "XXX..XXX..",
        "XX....XX..",
    ], 5),
    "y": _cell([
        "XX.....XX.",
        "XX.....XX.",
        "XX.....XX.",
        "XX.....XX.",
        "XX.....XX.",
        "XX.....XX.",
        ".XXXXXXXX.",
        "..XXXX.XX.",
        ".......XX.",
        "XX....XX..",
        ".XXXXXX...",
    ], 5),
    "z": _cell([
        "XXXXXXXX..",
        "XXXXXXXX..",
        ".....XX...",
        "....XX....",
        "...XX.....",
        "..XX......",
        ".XX.......",
        "XXXXXXXX..",
        "XXXXXXXX..",
    ], 5),
}
GLYPHS16.update(_LOWER)
