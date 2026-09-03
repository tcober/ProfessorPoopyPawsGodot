extends SceneTree

## THE LADDER PROBE — a rope ladder is ONE LANE WIDE and you are on it or off it.
##
##   /Applications/Godot.app/Contents/MacOS/Godot --path . \
##       --script tools/ladder_probe.gd
##
## Alembic's four great trees are reached by rope ladder and by nothing else, so the
## climb is load-bearing: it is the only join between the forest floor and a ring
## deck's stratum, and Prologue A opens with a ten-year-old climbing DOWN one before
## he has been taught anything at all. It shipped as ordinary 8-way walking wearing
## the climb animation, which left twenty pixels of side-to-side slop inside the two
## ladder cells — you could stroll up at an angle, hug one stile the whole way, and
## shuffle sideways while the art insisted you were holding on with both paws.
##
## PartyMember._climb now pins the body to the run's own centre line and takes only
## the SIGN of the vertical input. Everything here is a body-level consequence of
## that, and none of it is visible to any art lint:
##
##  1. the lane wins over a sideways press (it is not a suggestion);
##  2. a diagonal press climbs at FULL speed, not at 0.71 of it;
##  3. the hop is refused on the rungs, because the lane owns x and the hop does not;
##  4. the climb still ENDS — up onto the canopy stratum, down onto the ground —
##     which is the one thing a pin can plausibly break, and it would break it
##     silently: a body held on the centre line of a ladder it cannot leave looks
##     exactly like a body that is still climbing.
##
## MOVEMENT IS DRIVEN BY POLLED INPUT, NEVER BY ASSIGNING `velocity` (probes-and-shots
## gotcha 4b) — a PartyMember re-derives velocity from an Intent every physics frame.
## Positions are seeded by teleport, which is geometry and survives the rewrite.

## Tree 1's ladder in assets/maps/town.txt: cols 9-10, rows 12-22, ground from row 23,
## the `RR` landing at row 11. The lane is the middle of the pair.
const LADDER_COLS := Vector2i(9, 10)
const LANE_X := 160.0                 # (9 + 10 + 1) * 8
const FOOT_ROW := 24                  # ground, two rows under the last rung
const MID_ROW := 18                   # deep enough inside the shaft to test in place

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


func _settle(frames: int = 80) -> void:
	for i in frames:
		await process_frame


## Park a body at a cell centre and let the physics settle, with velocity zeroed so
## the previous test's momentum cannot leak into this one.
func _park(body: Node2D, cell: Vector2i, dx: float = 0.0) -> void:
	body.global_position = Vector2(cell) * 16.0 + Vector2(8.0 + dx, 8.0)
	body.velocity = Vector2.ZERO
	for i in 6:
		await physics_frame


## Hold real polled actions for `frames` physics frames.
func _hold(actions: Array, frames: int) -> void:
	for a in actions:
		Input.action_press(a)
	for i in frames:
		await physics_frame
	for a in actions:
		Input.action_release(a)
	await physics_frame


## Hold actions until `stop` answers true or the budget runs out; returns the frames
## actually spent. Used for the climb, because "how many frames is a storey" is
## exactly the kind of number that goes stale.
func _hold_until(actions: Array, stop: Callable, budget: int) -> int:
	for a in actions:
		Input.action_press(a)
	var spent := 0
	while spent < budget and not stop.call():
		await physics_frame
		spent += 1
	for a in actions:
		Input.action_release(a)
	await physics_frame
	return spent


func _terrain(map: Dictionary, body: Node2D) -> String:
	return MapData.terrain_at_px(map, body.global_position + Vector2(0.0, 8.0))


func _stratum(map: Dictionary, body: Node2D) -> String:
	return MapData.stratum_at_px(map, body.global_position + Vector2(0.0, 8.0))


func _run() -> void:
	Engine.max_fps = 60
	await process_frame
	var game := root.get_node("Game")
	var party := root.get_node("Party")
	game.call("reset_story")
	for f in ["prologue_done", "ebb_done"]:
		game.call("set_flag", f)
	# SOLO. A follower on a ladder is a fine thing to want, but it is party-ai's
	# question (the leash is stratum-aware) and a second body in the shaft would make
	# every position here an argument about who nudged whom.
	var roster: Array[StringName] = [&"basil"]
	party.call("set_roster", roster, &"basil")

	change_scene_to_file("res://scene/alembic_town.tscn")
	await _settle()
	ok(current_scene != null and current_scene.name == "AlembicTown",
			"Alembic Town loads")
	if current_scene == null or current_scene.name != "AlembicTown":
		print("ladder probe: %d FAILED" % _fail)
		quit(1)
		return
	var map: Dictionary = current_scene.map
	var body := _leader()

	# ---- 0. THE GRID STILL SAYS WHAT THIS PROBE ASSUMES ---------------------------
	# Every number below is a cell in town.txt. Assert them against the map rather
	# than trusting them, or a re-authored tree turns four real findings into four
	# tests of an empty patch of grass.
	ok(MapData.terrain_at(map, Vector2i(LADDER_COLS.x, MID_ROW)) == "ropeladder"
			and MapData.terrain_at(map, Vector2i(LADDER_COLS.y, MID_ROW)) == "ropeladder"
			and MapData.terrain_at(map, Vector2i(LADDER_COLS.x - 1, MID_ROW)) != "ropeladder"
			and MapData.terrain_at(map, Vector2i(LADDER_COLS.y + 1, MID_ROW)) != "ropeladder",
			"tree 1's ladder is exactly cols %d-%d" % [LADDER_COLS.x, LADDER_COLS.y])
	ok(MapData.terrain_run_center_x(map,
			Vector2(LADDER_COLS.x * 16 + 8, MID_ROW * 16 + 8)) == LANE_X,
			"...so its lane is x=%d" % int(LANE_X))
	ok(MapData.terrain_at(map, Vector2i(LADDER_COLS.x, FOOT_ROW)) != "ropeladder",
			"row %d is the ground under it" % FOOT_ROW)

	# ---- 1. WALKING ON PULLS YOU INTO THE LANE ------------------------------------
	# Approach off-centre, from the ground, the way a player actually arrives: they
	# are not going to line up with a two-cell shaft before they touch it. This is
	# the case the FUNNEL exists for — the rungs sit inside the trunk's four columns,
	# so the gap a 12px body actually fits through is 20px of the 32px pair, and
	# without a funnel this walk ends against bark with the ladder beside it.
	await _park(body, Vector2i(LADDER_COLS.x, FOOT_ROW), -6.0)
	var start_x := body.global_position.x
	var on_ladder := func() -> bool: return _terrain(map, body) == "ropeladder"
	await _hold_until(["move_up"], on_ladder, 90)
	ok(on_ladder.call(), "walking north off the ground gets onto the rungs")
	# Two frames' grace: the pull is exact but it starts the frame AFTER the feet
	# cross, so the crossing frame itself is still at the walk-in offset.
	await _hold(["move_up"], 3)
	ok(absf(body.global_position.x - LANE_X) < 0.5,
			"...and the lane takes the body from x=%.1f to the centre line (x=%.1f)"
			% [start_x, body.global_position.x])

	# ---- 2. THE LANE WINS OVER A SIDEWAYS PRESS -----------------------------------
	# The whole complaint, in one test: you should not be able to walk about on a
	# ladder. Pressed hard into a stile the body must not move, and pressed while
	# off-centre it must move the WRONG way — back to the middle.
	await _park(body, Vector2i(LADDER_COLS.x, MID_ROW), 0.0)
	var held := body.global_position
	await _hold(["move_left"], 30)
	ok(body.global_position.distance_to(held) < 1.0,
			"holding LEFT on the rungs moves the body %.1f px"
			% body.global_position.distance_to(held))
	await _hold(["move_right"], 30)
	ok(body.global_position.distance_to(held) < 1.0,
			"holding RIGHT on the rungs moves the body %.1f px"
			% body.global_position.distance_to(held))
	# Dropped off-lane and pressed FURTHER off it, the body still comes back. No
	# settle before the sample: the pull runs on an idle body too (it is the lane,
	# not a movement mode), so six quiet frames would recentre the body and leave
	# this measuring nothing.
	body.global_position = Vector2(LADDER_COLS.y, MID_ROW) * 16.0 + Vector2(13.0, 8.0)
	body.velocity = Vector2.ZERO
	await physics_frame
	var off_lane := body.global_position.x
	await _hold(["move_right"], 20)
	ok(off_lane > LANE_X + 2.0 and absf(body.global_position.x - LANE_X) < 0.5,
			"...and from x=%.1f, pressing further RIGHT still recovers the lane"
			% off_lane)

	# ---- 3. A DIAGONAL PRESS CLIMBS AT FULL SPEED ---------------------------------
	# _climb takes the SIGN of the vertical input, not the .y of a normalized vector,
	# so up+right is simply up. Taking the component instead would climb at 0.71x —
	# slow in a way no player could ever explain, on the one input a player pressing
	# toward a ladder is most likely to be holding.
	await _park(body, Vector2i(LADDER_COLS.x, MID_ROW))
	var y0 := body.global_position.y
	await _hold(["move_up"], 20)
	var straight := y0 - body.global_position.y
	await _park(body, Vector2i(LADDER_COLS.x, MID_ROW))
	y0 = body.global_position.y
	await _hold(["move_up", "move_right"], 20)
	var diagonal := y0 - body.global_position.y
	ok(straight > 20.0 and absf(diagonal - straight) < 3.0,
			"up+right climbs as fast as up (%.1f px vs %.1f px in 20 frames)"
			% [diagonal, straight])

	# ---- 4. YOU DO NOT HOP OFF A ROPE LADDER --------------------------------------
	await _park(body, Vector2i(LADDER_COLS.x, MID_ROW))
	held = body.global_position
	Input.action_press("jump")
	await physics_frame
	Input.action_release("jump")
	var airborne := false
	for i in 40:
		if bool(body.call("is_airborne")):
			airborne = true
		await physics_frame
	ok(not airborne and body.global_position.distance_to(held) < 1.0,
			"the hop is refused on the rungs")

	# ---- 5. THE CLIMB ENDS, BOTH WAYS — ACROSS THE SPLIT ---------------------------
	# Since the 2026-08-23 two-scene split, a floor ladder's top two rungs are a
	# TRAVEL MOUTH: the climb up leaves this scene entirely and continues on the
	# canopy scene's own rungs (Game.town_spawn "headN" seats the body there still
	# facing up). The pin's failure mode is unchanged — a body that can never
	# leave the lane looks exactly like one still climbing — it just has a scene
	# boundary in the middle of it now, so the probe rides the whole hand-off.
	await _park(body, Vector2i(LADDER_COLS.x, MID_ROW))
	var in_canopy := func() -> bool: \
			return current_scene != null and current_scene.name == "AlembicCanopy"
	var frames := await _hold_until(["move_up"], in_canopy, 600)
	ok(in_canopy.call() and frames < 600,
			"the climb UP hands the body to the canopy scene in %d frames" % frames)
	if not in_canopy.call():
		print("ladder probe: %d FAILED" % _fail)
		quit(1)
		return
	await _settle(80)                     # the canopy's entry fade + lock
	var cmap: Dictionary = current_scene.map
	body = _leader()
	ok(_terrain(cmap, body) == "ropeladder",
			"...arriving ON the canopy's own rungs (%s)" % _terrain(cmap, body))
	# fresh closures over the REASSIGNED map/body — a lambda captures by value
	var off_canopy_rungs := func() -> bool: \
			return _terrain(cmap, body) != "ropeladder"
	frames = await _hold_until(["move_up"], off_canopy_rungs, 300)
	ok(off_canopy_rungs.call() and frames < 300,
			"...and continues up onto the ring deck in %d frames" % frames)
	ok(absf(body.global_position.x - LANE_X) < 8.0,
			"...stepping off within the ladder's own columns (x=%.1f)"
			% body.global_position.x)

	# ...and DOWN: from the canopy's rungs, through the mouth, back to the floor.
	await _park(body, Vector2i(LADDER_COLS.x, 18))     # canopy z runs rows 16-22
	var in_town := func() -> bool: \
			return current_scene != null and current_scene.name == "AlembicTown"
	frames = await _hold_until(["move_down"], in_town, 600)
	ok(in_town.call() and frames < 600,
			"the climb DOWN hands the body back to the floor scene in %d frames"
			% frames)
	if not in_town.call():
		print("ladder probe: %d FAILED" % _fail)
		quit(1)
		return
	await _settle(80)
	map = current_scene.map
	body = _leader()
	ok(_terrain(map, body) == "ropeladder",
			"...arriving on the floor scene's rungs (%s)" % _terrain(map, body))
	var fmap: Dictionary = map
	var fbody := body
	var off_floor_rungs := func() -> bool: \
			return _terrain(fmap, fbody) != "ropeladder"
	frames = await _hold_until(["move_down"], off_floor_rungs, 300)
	ok(off_floor_rungs.call() and frames < 300,
			"...and continues down to the forest floor in %d frames" % frames)

	# ---- 6. OFF THE LADDER, NOTHING CHANGED ---------------------------------------
	# The lane is scoped to `ropeladder` cells and to nothing else. If it leaked, it
	# would leak on open ground — where every map in the game is one long horizontal
	# run of the same terrain, and the body would be dragged to the middle of it.
	await _park(body, Vector2i(LADDER_COLS.x, FOOT_ROW + 2))
	var walk_from := body.global_position
	await _hold(["move_left"], 30)
	ok(walk_from.x - body.global_position.x > 30.0,
			"a body on open grass still walks sideways freely (%d px)"
			% int(walk_from.x - body.global_position.x))

	print("ladder probe: ", "ALL PASS" if _fail == 0 else "%d FAILED" % _fail)
	quit(1 if _fail else 0)
