extends SceneTree

## THE ACADEMY PROBE — the precinct north of Alembic Town, and the one thing about
## it that no art lint can see: whether the WALK still works.
##
##   /Applications/Godot.app/Contents/MacOS/Godot --path . \
##       --script tools/academy_probe.gd
##
## The Python generator already asserts the composition (both cross-map walls are
## pierced in exactly one place, the stair spans its band, every anchor is reachable
## on the walkable graph). What it cannot assert is anything involving a BODY: that
## the town's north lane actually arrives here, that this scene's south lane actually
## goes back, that the arrival does not land you inside the trigger you just used, and
## that a 12x8 collision box fits through a two-cell gate between two drum towers.
##
## THE ONE THAT CAUGHT SOMETHING: `player_start` was authored one row from
## `exit_south`, so the spawn landed INSIDE its own exit zone and the scene bounced
## straight back to the town before a single frame drew. It looked exactly like a
## scene that failed to load.
##
## MOVEMENT IS DRIVEN BY POLLED INPUT, NEVER BY ASSIGNING `velocity`. A PartyMember
## re-derives its velocity from an Intent EVERY physics frame — `_gather_intent()`
## reads the Input axes, `_process_move()` writes `velocity` — so an assignment made
## before `await physics_frame` is overwritten before move_and_slide ever sees it.
## The first draft of this probe did exactly that and reported "moved 0 px" for a
## gate that is perfectly walkable. Synthesized presses live only in the polled Input
## state (probes-and-shots gotcha 4), which is the other half of the same rule.

var _fail := 0


func _initialize() -> void:
	_run()


func ok(cond: bool, what: String) -> void:
	if cond:
		print("  ok    ", what)
	else:
		_fail += 1
		print("  FAIL  ", what)


func _leader() -> Node2D:
	return root.get_node("Party").leader


## Ride out a scene change: the entry fade holds ENTRY_LOCK for a while and a body
## teleported inside it is swallowed (see the probes-and-shots skill, gotcha 1).
func _settle(frames: int = 80) -> void:
	for i in frames:
		await process_frame


## Hold a real polled action for `frames` physics frames, releasing early if the
## scene changes out from under us (an exit fires mid-walk and every body is freed).
func _hold(action: String, frames: int, while_in: String = "") -> void:
	Input.action_press(action)
	for i in frames:
		if while_in != "" and (current_scene == null or current_scene.name != while_in):
			break
		await physics_frame
	Input.action_release(action)
	await physics_frame


## Wait out any announce banner still holding the scene. `_busy` is what TravelScene
## gates every marker, door and exit on, and walking a body across a court full of
## announce zones sets it — so the very next exit test would refuse SILENTLY and read
## as a broken door. (This probe walked through the gate marker and parked on the
## orrery's before trying the south lane, and lost a real minute to it.)
func _await_free(frames: int = 240) -> void:
	for i in frames:
		if current_scene == null or not bool(current_scene.get("_busy")):
			return
		await process_frame


func _run() -> void:
	Engine.max_fps = 60
	await process_frame
	var game := root.get_node("Game")
	var party := root.get_node("Party")
	game.call("reset_story")
	for f in ["prologue_done", "ebb_done"]:
		game.call("set_flag", f)
	var roster: Array[StringName] = [&"basil", &"fuji"]
	party.call("set_roster", roster, &"basil")

	# ---- 1. THE PRECINCT LOADS AND THE SPAWN IS NOT IN ITS OWN EXIT ----------------
	change_scene_to_file("res://scene/academy.tscn")
	await _settle()
	ok(current_scene != null and current_scene.name == "Academy",
			"the Academy loads and STAYS loaded (the spawn is clear of ExitSouth)")
	if current_scene == null or current_scene.name != "Academy":
		print("academy probe: %d FAILED" % _fail)
		quit(1)
		return
	var map: Dictionary = current_scene.map
	var body := _leader()

	# ---- 2. EVERY MARKER IS ON WALKABLE GROUND ------------------------------------
	# An announce zone floating on a solid cell never fires, and nothing else notices:
	# the scene runs, the banner simply never comes.
	for loc in current_scene.get_node("Locations").get_children():
		var cell := Vector2i(int(loc.position.x / 16.0), int(loc.position.y / 16.0))
		ok(not MapData.is_solid(map, cell),
				"the %s marker stands on walkable ground" % loc.id)

	# ---- 3. THE GATE IS WIDE ENOUGH FOR A BODY ------------------------------------
	# Two cells between two drum towers, and a party member's box is 12x8. The map
	# graph says it is open; this walks it for real, because a graph that is 2 cells
	# wide and a body that is 12px wide have disagreed before (motion_probe's mayor).
	var gate := MapData.anchor_px(map, "gate")
	body.global_position = gate + Vector2(0.0, 40.0)
	body.velocity = Vector2.ZERO
	for i in 6:
		await physics_frame
	var before := body.global_position
	await _hold("move_up", 60)
	ok(body.global_position.y < before.y - 60.0,
			"a body walks NORTH through the gatehouse (moved %d px)"
			% int(before.y - body.global_position.y))

	# ---- 4. THE GRAND STAIR IS THE ONLY WAY UP, AND IT IS USABLE -------------------
	var stair := MapData.anchor_px(map, "hall")
	body.global_position = Vector2(stair.x - 24.0, MapData.anchor_px(map, "orrery").y)
	body.velocity = Vector2.ZERO
	for i in 6:
		await physics_frame
	var up_from := body.global_position
	await _hold("move_up", 90)
	ok(absf(body.global_position.y - up_from.y) < 90.0,
			"the terrace wall STOPS a body walking at it off-axis (moved %d px)"
			% int(up_from.y - body.global_position.y))

	# ---- 5. THE ROUND TRIP --------------------------------------------------------
	# Down the causeway to the town, and back up the lane to here. Both directions,
	# because a one-way door is a soft-lock and the two halves are wired in different
	# files (academy.gd's ExitSouth, alembic_town.gd's ExitNorth).
	await _await_free()
	body.global_position = MapData.anchor_px(map, "exit_south") + Vector2(0.0, -40.0)
	body.velocity = Vector2.ZERO
	for i in 6:
		await physics_frame
	await _hold("move_down", 90, "Academy")
	await _settle()
	ok(current_scene != null and current_scene.name == "AlembicTown",
			"walking out the south lane arrives in ALEMBIC TOWN")
	if current_scene == null or current_scene.name != "AlembicTown":
		print("academy probe: %d FAILED" % _fail)
		quit(1)
		return
	var tmap: Dictionary = current_scene.map
	body = _leader()
	var mouth := MapData.anchor_px(tmap, "exit_north")
	ok(body.global_position.distance_to(mouth) < 96.0,
			"...in the town's OWN north lane, not at its south gate (%d px from it)"
			% int(body.global_position.distance_to(mouth)))
	# and it must not immediately bounce back: the arrival has to clear ExitNorth
	await _settle(60)
	ok(current_scene != null and current_scene.name == "AlembicTown",
			"...and it STAYS there (the arrival is clear of ExitNorth)")

	await _await_free()
	body = _leader()
	body.global_position = mouth + Vector2(0.0, 40.0)
	body.velocity = Vector2.ZERO
	for i in 6:
		await physics_frame
	await _hold("move_up", 90, "AlembicTown")
	await _settle()
	ok(current_scene != null and current_scene.name == "Academy",
			"walking up the town's north lane arrives at THE ACADEMY")

	print("academy probe: ", "ALL PASS" if _fail == 0 else "%d FAILED" % _fail)
	quit(1 if _fail else 0)
