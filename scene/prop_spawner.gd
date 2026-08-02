class_name PropSpawner
extends Object

## Spawns a scene's generated Tier-3 props manifest
## (assets/tilesets/<scene>_props.txt, written by TileScene.emit_prop) as
## Sprite2Ds inside the scene's y-sorted World node. These are the props a
## body can stand both north and south of — the static tile layers can't
## depth-sort them; y-sort is unconditionally correct (see DESIGN.md
## "Z-order / layering doctrine"). Collision stays on the map's solid cells;
## the spawned sprites are visual only.
##
## Manifest rows:
##   prop <Name> <chars> <png> [anchor=top:<px>] [base_inset=<px>]
##                             [hframes=<n>] [each]
##   mask <png> <x> <y> <ysort_y>   — a TileScene.mask_band depth strip, placed
##     at an explicit pixel rect rather than derived from map chars (a band's
##     runs aren't a feature bbox). It hides the ~11px of sprite that hangs over
##     a cliff's lip from above, and BEING Y-SORTED is the point: as upper-layer
##     tiles the same pixels also sliced the head off anyone hopping on the
##     terrace below. See TileScene.mask_band.

## The party's feet convention: feet sit at node.y + 20 (48px cell, feet
## baseline 44). Props place their node origin on the same line to sort true.
const PLAYER_FEET := 20.0


static func build(props_path: String, map: Dictionary, world: Node2D) -> void:
	var f := FileAccess.open(props_path, FileAccess.READ)
	assert(f != null, "missing props manifest: " + props_path)
	var spawned: Array[Sprite2D] = []
	while not f.eof_reached():
		var line := f.get_line().strip_edges()
		if line.is_empty() or line.begins_with(";"):
			continue
		var parts := line.split(" ", false)
		if parts[0] == "mask":
			assert(parts.size() == 5, "bad mask row: " + line)
			spawned.append(_mask_strip(parts, world))
			continue
		assert(parts.size() >= 4 and parts[0] == "prop", "bad prop row: " + line)
		var top := 0
		var has_top := false
		var base_inset := 0.0
		var hframes := 1
		var each := false
		for opt in parts.slice(4):
			if opt == "each":
				each = true
			elif opt.begins_with("anchor=top:"):
				# signed, and the sign matters: a NEGATIVE offset hangs the art
				# above its footprint, which is how a great tree's crown gets to
				# be taller than the cells it stands over (a `-1` sentinel for
				# "unset" used to swallow that silently and bottom-anchor it).
				top = int(opt.trim_prefix("anchor=top:"))
				has_top = true
			elif opt.begins_with("base_inset="):
				base_inset = float(opt.trim_prefix("base_inset="))
			elif opt.begins_with("hframes="):
				hframes = int(opt.trim_prefix("hframes="))
			else:
				assert(false, "unknown prop option: " + opt)
		var tex: Texture2D = load("res://assets/tilesets/" + parts[3])
		var rects: Array[Rect2] = []
		if each:
			rects = _component_rects(map, parts[2])
		else:
			rects = [MapData.bbox_rect(map, parts[2])]
		for i in rects.size():
			var rect := rects[i]
			var spr := Sprite2D.new()
			spr.name = parts[1] if i == 0 else parts[1] + str(i + 1)
			spr.texture = tex
			spr.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
			spr.hframes = hframes
			# node origin on the feet line above the y-sort baseline (the
			# footprint's south edge, minus any baked contact-shadow inset)
			var base_y := rect.end.y - base_inset
			spr.position = Vector2(rect.get_center().x, base_y - PLAYER_FEET)
			# art anchors to the footprint: bottom on the south edge, or the
			# sprite top at bbox_top + <top> px (the bed-cover crop case)
			var art_top := rect.position.y + top if has_top \
					else rect.end.y - tex.get_height()
			spr.offset = Vector2(0.0, art_top + tex.get_height() / 2.0 - spr.position.y)
			world.add_child(spr)
			spawned.append(spr)
	# Props precede bodies in child order, so a body wins a y-sort tie and
	# draws over the prop it stands pressed against (matches the hand-authored
	# node order this replaces — TravelScene spawns the party first).
	for i in spawned.size():
		world.move_child(spawned[i], i)


## A mask_band depth strip: art at an explicit pixel rect, y-sorted at its own
## key rather than at the feet convention (it is scenery, not a body).
static func _mask_strip(parts: PackedStringArray, world: Node2D) -> Sprite2D:
	var spr := Sprite2D.new()
	spr.name = parts[1].get_basename()
	spr.texture = load("res://assets/tilesets/" + parts[1])
	spr.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	spr.centered = false
	var art := Vector2(float(parts[2]), float(parts[3]))
	spr.position = Vector2(art.x, float(parts[4]))
	spr.offset = Vector2(0.0, art.y - spr.position.y)
	world.add_child(spr)
	return spr


## 4-connected components of the chars' cells (several lamp posts share one
## map char); one pixel rect per component, in reading order so the spawned
## node names stay stable.
static func _component_rects(map: Dictionary, chars: String) -> Array[Rect2]:
	var cells: Array[Vector2i] = []
	for y in int(map.rows):
		var row: String = map.lines[y]
		for x in row.length():
			if chars.contains(row[x]):
				cells.append(Vector2i(x, y))
	var pending := {}
	for c in cells:
		pending[c] = true
	var rects: Array[Rect2] = []
	for start in cells:     # not `seed` — that shadows the global seed()
		if not pending.has(start):
			continue
		pending.erase(start)
		var comp: Array[Vector2i] = [start]
		var lo := start
		var hi := start
		var i := 0
		while i < comp.size():
			var c := comp[i]
			i += 1
			lo = Vector2i(mini(lo.x, c.x), mini(lo.y, c.y))
			hi = Vector2i(maxi(hi.x, c.x), maxi(hi.y, c.y))
			for n in [Vector2i(c.x + 1, c.y), Vector2i(c.x - 1, c.y),
					Vector2i(c.x, c.y + 1), Vector2i(c.x, c.y - 1)]:
				if pending.has(n):
					pending.erase(n)
					comp.append(n)
		rects.append(Rect2(lo.x * 16.0, lo.y * 16.0,
				(hi.x - lo.x + 1) * 16.0, (hi.y - lo.y + 1) * 16.0))
	return rects
