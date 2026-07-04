class_name TiledMap
extends Object

## Stamps the visible tiles of a tiled interior from its generated layout file
## (assets/tilesets/<name>_layout.txt, written by assets/_gen_tileset_*.py):
## named `layer` sections (lower = under entities, upper = over them, so
## bodies pass behind railings and furniture tops), one line per map row, one
## "cx,cy" atlas-coord token per cell ('-' = empty). Collision stays on the
## separate invisible layer (PaintedMap.build_collision), built from the same
## assets/maps/*.txt, so visuals and physics can't drift.
## Keep the token format in sync with assets/_tiles.py write_layout().

static func build(layout_path: String, layers: Dictionary) -> void:
	var f := FileAccess.open(layout_path, FileAccess.READ)
	assert(f != null, "missing layout file: " + layout_path)
	var target: TileMapLayer = null
	var y := 0
	while not f.eof_reached():
		var line := f.get_line().strip_edges()
		if line.is_empty() or line.begins_with(";"):
			continue
		if line.begins_with("layer "):
			var name := line.substr(6)
			assert(layers.has(name), "no TileMapLayer bound for layer: " + name)
			target = layers[name]
			y = 0
			continue
		assert(target != null, "layout row before any layer header")
		var toks := line.split(" ", false)
		for x in toks.size():
			if toks[x] == "-":
				continue
			var p := toks[x].split(",")
			target.set_cell(Vector2i(x, y), 0, Vector2i(int(p[0]), int(p[1])))
		y += 1
