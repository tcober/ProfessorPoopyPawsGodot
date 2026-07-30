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


## Stand at `pos`, press interact once, then mash the resulting beat to its
## end. Returns true only if the zone actually LOCKED the party — otherwise
## `_party_free` is true from the first frame and every check passes for free.
##
## The settle-and-reparK dance is not paranoia: _mash_until advances dialog
## with ATTACK, and the press that lands on the frame control comes back is a
## real attack — Fuji swings her tome, and the swing's forward lunge walks her
## straight out of the zone before the interact can fire.
## THE ROAM-BOX LINT (2026-07-29). A wandering villager is a solid StaticBody2D,
## so a villager standing in the wrong cell PLUGS a lane — this is the failure
## the map file records in its own header, where Mayor Hollis sealed the pier off
## just by stepping out of his door.
##
## THE TEST BLOCKS ONE CELL AT A TIME, and that is the whole subtlety. Blocking
## every cell of a box at once is the tempting version and it is WRONG: it fails
## on Alder, whose box spans all six rows of the harbour lane, for a state that
## cannot happen — one villager is one body in one cell, and the lane is six rows
## deep precisely so a body in it is a squeeze rather than a wall. So the real
## invariant is per-cell: wherever any ONE villager can stand, the town's
## load-bearing places stay reachable. Boxes sit in separate open areas, so no
## two villagers can conspire to close something neither closes alone.
##
## It also re-proves each box is honest ground — inside the map, never solid.
func _check_roam_boxes(street: Array[Node]) -> void:
	var map: Dictionary = current_scene.map
	var start := Vector2i(MapData.anchor_px(map, "player_start") / 16.0)
	# The three places the town cannot afford to lose: the way out on foot, the
	# crossing, and the door she works behind.
	var must := ["exit_south", "dock", "library"]
	var cells := 0
	var solid_at := ""
	var cut := ""
	for c in street:
		if not (c is NPC) or not (c as NPC).wander:
			continue
		var npc := c as NPC
		var box: Rect2i = npc.wander_cells
		for y in range(box.position.y, box.end.y):
			for x in range(box.position.x, box.end.x):
				var cell := Vector2i(x, y)
				if MapData.is_solid(map, cell):
					if solid_at == "":
						solid_at = "%s: %s" % [npc.display_name, cell]
					continue
				cells += 1
				var seen := _reach(map, start, [cell])
				for place in must:
					if not seen.has(Vector2i(MapData.anchor_px(map, place) / 16.0)) \
							and cut == "":
						cut = "%s on %s cuts %s" % [npc.display_name, cell, place]
	_check("every roam box is walkable ground%s"
			% ("" if solid_at == "" else " — " + solid_at), solid_at == "")
	_check("no villager can plug the town from any of its %d roam cells%s"
			% [cells, "" if cut == "" else " — " + cut], cut == "")


## 4-connected flood over the walkable graph, minus an explicit blocked set.
func _reach(map: Dictionary, start: Vector2i, blocked: Array) -> Dictionary:
	var seen := {start: true}
	var q: Array[Vector2i] = [start]
	var head := 0
	while head < q.size():
		var c: Vector2i = q[head]
		head += 1
		for d in [Vector2i.RIGHT, Vector2i.LEFT, Vector2i.DOWN, Vector2i.UP]:
			var n: Vector2i = c + d
			if seen.has(n) or blocked.has(n) or MapData.is_solid(map, n):
				continue
			seen[n] = true
			q.append(n)
	return seen


## `mark` is either a fixed Vector2 or a Callable returning one. Wandering NPCs
## need the Callable form — see the caller in the ask-around gate.
func _interact_at(mark: Variant) -> bool:
	var at := func() -> Vector2:
		return mark.call() if mark is Callable else mark as Vector2
	await _wait_frames(30)
	_player().velocity = Vector2.ZERO
	_player().global_position = at.call()
	await _wait_frames(8)
	_player().velocity = Vector2.ZERO
	_player().global_position = at.call()
	await _wait_frames(10)
	Input.action_press("interact")
	await _wait_frames(4)
	Input.action_release("interact")
	await _wait_frames(20)
	var locked := not _party_free()
	var done: bool = await _mash_until(_party_free, 9000)
	return locked and done


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
	ok = await _interact_at(MapData.anchor_px(lib_map, "kettle") + Vector2(16.0, 32.0))
	_check("a look-at zone answers on interact", ok)
	_check("the look-at line closes and gives her back", _party_free())

	# ---- her own door, out into the Ebb night
	_player().global_position = MapData.anchor_px(lib_map, "exit_door")
	ok = await _mash_until(func() -> bool:
			return _scene_is("res://scene/lanternwood.tscn"), 900)
	_check("her own door lands her in Lanternwood", ok)
	await _wait_frames(40)               # entry fade settles; villagers cast
	var street: Array[Node] = current_scene.get_node("World").get_children()
	_check("the Ebb-night street is peopled",
			street.any(func(c: Node) -> bool: return c is NPC))
	_check_roam_boxes(street)

	# ---- the street's OWN gate: the whole neighbourhood tells her the same
	# nothing, and the only place left to look is her own shelves
	# Counted from the street rather than hardcoded at 3 (2026-07-29): MAYOR
	# HOLLIS is out on his step on the Ebb night too, so the street is FOUR
	# people now. He is deliberately not part of the gate — he hangs off
	# _on_mayor_talked, not _on_villager_talked, so ASK_GATE still means the
	# three neighbours — but he is very much somebody she can talk to, and a
	# probe that expects a fixed headcount breaks every time the street grows.
	var folk: Array[Node] = []
	for c in street:
		if c is NPC:
			folk.append(c)
	var asked := 0
	for c in folk:
		# talk from a step SOUTH: the 20px TalkZone reaches, and standing
		# on the body itself just depenetrates her back off it.
		#
		# The mark is a CALLABLE, not a captured Vector2 (2026-07-29): the three
		# neighbours idle-wander now, and _interact_at burns ~48 frames settling
		# before it presses — long enough for a villager to leave a position
		# sampled up here. Re-reading at every re-park closes the race, and it
		# closes it the honest way: the probe chases her exactly like a player
		# would rather than the wander being tuned down to suit the probe.
		if await _interact_at(func() -> Vector2:
				return (c as NPC).global_position + Vector2(0.0, 18.0)):
			asked += 1
	_check("every Ebb-night neighbour answers (%d/%d)" % [asked, folk.size()],
		folk.size() >= 3 and asked == folk.size())
	_check("asking the whole street opens the research beat",
			game.call("flag", "asked_around"))

	# ---- the non-ebb phase opens the room with no cutscene at all
	game.call("reset_story")
	game.set("library_phase", "night")
	game.call("set_flag", "ebb_done")
	party.call("set_roster", [&"fuji"] as Array[StringName], &"fuji")
	change_scene_to_file("res://scene/library.tscn")
	await _wait_frames(30)
	_check("a non-ebb phase opens the room playable", _party_free())

	# ---- Act 1 beat 2: the research gate. The ledger is a REAL gate — shelf
	# nine is just books until she has read that the catalogue disagrees with
	# it — so the order of these four searches is the whole test.
	game.call("reset_story")
	game.set("library_phase", "research")
	game.call("set_flag", "ebb_done")
	game.call("set_flag", "asked_around")
	party.call("set_roster", [&"fuji"] as Array[StringName], &"fuji")
	change_scene_to_file("res://scene/library.tscn")
	await _wait_frames(20)
	_check("the research night locks her for its opening", not _party_free())
	ok = await _mash_until(_party_free, 9000)
	_check("the opening hands control back at the desk", ok)

	ok = await _interact_at(MapData.anchor_px(lib_map, "stack_c"))
	_check("shelf nine answers before the ledger", ok)
	_check("...but does NOT give up the thesis yet",
			not game.call("flag", "thesis_found"))

	ok = await _interact_at(MapData.anchor_px(lib_map, "desk_spot"))
	_check("the ledger reads", ok and game.call("flag", "ledger_read"))

	ok = await _interact_at(MapData.anchor_px(lib_map, "stack_a"))
	_check("a wrong shelf still just reads its plate",
			ok and not game.call("flag", "thesis_found"))

	ok = await _interact_at(MapData.anchor_px(lib_map, "stack_c"))
	_check("shelf nine gives up the thesis once the ledger is read",
			ok and game.call("flag", "thesis_found"))
	_check("the find leaves her at the desk lamp, free, in her own room",
			_party_free() and _scene_is("res://scene/library.tscn")
			and _player().global_position.distance_to(
					MapData.anchor_px(lib_map, "desk_spot")) < 24.0)

	# ---- the town door: the arch TRAVELS, and never on a blank phase (which
	# library.gd reads as the Ebb cutscene — walking in must not replay it)
	var town_map: Dictionary = MapData.load_map("res://assets/maps/lanternwood.txt")
	game.call("reset_story")
	game.call("set_flag", "ebb_done")
	game.call("set_flag", "asked_around")
	party.call("set_roster", [&"fuji"] as Array[StringName], &"fuji")
	change_scene_to_file("res://scene/lanternwood.tscn")
	await _wait_frames(90)               # entry fade + the marker's entry lock
	_player().global_position = MapData.anchor_px(town_map, "library")
	ok = await _mash_until(func() -> bool:
			return _scene_is("res://scene/library.tscn"), 900)
	_check("the library arch travels into the hall", ok)
	await _wait_frames(20)
	_check("the arch opens the RESEARCH beat, not the Ebb replay",
			not _party_free() and not puppet_up.call())

	# ---- and back out: the arrival stands ON the marker, so only _standing
	# keeps the door from firing again and walking her straight back inside
	_player().global_position = MapData.anchor_px(lib_map, "exit_door")
	ok = await _mash_until(func() -> bool:
			return _scene_is("res://scene/lanternwood.tscn"), 2000)
	_check("her door lands her back on the library step", ok)
	await _wait_frames(90)               # well past ENTRY_LOCK
	_check("the step does not bounce her back inside",
			_scene_is("res://scene/lanternwood.tscn"))

	print("library probe: %s" % ("ALL PASS" if _fails == 0 else "%d FAILED" % _fails))
	quit(1 if _fails > 0 else 0)
