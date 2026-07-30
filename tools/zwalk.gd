extends SceneTree

## THE Z-ORDER WALKAROUND. Drives a body to every position in a scene where the
## layering doctrine can go wrong, crops the frame around it, and tiles the crops
## into CONTACT SHEETS you eyeball a hundred at a time.
##
##   /Applications/Godot.app/Contents/MacOS/Godot --path . \
##       --script tools/zwalk.gd -- res://scene/alembic_town.tscn /tmp/zwalk [beat:N]
##
## It must run WINDOWED (the same GL note as tools/shot.gd: --headless renders
## black on GL Compatibility), and it pins Engine.max_fps like every other tool
## here, because an occluded macOS window runs uncapped.
##
## WHY A HARNESS AND NOT A LIST OF SHOTS. Every z-order bug this project has had
## was found by standing in one specific place — pressed south into a cliff,
## in the NOTCH beside a band step, on the terrace below a mask strip, north of a
## trunk, south of a fence — and there are hundreds of those places in a stacked
## town. The positions are therefore DERIVED FROM THE MAP rather than typed: move
## a band and the harness follows it, and a new band cannot be forgotten.
##
## The four families it generates, one contact sheet each, named for the failure
## they hunt:
##   PRESSED   the cell NORTH of every face-band run, body shoved south. The
##             mask-band case: ~11px of sprite hangs past the physics box, and
##             the band's own top 12px must be re-drawn over it.
##   NOTCH     the cell beside every band STEP, at the lower run's level. Bands
##             staircase, so a body can stand level with a wall — and it must
##             NOT be masked there (masking it clips the character's face).
##   BELOW     the cell SOUTH of every run's foot. A body down there must not be
##             masked either; as upper-layer tiles this case sliced heads off.
##   PROPS     the four cells around every Tier-3 prop component. Walk-behind:
##             north of a trunk is BEHIND it, south is IN FRONT of it, and a
##             pressed body's sunk feet must not draw over a standable prop (the
##             2026-07-19 fence lesson).

const CROP := 96           ## px of game view per cell of the contact sheet
const COLS := 6            ## cells per contact-sheet row
const SETTLE := 6          ## frames to let the camera snap and the body settle
const MAX_PER_SHEET := 36

var _map: Dictionary
var _out := "/tmp/zwalk"


func _initialize() -> void:
	_run()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 2:
		push_error("usage: -- <scene.tscn> <out_dir_prefix> [beat:N]")
		quit(1)
		return
	Engine.max_fps = 60
	await process_frame
	_out = args[1]
	var scene_path := args[0]
	for i in range(2, args.size()):
		if args[i].begins_with("beat:"):
			var table: GDScript = load("res://scene/chapters.gd")
			var b: Dictionary = table.BEATS[int(args[i].split(":")[1])]
			scene_path = b["scene"]
			root.get_node("Game").call("reset_story")
			for f: String in b["flags"]:
				root.get_node("Game").call("set_flag", f)
			for k: String in b["state"]:
				root.get_node("Game").set(k, b["state"][k])
			root.get_node("Party").call("set_roster", b["roster"], b["lead"])
	change_scene_to_file(scene_path)
	for i in 70:                       # ride out the entry fade AND its lock
		await process_frame
	_map = current_scene.map
	# PIN THE SCENE BUSY FOR THE WHOLE WALK. Teleporting a body across a town
	# drags it through every travel marker, every door and both lift landings, and
	# the first one that fires changes the scene and frees the body out from under
	# the harness. `_busy` is the flag TravelScene already gates every marker,
	# exit, announce and the lift ride on, so one assignment refuses all of them
	# and nothing has to know about this tool.
	current_scene.set("_busy", true)
	var families := _positions()
	for name in families:
		var spots: Array = families[name]
		print("%s: %d spots" % [name, spots.size()])
		var page := 0
		while page * MAX_PER_SHEET < spots.size():
			var slice: Array = spots.slice(page * MAX_PER_SHEET,
					(page + 1) * MAX_PER_SHEET)
			await _sheet("%s_%s%d" % [_out, name, page], slice)
			page += 1
	quit()


## Every place the layering doctrine can go wrong, derived from the map itself.
func _positions() -> Dictionary:
	var solid: Dictionary = _map.solid
	var lines: PackedStringArray = _map.lines
	var cols := int(_map.cols)
	var rows := int(_map.rows)
	# Every maximal vertical run of SOLID cells that is at least 2 tall and has a
	# walkable cell due north of it — i.e. every face a body can be pressed onto.
	var runs: Array = []               # [tx, top_ty, height]
	for tx in cols:
		var ty := 0
		while ty < rows:
			if solid.has(Vector2i(tx, ty)):
				var h := 0
				while solid.has(Vector2i(tx, ty + h)):
					h += 1
				if h >= 2 and ty > 0 and not solid.has(Vector2i(tx, ty - 1)):
					runs.append([tx, ty, h])
				ty += h
			else:
				ty += 1
	var tops := {}
	for r: Array in runs:
		if not tops.has(r[0]):
			tops[r[0]] = []
		(tops[r[0]] as Array).append(r[1])
	var pressed: Array = []
	var notch: Array = []
	var below: Array = []
	# COLLAPSE THE RUNS INTO SEGMENTS FIRST. One spot per column gives 150 crops of
	# the same wall for a 44-cell band, which is noise you stop looking at. A
	# segment is consecutive columns sharing a top row — the exact grouping
	# mask_band itself emits a strip for — and the three places worth standing on
	# one are its MIDDLE and its two ENDS, because the overhang rule and the
	# tree_edge_return corners are both about what happens at an end.
	runs.sort_custom(func(a, b): return a[1] < b[1] or (a[1] == b[1] and a[0] < b[0]))
	var segs: Array = []               # [top_ty, tx0, cols, height]
	for r: Array in runs:
		if not segs.is_empty() and segs[-1][0] == r[1] \
				and segs[-1][1] + segs[-1][2] == r[0] and segs[-1][3] == r[2]:
			segs[-1][2] += 1
		else:
			segs.append([r[1], r[0], 1, r[2]])
	for sg: Array in segs:
		var ty: int = sg[0]
		var x0: int = sg[1]
		var n: int = sg[2]
		var h: int = sg[3]
		for tx in _pick(x0, n):
			pressed.append(_spot(tx, ty - 1, Vector2(0.0, 6.0),
					"press %d,%d h%d" % [tx, ty, h]))
			if not solid.has(Vector2i(tx, ty + h)) and ty + h < rows:
				below.append(_spot(tx, ty + h, Vector2.ZERO,
						"below %d,%d" % [tx, ty + h]))
	# NOTCH: a STEP is a neighbouring run starting exactly one row lower, and the
	# notch is the walkable cell beside this run at the neighbour's level.
	for r: Array in runs:
		var tx: int = r[0]
		var ty: int = r[1]
		for dx in [-1, 1]:
			var nb: Array = tops.get(tx + dx, [])
			if not nb.has(ty + 1):
				continue
			if not solid.has(Vector2i(tx + dx, ty)) and tx + dx >= 0 \
					and tx + dx < cols:
				notch.append(_spot(tx + dx, ty, Vector2(0.0, 6.0),
						"notch %d,%d" % [tx + dx, ty]))
	# PROPS: the four cells around every Tier-3 component. The manifest is the
	# source of truth for which chars are y-sorted art.
	var props: Array = []
	var seen := {}
	for chars in _prop_chars():
		for comp in _components(chars):
			var lo: Vector2i = comp[0]
			var hi: Vector2i = comp[1]
			for c in [Vector2i((lo.x + hi.x) / 2, lo.y - 1),
					Vector2i((lo.x + hi.x) / 2, hi.y + 1),
					Vector2i(lo.x - 1, (lo.y + hi.y) / 2),
					Vector2i(hi.x + 1, (lo.y + hi.y) / 2)]:
				if seen.has(c) or solid.has(c):
					continue
				if c.x < 0 or c.y < 0 or c.x >= cols or c.y >= rows:
					continue
				seen[c] = true
				props.append(_spot(c.x, c.y, Vector2.ZERO,
						"%s %d,%d" % [chars, c.x, c.y]))
	return {"pressed": pressed, "notch": notch, "below": below, "props": props}


## A segment's middle and its two ends, de-duplicated for short segments.
func _pick(x0: int, n: int) -> Array:
	var out: Array = []
	for tx in [x0, x0 + n / 2, x0 + n - 1]:
		if not out.has(tx):
			out.append(tx)
	return out


func _spot(tx: int, ty: int, nudge: Vector2, label: String) -> Dictionary:
	return {"pos": Vector2(tx * 16 + 8, ty * 16 + 8) + nudge, "label": label}


## The chars named by the scene's Tier-3 props manifest — the y-sorted art whose
## walk-behind reads are what the PROPS family checks.
func _prop_chars() -> Array:
	var out: Array = []
	var path := "res://assets/tilesets/%s_props.txt" % _map_name()
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return out
	while not f.eof_reached():
		var parts := f.get_line().strip_edges().split(" ", false)
		if parts.size() >= 4 and parts[0] == "prop" and not out.has(parts[2]):
			out.append(parts[2])
	return out


func _map_name() -> String:
	return (current_scene.get("MAP_PATH") as String).get_file().get_basename()


func _components(chars: String) -> Array:
	var lines: PackedStringArray = _map.lines
	var pending := {}
	for y in int(_map.rows):
		for x in (lines[y] as String).length():
			if chars.contains((lines[y] as String)[x]):
				pending[Vector2i(x, y)] = true
	var out: Array = []
	for start in pending.keys():
		if not pending.has(start):
			continue
		pending.erase(start)
		var comp: Array[Vector2i] = [start]
		var lo: Vector2i = start
		var hi: Vector2i = start
		var i := 0
		while i < comp.size():
			var c: Vector2i = comp[i]
			i += 1
			lo = Vector2i(mini(lo.x, c.x), mini(lo.y, c.y))
			hi = Vector2i(maxi(hi.x, c.x), maxi(hi.y, c.y))
			for n in [Vector2i(c.x + 1, c.y), Vector2i(c.x - 1, c.y),
					Vector2i(c.x, c.y + 1), Vector2i(c.x, c.y - 1)]:
				if pending.has(n):
					pending.erase(n)
					comp.append(n)
		out.append([lo, hi])
	return out


## Drive the body to each spot, crop the frame around it, tile the crops.
func _sheet(path: String, spots: Array) -> void:
	var party := root.get_node("Party")
	var body: Node2D = party.leader
	if not is_instance_valid(body):
		push_error("the leader was freed — a trigger fired mid-walk")
		return
	var cam: Camera2D = null
	for c in body.get_children():
		if c is Camera2D:
			cam = c
	var view := MapData.view_size()
	var rows := int(ceil(float(spots.size()) / COLS))
	var sheet: Image = null
	var scale := 1.0
	for i in spots.size():
		var spot: Dictionary = spots[i]
		# HOLD the body there for a few frames: one teleport is not enough, the
		# camera glides and the body depenetrates out of a wall over 2-3 steps.
		for f in SETTLE:
			body.global_position = spot["pos"]
			body.velocity = Vector2.ZERO
			await physics_frame
		cam.reset_smoothing()
		await process_frame
		RenderingServer.force_draw()
		var frame := root.get_viewport().get_texture().get_image()
		if sheet == null:
			scale = float(frame.get_width()) / view.x
			sheet = Image.create(int(COLS * CROP * scale),
					int(rows * CROP * scale), false, frame.get_format())
			sheet.fill(Color(0.06, 0.05, 0.11))
		# where the body actually IS on screen — the camera clamps at the map
		# edges, so it is NOT always the centre of the frame
		var on_screen: Vector2 = (body.global_position
				- cam.get_screen_center_position() + view * 0.5) * scale
		var half := CROP * scale * 0.5
		var want := Rect2i(Vector2i(on_screen - Vector2(half, half)),
				Vector2i(int(CROP * scale), int(CROP * scale)))
		var src := want.intersection(Rect2i(Vector2i.ZERO, frame.get_size()))
		if src.size.x <= 0 or src.size.y <= 0:
			continue
		# SHIFT THE DESTINATION BY WHATEVER THE CLIP TOOK. Near a map edge the
		# camera stops following, so the body is off-centre and `want` hangs off
		# the frame; blitting the clipped rect at the cell's corner anyway slides
		# every one of those crops sideways and the body stops being where the
		# sheet says it is — which is worse than a missing crop, because you read
		# the wrong cell and trust it.
		var dst := Vector2i(int((i % COLS) * CROP * scale),
				int((i / COLS) * CROP * scale)) + (src.position - want.position)
		sheet.blit_rect(frame, src, dst)
	if sheet != null:
		sheet.save_png(path + ".png")
		print("  wrote ", path, ".png  (", spots.size(), " spots)")
		var f := FileAccess.open(path + ".txt", FileAccess.WRITE)
		for i in spots.size():
			f.store_line("%d,%d  %s" % [i % COLS, i / COLS, spots[i]["label"]])
