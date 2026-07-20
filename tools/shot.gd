extends SceneTree

## Screenshot tool for eyeballing scenes at game zoom. Must run WINDOWED (not
## --headless: the dummy rasterizer renders black on GL Compatibility).
##
##   /Applications/Godot.app/Contents/MacOS/Godot --path . \
##       --script tools/shot.gd -- res://scene/meadow.tscn /tmp/shot.png \
##       [frames] [phase:<name>] [bphase:<name>] [roster:<id>[:<id>...]] \
##       [flag:<name> ...] [pos:<x>:<y>] [action:pressFrame:releaseFrame ...]
##
## The optional action args synthesize input mid-run (e.g. move_up:20:45
## interact:60:62) so interactive beats can be screenshot end-to-end.
## phase:<name> sets Game.town_thesis_phase before the scene loads (the only
## way to shoot town_thesis's dash/call/fountain dressings); roster:<ids>
## swaps the party first (story scenes assume e.g. the solo basil_student —
## the boot default is the adult pair); flag:<name> pre-sets story flags so
## staged states (the hidden goose, the open gate) can be shot directly;
## pos:<x>:<y> teleports the leader right after load (the camera follows).


func _initialize() -> void:
	_run()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 2:
		push_error("usage: -- <scene.tscn> <out.png> [frames] [action:press:release ...]")
		quit(1)
		return
	var wait := 30 if args.size() < 3 else int(args[2])
	var presses: Array = []
	var phase := ""
	var bphase := ""
	var roster: Array[StringName] = []
	var flags: Array[String] = []
	var pos := Vector2.INF
	for i in range(3, args.size()):
		var p := args[i].split(":")
		if p[0] == "phase":
			phase = p[1]
			continue
		if p[0] == "bphase":             # the bluff's phase router
			bphase = p[1]
			continue
		if p[0] == "roster":
			for id in p.slice(1):
				roster.append(StringName(id))
			continue
		if p[0] == "flag":               # pre-set a story flag (staged states)
			flags.append(p[1])
			continue
		if p[0] == "pos":                # teleport the leader after load
			pos = Vector2(float(p[1]), float(p[2]))
			continue
		presses.append([p[0], int(p[1]), int(p[2]) if p.size() > 2 else int(p[1]) + 1])
	await process_frame
	# an occluded macOS window runs UNCAPPED — pin 60fps so the frame arg
	# and press frames track wall-clock (the cutscene timers' clock)
	Engine.max_fps = 60
	# runtime lookups, not autoload identifiers — --script runs compile this
	# file before autoloads register
	if phase != "":
		root.get_node("Game").set("town_thesis_phase", phase)
	if bphase != "":
		root.get_node("Game").set("bluff_phase", bphase)
	for f in flags:
		root.get_node("Game").call("set_flag", f)
	if not roster.is_empty():
		root.get_node("Party").call("set_roster", roster)
	change_scene_to_file(args[0])
	if pos != Vector2.INF:
		for i in 5:
			await process_frame
		var players := get_nodes_in_group("player")
		if players.size() > 0:
			(players[0] as Node2D).global_position = pos
	for i in wait:
		for pr in presses:
			if i == pr[1]:
				Input.action_press(pr[0])
			elif i == pr[2]:
				Input.action_release(pr[0])
		await process_frame
	# macOS suspends drawing for occluded windows — the framebuffer goes
	# stale and get_image() returns an old frame. Force a fresh draw.
	RenderingServer.force_draw()
	var img := root.get_viewport().get_texture().get_image()
	img.save_png(args[1])
	print("shot saved: ", args[1])
	quit()
