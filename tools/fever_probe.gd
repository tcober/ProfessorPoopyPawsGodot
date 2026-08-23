extends SceneTree

## PROLOGUE A0 "THE FEVER" probe (2026-08-22) — the cold open, end-to-end:
##
##   A0-1 the quiet house (house_fever: wake, no sunrise, stairs down)
##   A0-2 the doctor leaving (downstairs_fever on the BARE twin — the front
##        door must refuse before the bedside; crates, no boiler)
##   A0-3 her room (momroom: the bedside beat sets prologue_doctor_heard)
##   A0-4 out (town_fever: the home door -> the School marker)
##   A0-5 the reading room (the search gate: the still-room REFUSES until
##        the enchantment stack has failed him twice; then the find + the
##        copy set prologue_herbal_found)
##   A0-6 the simmer (home through the front door, the hearth gate, the
##        mash -> prologue_remedy_made)
##   A0-7 she drinks (momroom again -> prologue_mom_better; the door out
##        plays "THAT NIGHT.")
##   A0-8 the middle of the night (downstairs_fever now loads the BUILT
##        map — the Boiler prop exists — and closes on "TWO SUMMERS
##        LATER." into house_fest, where prologue_probe's chain begins)
##
## Coverage note: this probe ends where tools/prologue_probe.gd starts
## (house_fest), so the two together cover the full chain from the title
## cards to the Ebb.
##
## Same conventions as tools/prologue_probe.gd: synthesized POLLED input,
## walk-gates driven by teleporting to map-derived goals, pollable
## end-states only. Must run WINDOWED (the dummy rasterizer renders black
## and wall-clock timers drive the dialog):
##   /Applications/Godot.app/Contents/MacOS/Godot --path . \
##       --script tools/fever_probe.gd

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


## Stand at `pos`, press interact once, then mash the resulting beat out
## (the library_probe idiom — settle twice so a tome-swing can't lunge the
## body out of the zone before the press lands).
func _interact_at(pos: Vector2) -> bool:
	await _wait_frames(30)
	_player().velocity = Vector2.ZERO
	_player().global_position = pos
	await _wait_frames(8)
	_player().velocity = Vector2.ZERO
	_player().global_position = pos
	await _wait_frames(10)
	Input.action_press("interact")
	await _wait_frames(4)
	Input.action_release("interact")
	await _wait_frames(20)
	var locked := not _party_free()
	var done: bool = await _mash_until(_party_free, 9000)
	return locked and done


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
	Engine.max_fps = 60
	await process_frame
	game = root.get_node("Game")
	party = root.get_node("Party")
	print("== the fever (Prologue A0) ==")
	var ok := false

	# ==== A0-1 THE QUIET HOUSE ===============================================
	_stage("A0-1 - THE QUIET HOUSE")
	await _wait_frames(60)
	_check("the cold open stages in the fever loft",
			_scene_is("res://scene/house_fever.tscn"))
	var house_map: Dictionary = MapData.load_map("res://assets/maps/house.txt")
	ok = await _mash_until(_party_free, 3000)
	_check("the wake hands control back", ok and game.flag("prologue_fever"))
	_player().global_position = MapData.anchor_px(house_map, "exit_door")
	var in_down := func() -> bool: return _scene_is("res://scene/downstairs_fever.tscn")
	ok = await _mash_until(in_down, 1200)
	_check("the stairs descend to the fever downstairs", ok)
	await _wait_frames(30)

	# ==== A0-2 THE DOCTOR LEAVING ============================================
	# the BARE twin: crates where the boiler will stand, and no boiler
	_check("the pre-lab room has crates and no boiler",
			current_scene.get_node_or_null("World/Crates") != null
			and current_scene.get_node_or_null("World/Boiler") == null)
	var bare_map: Dictionary = MapData.load_map("res://assets/maps/downstairs_bare.txt")
	var doctor_gone := func() -> bool: return game.flag("prologue_doctor_gone")
	ok = await _mash_until(doctor_gone, 6000)
	_check("the doctor leaves and Sage asks again", ok)
	ok = await _mash_until(_party_free, 3000)
	_check("the doctor beat hands control back", ok)
	# the front door must REFUSE before the bedside
	_player().global_position = MapData.anchor_px(bare_map, "exit_door")
	await _wait_frames(50)
	_check("the front door refuses before her room", in_down.call())
	ok = await _mash_until(_party_free, 2400)
	await _wait_frames(20)
	# through Mom's door — the zone derives from the ' bbox (walkable here)
	var mdoor: Rect2 = MapData.bbox_rect(bare_map, "'")
	_player().global_position = Vector2(mdoor.get_center().x, mdoor.end.y - 8.0)
	var in_mom := func() -> bool: return _scene_is("res://scene/momroom.tscn")
	ok = await _mash_until(in_mom, 1200)
	_check("Mom's door walks through into her room", ok)
	await _wait_frames(30)

	# ==== A0-3 HER ROOM ======================================================
	var mom_map: Dictionary = MapData.load_map("res://assets/maps/momroom.txt")
	# the bedside gate: teleport into the full-width band below the bed
	await _wait_frames(60)
	_player().global_position = Vector2(MapData.size_px(mom_map).x * 0.5, 104.0)
	var heard := func() -> bool: return game.flag("prologue_doctor_heard")
	ok = await _mash_until(heard, 6000)
	_check("the bedside sets prologue_doctor_heard", ok)
	ok = await _mash_until(_party_free, 3000)
	_check("the bedside hands control back", ok)
	_player().global_position = MapData.anchor_px(mom_map, "exit_door")
	ok = await _mash_until(in_down, 1200)
	_check("her door leads back to the great room", ok)
	await _wait_frames(40)

	# ==== A0-4 OUT ===========================================================
	_player().global_position = MapData.anchor_px(bare_map, "exit_door")
	var in_town := func() -> bool: return _scene_is("res://scene/town_fever.tscn")
	ok = await _mash_until(in_town, 1600)
	_check("the front door now opens onto the grey morning", ok)
	await _wait_frames(80)                 # the entry fade + lock
	var town_map: Dictionary = MapData.load_map("res://assets/maps/town_fest.txt")
	_player().global_position = MapData.anchor_px(town_map, "school")
	var in_lib := func() -> bool: return _scene_is("res://scene/academy_library.tscn")
	ok = await _mash_until(in_lib, 3000)
	_check("the School marker travels to the reading room", ok)
	await _wait_frames(40)

	# ==== A0-5 THE READING ROOM ==============================================
	var lib_map: Dictionary = MapData.load_map("res://assets/maps/academy_library.txt")
	ok = await _mash_until(_party_free, 3000)
	_check("the reading room hands control straight back", ok)
	# the still-room REFUSES while the fancy shelf still might answer
	ok = await _interact_at(MapData.anchor_px(lib_map, "stack_c"))
	_check("the still-room refuses first (it's ENCHANTMENT he wants)",
			ok and not game.flag("prologue_herbal_found"))
	# the fancy shelf, twice — the second read fails him properly
	ok = await _interact_at(MapData.anchor_px(lib_map, "stack_a"))
	_check("enchantment read once", ok and not game.flag("prologue_wrong_shelf"))
	ok = await _interact_at(MapData.anchor_px(lib_map, "stack_a"))
	_check("enchantment fails him twice", ok and game.flag("prologue_wrong_shelf"))
	# now the plain shelf gives up the recipe, and he copies it at the desk
	ok = await _interact_at(MapData.anchor_px(lib_map, "stack_c"))
	_check("the still-room yields the recipe (copied, not borrowed)",
			ok and game.flag("prologue_herbal_found"))
	_player().global_position = MapData.anchor_px(lib_map, "exit_door")
	ok = await _mash_until(in_town, 1600)
	_check("the reading room door leads back to town", ok)
	await _wait_frames(80)

	# ==== A0-6 THE SIMMER ====================================================
	# the home zone hangs over the trunk face (2026-08-22) — seat the body a
	# few px into the face and let depenetration press it flush, overlapping
	# the raised zone (the zwalk seating idiom)
	_player().global_position = MapData.anchor_px(town_map, "home") + Vector2(8.0, -8.0)
	ok = await _mash_until(in_down, 2000)
	_check("the home door leads back inside", ok)
	await _wait_frames(40)
	# the simmer's gate is the hearth's foot band; the mash is the meter
	var hearth: Rect2 = MapData.bbox_rect(bare_map, "H")
	ok = await _mash_until(_party_free, 4000)
	_check("the simmer hands over the walk to the hearth", ok)
	_player().global_position = Vector2(hearth.get_center().x, hearth.end.y + 8.0)
	var remedy := func() -> bool: return game.flag("prologue_remedy_made")
	ok = await _mash_until(remedy, 9000)
	_check("the simmer makes the remedy", ok)
	ok = await _mash_until(_party_free, 3000)
	_check("the simmer hands control back", ok)
	await _wait_frames(20)

	# ==== A0-7 SHE DRINKS ====================================================
	_player().global_position = Vector2(mdoor.get_center().x, mdoor.end.y - 8.0)
	ok = await _mash_until(in_mom, 1200)
	_check("Mom's door opens with the cup in hand", ok)
	await _wait_frames(60)
	_player().global_position = Vector2(MapData.size_px(mom_map).x * 0.5, 104.0)
	var better := func() -> bool: return game.flag("prologue_mom_better")
	ok = await _mash_until(better, 9000)
	_check("she drinks it and sleeps", ok)
	ok = await _mash_until(_party_free, 3000)
	_check("the drink hands control back", ok)
	_player().global_position = MapData.anchor_px(mom_map, "exit_door")
	ok = await _mash_until(in_down, 2400)   # the THAT NIGHT. card plays here
	_check("her door plays the night card and returns", ok)
	await _wait_frames(40)

	# ==== A0-8 THE MIDDLE OF THE NIGHT =======================================
	# THE SWAP: the same scene file now loads the BUILT map — the boiler
	# prop exists and the crates are gone
	_check("the corner is BUILT (boiler in, crates out)",
			current_scene.get_node_or_null("World/Boiler") != null
			and current_scene.get_node_or_null("World/Crates") == null)
	var in_fest := func() -> bool: return _scene_is("res://scene/house_fest.tscn")
	ok = await _mash_until(in_fest, 6000)
	_check("the night close hands to the festival morning", ok)
	_check("the fever chapter's whole ladder is set",
			game.flag("prologue_fever") and game.flag("prologue_doctor_gone")
			and game.flag("prologue_doctor_heard")
			and game.flag("prologue_wrong_shelf")
			and game.flag("prologue_herbal_found")
			and game.flag("prologue_remedy_made")
			and game.flag("prologue_mom_better"))
	_check("still the kid roster", party.roster.size() == 1
			and party.roster[0] == &"kid_basil")

	print("== %d check(s) failed ==" % _fails)
	quit(1 if _fails > 0 else 0)
