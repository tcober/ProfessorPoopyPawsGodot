extends SceneTree

## Round-trip probe for the save system.
##
## The characteristic save bug is not a crash, it is SILENT LOSS: a field added
## to Game and forgotten in the serializer, so a save loads looking fine and is
## quietly missing your hat. So this builds a run with something in every single
## field a save is supposed to carry, writes it, wipes the session down to a
## fresh boot, reads it back, and compares field by field.
##
## It also asserts the two refusals, which matter more than the happy path:
## a version mismatch must be REFUSED rather than half-applied, and loading over
## a session in progress must not OR the two runs together.
##
## Must run WINDOWED (the GL Compatibility renderer draws black headless):
##   /Applications/Godot.app/Contents/MacOS/Godot --path . --script tools/save_probe.gd

var _fails := 0
var game: Node
var party: Node


func _initialize() -> void:
	_run()


func _check(label: String, cond: bool) -> void:
	print(("  ok    " if cond else "  FAIL  ") + label)
	if not cond:
		_fails += 1


func _wait_frames(n: int) -> void:
	for i in n:
		await process_frame


func _run() -> void:
	await process_frame
	Engine.max_fps = 60
	game = root.get_node("Game")
	party = root.get_node("Party")
	print("save probe:")

	SaveGame.delete()
	_check("no save to begin with", not SaveGame.has_save())
	_check("peek on an empty slot is empty", SaveGame.peek().is_empty())
	_check("loading nothing returns no scene", SaveGame.load_into(self) == "")

	# ---- build a run with something in EVERY field a save carries
	game.call("reset_story")
	party.call("set_roster", [&"basil", &"fuji"] as Array[StringName], &"fuji")
	change_scene_to_file("res://scene/meadow.tscn")
	await _wait_frames(20)

	game.call("set_flag", "ebb_done")
	game.call("set_flag", "thesis_found")
	game.set("overworld_spawn", "lanternwood")
	game.set("fuji_tome", &"bound_ledger")
	var sheet = game.call("sheet", &"fuji")
	sheet.level = 6
	sheet.exp_total = StatBlock.exp_at(6) + 11
	StatBlock.apply_growth(sheet)
	sheet.equip(Item.Kind.WEAPON, &"bound_ledger")
	sheet.equip(Item.Kind.HEAD, &"earflaps")
	game.call("add_item", &"tonic", 3)
	game.call("add_item", &"oilskin", 1)
	game.set("loaded", Alchemy.make(Compound.Kind.PLASMA))
	game.set("spares", [Alchemy.make(Compound.Kind.FROST)] as Array[Compound])
	game.set("ammo_left", 2)

	_check("the save wrote", SaveGame.save(self))
	_check("...and the file is there", SaveGame.has_save())
	_check("the summary names where and who",
		SaveGame.summary().contains("FUJI") and SaveGame.summary().contains("6"))

	# ---- wipe the session to a fresh boot, then read it back
	game.call("reset_story")
	party.call("set_roster", [&"basil"] as Array[StringName], &"basil")
	_check("the wipe took", game.call("sheet", &"fuji").level == 1
		and game.call("item_count", &"tonic") == 0)

	var scene := SaveGame.load_into(self)
	_check("load returned the saved scene", scene.ends_with("meadow.tscn"))

	# ---- field by field
	_check("flags came back", game.call("flag", "ebb_done")
		and game.call("flag", "thesis_found"))
	_check("routers came back", game.get("overworld_spawn") == "lanternwood")
	_check("fuji_tome came back", game.get("fuji_tome") == &"bound_ledger")

	var back = game.call("sheet", &"fuji")
	_check("level came back", back.level == 6)
	_check("banked EXP came back", back.exp_total == StatBlock.exp_at(6) + 11)
	_check("growth was re-derived for the level", back.base["vit"] > 0)
	_check("the weapon came back",
		back.equipped(Item.Kind.WEAPON) != null
			and back.equipped(Item.Kind.WEAPON).id == &"bound_ledger")
	_check("the hat came back",
		back.equipped(Item.Kind.HEAD) != null
			and back.equipped(Item.Kind.HEAD).id == &"earflaps")
	_check("an empty slot stayed empty", back.equipped(Item.Kind.BODY) == null)
	_check("gear still moves the totals", back.stat("mig") > back.base["mig"])

	_check("stacked items came back with their count",
		game.call("item_count", &"tonic") == 3)
	_check("single items came back", game.call("item_count", &"oilskin") == 1)

	var loaded = game.get("loaded")
	_check("the loaded compound came back",
		loaded != null and loaded.kind == Compound.Kind.PLASMA)
	_check("...rebuilt from its KIND, so its stats are current",
		loaded != null and loaded.damage == Alchemy.make(Compound.Kind.PLASMA).damage)
	_check("spares came back", game.get("spares").size() == 1
		and game.get("spares")[0].kind == Compound.Kind.FROST)
	_check("ammo came back", game.get("ammo_left") == 2)

	_check("the roster came back", party.get("roster").size() == 2)
	_check("...and who was leading", party.get("leader_id") == &"fuji")

	# ---- the refusals
	# A load must START from a clean run: without the reset inside load_into, a
	# flag from the abandoned session survives into the loaded one.
	game.call("set_flag", "a_flag_from_the_abandoned_run")
	SaveGame.load_into(self)
	_check("loading over a live session does not OR the two together",
		not game.call("flag", "a_flag_from_the_abandoned_run"))

	# A save from another version is refused whole, never half-applied.
	var f := FileAccess.open(SaveGame.SAVE_PATH, FileAccess.READ)
	var raw := f.get_as_text()
	f.close()
	var bumped := raw.replace('"version": %d' % SaveGame.VERSION,
		'"version": %d' % (SaveGame.VERSION + 99))
	f = FileAccess.open(SaveGame.SAVE_PATH, FileAccess.WRITE)
	f.store_string(bumped)
	f.close()
	_check("a foreign version is refused, not half-read", SaveGame.peek().is_empty())
	_check("...and load reports nothing rather than a broken run",
		SaveGame.load_into(self) == "")

	# Garbage in the slot must not throw.
	f = FileAccess.open(SaveGame.SAVE_PATH, FileAccess.WRITE)
	f.store_string("{ this is not json ")
	f.close()
	_check("unparseable save is refused quietly", SaveGame.peek().is_empty())

	SaveGame.delete()
	_check("delete removes the slot", not SaveGame.has_save())

	print("save probe: %s" % ("ALL PASS" if _fails == 0 else "%d FAILED" % _fails))
	quit(1 if _fails > 0 else 0)
