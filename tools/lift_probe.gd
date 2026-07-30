extends SceneTree

## THE DINGHY LIFT — Alembic Town's one machine, and the one place the two
## walkable storeys are joined by CODE rather than by authoring (the shaft is
## SOLID; see TileScene.assert_lift for why a walkable shaft is not an option).
## Everything the build-time asserts CANNOT see is checked here: that the ride
## actually crosses strata in both directions, that it carries the follower, that
## it does not re-fire under the body it just deposited, and that it refuses out
## loud instead of silently when the scene is busy.
##
##   /Applications/Godot.app/Contents/MacOS/Godot --path . \
##       --script tools/lift_probe.gd
##
## Duck-typed throughout: a --script probe that names the Player class drags
## player.gd into the tool's own compile, before autoloads register.

var _fails: Array[String] = []


func _initialize() -> void:
	_run()


func _check(label: String, cond: bool, detail := "") -> void:
	if cond:
		print("  ok    ", label)
	else:
		print("  FAIL  ", label, "  ", detail)
		_fails.append(label)


func _run() -> void:
	# An occluded macOS window runs UNCAPPED, and the ride is a 1.1s wall-clock
	# tween measured here in frames. Pin the rate or the budgets mean nothing.
	Engine.max_fps = 60
	await process_frame
	change_scene_to_file("res://scene/alembic_town.tscn")
	# TravelScene holds ENTRY_LOCK (0.8s) before its zones deliver anything —
	# a teleport inside that window fires body_entered and has it swallowed,
	# and Godot never re-fires an entry. Wait the lock out first.
	for i in 90:
		await process_frame
	var party := root.get_node("Party")
	var scene := current_scene
	var map: Dictionary = scene.map
	var up_px: Vector2 = MapData.anchor_px(map, "lift_up")
	var down_px: Vector2 = MapData.anchor_px(map, "lift_down")
	_check("lift_up stands on the forest floor",
			MapData.stratum_at_px(map, up_px) == "ground")
	_check("lift_down stands on the canopy",
			MapData.stratum_at_px(map, down_px) == "canopy")

	# ---- UP: the plaza landing -> the boardwalk ------------------------------
	party.place(up_px)
	var leader: Node2D = party.leader
	var follower: Node2D = null
	for m in party.members:
		if m != leader:
			follower = m
	await _settle(120)
	_check("the ride up crosses to the canopy",
			MapData.stratum_at_px(map, leader.global_position) == "canopy",
			str(leader.global_position))
	_check("the ride up carries the follower",
			MapData.stratum_at_px(map, follower.global_position) == "canopy",
			str(follower.global_position))
	# R33 — an arrival must not re-fire the zone it lands in. It lands ON the
	# destination anchor (the door convention), so what has to hold is that the
	# latch resynced from the real overlaps keeps it shut until the body leaves.
	var landed := leader.global_position
	await _settle(150)
	_check("standing at the top does not ride again",
			leader.global_position.distance_to(landed) < 4.0,
			"drifted to " + str(leader.global_position))

	# ---- DOWN: the boardwalk -> the plaza landing ----------------------------
	# step OFF the landing first, so body_exited re-arms it — riding back from a
	# body that never left is not a case the game can produce.
	party.place(down_px + Vector2(-48.0, 0.0))
	await _settle(20)
	party.place(down_px)
	await _settle(120)
	_check("the ride down crosses to the forest floor",
			MapData.stratum_at_px(map, leader.global_position) == "ground",
			str(leader.global_position))

	# ---- R34: it must REFUSE OUT LOUD, never silently ------------------------
	# A machine that does nothing reads as broken, so a step onto a landing while
	# the scene is busy owes the player a line. Force _busy and step on.
	# Step OFF first for the same reason as above: the ride down deposited the body
	# ON this landing, and a zone the body never left has no entry left to refuse.
	party.place(up_px + Vector2(-48.0, 0.0))
	await _settle(20)
	scene.set("_busy", true)
	party.place(up_px)
	await _settle(90)
	_check("a busy scene refuses the ride",
			MapData.stratum_at_px(map, leader.global_position) == "ground",
			str(leader.global_position))
	var hint: Label = null
	for c in scene.get_node("Theater").get_children():
		if c is Label and (c as Label).text.contains("HOIST"):
			hint = c
	_check("...and says so", hint != null and hint.modulate.a > 0.0)
	scene.set("_busy", false)

	print()
	if _fails.is_empty():
		print("== lift probe PASS ==")
		quit()
		return
	print("== %d check(s) FAILED ==" % _fails.size())
	quit(1)


func _settle(frames: int) -> void:
	for i in frames:
		await physics_frame
