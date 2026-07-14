"""Shared 5x7 pixel font: glyph bitmaps + a draw helper.

Used by _gen_font.py (bakes assets/font/pixel_font.png + .fnt for Godot Labels) and by
art generators that stamp text straight into images (title logo, chalkboard, signs).
Caps + LOWERCASE + digits + basic punctuation. UI chrome stays uppercase by
convention; mixed case is for the dialog system (2026-07-12). Lowercase glyphs
are 7-row bitmaps like the caps, but sit 2px lower via YOFF (x-height rows
2-6 of the line box; descenders dip 2px below the baseline — _gen_font.py
writes the per-char yoffset and a lineHeight that clears them). draw_text()
still uppercases: art generators stamp caps-only signage.
"""

# 7 rows x 5 cols, 'X' = pixel on.
GLYPHS = {
    "A": [".XXX.", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    "B": ["XXXX.", "X...X", "X...X", "XXXX.", "X...X", "X...X", "XXXX."],
    "C": [".XXXX", "X....", "X....", "X....", "X....", "X....", ".XXXX"],
    "D": ["XXXX.", "X...X", "X...X", "X...X", "X...X", "X...X", "XXXX."],
    "E": ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "XXXXX"],
    "F": ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "X...."],
    "G": [".XXXX", "X....", "X....", "X..XX", "X...X", "X...X", ".XXXX"],
    "H": ["X...X", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    "I": ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "XXXXX"],
    "J": ["..XXX", "...X.", "...X.", "...X.", "...X.", "X..X.", ".XX.."],
    "K": ["X...X", "X..X.", "X.X..", "XX...", "X.X..", "X..X.", "X...X"],
    "L": ["X....", "X....", "X....", "X....", "X....", "X....", "XXXXX"],
    "M": ["X...X", "XX.XX", "X.X.X", "X.X.X", "X...X", "X...X", "X...X"],
    "N": ["X...X", "XX..X", "X.X.X", "X..XX", "X...X", "X...X", "X...X"],
    "O": [".XXX.", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    "P": ["XXXX.", "X...X", "X...X", "XXXX.", "X....", "X....", "X...."],
    "Q": [".XXX.", "X...X", "X...X", "X...X", "X.X.X", "X..X.", ".XX.X"],
    "R": ["XXXX.", "X...X", "X...X", "XXXX.", "X.X..", "X..X.", "X...X"],
    "S": [".XXXX", "X....", "X....", ".XXX.", "....X", "....X", "XXXX."],
    "T": ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "..X.."],
    "U": ["X...X", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    "V": ["X...X", "X...X", "X...X", "X...X", "X...X", ".X.X.", "..X.."],
    "W": ["X...X", "X...X", "X...X", "X.X.X", "X.X.X", "XX.XX", "X...X"],
    "X": ["X...X", "X...X", ".X.X.", "..X..", ".X.X.", "X...X", "X...X"],
    "Y": ["X...X", "X...X", ".X.X.", "..X..", "..X..", "..X..", "..X.."],
    "Z": ["XXXXX", "....X", "...X.", "..X..", ".X...", "X....", "XXXXX"],
    "0": [".XXX.", "X...X", "X..XX", "X.X.X", "XX..X", "X...X", ".XXX."],
    "1": ["..X..", ".XX..", "..X..", "..X..", "..X..", "..X..", "XXXXX"],
    "2": [".XXX.", "X...X", "....X", "..XX.", ".X...", "X....", "XXXXX"],
    "3": ["XXXX.", "....X", "....X", ".XXX.", "....X", "....X", "XXXX."],
    "4": ["...X.", "..XX.", ".X.X.", "X..X.", "XXXXX", "...X.", "...X."],
    "5": ["XXXXX", "X....", "XXXX.", "....X", "....X", "X...X", ".XXX."],
    "6": [".XXX.", "X....", "X....", "XXXX.", "X...X", "X...X", ".XXX."],
    "7": ["XXXXX", "....X", "...X.", "..X..", ".X...", ".X...", ".X..."],
    "8": [".XXX.", "X...X", "X...X", ".XXX.", "X...X", "X...X", ".XXX."],
    "9": [".XXX.", "X...X", "X...X", ".XXXX", "....X", "....X", ".XXX."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".XX..", ".XX.."],
    ",": [".....", ".....", ".....", ".....", "..XX.", "..X..", ".X..."],
    "!": ["..X..", "..X..", "..X..", "..X..", "..X..", ".....", "..X.."],
    "?": [".XXX.", "X...X", "....X", "..XX.", "..X..", ".....", "..X.."],
    "'": ["..X..", "..X..", ".....", ".....", ".....", ".....", "....."],
    "\"": [".X.X.", ".X.X.", ".....", ".....", ".....", ".....", "....."],
    "-": [".....", ".....", ".....", ".XXX.", ".....", ".....", "....."],
    ":": [".....", ".XX..", ".XX..", ".....", ".XX..", ".XX..", "....."],
    ";": [".....", ".XX..", ".XX..", ".....", ".XX..", ".X...", "X...."],
    "(": ["...X.", "..X..", ".X...", ".X...", ".X...", "..X..", "...X."],
    ")": [".X...", "..X..", "...X.", "...X.", "...X.", "..X..", ".X..."],
    "/": ["....X", "...X.", "...X.", "..X..", ".X...", ".X...", "X...."],
    "+": [".....", "..X..", "..X..", "XXXXX", "..X..", "..X..", "....."],
    "=": [".....", ".....", "XXXXX", ".....", "XXXXX", ".....", "....."],
    "*": [".....", "X.X.X", ".XXX.", "XXXXX", ".XXX.", "X.X.X", "....."],
    "▼": [".....", ".....", "XXXXX", ".XXX.", "..X..", ".....", "....."],
    # ---- lowercase (2026-07-12, for the dialog system). Same 5x7 cell; YOFF
    # below sinks each glyph 2px so the x-height fills line rows 2-6 and the
    # descender letters (g j p q y) dip 2px below the baseline. Ascenders
    # (b d f h i k l t) keep yoff 0 and use the full 7 rows.
    "a": [".XXX.", "....X", ".XXXX", "X...X", ".XXXX", ".....", "....."],
    "b": ["X....", "X....", "X....", "XXXX.", "X...X", "X...X", "XXXX."],
    "c": [".XXX.", "X....", "X....", "X....", ".XXX.", ".....", "....."],
    "d": ["....X", "....X", "....X", ".XXXX", "X...X", "X...X", ".XXXX"],
    "e": [".XXX.", "X...X", "XXXXX", "X....", ".XXX.", ".....", "....."],
    "f": ["..XX.", ".X...", ".X...", "XXXX.", ".X...", ".X...", ".X..."],
    "g": [".XXXX", "X...X", "X...X", "X...X", ".XXXX", "....X", ".XXX."],
    "h": ["X....", "X....", "X....", "XXXX.", "X...X", "X...X", "X...X"],
    "i": ["..X..", ".....", ".XX..", "..X..", "..X..", "..X..", ".XXX."],
    "j": ["..X..", ".....", "..X..", "..X..", "..X..", "X.X..", ".X..."],
    "k": ["X....", "X....", "X..X.", "X.X..", "XXX..", "X.X..", "X..X."],
    "l": ["..X..", "..X..", "..X..", "..X..", "..X..", "..X..", "...XX"],
    "m": ["XXXX.", "X.X.X", "X.X.X", "X.X.X", "X.X.X", ".....", "....."],
    "n": ["XXXX.", "X...X", "X...X", "X...X", "X...X", ".....", "....."],
    "o": [".XXX.", "X...X", "X...X", "X...X", ".XXX.", ".....", "....."],
    "p": ["XXXX.", "X...X", "X...X", "X...X", "XXXX.", "X....", "X...."],
    "q": [".XXXX", "X...X", "X...X", "X...X", ".XXXX", "....X", "....X"],
    "r": ["X.XX.", "XX..X", "X....", "X....", "X....", ".....", "....."],
    "s": [".XXXX", "X....", ".XXX.", "....X", "XXXX.", ".....", "....."],
    "t": [".X...", ".X...", "XXXX.", ".X...", ".X...", ".X...", "..XX."],
    "u": ["X...X", "X...X", "X...X", "X...X", ".XXXX", ".....", "....."],
    "v": ["X...X", "X...X", "X...X", ".X.X.", "..X..", ".....", "....."],
    "w": ["X...X", "X...X", "X.X.X", "X.X.X", ".X.X.", ".....", "....."],
    "x": ["X...X", ".X.X.", "..X..", ".X.X.", "X...X", ".....", "....."],
    "y": ["X...X", "X...X", "X...X", "X...X", ".XXXX", "....X", ".XXX."],
    "z": ["XXXXX", "...X.", "..X..", ".X...", "XXXXX", ".....", "....."],
}

# per-char y offset from the line top (see the lowercase note above)
YOFF = {c: 2 for c in "acegjmnopqrsuvwxy"}
YOFF["z"] = 2

CHAR_W, CHAR_H = 5, 7
ADVANCE = 6          # monospace advance at scale 1


def draw_text(put, text, x, y, color, scale=1):
    """Stamp `text` with pixel-callback put(px, py, color). Returns end x."""
    cx = x
    for ch in text.upper():
        rows = GLYPHS.get(ch, GLYPHS["?"])
        for ry, row in enumerate(rows):
            for rx, bit in enumerate(row):
                if bit == "X":
                    for sy in range(scale):
                        for sx in range(scale):
                            put(cx + rx * scale + sx, y + ry * scale + sy, color)
        cx += ADVANCE * scale
    return cx


def text_width(text, scale=1):
    return len(text) * ADVANCE * scale - scale  # trim trailing gap
