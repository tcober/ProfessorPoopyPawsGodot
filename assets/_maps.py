#!/usr/bin/env python3
"""Loader for assets/maps/*.txt — the shared map source of truth.

The same file drives the Python scene painters (assets/_gen_scene_*.py) and the
Godot runtime (scene/map_data.gd builds collision + logic queries from it), so
paint and physics can never drift apart. Format, line-oriented:

    ; comment (only before the map section)
    legend <char> <terrain> <walk|solid> [stratum:<name>]
    anchor <name> <tile_x> <tile_y>
    map
    <one row of <cols> legend chars per line, top to bottom>

THE OPTIONAL `stratum:` TOKEN (2026-07-29) is how one grid carries two or three
STACKED WALKABLE STOREYS — a forest floor, the plank canopy above it, a stone
terrace — without the engine growing an elevation system. It works because a
cell is exactly one (x, y) with one walk/solid bit, so the storeys are
unambiguous IFF THEY ARE DISJOINT IN THE GRID; then "a bridge over walkable
ground" is not discouraged, it is unrepresentable. It defaults to `ground`, so
every map written before it means what it always meant. TileScene.assert_strata()
is what makes the token load-bearing rather than decorative.

Keep scene/map_data.gd's parser in sync with this one.
"""


class MapData:
    def __init__(self, path):
        self.path = path
        self.legend = {}    # char -> {"terrain": str, "solid": bool}
        self.anchors = {}   # name -> (tx, ty)
        self.rows = []      # list[str], one per tile row
        in_map = False
        for raw in open(path):
            line = raw.rstrip("\n")
            if in_map:
                if line:
                    self.rows.append(line)
                continue
            line = line.strip()
            if not line or line.startswith(";"):
                continue
            parts = line.split()
            if parts[0] == "legend":
                ch, terrain, walk = parts[1], parts[2], parts[3]
                assert len(ch) == 1 and walk in ("walk", "solid"), f"bad legend: {line}"
                # trailing options; only `stratum:<name>` exists so far, and an
                # unrecognized one is a HARD error rather than ignored — a
                # silently-dropped `startum:canopy` typo would default the whole
                # storey back to `ground` and fuse it to the forest floor
                stratum = "ground"
                for opt in parts[4:]:
                    assert opt.startswith("stratum:"), \
                        f"{path}: unknown legend option {opt!r} in: {line}"
                    stratum = opt.split(":", 1)[1]
                    assert stratum, f"{path}: empty stratum name in: {line}"
                self.legend[ch] = {"terrain": terrain, "solid": walk == "solid",
                                   "stratum": stratum}
            elif parts[0] == "anchor":
                self.anchors[parts[1]] = (int(parts[2]), int(parts[3]))
            elif parts[0] == "map":
                in_map = True
            else:
                raise ValueError(f"{path}: unrecognized line: {line}")
        assert self.rows, f"{path}: no map section"
        self.cols = len(self.rows[0])
        self.rows_n = len(self.rows)
        for i, row in enumerate(self.rows):
            assert len(row) == self.cols, f"{path}: row {i} is {len(row)} wide, want {self.cols}"
            for ch in row:
                assert ch in self.legend, f"{path}: row {i} has undeclared char {ch!r}"
        for name, (tx, ty) in self.anchors.items():
            assert 0 <= tx < self.cols and 0 <= ty < self.rows_n, f"{path}: anchor {name} out of bounds"

    def at(self, tx, ty):
        """Legend char at tile (tx, ty); solid off-map."""
        if 0 <= tx < self.cols and 0 <= ty < self.rows_n:
            return self.rows[ty][tx]
        return None

    def stratum(self, tx, ty):
        """Which walkable STOREY tile (tx, ty) belongs to — None off-map and
        None on a solid cell, because a wall is not a floor and every caller
        wants those two answers to be the same answer. Compare two cells'
        strata and `None != None` is exactly wrong, so callers test against a
        NAME, never against each other."""
        ch = self.at(tx, ty)
        if ch is None or self.legend[ch]["solid"]:
            return None
        return self.legend[ch]["stratum"]

    def strata(self):
        """Every stratum name a WALKABLE legend char declares. A single-storey
        map returns {"ground"}."""
        return {d["stratum"] for d in self.legend.values() if not d["solid"]}

    def mask(self, chars):
        """[rows][cols] bool grid: cell char in `chars` (a string of legend chars)."""
        return [[ch in chars for ch in row] for row in self.rows]

    def solid_cells(self):
        return {(x, y) for y, row in enumerate(self.rows)
                for x, ch in enumerate(row) if self.legend[ch]["solid"]}
