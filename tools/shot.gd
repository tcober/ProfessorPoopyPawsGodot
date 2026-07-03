extends SceneTree

## Screenshot tool for eyeballing scenes at game zoom. Must run WINDOWED (not
## --headless: the dummy rasterizer renders black on GL Compatibility).
##
##   /Applications/Godot.app/Contents/MacOS/Godot --path . \
##       --script tools/shot.gd -- res://scene/test_room.tscn /tmp/shot.png [frames]


func _initialize() -> void:
	_run()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 2:
		push_error("usage: -- <scene.tscn> <out.png> [frames]")
		quit(1)
		return
	var wait := 30 if args.size() < 3 else int(args[2])
	await process_frame
	change_scene_to_file(args[0])
	for i in wait:
		await process_frame
	var img := root.get_viewport().get_texture().get_image()
	img.save_png(args[1])
	print("shot saved: ", args[1])
	quit()
