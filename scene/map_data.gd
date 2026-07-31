class_name MapData
extends Object

## Loader for assets/maps/*.txt — the shared map source of truth. The same file
## drives the Python scene painters, so paint and collision can never drift.
## Keep this parser in sync with assets/_maps.py.
##
## A legend line is `legend <char> <terrain> <walk|solid> [stratum:<name>]`. The
## optional stratum names which walkable STOREY the char belongs to — a forest
## floor, the plank canopy over it, a stone terrace — in ONE grid, which works
## only because the storeys are disjoint in it (see assets/_maps.py and
## TileScene.assert_strata, which is what enforces the disjointness at build
## time). It defaults to "ground", so every map written before it is unchanged.

static func load_map(path: String) -> Dictionary:
	var legend := {}
	var anchors := {}
	var lines := PackedStringArray()
	var solid := {}
	var strata := {}
	var in_map := false
	var f := FileAccess.open(path, FileAccess.READ)
	assert(f != null, "missing map file: " + path)
	while not f.eof_reached():
		var line := f.get_line()
		if in_map:
			if not line.is_empty():
				lines.append(line)
			continue
		line = line.strip_edges()
		if line.is_empty() or line.begins_with(";"):
			continue
		var parts := line.split(" ", false)
		match parts[0]:
			"legend":
				# trailing options; only `stratum:<name>` exists so far, and an
				# unrecognized one is a HARD error rather than ignored — a
				# silently-dropped `startum:canopy` typo would default the whole
				# storey back to "ground" and fuse it to the forest floor
				var stratum := "ground"
				for i in range(4, parts.size()):
					var opt := parts[i]
					assert(opt.begins_with("stratum:"),
							"%s: unknown legend option '%s'" % [path, opt])
					stratum = opt.substr(8)
					assert(not stratum.is_empty(), "%s: empty stratum name" % path)
				# THE TERRAIN NAME IS STORED, and it was not until 2026-07-30. The
				# Python parser (_maps.py) has always kept it, so the two sides of
				# the one map format had drifted: anything asking this side what a
				# cell IS — rather than merely whether it is solid — got a missing
				# key, which in GDScript is an error every call and a null result.
				# The rope-ladder climb was written against it and was dead on
				# arrival, silently, while logging twice per physics frame per body.
				legend[parts[1]] = {"terrain": parts[2],
						"solid": parts[3] == "solid", "stratum": stratum}
				if parts[3] != "solid":
					strata[stratum] = true
			"anchor":
				anchors[parts[1]] = Vector2i(int(parts[2]), int(parts[3]))
			"map":
				in_map = true
	assert(not lines.is_empty(), "no map section in " + path)
	for y in lines.size():
		var row := lines[y]
		for x in row.length():
			# a hand-typed grid char with no legend line is the most common map
			# typo — name it instead of failing on a raw dictionary index
			assert(legend.has(row[x]),
					"%s row %d: map char '%s' has no legend entry" % [path, y, row[x]])
			if legend[row[x]]["solid"]:
				solid[Vector2i(x, y)] = true
	return {
		"cols": lines[0].length(), "rows": lines.size(),
		"lines": lines, "legend": legend, "solid": solid, "anchors": anchors,
		"strata": strata,
	}


## Off-map counts as solid so queries never walk out of the world.
static func is_solid(map: Dictionary, cell: Vector2i) -> bool:
	if cell.x < 0 or cell.y < 0 or cell.x >= int(map.cols) or cell.y >= int(map.rows):
		return true
	return map.solid.has(cell)


## Which walkable STOREY a cell belongs to — "" off-map and "" on a solid cell,
## because a wall is not a floor and every caller wants those two answers to be
## the same answer. A single-storey map answers "ground" everywhere walkable.
##
## This is what a stratum-aware party leash needs: teleporting a stranded
## follower to its leader is only ever correct WITHIN one stratum — on a stacked
## map the shortest line from a follower on the forest floor to a leader on the
## canopy runs straight up through the boardwalk, and warping it there drops a
## body onto a storey it has no way down from.
static func stratum_at(map: Dictionary, cell: Vector2i) -> String:
	if cell.x < 0 or cell.y < 0 or cell.x >= int(map.cols) or cell.y >= int(map.rows):
		return ""
	var ch: String = (map.lines[cell.y] as String)[cell.x]
	assert(map.legend.has(ch), "no legend entry for map char '%s'" % ch)
	if map.legend[ch]["solid"]:
		return ""
	return map.legend[ch]["stratum"]


## The stratum of a WORLD-PIXEL position — the form a body's global_position is
## already in, so callers never hand-divide by the tile size.
static func stratum_at_px(map: Dictionary, pos: Vector2) -> String:
	return stratum_at(map, Vector2i(floori(pos.x / 16.0), floori(pos.y / 16.0)))


## The TERRAIN NAME of a cell — the legend's second column, e.g. "grass",
## "ropeladder", "deck". Unlike stratum_at this answers for SOLID cells too, and
## returns "" off the map. Bodies use it to ask what they are standing on when the
## walk/solid bit is not enough: a rope ladder is walkable ground that must be
## CLIMBED rather than walked across.
static func terrain_at(map: Dictionary, cell: Vector2i) -> String:
	if cell.x < 0 or cell.y < 0 or cell.x >= map.cols or cell.y >= map.rows:
		return ""
	var ch: String = (map.lines[cell.y] as String)[cell.x]
	if not map.legend.has(ch):
		return ""
	return map.legend[ch]["terrain"]


static func terrain_at_px(map: Dictionary, pos: Vector2) -> String:
	return terrain_at(map, Vector2i(floori(pos.x / 16.0), floori(pos.y / 16.0)))


static func size_px(map: Dictionary) -> Vector2:
	return Vector2(map.cols, map.rows) * 16.0


## Pixel center of a named anchor tile.
static func anchor_px(map: Dictionary, name: String) -> Vector2:
	assert(map.anchors.has(name), "unknown anchor: " + name)
	return Vector2(map.anchors[name] as Vector2i) * 16.0 + Vector2(8.0, 8.0)


## Pixel rect enclosing every cell whose char is in `chars` (a feature's bbox).
## Props and interact zones derive their placement from this, so moving a feature
## char in the map txt moves it in-game.
static func bbox_rect(map: Dictionary, chars: String) -> Rect2:
	var found := false
	var x0 := 0
	var y0 := 0
	var x1 := 0
	var y1 := 0
	for y in int(map.rows):
		var row: String = map.lines[y]
		for x in row.length():
			if not chars.contains(row[x]):
				continue
			x0 = x if not found else mini(x0, x)
			y0 = y if not found else mini(y0, y)
			x1 = x if not found else maxi(x1, x)
			y1 = y if not found else maxi(y1, y)
			found = true
	assert(found, "bbox_rect: no cells match '" + chars + "'")
	return Rect2(x0 * 16.0, y0 * 16.0, (x1 - x0 + 1) * 16.0, (y1 - y0 + 1) * 16.0)


## Pin a camera's scroll limits to a rect starting at the origin — pass
## size_px(map) for a scene that scrolls with the map, or view_size() for a
## one-screen room whose camera must never move.
static func clamp_camera(cam: Camera2D, size: Vector2) -> void:
	cam.limit_left = 0
	cam.limit_top = 0
	cam.limit_right = int(size.x)
	cam.limit_bottom = int(size.y)


## The configured base viewport (384x216) — the size of one screen, from
## project settings so a viewport change can't leave a stale hardcoded clamp.
static func view_size() -> Vector2:
	return Vector2(
		ProjectSettings.get_setting("display/window/size/viewport_width"),
		ProjectSettings.get_setting("display/window/size/viewport_height"),
	)
