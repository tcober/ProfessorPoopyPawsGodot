class_name MapData
extends Object

## Loader for assets/maps/*.txt — the shared map source of truth. The same file
## drives the Python scene painters, so paint and collision can never drift.
## Keep this parser in sync with assets/_maps.py.

static func load_map(path: String) -> Dictionary:
	var legend := {}
	var anchors := {}
	var lines := PackedStringArray()
	var solid := {}
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
				legend[parts[1]] = {"solid": parts[3] == "solid"}
			"anchor":
				anchors[parts[1]] = Vector2i(int(parts[2]), int(parts[3]))
			"map":
				in_map = true
	assert(not lines.is_empty(), "no map section in " + path)
	for y in lines.size():
		var row := lines[y]
		for x in row.length():
			if legend[row[x]]["solid"]:
				solid[Vector2i(x, y)] = true
	return {
		"cols": lines[0].length(), "rows": lines.size(),
		"lines": lines, "legend": legend, "solid": solid, "anchors": anchors,
	}


## Off-map counts as solid so queries never walk out of the world.
static func is_solid(map: Dictionary, cell: Vector2i) -> bool:
	if cell.x < 0 or cell.y < 0 or cell.x >= int(map.cols) or cell.y >= int(map.rows):
		return true
	return map.solid.has(cell)


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
