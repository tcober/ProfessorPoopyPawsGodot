#!/usr/bin/env python3
"""Title-screen art, 640x360 — an epic Paper Girls / dreamy-Adventure-Time sunset over
the autumn forest from the user's poster sketch:

  posterized indigo->magenta->gold gradient sky (dither-banded), stars + sparkles,
  a giant setting sun, layered pink/purple cloud banks, a distant mountain ridge,
  silhouetted autumn canopy with rim light, a warm leaf-litter path framed by dark
  trunks, and the stacked yellow logo.

Writes assets/title_bg.png + the falling-leaf particle texture assets/leaf.png.
Basil, the leaves, and the prompt are live nodes in scene/title.tscn.
Re-run: python3 assets/_gen_title.py
"""
import struct, zlib, os, sys, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _pixfont import draw_text

W, H = 640, 360

buf = bytearray(W * H * 4)

def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        o = (y * W + x) * 4
        buf[o:o + 4] = bytes(c[:3]) + b"\xff"

def h2(x, y, salt=0):
    n = (x * 374761393 + y * 668265263 + salt * 2246822519) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return (n ^ (n >> 16)) & 0xFF

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def posterize(c, x, y, step=20):
    out = []
    for ch in c:
        q, r = divmod(ch, step)
        if r > step * (0.66 if (x + y) % 2 else 0.33):
            q += 1
        out.append(max(0, min(255, q * step)))
    return tuple(out)

# ---- sky: posterized sunset gradient ------------------------------------------
STOPS = [(0, (26, 22, 66)), (95, (84, 50, 128)), (165, (170, 78, 148)),
         (215, (238, 132, 108)), (250, (252, 186, 118)), (H, (252, 200, 130))]
for y in range(H):
    for si in range(len(STOPS) - 1):
        y0, c0 = STOPS[si]
        y1, c1 = STOPS[si + 1]
        if y0 <= y < y1:
            base = lerp(c0, c1, (y - y0) / max(1, y1 - y0))
            break
    for x in range(W):
        put(x, y, posterize(base, x, y))

# ---- stars + sparkles in the high sky ------------------------------------------
for y in range(0, 150):
    fade = 1.0 - y / 150.0
    for x in range(W):
        r = h2(x, y, 1)
        if r < int(3 * fade):
            put(x, y, (238, 236, 255))
        elif r < int(5 * fade):
            put(x, y, (170, 160, 220))
for (sx, sy) in ((80, 34), (210, 60), (555, 26), (480, 88), (300, 22)):
    put(sx, sy, (255, 255, 255))
    for d in (1, 2):
        for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d)):
            put(sx + dx, sy + dy, (240, 236, 255) if d == 1 else (190, 170, 230))

# ---- the giant setting sun -------------------------------------------------------
SUNX, SUNY, SUNR = 452, 208, 86
SUN_BANDS = [(1.0, (250, 158, 96)), (0.86, (253, 190, 110)),
             (0.66, (255, 216, 138)), (0.4, (255, 240, 178))]
for y in range(SUNY - SUNR, SUNY + SUNR + 1):
    for x in range(SUNX - SUNR, SUNX + SUNR + 1):
        d = math.hypot(x - SUNX, y - SUNY) / SUNR
        if d > 1.0:
            continue
        for thr, col in SUN_BANDS:
            if d <= thr:
                c = col
        # dither the band seams
        put(x, y, posterize(c, x, y, 14))
# halo: brighten sky in a ring
for y in range(SUNY - SUNR - 10, SUNY + SUNR + 11):
    for x in range(SUNX - SUNR - 10, SUNX + SUNR + 11):
        d = math.hypot(x - SUNX, y - SUNY)
        if SUNR < d <= SUNR + 9 and (x + y) % 2 == 0 and 0 <= y < H:
            o = (y * W + x) * 4
            r, g, b = buf[o], buf[o + 1], buf[o + 2]
            put(x, y, (min(255, r + 26), min(255, g + 16), b))

# ---- cloud banks ------------------------------------------------------------------
CLOUD_BANDS = [
    (118, 16, (255, 196, 208), (208, 122, 170), (150, 84, 150)),
    (168, 20, (255, 206, 190), (224, 128, 158), (160, 88, 148)),
    (226, 22, (255, 214, 168), (238, 148, 128), (188, 100, 124)),
]
for (cy, ch_, lit, body, shad) in CLOUD_BANDS:
    for y in range(cy - ch_, cy + ch_):
        for x in range(W):
            # coarse coherent masses + a soft dithered fringe
            clump = h2(x // 16, y // 8, cy) * 0.8 + h2(x // 6, y // 4, cy + 1) * 0.2
            vy = (y - (cy - ch_)) / (2 * ch_)
            thr = 132 - abs(vy - 0.45) * 200
            if clump < thr or (clump < thr + 14 and (x + y) % 2 == 0):
                if vy < 0.3:
                    c = lit
                elif vy < 0.7:
                    c = body
                else:
                    c = shad
                put(x, y, posterize(c, x, y, 16))

# ---- distant mountain ridge --------------------------------------------------------
for x in range(W):
    ridge = 238 + int(10 * math.sin(x * 0.02)) + (h2(x // 7, 0, 9) % 7) - 3
    for y in range(ridge, 262):
        put(x, y, (74, 46, 106) if y > ridge + 1 else (222, 128, 116))

# ---- autumn canopy silhouette with rim light ----------------------------------------
for x in range(W):
    crown = 258 + (h2(x // 11, 1, 10) % 14) - 4 + (h2(x // 4, 2, 11) % 5) - 2
    for y in range(crown, 300):
        deep = (52, 32, 60)
        if y <= crown + 1:
            c = (236, 138, 74)                              # sun-kissed rim
        elif h2(x, y, 12) < 26:
            c = (150, 70, 62)                               # inner leaf glints
        else:
            c = deep
        put(x, y, c)

# ---- foreground: leaf litter + path -------------------------------------------------
for y in range(295, H):
    t = (y - 295) / (H - 295)
    half = int(20 + t * 150)
    for x in range(W):
        on_path = abs(x - 320) < half - (h2(0, y, 13) % 8)
        r = h2(x, y, 14)
        if on_path:
            if abs(x - 320) > half - 12 and r % 3 == 0:
                c = (178, 84, 58)
            elif r < 36:
                c = (206, 118, 74)
            elif r > 224:
                c = (246, 178, 108)
            else:
                c = (228, 148, 88)
        else:
            if r < 42:
                c = (128, 48, 48)
            elif r > 228:
                c = (196, 96, 62)
            else:
                c = (162, 66, 52)
        put(x, y, c)

# ---- framing trunks with rim light ---------------------------------------------------
def trunk(base_x, top_y, w):
    for y in range(top_y, H):
        t = (y - top_y) / max(1, H - top_y)
        half = max(2, int(w * (0.55 + 0.45 * t)))
        wob = (h2(0, y // 6, base_x) % 3) - 1
        for x in range(base_x - half + wob, base_x + half + wob + 1):
            if x <= base_x - half + wob + 1:
                c = (244, 148, 84)                          # sunset rim
            elif x >= base_x + half + wob - 1:
                c = (16, 10, 22)
            elif h2(x, y, 15) < 20:
                c = (52, 30, 46)
            else:
                c = (30, 18, 34)
            put(x, y, c)

trunk(38, 0, 15)
trunk(112, 60, 8)
trunk(586, 20, 13)
trunk(516, 96, 7)

# canopy spill over the trunk tops
for y in range(0, 110):
    fade = 1.0 - y / 110.0
    for x in range(W):
        if x < 180 or x > 470:
            if h2(x, y, 16) < int(120 * fade):
                put(x, y, (66, 36, 66) if h2(y, x, 17) % 3 else (150, 70, 84))

# ---- logo -----------------------------------------------------------------------------
for i, line in enumerate(("PROFESSOR", "POOPY", "PAWS")):
    x, y, s = 26, 26 + i * 52, 5
    draw_text(put, line, x + 4, y + 4, (56, 24, 62), s)     # deep plum shadow
    draw_text(put, line, x, y, (255, 228, 108), s)

# ---- save -----------------------------------------------------------------------------
raw = bytearray()
for y in range(H):
    raw.append(0)
    raw += buf[y * W * 4:(y + 1) * W * 4]

def chunk(tag, data):
    c = tag + data
    return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

def save(path, w, h, body):
    open(path, "wb").write(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(body), 9))
        + chunk(b"IEND", b""))

save(os.path.join(HERE, "title_bg.png"), W, H, raw)

# ---- tiny leaf particle texture ---------------------------------------------------------
LW = LH = 5
lb = bytearray(LW * LH * 4)
for yy, row in enumerate(("..X..", ".XXX.", "XXXXX", ".XXX.", "..X..")):
    for xx, bit in enumerate(row):
        if bit == "X":
            o = (yy * LW + xx) * 4
            col = (238, 148, 88, 255) if (xx + yy) % 2 else (255, 196, 110, 255)
            lb[o:o + 4] = bytes(col)
lraw = bytearray()
for y in range(LH):
    lraw.append(0)
    lraw += lb[y * LW * 4:(y + 1) * LW * 4]
save(os.path.join(HERE, "leaf.png"), LW, LH, lraw)
print("wrote title_bg.png (640x360) + leaf.png")
