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
				legend[parts[1]] = {"terrain": parts[2], "solid": parts[3] == "solid"}
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
	return Vector2(map.cols, map.rows) * 32.0


## Pixel center of a named anchor tile.
static func anchor_px(map: Dictionary, name: String) -> Vector2:
	assert(map.anchors.has(name), "unknown anchor: " + name)
	return Vector2(map.anchors[name] as Vector2i) * 32.0 + Vector2(16.0, 16.0)
