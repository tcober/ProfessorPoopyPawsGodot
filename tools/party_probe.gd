extends SceneTree

## Behavioral probe for the party AI (the walk-away-from-combat bug class).
## Phase 1: forces the follower into combat with an unkillable slime, drags
## the leader away (RIGHT — open meadow; left hits the west wall in ~0.7s),
## lets the fight end, and checks the settle. Phase 2: strands the follower
## 400px out to exercise the off-screen catch-up teleport. Asserts:
##   1. the brain's mood never flip-flops (a handful of transitions total —
##      boundary jitter would show as dozens),
##   2. the follower never moves more than a stride in one frame while it
##      stays inside the camera view (in-view teleport pop; the designed
##      pop-IN from off-screen arrives from outside the view and is allowed),
##   3. the follower settles back at trailing distance both times.
## Must run WINDOWED (same GL note as tools/shot.gd):
##   /Applications/Godot.app/Contents/MacOS/Godot --path . --script tools/party_probe.gd

const FRAMES := 700
const LEAVE_AT := 120       # leader starts walking away
const STOP_AT := 370        # ...and stops
const CALL_OFF_AT := 480    # slime yanked out of range — fight ends
const SETTLE_CHECK := 560   # phase-1 settle assert + phase-2 stranding
const POP_LIMIT := 16.0     # px per physics frame; sprint is ~3.1


func _initialize() -> void:
	_run()


func _run() -> void:
	# Same hazard town_probe carried: an occluded macOS window runs uncapped,
	# and this probe measures distances a delta-driven body covers over a
	# fixed FRAME budget. Pin the rate or the numbers mean nothing.
	Engine.max_fps = 60
	await process_frame
	# Fuji's kit is flag-gated (Act 1 beat 3 is where she makes it), and this
	# probe runs on the boot roster with Game.flags empty — so without these she
	# is UNARMED here and the probe would quietly certify a follower that never
	# swings. Chapters.KIT_ARMED is the same list the sandbox beats carry.
	for f in ["fuji_darts_made", "fuji_tome_taken", "fuji_kit_made"]:
		root.get_node("Game").call("set_flag", f)
	change_scene_to_file("res://scene/meadow.tscn")
	await process_frame
	await process_frame

	var party := root.get_node("Party")
	var leader: Node2D = party.leader
	var follower: Node2D = null
	for m in party.members:
		if m != leader:
			follower = m
	var brain := follower.get_node("Brain")

	# Pin an effectively unkillable slime onto the follower so ENGAGE holds
	# until the leash — not the slime's death — ends the fight.
	var slime: Node2D = null
	for child in current_scene.get_node("World").get_children():
		if child is Slime:
			slime = child
			break
	var slime_health := slime.get_node("HealthComponent")
	slime_health.max_health = 99999
	slime_health.current_health = 99999
	slime.global_position = follower.global_position + Vector2(40.0, 0.0)

	var moods: Array = [[0, brain._mood]]
	var pops: Array = []
	var prev: Vector2 = follower.global_position
	var prev_visible := true
	var settle_dist := -1.0
	var view_half := MapData.view_size() * 0.5

	for i in FRAMES:
		if i == LEAVE_AT:
			Input.action_press("move_right")
		elif i == STOP_AT:
			Input.action_release("move_right")
		elif i == CALL_OFF_AT:
			slime.global_position += Vector2(2000.0, 0.0)
		elif i == SETTLE_CHECK:
			settle_dist = follower.global_position.distance_to(leader.global_position)
			# Phase 2: strand the follower far out — the off-screen teleport
			# must bring it home without an in-view pop.
			follower.global_position = leader.global_position - Vector2(400.0, 0.0)
			prev = follower.global_position
			prev_visible = false
		await physics_frame
		var cam: Camera2D = follower.get_viewport().get_camera_2d()
		var from_center := (follower.global_position - cam.get_screen_center_position()).abs()
		var visible := from_center.x <= view_half.x and from_center.y <= view_half.y
		var jump := follower.global_position.distance_to(prev)
		if visible and prev_visible and jump > POP_LIMIT:
			pops.append([i, jump])
		prev = follower.global_position
		prev_visible = visible
		if moods[-1][1] != brain._mood:
			moods.append([i, brain._mood])

	var names := ["FOLLOW", "ENGAGE", "RETURN"]
	var trail: Array = []
	for m: Array in moods:
		trail.append("%d:%s" % [m[0], names[m[1]]])
	var final_dist := follower.global_position.distance_to(leader.global_position)
	var engaged := false
	for m: Array in moods:
		if m[1] == 1:
			engaged = true
	print("mood trail: ", ", ".join(trail))
	print("transitions: ", moods.size() - 1, "  (PASS <= 8, flip-flop reads as dozens)")
	print("watched pops > %spx: " % POP_LIMIT, pops.size(), "  ", pops, "  (PASS == 0)")
	print("engaged at all: ", engaged, "  (PASS true)")
	print("phase-1 settle distance: %.1f  (PASS < 60)" % settle_dist)
	print("phase-2 final distance: %.1f  (PASS < 60 — teleport brought it home)" % final_dist)
	var ok := moods.size() - 1 <= 8 and pops.is_empty() and engaged \
			and settle_dist < 60.0 and final_dist < 60.0
	ok = await _phase3_across_a_fascia() and ok
	print("PROBE ", "PASS" if ok else "FAIL")
	quit(0 if ok else 1)


## PHASE 3 — THE LEASH ACROSS THE BOUGHS (rewritten for the 2026-08-23 split).
## The stacked-grid version parked the leader on a ring deck and the follower on
## the forest floor and demanded the catch-up teleport land both on one stratum.
## The split retired cross-strata leashes — each town scene is one storey now —
## but the teleport's real obligation survives up here in a sharper form: the
## canopy's walkable web is four discs and three bridges over THE DROP, so
## however the follower gets home (walking the bridges, or the off-screen warp),
## it must end beside the leader with its feet on DECK — never seated in the
## void beside it, which renders as a body standing on thirty feet of air.
func _phase3_across_a_fascia() -> bool:
	change_scene_to_file("res://scene/alembic_canopy.tscn")
	for i in 20:
		await process_frame
	var party := root.get_node("Party")
	var map: Dictionary = current_scene.map
	var leader: Node2D = party.leader
	var follower: Node2D = null
	for m in party.members:
		if m != leader:
			follower = m
	# THE LEADER ON TREE 4'S RING, THE FOLLOWER ALL THE WAY WEST ON TREE 1'S.
	# One row south of the door anchors — a body parked ON `door4`/`home` fires
	# their zones and change_scene frees every member mid-probe.
	leader.global_position = MapData.anchor_px(map, "door4") + Vector2(0.0, 8.0)
	follower.global_position = MapData.anchor_px(map, "home") + Vector2(0.0, 8.0)
	for c in leader.get_children():
		if c is Camera2D:
			(c as Camera2D).reset_smoothing()
	var start_d := follower.global_position.distance_to(leader.global_position)
	for i in 600:
		await physics_frame
	var dist := follower.global_position.distance_to(leader.global_position)
	var feet := follower.global_position + Vector2(0.0, 6.0)
	var seated := not MapData.is_solid(map,
			Vector2i(int(feet.x / 16.0), int(feet.y / 16.0)))
	print("phase-3 follower dist %.1f -> %.1f, on walkable deck: %s  (PASS < 60, true)"
			% [start_d, dist, seated])
	return start_d > 400.0 and dist < 60.0 and seated
