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
	await process_frame
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
	print("PROBE ", "PASS" if ok else "FAIL")
	quit(0 if ok else 1)
