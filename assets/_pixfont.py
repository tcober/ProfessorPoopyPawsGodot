"""Shared 5x7 pixel font: glyph bitmaps + a draw helper.

Used by _gen_font.py (bakes assets/font/pixel_font.png + .fnt for Godot Labels) and by
art generators that stamp text straight into images (title logo, chalkboard, signs).
Caps + digits + basic punctuation; text is expected to be uppercase.
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
}

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
