extends SceneTree

## One-shot probe for the town's home-arrival placement: runs the REAL flow —
## boots the downstairs, walks out the front door, and prints party member
## positions after THE BOUGHS load (since the 2026-08-23 split the front door
## opens onto the canopy scene, not the floor town).
##
##   /Applications/Godot.app/Contents/MacOS/Godot --headless --path . \
##       --script tools/town_probe.gd


func _initialize() -> void:
	_run()


func _run() -> void:
	# An OCCLUDED macOS window runs UNCAPPED (~2000fps). This probe budgets in
	# FRAMES — 90 frames of held input, a 4000-frame timeout — while the body
	# it is driving moves by `delta`, so uncapped the party travels almost no
	# distance before the budget runs out and the walk silently fails. Pin the
	# rate so frame budgets track wall-clock (the same fix prologue_probe and
	# shot.gd carry; this probe never got it, which is what made its results
	# depend on whether the window happened to be visible).
	Engine.max_fps = 60
	await process_frame
	var party := root.get_node("/root/Party")
	change_scene_to_file("res://scene/downstairs.tscn")
	for i in 10:
		await process_frame
	print("downstairs members=",
		  party.members.map(func(m): return "%s %s" % [m.member_id, m.global_position]))
	Input.action_press("move_down")
	var frames := 0
	while current_scene == null or current_scene.name != "AlembicCanopy":
		await process_frame
		frames += 1
		if frames == 90:
			Input.action_release("move_down")
		if frames > 4000:
			print("never reached the boughs")
			quit(1)
			return
	Input.action_release("move_down")
	print("the boughs reached after ", frames, " frames")
	for i in 5:
		await process_frame
		print("f", i, " leader=", party.leader_id, " members=",
			  party.members.map(func(m): return "%s %s" % [m.member_id, m.global_position]))
	for i in 300:
		await process_frame
	print("settled leader=", party.leader_id, " members=",
		  party.members.map(func(m): return "%s %s" % [m.member_id, m.global_position]))
	# walk back up through Basil's door — should land in the downstairs
	Input.action_press("move_up")
	frames = 0
	while current_scene == null or current_scene.name != "Downstairs":
		await process_frame
		frames += 1
		if frames == 120:
			Input.action_release("move_up")
		if frames > 4000:
			print("never returned downstairs; current=",
				  str(current_scene.name) if current_scene else "null")
			quit(1)
			return
	Input.action_release("move_up")
	print("downstairs reached after ", frames, " frames; members=",
		  party.members.map(func(m): return "%s %s" % [m.member_id, m.global_position]))
	quit()
