extends SceneTree

## Screenshot tool for eyeballing scenes at game zoom. Must run WINDOWED (not
## --headless: the dummy rasterizer renders black on GL Compatibility).
##
##   /Applications/Godot.app/Contents/MacOS/Godot --path . \
##       --script tools/shot.gd -- res://scene/meadow.tscn /tmp/shot.png \
##       [frames] [action:pressFrame:releaseFrame ...]
##
## The optional action args synthesize input mid-run (e.g. move_up:20:45
## interact:60:62) so interactive beats can be screenshot end-to-end.


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
	for i in range(3, args.size()):
		var p := args[i].split(":")
		presses.append([p[0], int(p[1]), int(p[2]) if p.size() > 2 else int(p[1]) + 1])
	await process_frame
	change_scene_to_file(args[0])
	for i in wait:
		for pr in presses:
			if i == pr[1]:
				Input.action_press(pr[0])
			elif i == pr[2]:
				Input.action_release(pr[0])
		await process_frame
	var img := root.get_viewport().get_texture().get_image()
	img.save_png(args[1])
	print("shot saved: ", args[1])
	quit()
