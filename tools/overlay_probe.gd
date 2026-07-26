extends SceneTree

## Proves the MODAL CONTRACT that scene/overlay.gd now owns: DevMenu and MixMenu
## must each refuse to open while the other is up. That guard used to exist only
## on MixMenu's side, so `0` opened the chapter selector straight over an open
## mixing bench and closing it unpaused the tree underneath (2026-07-25 sweep).
##
## Worth its own tool because the failure is SILENT in the shape that matters:
## Overlay.any_open() resolves the autoloads by NAME, and a lookup that returned
## null would make the guard vacuously false — the menus would still open, still
## look right, and still corrupt each other. So this asserts BOTH directions and
## asserts the lookup really found the nodes.

var _fails := 0


func check(label: String, ok: bool, detail := "") -> void:
	print("  %s  %s%s" % ["ok  " if ok else "FAIL", label,
			"" if ok or detail.is_empty() else "  <- " + detail])
	if not ok:
		_fails += 1


func _initialize() -> void:
	root.set_process_mode(Node.PROCESS_MODE_ALWAYS)
	_run.call_deferred()


func _run() -> void:
	await process_frame
	print("overlay probe:")

	# 1. the lookup itself — everything below is meaningless if this is null
	var dev := root.get_node_or_null(NodePath(&"DevMenu"))
	var mix := root.get_node_or_null(NodePath(&"MixMenu"))
	check("Overlay's autoload lookup finds DevMenu", dev != null)
	check("Overlay's autoload lookup finds MixMenu", mix != null)
	if dev == null or mix == null:
		return _finish()

	check("nothing open to start with", not Overlay.any_open(self))

	# 2. bench up -> the chapter selector must refuse
	mix._open()
	check("the bench reports itself open", Overlay.any_open(self))
	check("...and DevMenu sees it (0 would refuse)",
			Overlay.any_open(self, dev))
	check("...while the bench does not count ITSELF",
			not Overlay.any_open(self, mix))
	check("the bench paused the tree", paused)
	mix._close()

	# 3. and the mirror: selector up -> the bench must refuse
	dev._open()
	check("the selector reports itself open", Overlay.any_open(self))
	check("...and MixMenu sees it (M would refuse)",
			Overlay.any_open(self, mix))
	check("...while the selector does not count ITSELF",
			not Overlay.any_open(self, dev))
	dev._close()
	check("closing the selector unpaused the tree", not paused)

	_finish()


func _finish() -> void:
	print("overlay probe: %s" % ["ALL PASS" if _fails == 0 else "%d FAILED" % _fails])
	quit(1 if _fails else 0)
