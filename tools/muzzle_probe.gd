extends SceneTree

## A projectile must never be BORN inside a wall (2026-07-29).
##
## Run it after touching a muzzle offset, a projectile collision shape, or a
## body's collision box — the three numbers PartyMember.place_muzzle balances:
##   /Applications/Godot.app/Contents/MacOS/Godot --path . --script tools/muzzle_probe.gd
##
## Asserted as the invariant rather than as "the bolt survives N frames", which
## measures nothing: `queue_free` runs at the end of the frame and a bolt fired
## point-blank at rock is legitimately gone a physics step later either way. The
## thing that broke was the SPAWN — a bolt already overlapping a tile on frame
## zero is freed before it is ever drawn, so the shot is invisible and the ammo
## is spent. So: intersect the projectile's own shape, at its own spawn
## transform, against the wall layer. Empty or it never existed.
##
## BOTH AXES, because the first pass only covered one. Firing INTO the wall is
## the along-the-facing case; firing PAST it — sideways, from a body pressed
## against it — is the across-the-facing case, and it escaped a probe that only
## ever fired north.
##
## Autoloads are reached through /root — a --script tool compiles before they
## register, so naming `Game` or a party class poisons the run.

var _fails := 0


func _initialize() -> void:
	Engine.max_fps = 60
	_run()


func _ok(cond: bool, what: String) -> void:
	if cond:
		print("  ok   ", what)
	else:
		_fails += 1
		print("  FAIL ", what)


func _frames(n: int) -> void:
	for i in n:
		await process_frame


func _newest(world: Node, kind: String) -> Node2D:
	var found: Node2D = null
	for c in world.get_children():
		var s: Script = c.get_script()
		if s != null and s.resource_path.ends_with(kind):
			found = c
	return found


func _who(members: Array, id: String) -> Node2D:
	for m in members:
		if String(m.member_id) == id:
			return m
	return null


func _fire_at(who: Node2D, world: Node, spawn: String, kind: String,
		clearance: float, face_y: float, face: Vector2) -> void:
	# origin placed so the body's box top (origin+2) sits `clearance` px south
	# of the face's bottom edge
	who.global_position = Vector2(20 * 16 + 8, face_y + clearance - 2.0)
	who.velocity = Vector2.ZERO
	who.facing = face
	await _frames(4)
	who.call(spawn)
	var shot := _newest(world, kind)
	if shot == null:
		_ok(false, "%s spawned at all at %dpx" % [kind, int(clearance)])
		return
	# The projectile's own collider, at the transform it was just handed.
	var query := PhysicsShapeQueryParameters2D.new()
	var col: CollisionShape2D = shot.get_node("CollisionShape2D")
	query.shape = col.shape
	query.transform = shot.global_transform * col.transform
	query.collision_mask = 1                     # walls only
	var stuck := shot.get_world_2d().direct_space_state.intersect_shape(query, 1)
	var where := "INTO the wall" if face == Vector2.UP else "PAST the wall"
	if face != Vector2.UP or clearance >= 12.0:
		# Sideways there is ALWAYS a free lane — place_muzzle slides the shot off
		# the barrel line to find it — so this holds at every clearance.
		_ok(stuck.is_empty(),
			"%s fired %s is born clear at %dpx of clearance"
			% [kind, where, int(clearance)])
	else:
		# Flush and firing INTO it: the body's own origin is inside the solid
		# cell and the wall spans the whole lane, so there is no legal muzzle in
		# any direction. Asserted so the limit stays a KNOWN one — if this ever
		# starts passing, the collision box moved and place_muzzle's arithmetic
		# needs re-deriving.
		_ok(not stuck.is_empty(),
			"%s fired %s has nowhere to go at %dpx (flush, by geometry)"
			% [kind, where, int(clearance)])
	await _frames(6)


func _run() -> void:
	var game := root.get_node("Game")
	var party := root.get_node("Party")
	game.call("set_flag", "ebb_done")
	for f in ["fuji_darts_made", "fuji_tome_taken", "fuji_kit_made"]:
		game.call("set_flag", f)
	change_scene_to_file("res://scene/lanternwood.tscn")
	await _frames(24)
	var world: Node = current_scene.get_node("World")
	var members: Array = party.get("members")

	# BAND D (rows 41-42) is the cliff just north of the gate lane; its south
	# face ends at the top of row 43, y = 688. Fire NORTH into it from four
	# clearances — 2px is pressed against the rock, 40px is comfortably clear.
	# Fired straight on the bodies — place_muzzle knows nothing about leadership,
	# and swapping the lead here would only add a camera handover.
	for who_id in ["basil", "fuji"]:
		var spawn := "_spawn_bolt" if who_id == "basil" else "_spawn_dart"
		var kind := "laser_bolt.gd" if who_id == "basil" else "blow_dart.gd"
		for face in [Vector2.UP, Vector2.RIGHT, Vector2.LEFT]:
			print("%s, %s:" % [who_id, "into" if face == Vector2.UP else "past"])
			for c in [2.0, 4.0, 12.0, 22.0, 40.0]:
				await _fire_at(_who(members, who_id), world, spawn, kind,
						c, 688.0, face)

	print("muzzle_probe: ", "PASS" if _fails == 0 else "%d FAILED" % _fails)
	quit(1 if _fails else 0)
