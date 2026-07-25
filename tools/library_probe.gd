extends SceneTree

## Library-scene probe (2026-07-24) — the ONE scene, not the whole chapter.
## scene/library.gd's "ebb" beat is long (the coffee casts, the quake that
## lands ON a cast, the dead wand) and ends by handing CONTROL back in the
## room, so a shot.gd frame guess can't tell you whether it finished. This
## drives just that beat with synthesized POLLED input (actions only exist
## in the polled state — the shot.gd gotcha) and asserts:
##
##   the room boots playable (solo Fuji spawns, camera pinned) -> the beat
##   runs to the end -> control comes back IN the room -> the look-at zones
##   answer -> her own door lands her in Ebb-night Lanternwood.
##
## Must run WINDOWED (the dummy rasterizer renders black, and wall-clock
## timers drive the dialog):
##   /Applications/Godot.app/Contents/MacOS/Godot --path . \
##       --script tools/library_probe.gd

var _fails := 0
var _last_press := 0

# autoloads aren't compile-time identifiers under --script; runtime lookup
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


func _wait_frames(n: int) -> void:
	for i in n:
		await process_frame


func _player() -> Node2D:
	var players := get_nodes_in_group("player")
	return players[0] if players.size() > 0 else null


func _party_free() -> bool:
	return _player() != null and _player().is_physics_processing()


func _scene_is(path: String) -> bool:
	return current_scene != null and current_scene.scene_file_path == path


## Advance dialog by pressing attack every 250ms (comfortably past the
## DialogBox swallow window) until pred() holds or the frame budget dies.
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


func _run() -> void:
	await process_frame
	# an OCCLUDED macOS window runs UNCAPPED (~2000fps): frame budgets burn
	# in real seconds while wall-clock cutscene timers don't advance faster
	Engine.max_fps = 60
	game = root.get_node("Game")
	party = root.get_node("Party")
	var lib_map: Dictionary = MapData.load_map("res://assets/maps/library.txt")

	print("library probe:")
	# ---- the "ebb" beat: the sync gag, then the dead wand
	game.call("reset_story")
	game.set("library_phase", "ebb")
	party.call("set_roster", [&"basil", &"fuji"] as Array[StringName], &"basil")
	change_scene_to_file("res://scene/library.tscn")
	await _wait_frames(20)
	_check("the room loads", _scene_is("res://scene/library.tscn"))
	# the room sets its own cast: the live flow arrives carrying the ADULTS
	# roster off ebb.tscn, and the story stays with HER from here
	_check("the room forces the solo Fuji roster", party.get("roster").size() == 1
			and party.get("roster")[0] == &"fuji" and party.get("leader_id") == &"fuji")
	_check("her body is spawned but locked for the cutscene", not _party_free())
	var puppet_up := func() -> bool:
		for c in current_scene.get_node("World").get_children():
			if c is NPC:
				return true
		return false
	_check("the NPC puppet acts the beat", puppet_up.call())

	# the beat ends by handing control back IN the room — no fade, no card,
	# nothing drags her out. That unlock IS the end-state.
	var ok := await _mash_until(_party_free, 9000)
	_check("the beat hands control back in the room", ok)
	_check("the Ebb flag is set by the beat", game.call("flag", "ebb_done"))
	_check("the puppet is gone (her own body has the room)", not puppet_up.call())
	_check("she is still IN the library", _scene_is("res://scene/library.tscn"))
	var cam := _player().get_node("Camera2D") as Camera2D
	_check("the quake left the camera centered", cam.offset == Vector2.ZERO)

	# ---- the free room: a look-at zone answers, and it doesn't trap her
	_player().global_position = MapData.anchor_px(lib_map, "kettle") + Vector2(16.0, 32.0)
	await _wait_frames(10)
	Input.action_press("interact")
	await _wait_frames(4)
	Input.action_release("interact")
	await _wait_frames(20)
	var dialog: Node = current_scene.get_node("Theater").get("dialog")
	_check("a look-at zone answers on interact", dialog.visible)
	ok = await _mash_until(func() -> bool: return not dialog.visible, 600)
	_check("the look-at line closes and gives her back", ok and _party_free())

	# ---- her own door, out into the Ebb night
	_player().global_position = MapData.anchor_px(lib_map, "exit_door")
	ok = await _mash_until(func() -> bool:
			return _scene_is("res://scene/lanternwood.tscn"), 900)
	_check("her own door lands her in Lanternwood", ok)
	await _wait_frames(40)               # entry fade settles; villagers cast
	_check("the Ebb-night street is peopled",
			current_scene.get_node("World").get_children().any(
					func(c: Node) -> bool: return c is NPC))

	# ---- the non-ebb phase opens the room with no cutscene at all
	game.call("reset_story")
	game.set("library_phase", "night")
	game.call("set_flag", "ebb_done")
	party.call("set_roster", [&"fuji"] as Array[StringName], &"fuji")
	change_scene_to_file("res://scene/library.tscn")
	await _wait_frames(30)
	_check("a non-ebb phase opens the room playable", _party_free())

	print("library probe: %s" % ("ALL PASS" if _fails == 0 else "%d FAILED" % _fails))
	quit(1 if _fails > 0 else 0)
