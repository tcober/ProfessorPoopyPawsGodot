extends SceneTree

## THE RECITAL CHAIN probe (2026-07-25) — the three legs Prologue A gained
## between the whirligig's flight and the "THREE SUMMERS LATER." card, driven
## on their own so a failure names itself in seconds instead of cascading
## through the full chapter probe's frame budgets.
##
##   A12 the BREW (staged from scene/chapters.gd, so the flag ladder can never
##        drift from the dev menu's) — the workbench walk-gate, the stir mash,
##        prologue_potion_made -> the front door
##   A13 across town — the SPENT south gate must refuse, the Academy door must
##        travel
##   A14 the RECITAL — the aisle walk-gate, the four colours, prologue_recital,
##        the montage, the student roster
##
## Same conventions as tools/prologue_probe.gd: synthesized POLLED input,
## walk-gates driven by TELEPORTING to a goal derived from the map, and every
## pollable end-state is a flag, a scene swap, or the party unlock. Must run
## WINDOWED (the dummy rasterizer renders black and wall-clock timers drive the
## dialog):
##   /Applications/Godot.app/Contents/MacOS/Godot --path . \
##       --script tools/recital_probe.gd

var _fails := 0
var _last_press := 0

var game: Node
var party: Node


func _initialize() -> void:
	_run()


func _check(label: String, cond: bool) -> void:
	if cond:
		print("  ok    ", label)
	else:
		print("  FAIL  ", label)
		_fails += 1


func _mash_until(pred: Callable, max_frames: int) -> bool:
	for i in max_frames:
		if pred.call():
			Input.action_release("attack")
			return true
		var now := Time.get_ticks_msec()
		if now - _last_press > 250:
			_last_press = now
			Input.action_press("attack")
		elif now - _last_press > 120:
			Input.action_release("attack")
		await process_frame
	Input.action_release("attack")
	return false


func _wait_frames(n: int) -> void:
	for i in n:
		await process_frame


func _scene_is(path: String) -> bool:
	return current_scene != null and current_scene.scene_file_path == path


func _player() -> Node2D:
	var players := get_nodes_in_group("player")
	return players[0] if players.size() > 0 else null


func _party_free() -> bool:
	var p := _player()
	return p != null and p.is_physics_processing()


## Stage a beat exactly the way dev_menu.gd does, by NAME — chapters.gd is the
## single source of truth for the flag ladders, and a probe that re-typed them
## would drift from the menu the moment one changed.
func _stage(beat_name: String) -> void:
	var table: GDScript = load("res://scene/chapters.gd")
	for b: Dictionary in table.BEATS:
		if b.get("name", "") != beat_name:
			continue
		game.call("reset_story")
		for f: String in b["flags"]:
			game.call("set_flag", f)
		for k: String in b["state"]:
			game.set(k, b["state"][k])
		party.call("set_roster", b["roster"], b["lead"])
		change_scene_to_file(b["scene"])
		return
	_check("beat exists in chapters.gd: " + beat_name, false)


func _run() -> void:
	# an OCCLUDED macOS window runs UNCAPPED — pin 60fps so frame budgets track
	# the wall-clock the cutscene timers actually run on
	Engine.max_fps = 60
	await process_frame
	game = root.get_node("Game")
	party = root.get_node("Party")
	print("== the recital chain ==")
	var ok := false

	# ==== A12 THE BREW ========================================================
	_stage("A12 - THE BREW")
	await _wait_frames(60)
	_check("the brew stages in the fest downstairs",
			_scene_is("res://scene/downstairs_fest.tscn"))
	var down_map: Dictionary = MapData.load_map("res://assets/maps/downstairs.txt")
	ok = await _mash_until(_party_free, 3000)
	_check("the brew beat hands over the walk to the bench", ok)
	# the front door must REFUSE mid-brew: out there the south gate is spent
	# and the Academy door is still dead, so leaving is a dead wander
	_player().global_position = MapData.anchor_px(down_map, "exit_door")
	await _wait_frames(50)
	_check("the front door refuses mid-brew",
			_scene_is("res://scene/downstairs_fest.tscn"))
	ok = await _mash_until(_party_free, 2400)
	await _wait_frames(20)
	# the bench top is the map's only `E` block, and its pocket has exactly one
	# entrance — the band over it cannot be walked around
	_player().global_position = MapData.bbox_rect(down_map, "E").get_center()
	var potion := func() -> bool: return game.flag("prologue_potion_made")
	ok = await _mash_until(potion, 6000)
	_check("the stir mash brews the potion", ok)
	ok = await _mash_until(_party_free, 3000)
	_check("the brew hands control back", ok)
	await _wait_frames(20)
	_player().global_position = MapData.anchor_px(down_map, "exit_door")
	# the front door opens onto THE BOUGHS since the 2026-08-23 split — ride
	# tree 1's ladder mouth down to the town
	var in_boughs := func() -> bool: return _scene_is("res://scene/canopy_fest.tscn")
	ok = await _mash_until(in_boughs, 1600)
	_check("the brewed flask leaves by the front door", ok)
	await _wait_frames(70)
	var canopy_map: Dictionary = MapData.load_map("res://assets/maps/canopy_fest.txt")
	_player().global_position = MapData.anchor_px(canopy_map, "head1") + Vector2(8.0, 8.0)
	var in_town := func() -> bool: return _scene_is("res://scene/town_fest.tscn")
	ok = await _mash_until(in_town, 1600)
	_check("...and rides the ladder down with it", ok)
	await _wait_frames(70)

	# ==== A13 ACROSS TOWN =====================================================
	var town_map: Dictionary = MapData.load_map("res://assets/maps/town_fest.txt")
	# the headland is SPENT: this road would re-enter bluff "meet" with every
	# part flag set and replay the flight finale
	_player().global_position = MapData.anchor_px(town_map, "exit_south")
	await _wait_frames(70)
	_check("the spent south gate refuses", _scene_is("res://scene/town_fest.tscn"))
	ok = await _mash_until(_party_free, 2400)
	await _wait_frames(20)
	# land ON the location zone, which is a 16x12 rect centred on its anchor —
	# NOT anchor+40, which is town_thesis's separate dash GOAL area
	_player().global_position = MapData.anchor_px(town_map, "school")
	var in_hall := func() -> bool: return _scene_is("res://scene/hall.tscn")
	ok = await _mash_until(in_hall, 3000)
	_check("the Academy door travels to the recital", ok)
	await _wait_frames(60)

	# ==== A14 THE RECITAL =====================================================
	var hall_map: Dictionary = MapData.load_map("res://assets/maps/hall.txt")
	# gate the unlock check on being in the HALL: _party_free alone is
	# trivially true in the town we just left, and would pass without the
	# recital ever starting
	var aisle_open := func() -> bool: return in_hall.call() and _party_free()
	ok = await _mash_until(aisle_open, 3000)
	_check("the recital hands over the walk up the aisle", ok)
	# the band across the pit row south of the apron riser — the only row
	# touching it (the stage is a sealed region nobody walks onto); derived
	# from the D bbox, so the 2026-08-04 great-hall rebuild moved it with
	# the map and this probe never needed an edit
	var apron: Rect2 = MapData.bbox_rect(hall_map, "D")
	_player().global_position = Vector2(apron.get_center().x, apron.end.y + 8.0)
	var recital := func() -> bool: return game.flag("prologue_recital")
	ok = await _mash_until(recital, 9000)
	_check("the recital plays out (four colours, four bursts)", ok)
	var in_bluff := func() -> bool: return _scene_is("res://scene/bluff.tscn")
	ok = await _mash_until(in_bluff, 3000)
	_check("the recital hands off to the sunset romance", ok)
	_check("swapped to the student roster", party.roster.size() == 1
			and party.roster[0] == &"basil_student")

	# ==== B6 must still be the NAMING =========================================
	# state = {} in the chapter table is load-bearing: it relies on
	# reset_story() blanking hall_phase, or a jump down from A14 would play the
	# kid recital with the student roster (the wrong SpriteFrames contract)
	_stage("B6 - THE NAMING")
	await _wait_frames(60)
	_check("B6 still routes to the naming, not the recital",
			_scene_is("res://scene/hall.tscn") and game.hall_phase == ""
			and not game.flag("prologue_recital"))

	print("== %d check(s) failed ==" % _fails)
	quit(1 if _fails > 0 else 0)
