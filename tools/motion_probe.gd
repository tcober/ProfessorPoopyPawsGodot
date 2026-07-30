extends SceneTree

## Behavioral probe for Act 1 beat 3b, "THE MOTION" (Mayor Hollis) and beat 4's
## opening, "THE CROSSING" — the chain that turns a librarian with a stolen
## thesis into somebody her town has formally asked to go, and then puts her on
## the water. defence_probe.gd owns the fight; this owns everything after it.
##
## Asserts, in the order the player meets them:
##
##   1. THE GEOMETRY the beat rests on — the pier deck, the berth under the
##      launch, the mayor's post, and the ONE that actually bit: a mayor is a
##      solid 12x8 body, so a mayor standing in a one-cell lane is a WALL. The
##      route from the gate to the pier must survive him.
##   2. HE IS A FIXTURE, not a quest-giver who appears on cue: three states
##      (Ebb night / the beat opener / post-departure), three live line sets.
##   3. ...but NOT in the street during the fight, and stepping out of the hall
##      the moment it is over — the transition inside ONE scene load.
##   4. THE MOTION runs on `talked`, sets both flags, and holds the party for
##      the whole beat (NPC._talk unlocks BEFORE it emits, so _on_mayor_talked
##      re-locking before its first await is load-bearing).
##   5. ...and never runs twice.
##   6. THE PIER refuses before the launch is hers, and says so — then casts
##      off once it is, and lands her on Forest Land's west shingle.
##
## Staged BY NAME out of chapters.gd, never by index (recital_probe's rule):
## the table is the single source of truth for what a beat needs, so staging
## through it means this probe also proves the table.
##
## Must run WINDOWED (the GL Compatibility renderer draws black headless):
##   /Applications/Godot.app/Contents/MacOS/Godot --path . --script tools/motion_probe.gd

const MAP_PATH := "res://assets/maps/lanternwood.txt"
const OW_MAP_PATH := "res://assets/maps/overworld.txt"
const TOWN := "res://scene/lanternwood.tscn"
const OVERWORLD := "res://scene/overworld.tscn"
const MAYOR := "Mayor Hollis"

## overworld.gd's return-spawn drop and Fuji's chibi frames, read from the script
## under test rather than re-typed, so a retune there fails loudly here instead of
## silently passing against a stale copy.
##
## LOADED LAZILY, AND NEVER `preload`ed — this cost a whole run to find. `preload`
## compiles overworld.gd as part of THIS tool's own compile, which happens before
## the autoloads register, so its `Game.` / `Party.` references fail, the script is
## left broken, and `overworld.tscn` then instantiates its root as a **scriptless
## Node2D**. The symptom is nothing like the cause: "Invalid access to property
## 'player' on a base object of type 'Node2D'" from a scene that works perfectly in
## the game. Same trap tools/CLAUDE.md records for naming the `Player` class in a
## probe. A runtime `load()` is fine: by then the autoloads exist.
static var _ow_consts: Dictionary = {}


func _ow(name: String) -> Variant:
	if _ow_consts.is_empty():
		_ow_consts = (load("res://scene/overworld.gd") as GDScript) \
				.get_script_constant_map()
	return _ow_consts[name]

var _fails := 0
var _last_press := 0
var game: Node
var party: Node

## The three line sets the fixture hands out, captured as they are met.
var _lines: Dictionary = {}


func _initialize() -> void:
	_run()


func _check(label: String, cond: bool) -> void:
	print(("  ok    " if cond else "  FAIL  ") + label)
	if not cond:
		_fails += 1


## Something true about the map worth printing but not worth failing over —
## the pinch numbers, so a later map edit that moves an anchor into a lane
## shows up in the run output next to the check that would catch it.
func _note(label: String) -> void:
	print("  note  " + label)


func _wait_frames(n: int) -> void:
	for i in n:
		await process_frame


## Apply a chapters.gd beat exactly as dev_menu._launch does, looked up by name.
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


func _scene_is(path: String) -> bool:
	return current_scene != null and current_scene.scene_file_path == path


func _enemies() -> Array:
	return get_nodes_in_group("enemies")


func _party_free() -> bool:
	var p: Node2D = party.leader
	return p != null and is_instance_valid(p) and p.is_physics_processing()


## Mayor Hollis in the street, or null. Matched by display_name rather than by
## type: the Ebb-night street has three other NPCs standing in it.
func _mayor() -> Node:
	var world := current_scene.get_node_or_null("World")
	if world == null:
		return null
	for c in world.get_children():
		if c is NPC and (c as NPC).display_name == MAYOR:
			return c
	return null


## Advance dialog by pressing attack every 250ms (past DialogBox's swallow
## window) until pred() holds or the budget dies — library_probe's helper, plus
## a per-frame `watch` so a caller can assert about the frames INSIDE a beat
## (was the party ever free? did his slate come back out?). watch never runs on
## the frame pred first holds, so an end-of-beat unlock can't trip it.
func _mash_until(pred: Callable, max_frames: int, watch := Callable()) -> bool:
	for i in max_frames:
		if pred.call():
			Input.action_release("attack")
			return true
		if watch.is_valid():
			watch.call()
		var now := Time.get_ticks_msec()
		if now - _last_press > 250:
			_last_press = now
			Input.action_press("attack")
		elif now - _last_press > 120:
			Input.action_release("attack")
		await process_frame
	Input.action_release("attack")
	return false


## Plant the leader somewhere and let physics settle her there. The double park
## is the library_probe dance: a settle frame can depenetrate her a pixel or
## two off a cell edge, and every zone in this beat is 16px tall.
func _park(pos: Vector2) -> void:
	var p: Node2D = party.leader
	p.velocity = Vector2.ZERO
	p.global_position = pos
	await _wait_frames(6)
	p.velocity = Vector2.ZERO
	p.global_position = pos
	await _wait_frames(8)


## Hold a movement action for `frames` and give the body back. Real polled
## input, never an InputEvent — a synthesized press only exists in the polled
## state (the shot.gd gotcha), which is why every action in this project is
## polled in the first place.
func _hold(action: String, frames: int) -> void:
	Input.action_press(action)
	await _wait_frames(frames)
	Input.action_release(action)
	await _wait_frames(4)


## Steer the leader toward a point with real polled input until she is within
## `within` px, or the budget dies. Returns whether she got there.
##
## Deliberately NOT pathfinding: it presses the dominant axis toward the goal and
## re-decides every frame, which is roughly what a player does and — the point —
## will WEDGE on a genuine chokepoint instead of teleporting past it. That is the
## failure this probe exists to catch, so the crude steering is the feature.
## It walks the OTHER axis for a moment whenever it stops making progress, which
## is what gets it around a corner without turning into A*.
func _walk_to(goal: Vector2, within := 24.0, max_frames := 480) -> bool:
	var p: Node2D = party.leader
	var actions := ["move_left", "move_right", "move_up", "move_down"]
	var stuck := 0
	var last := p.global_position
	var cross := 0
	for i in max_frames:
		var d := goal - p.global_position
		if d.length() <= within:
			for a in actions:
				Input.action_release(a)
			return true
		var horiz := absf(d.x) > absf(d.y)
		if cross > 0:                            # nudging along the other axis
			cross -= 1
			horiz = not horiz
		for a in actions:
			Input.action_release(a)
		if horiz:
			Input.action_press("move_right" if d.x > 0.0 else "move_left")
		else:
			Input.action_press("move_down" if d.y > 0.0 else "move_up")
		await process_frame
		if i % 10 == 9:
			stuck = stuck + 1 if p.global_position.distance_to(last) < 4.0 else 0
			last = p.global_position
			if stuck >= 2:
				cross = 24                       # pinned: try the other axis
				stuck = 0
	for a in actions:
		Input.action_release(a)
	return p.global_position.distance_to(goal) <= within


## Wait for the party to be frozen — the tell that a staged beat has taken the
## body. Guards the false pass: without it every "did the beat run" check below
## would be true from frame one.
func _wait_locked(max_frames: int) -> bool:
	for i in max_frames:
		if not _party_free():
			return true
		await process_frame
	return false


# ---- the map, read as a graph -------------------------------------------------------

## char -> terrain class name, straight out of the map txt's legend lines.
## MapData keeps only `solid`, and these checks are ABOUT the classes the map
## header chose — `dock` for a deck you walk on, `berth` for the water the
## launch sits in — so parse the class names here.
func _classes(path: String) -> Dictionary:
	var out := {}
	var f := FileAccess.open(path, FileAccess.READ)
	while not f.eof_reached():
		var line := f.get_line().strip_edges()
		if line.begins_with("map"):
			break
		var parts := line.split(" ", false)
		if parts.size() >= 4 and parts[0] == "legend":
			out[parts[1]] = parts[2]
	return out


func _cell(map: Dictionary, anchor: String) -> Vector2i:
	return map.anchors[anchor] as Vector2i


func _char_at(map: Dictionary, c: Vector2i) -> String:
	return (map.lines[c.y] as String)[c.x]


func _klass(map: Dictionary, classes: Dictionary, c: Vector2i) -> String:
	return classes.get(_char_at(map, c), "?")


## Flood the walkable graph 4-connected from `start`, treating `blocked` as
## wall. 4-connected on purpose: a body cannot slip through a diagonal gap
## between two solid cells, so an 8-connected flood would prove a route the
## player can't walk.
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


## One shortest walkable path between two cells (empty if there is none). Any
## single cell that cuts `from` off from `to` must lie on EVERY path between
## them, so testing the cells of one shortest path finds every chokepoint
## without flooding the map once per cell.
func _path(map: Dictionary, from: Vector2i, to: Vector2i) -> Array:
	var came := {from: from}
	var q: Array[Vector2i] = [from]
	var head := 0
	while head < q.size():
		var c: Vector2i = q[head]
		head += 1
		if c == to:
			break
		for d in [Vector2i.RIGHT, Vector2i.LEFT, Vector2i.DOWN, Vector2i.UP]:
			var n: Vector2i = c + d
			if came.has(n) or MapData.is_solid(map, n):
				continue
			came[n] = c
			q.append(n)
	if not came.has(to):
		return []
	var out: Array = []
	var walk: Vector2i = to
	while walk != from:
		out.append(walk)
		walk = came[walk]
	out.append(from)
	out.reverse()
	return out


## Cells that single-handedly sever `from` from `to` — the map's pinches.
func _chokepoints(map: Dictionary, from: Vector2i, to: Vector2i) -> Array:
	var out: Array = []
	for c: Vector2i in _path(map, from, to):
		if c == from or c == to:
			continue
		if not _reach(map, from, [c]).has(to):
			out.append(c)
	return out


func _run() -> void:
	await process_frame
	# an OCCLUDED macOS window runs UNCAPPED (~2000fps): frame budgets burn in
	# real seconds while wall-clock cutscene timers don't advance any faster
	Engine.max_fps = 60
	game = root.get_node("Game")
	party = root.get_node("Party")
	var map: Dictionary = MapData.load_map(MAP_PATH)

	print("motion probe:")
	_test_geometry(map)
	await _test_ebb_night_fixture(map)
	await _test_defence_handoff(map)
	await _test_the_motion(map)
	await _test_the_crossing(map)
	await _test_the_landing()

	print("motion probe: %s" % ("ALL PASS" if _fails == 0 else "%d FAILED" % _fails))
	quit(1 if _fails > 0 else 0)


# ---- 1. THE GEOMETRY ----------------------------------------------------------------
# Everything below is authored in assets/maps/lanternwood.txt and nowhere else, so
# these read the map txt directly. They are cheap and they run FIRST because every
# behavioural failure further down has a geometry explanation first.

func _test_geometry(map: Dictionary) -> void:
	print(" the geometry the beat rests on:")
	var classes := _classes(MAP_PATH)
	var dock := _cell(map, "dock")
	var post := _cell(map, "mayor_pos")
	var hall := _cell(map, "moot_hall")
	var start := _cell(map, "player_start")

	# The pier is where she boards. A solid deck cell is a pier you cannot walk
	# out onto, and DockZone would never see her.
	_check("the dock anchor is a walkable `dock` cell (%s)" % _klass(map, classes, dock),
		not MapData.is_solid(map, dock) and _klass(map, classes, dock) == "dock")

	# The launch is a Tier-3 prop on the berth, y-sorted SOUTH of the deck so the
	# hull swallows a body's sprite overhang. Berth north of deck, or berth that
	# is walkable, and she stands on open water with the boat behind her.
	var berth_ok := true
	for x in range(dock.x - 2, dock.x + 3):
		var below := Vector2i(x, dock.y + 1)
		if _klass(map, classes, below) != "berth" or not MapData.is_solid(map, below):
			berth_ok = false
	_check("the berth is solid water directly SOUTH of the deck", berth_ok)

	# He steps out of a door, so the door cell has to be one she can stand on,
	# and the lane through it has to be a lane — a door cell with one open side
	# is a cul-de-sac the player has to reverse out of.
	var hall_sides := 0
	for d in [Vector2i.RIGHT, Vector2i.LEFT, Vector2i.DOWN, Vector2i.UP]:
		if not MapData.is_solid(map, hall + d):
			hall_sides += 1
	_check("the moot hall door is walkable and its lane runs THROUGH it (%d open sides)"
			% hall_sides,
		not MapData.is_solid(map, hall) and hall_sides >= 2)

	# THE ONE THAT BIT. An NPC is a solid StaticBody2D with a 12x8 box in a 16px
	# cell, so a mayor standing in a one-cell lane is a WALL. A post with one
	# open side means the player walks up to him and can go no further.
	var post_sides := 0
	for d in [Vector2i.RIGHT, Vector2i.LEFT, Vector2i.DOWN, Vector2i.UP]:
		if not MapData.is_solid(map, post + d):
			post_sides += 1
	_check("the mayor's post has walkable cells on more than one side (%d)" % post_sides,
		not MapData.is_solid(map, post) and post_sides >= 2)

	# ...and the same fact stated as the thing it protects: the pier has to be
	# walkable-to at all.
	_check("the pier is reachable on foot from the gate",
		_reach(map, start, []).has(dock))

	# THE MOST VALUABLE CHECK IN THIS PROBE. Placing the moot hall pinched the
	# harbour lane to a single cell, and a mayor parked in a pinch SEALS THE PIER
	# OFF ENTIRELY — the beat hands her a boat she can no longer reach, with
	# nothing on screen to say why. Flood the walkable graph with his cell
	# removed and prove the crossing is still there.
	_check("THE MAYOR CANNOT SEAL THE PIER — the crossing survives him standing on it",
		_reach(map, start, [post]).has(dock))

	# His walk starts at the hall door, and the player has to be able to follow
	# the same route on foot (theater.walk tweens with collision off; she does not).
	_check("his door and his post are on the same walkable graph",
		_reach(map, hall, []).has(post) and _reach(map, start, []).has(hall))

	# Not a failure — the numbers behind the check above, printed so a map edit
	# that drops an anchor into the pinch is visible in the run output.
	var chokes := _chokepoints(map, start, dock)
	_note("single-cell chokepoints on the route to the pier: %s" % str(chokes))
	if chokes.has(hall):
		_note("...the mayor's SPAWN cell %s is one of them — he is a wall in the"
				% str(hall) + " harbour lane for the length of his walk out")


# ---- 2. THE FIXTURE, state one: the Ebb night ---------------------------------------
# He is out on his step the night the magic dies, already writing it up, so that by
# the time he sends her the player has met him. If this state is missing he is a
# quest-giver who materialises on cue, which is the thing the beat is built not to be.

func _test_ebb_night_fixture(map: Dictionary) -> void:
	print(" the fixture, state one — the Ebb night:")
	await _stage("LANTERNWOOD - EBB NIGHT")
	await _wait_frames(60)
	var m := _mayor()
	_check("Mayor Hollis is in the street on the Ebb night, unasked", m != null)
	if m == null:
		return
	_check("...on his own step (the mayor_pos anchor)",
		(m as Node2D).global_position.distance_to(MapData.anchor_px(map, "mayor_pos")) < 2.0)
	_check("...with something to say (an NPC with no lines cannot be talked to at all)",
		(m as NPC).lines.size() > 0)
	_lines["ebb"] = (m as NPC).lines


# ---- 3. THE DEFENCE: he is not in the street, then he is ----------------------------
# _spawn_mayor returns early for the length of the fight and _finish_defence walks him
# out of the hall the moment it is clear. That transition happens inside ONE scene
# load, with no door and no fade to hide behind, which is why it is the part most
# likely to be broken.

func _test_defence_handoff(map: Dictionary) -> void:
	print(" the defence handoff — out of the hall, into the lane:")
	await _stage("THE DEFENCE OF LANTERNWOOD")
	await _wait_frames(40)
	_check("the fight stages into Lanternwood with solo Fuji armed",
		_scene_is(TOWN) and party.roster.size() == 1 and party.leader_id == &"fuji"
			and party.leader.armed_tome())
	_check("three slimes in the lanes and the scene knows it (_alive=%d)"
			% current_scene._alive,
		_enemies().size() == 3 and current_scene._alive == 3)

	# A mayor standing calmly in a lane with a slime in it is a worse joke than
	# any of his — and he is a solid body, so he would also be cover.
	_check("NO mayor in the street while the lanes are full", _mayor() == null)

	# The pier is held for the same reason the south gate is: leaving mid-fight
	# drops the whole set-piece. boat_ready is forced on here so the refusal
	# under test is the _alive guard and not the not-hers-to-take one — nothing
	# else can produce "armed launch, live slimes", and a guard nobody can reach
	# is a guard nobody has tested.
	game.call("set_flag", "boat_ready")
	current_scene.theater.hint("", 0.1)
	await _park(MapData.anchor_px(map, "dock"))
	await _wait_frames(24)
	_check("the pier refuses to cast off while something is in the lanes", _scene_is(TOWN))
	_check("...and SAYS so (a travel door that silently refuses reads as broken)",
		String(current_scene.theater._hint.text).contains("LANES"))
	# ...and off it again, or body_entered never re-fires when it reopens.
	await _park(MapData.anchor_px(map, "player_start"))

	# Clear the lanes through HealthComponent: what is under test is the beat's
	# handoff, not the damage pipeline (rpg_probe covers that end to end).
	for e in _enemies():
		var health = e.get_node("HealthComponent")
		health.take_damage(health.current_health)
	# First sighting, on the frame he appears — _finish_defence sets his position
	# to the hall door and starts the tween, so a mayor who is already at his post
	# means the walk never happened and he just popped into the street.
	var first_seen := Vector2.INF
	for i in 240:
		var m := _mayor()
		if m != null:
			first_seen = (m as Node2D).global_position
			break
		await process_frame
	_check("clearing the lanes sets town_defended", game.call("flag", "town_defended"))
	_check("...and puts a mayor in the street inside the SAME scene load",
		first_seen != Vector2.INF)
	var hall_px := MapData.anchor_px(map, "moot_hall")
	var post_px := MapData.anchor_px(map, "mayor_pos")
	_check("he comes OUT OF THE HALL — first seen at the moot hall door, not at his post",
		first_seen.distance_to(hall_px) < first_seen.distance_to(post_px))
	await _wait_frames(200)                      # the 34px/s walk is ~2.1s
	var m := _mayor()
	_check("...and the walk lands him on his post",
		m != null and (m as Node2D).global_position.distance_to(post_px) < 2.0)
	_check("...with the beat opener on him, not the Ebb-night lines",
		m != null and (m as NPC).lines.size() > 0
			and (m as NPC).lines != _lines.get("ebb", PackedStringArray()))
	if m != null:
		_lines["opener"] = (m as NPC).lines

	# The geometry checks above only prove a GRAPH. Walk the harbour lane for
	# real, with him standing in the street, and confirm a body actually fits —
	# a lane you can see through and not walk down is the failure this catches.
	# (It caught it: at five terrace rows this lane was one cell of headroom and
	# he sealed the pier off just by standing in it. LEVEL 1 is six rows now.)
	#
	# The route is deliberately right-then-up-then-back: walking east runs her to
	# the shore wall, so reaching him means coming back WEST along the forecourt,
	# which is the actual path a player takes and the one a pinch would break.
	await _park(Vector2(30 * 16 + 8, 48 * 16 + 8))
	await _hold("move_right", 200)
	_check("she can walk the whole harbour lane past the hall (x=%d)"
			% int(party.leader.global_position.x),
		party.leader.global_position.x >= post_px.x - 8.0)
	# ...and now STEER to him rather than holding fixed durations. Tuned frame
	# counts encode one map layout and go quietly wrong the next time a cell
	# moves; a body that walks itself to the target proves the thing the check is
	# actually about, which is that a route exists a player could find.
	var reached := await _walk_to(post_px, 24.0, 480)
	_check("...and around onto the forecourt to reach his talk zone (%dpx away)"
			% int(party.leader.global_position.distance_to(post_px)), reached)


# ---- 4. THE MOTION -----------------------------------------------------------------

func _test_the_motion(map: Dictionary) -> void:
	print(" THE MOTION:")
	await _stage("THE MOTION (MAYOR HOLLIS)")
	await _wait_frames(60)
	_check("the beat stages a quiet town with the mayor already on his step",
		_scene_is(TOWN) and _enemies().is_empty() and _mayor() != null)
	var m := _mayor()
	if m == null:
		return
	_check("...at the mayor_pos anchor",
		(m as Node2D).global_position.distance_to(MapData.anchor_px(map, "mayor_pos")) < 2.0)
	_check("neither flag is set before she talks to him",
		not game.call("flag", "mayor_briefed") and not game.call("flag", "boat_ready"))

	# Talk from a step SOUTH: the 20px TalkZone reaches, and standing on the body
	# itself just depenetrates her back off it.
	await _park((m as Node2D).global_position + Vector2(0.0, 18.0))
	Input.action_press("interact")
	await _wait_frames(4)
	Input.action_release("interact")
	var locked := await _wait_locked(60)
	_check("the conversation takes the body", locked)

	# NPC._talk unlocks the party BEFORE it emits `talked`, so _on_mayor_talked
	# re-locking before its first await is load-bearing. If it ever slips behind
	# an await, she walks out from under the beat mid-sentence — and npc.gd would
	# arm a SECOND conversation through the first one, because it only refuses
	# while the party is frozen.
	# A GDScript lambda captures by VALUE. `ever_free = true` inside the closure
	# assigns a COPY, so reading a plain bool back out here is always false and this
	# check silently passes forever. An Array is the reference container.
	var ever_free := [false]
	var watch := func() -> void:
		if _party_free():
			ever_free[0] = true
	var ran: bool = await _mash_until(func() -> bool:
			return game.call("flag", "mayor_briefed"), 9000, watch)
	_check("talking to him runs the beat to the end (mayor_briefed)", ran)
	_check("...and it hands her the launch (boat_ready)", game.call("flag", "boat_ready"))
	_check("the party is LOCKED for the WHOLE beat — she never walks out from under it",
		locked and not ever_free[0])
	await _wait_frames(6)
	_check("...and free again the moment it is over", _party_free())

	# He is a fixture, so the beat changes only his LINES.
	_check("his lines change to the post-departure set",
		(m as NPC).lines.size() > 0 and (m as NPC).lines != _lines.get("opener",
			PackedStringArray()))
	_lines["after"] = (m as NPC).lines

	# Idempotence. _on_mayor_talked early-returns on mayor_briefed; if it ever
	# stops, every later chat with him replays forty lines of minutes and re-fires
	# theater.hint over whatever the player is doing. His slate coming back out
	# (play_act) is the tell — nothing else in this scene plays that clip.
	await _park((m as Node2D).global_position + Vector2(0.0, 18.0))
	Input.action_press("interact")
	await _wait_frames(4)
	Input.action_release("interact")
	var locked2 := await _wait_locked(60)
	var saw_act := [false]                       # by-value capture again — see above
	var watch_act := func() -> void:
		if (m as NPC).sprite.animation == "act":
			saw_act[0] = true
	await _mash_until(_party_free, 3000, watch_act)
	_check("talking to him again does NOT re-run the beat", locked2 and not saw_act[0])
	_check("...and his lines are unchanged by it",
		(m as NPC).lines == _lines.get("after", PackedStringArray()))


# ---- 5/6. THE FIXTURE state three, and THE CROSSING --------------------------------

func _test_the_crossing(map: Dictionary) -> void:
	print(" the fixture, state three — and THE CROSSING:")
	await _stage("THE CROSSING (THE PIER)")
	await _wait_frames(90)                       # entry fade + the marker entry lock
	var m := _mayor()
	_check("a briefed mayor is still on his step (he does not leave when she does)",
		m != null and (m as NPC).lines.size() > 0)
	if m != null:
		_lines["fresh"] = (m as NPC).lines
		# The post-departure lines are written out TWICE in lanternwood.gd — once
		# in _spawn_mayor's ladder, once at the end of _the_motion. Nothing ties
		# the two copies together, so a rewrite of one silently gives him
		# different lines depending on whether the player left the town.
		_check("...saying exactly what the beat left him saying (the two copies agree)",
			(m as NPC).lines == _lines.get("after", PackedStringArray()))
	_check("all three states give him DIFFERENT lines",
		_lines.get("ebb") != _lines.get("opener")
			and _lines.get("opener") != _lines.get("after")
			and _lines.get("ebb") != _lines.get("after"))

	# THE BANNER RACE. Every first trip to the pier crosses the moot hall's door
	# cell — it sits IN the one-cell harbour lane — which fires TravelScene's
	# announce and holds _busy for BANNER_IN + HOLD + OUT twice over (name +
	# locked_text = 4.4s). The walk from that door to the pier is ~1.4s, so she
	# arrives while _busy is still true and _on_dock returns with no cast-off and
	# no hint. DockZone is a plain Area2D, so body_entered will not re-fire while
	# she stands there: the pier is dead until she steps off and back on.
	await _park(MapData.anchor_px(map, "moot_hall"))
	await _wait_frames(20)
	_check("standing on the hall door starts its banner (the precondition)",
		current_scene._busy)
	party.leader.global_position = MapData.anchor_px(map, "dock")
	var cast_off := false
	for i in 300:                                # 5s > the 4.4s banner
		if not _party_free():                    # _cast_off's first act is lock_party
			cast_off = true
			break
		party.leader.velocity = Vector2.ZERO
		await process_frame
	_check("the pier still answers right after the moot hall banner", cast_off)

	# ...and now the clean case, from a fresh entry with no banner running.
	await _stage("THE CROSSING (THE PIER)")
	await _wait_frames(60)
	_check("the pier beat stages with an armed launch and no fight",
		game.call("flag", "boat_ready") and _enemies().is_empty())
	await _park(MapData.anchor_px(map, "dock"))
	_check("stepping onto the pier takes the body for the departure",
		await _wait_locked(90))
	var gone: bool = await _mash_until(func() -> bool:
			return _scene_is(OVERWORLD), 1800)
	_check("she casts off and the crossing lands somewhere", gone)
	_check("...leaving Lanternwood behind her (left_lanternwood)",
		game.call("flag", "left_lanternwood"))
	_check("...routed to the west shingle, not the town gate",
		game.overworld_spawn == "landing")
	_check("...on the overworld", _scene_is(OVERWORLD))


# ---- 7. THE LANDING ----------------------------------------------------------------
# Solo Fuji on the travel map for the first time. A landing that misses its marker
# puts her in the sea, and a chibi that never repoints its frames lands Basil on the
# beach in the middle of a chapter he is not in yet.

func _test_the_landing() -> void:
	print(" the landing:")
	if not _scene_is(OVERWORLD):
		_check("the crossing reached the overworld (landing checks skipped)", false)
		return
	var ow: Dictionary = MapData.load_map(OW_MAP_PATH)
	var chibi: Node2D = current_scene.get("player") as Node2D
	if chibi == null:
		_check("the overworld handed the probe its chibi (nothing else can be "
				+ "checked without it)", false)
		return
	var want := MapData.anchor_px(ow, "landing") + Vector2(0.0, _ow("ARRIVE_DROP"))
	var arrived := chibi.global_position
	_check("the chibi arrives at the landing marker + ARRIVE_DROP",
		arrived.distance_to(want) < 2.0)
	var cell := Vector2i(arrived / 16.0)
	_check("...on a WALKABLE cell (%s), not inside the coast" % str(cell),
		not MapData.is_solid(ow, cell))
	var frames := (chibi.get_node("AnimatedSprite2D") as AnimatedSprite2D).sprite_frames
	_check("...as FUJI — overworld.gd repointed the chibi's SpriteFrames",
		frames != null and frames.resource_path == _ow("FUJI_CHIBI_FRAMES"))

	# The graph says she can get to town; polled input says she is not wedged.
	_check("Alembic Town's gate is reachable on foot from the shingle",
		_reach(ow, cell, []).has(_cell(ow, "town")))
	var before := chibi.global_position
	await _hold("move_right", 40)
	_check("...and she actually walks when told to (moved %dpx)"
			% int(chibi.global_position.distance_to(before)),
		chibi.global_position.distance_to(before) > 16.0)

	# ...and the chapters row for the same place lands identically, so the dev
	# menu and the real crossing can never drift apart.
	await _stage("THE WEST SHINGLE (LANDED)")
	await _wait_frames(40)
	_check("the chapters row THE WEST SHINGLE (LANDED) lands on the same stones",
		_scene_is(OVERWORLD)
			and (current_scene.get("player") as Node2D) != null
			and (current_scene.get("player") as Node2D).global_position.distance_to(want) < 2.0)
