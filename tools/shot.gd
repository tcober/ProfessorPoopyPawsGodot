extends SceneTree

## Screenshot tool for eyeballing scenes at game zoom. Must run WINDOWED (not
## --headless: the dummy rasterizer renders black on GL Compatibility).
##
##   /Applications/Godot.app/Contents/MacOS/Godot --path . \
##       --script tools/shot.gd -- res://scene/meadow.tscn /tmp/shot.png \
##       [frames] [phase:<name>] [bphase:<name>] [roster:<id>[:<id>...]] \
##       [flag:<name> ...] [pos:<x>:<y>] [action:pressFrame:releaseFrame ...]
##
## beat:<n> stages a whole story beat from scene/chapters.gd — the same table
## the in-game chapter selector (0) reads — scene, roster, routers and flags in
## one arg, which is the only way to shoot the beats needing town_spawn /
## interior_spawn / library_phase (none of which has an arg of its own). It can
## stand in for the scene argument, since the table names the scene:
##
##       --script tools/shot.gd -- beat:14 /tmp/kiss.png 90
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
	var beat := -1
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
		if p[0] == "beat":               # stage a whole beat from the table
			beat = int(p[1])
			continue
		# NOTE: anything unrecognized falls through as an input action, so a new
		# key: arg MUST be dispatched above or it is silently eaten as a press
		presses.append([p[0], int(p[1]), int(p[2]) if p.size() > 2 else int(p[1]) + 1])
	var scene_path := args[0]
	if beat < 0 and scene_path.begins_with("beat:"):
		beat = int(scene_path.split(":")[1])
	await process_frame
	# an occluded macOS window runs UNCAPPED — pin 60fps so the frame arg
	# and press frames track wall-clock (the cutscene timers' clock)
	Engine.max_fps = 60
	# runtime lookups, not autoload identifiers — --script runs compile this
	# file before autoloads register
	if beat >= 0:
		# scene/chapters.gd is deliberately autoload-free so it can be load()ed
		# here; it is the same table the in-game chapter selector reads
		var table: GDScript = load("res://scene/chapters.gd")
		var b: Dictionary = table.BEATS[beat]
		scene_path = b["scene"]
		root.get_node("Game").call("reset_story")
		for f: String in b["flags"]:
			root.get_node("Game").call("set_flag", f)
		for k: String in b["state"]:
			root.get_node("Game").set(k, b["state"][k])
		root.get_node("Party").call("set_roster", b["roster"], b["lead"])
		print("beat ", beat, ": ", b["name"], " -> ", scene_path)
	# the individual args below still win, so a beat can be shot with one knob
	# nudged (e.g. beat:14 bphase:call1)
	if phase != "":
		root.get_node("Game").set("town_thesis_phase", phase)
	if bphase != "":
		root.get_node("Game").set("bluff_phase", bphase)
	for f in flags:
		root.get_node("Game").call("set_flag", f)
	if not roster.is_empty():
		root.get_node("Party").call("set_roster", roster)
	change_scene_to_file(scene_path)
	for i in wait:
		# pos: HOLD the leader at the target through the whole wait — a
		# scene's own _place_player runs after its entry fade and used to
		# stomp a one-shot frame-5 teleport back onto the spawn marker
		if pos != Vector2.INF and i >= 5:
			# zone scenes: the leader rides the "player" group; the OVERWORLD
			# chibi has no group (markers gate on identity there) — fall back
			# to the scene's own `player` reference
			var players := get_nodes_in_group("player")
			var body := players[0] as Node2D if players.size() > 0 \
					else current_scene.get("player") as Node2D
			if body != null:
				body.global_position = pos
				if i == 10:              # one clean camera snap, no glide
					for c in body.get_children():
						if c is Camera2D:
							(c as Camera2D).reset_smoothing()
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
