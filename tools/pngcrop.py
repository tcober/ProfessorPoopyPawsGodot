#!/usr/bin/env python3
"""Crop cells out of a tools/zwalk.gd CONTACT SHEET so they can be eyeballed one
at a time instead of thirty-six at a time.

zwalk tiles 96px game crops into a 6-wide sheet at whatever scale the window
happened to be, which is exactly the right format for spotting an outlier and
exactly the wrong one for judging eleven pixels of coat-tail. This pulls named
cells back out at native scale, optionally magnified, and stacks them in a strip
with the sheet's own label file as the caption source.

    python3 tools/pngcrop.py /tmp/zv1_pressed0.png 0,0 1,0 5,2 -o /tmp/look.png
    python3 tools/pngcrop.py /tmp/zv1_pressed0.png --all-row 3 -m 2

stdlib only, like everything else in this pipeline — there is no PIL here and
adding one for a debugging tool would be the tail wagging the dog.
"""
import os, struct, sys, zlib

CELL = 288          # zwalk's CROP(96) * the 3x dev window; overridable with -c
COLS = 6            # zwalk.COLS


def read_png(path):
    """(w, h, rows) where rows[y] is a bytearray of RGBA. Handles the colour
    types the Godot viewport actually writes (8-bit RGB / RGBA)."""
    data = open(path, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"{path}: not a PNG"
    i, idat, w, h, depth, ctype = 8, bytearray(), 0, 0, 0, 0
    while i < len(data):
        (ln,) = struct.unpack(">I", data[i:i + 4])
        tag = data[i + 4:i + 8]
        body = data[i + 8:i + 8 + ln]
        if tag == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", body[:10])
            assert depth == 8, f"{path}: {depth}-bit PNG unsupported"
            assert ctype in (2, 6), f"{path}: colour type {ctype} unsupported"
        elif tag == b"IDAT":
            idat += body
        elif tag == b"IEND":
            break
        i += 12 + ln
    bpp = 3 if ctype == 2 else 4
    raw = zlib.decompress(bytes(idat))
    stride = w * bpp
    rows, prev = [], bytearray(stride)
    p = 0
    for _y in range(h):
        f = raw[p]
        line = bytearray(raw[p + 1:p + 1 + stride])
        p += 1 + stride
        # the five PNG filters, unfiltered in place
        if f == 1:
            for x in range(bpp, stride):
                line[x] = (line[x] + line[x - bpp]) & 255
        elif f == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 255
        elif f == 3:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                line[x] = (line[x] + ((a + prev[x]) >> 1)) & 255
        elif f == 4:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                c = prev[x - bpp] if x >= bpp else 0
                b = prev[x]
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 255
        elif f != 0:
            raise AssertionError(f"{path}: bad filter {f}")
        prev = line
        if bpp == 3:                       # widen to RGBA so callers see one shape
            out = bytearray(w * 4)
            for x in range(w):
                out[x * 4:x * 4 + 3] = line[x * 3:x * 3 + 3]
                out[x * 4 + 3] = 255
            rows.append(out)
        else:
            rows.append(line)
    return w, h, rows


def write_png(path, w, h, rows):
    buf = bytearray()
    for y in range(h):
        buf.append(0)
        buf += rows[y]

    def chunk(tag, body):
        return (struct.pack(">I", len(body)) + tag + body
                + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(bytes(buf), 6))
           + chunk(b"IEND", b""))
    open(path, "wb").write(png)


def main(argv):
    src = argv[0]
    out = "/tmp/pngcrop.png"
    mag, cell, cols = 1, CELL, COLS
    want, rest = [], []
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "-o":
            i += 1
            out = argv[i]
        elif a == "-m":
            i += 1
            mag = int(argv[i])
        elif a == "-c":
            i += 1
            cell = int(argv[i])
        elif a == "--all-row":
            i += 1
            want += [(c, int(argv[i])) for c in range(cols)]
        elif "," in a:
            cx, cy = a.split(",")
            want.append((int(cx), int(cy)))
        else:
            rest.append(a)
        i += 1
    w, h, rows = read_png(src)
    assert want, "name at least one cell as x,y"
    n = len(want)
    ow, oh = cell * mag * n, cell * mag
    dst = [bytearray(ow * 4) for _ in range(oh)]
    for k, (cx, cy) in enumerate(want):
        for y in range(cell):
            sy = cy * cell + y
            if sy >= h:
                continue
            srow = rows[sy]
            for x in range(cell):
                sx = cx * cell + x
                if sx >= w:
                    continue
                px = srow[sx * 4:sx * 4 + 4]
                for my in range(mag):
                    drow = dst[y * mag + my]
                    base = (k * cell + x) * mag
                    for mx in range(mag):
                        o = (base + mx) * 4
                        drow[o:o + 4] = px
    write_png(out, ow, oh, dst)
    labels = os.path.splitext(src)[0] + ".txt"
    if os.path.exists(labels):
        tab = {}
        for line in open(labels):
            line = line.strip()
            if not line:
                continue
            key, _, lab = line.partition("  ")
            tab[key] = lab
        print(" | ".join(tab.get(f"{cx},{cy}", "?") for cx, cy in want))
    print("wrote", out, ow, "x", oh)


if __name__ == "__main__":
    main(sys.argv[1:])
