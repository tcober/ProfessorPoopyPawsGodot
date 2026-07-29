extends SceneTree

## Behavioral probe for Act 1 beat 3, "THE DEFENCE OF LANTERNWOOD" — the first
## real fight in the game, and the first place the RPG layer is load-bearing in
## a story scene rather than in the sandbox meadow.
##
## Asserts:
##   1. the beat stages solo Fuji into the terraced Ebb-night street,
##   2. she arrives ARMED (the kit flags are on the beat, not assumed),
##   3. three enemies spawn, on real map anchors, and a HUD comes with them,
##   4. the SECOND kill levels her — the whole fight is tuned around that,
##   5. clearing the lanes sets `town_defended` and leaves a tonic in the snow,
##   6. walking over the tonic puts it in the party-wide satchel,
##   7. re-entering a defended town does NOT restage the fight.
##
## Staged BY NAME out of chapters.gd, never by index (recital_probe's rule):
## chapters.gd is the single source of truth for the flag ladders, and inserting
## one row shifts every hard-coded `beat:<n>` in the repo.
##
## Must run WINDOWED (the GL Compatibility renderer draws black headless):
##   /Applications/Godot.app/Contents/MacOS/Godot --path . --script tools/defence_probe.gd

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


## Apply a chapters.gd beat exactly as dev_menu._launch does, looked up by name.
func _stage(beat_name: String) -> void:
	var table: GDScript = load("res://scene/chapters.gd")
	for b: Dictionary in table.BEATS:
		if b.get("name", "") != beat_name:
			continue
		game.call("reset_story")
		for f: String in b["flags"]:
			game.call("set_flag", f)
		for k: String in b["state"]:
			game.set(k, b["state"][k])
		party.call("set_roster", b["roster"], b["lead"])
		change_scene_to_file(b["scene"])
		return
	_check("beat exists in chapters.gd: " + beat_name, false)


func _enemies() -> Array:
	return get_nodes_in_group("enemies")


func _run() -> void:
	await process_frame
	Engine.max_fps = 60
	game = root.get_node("Game")
	party = root.get_node("Party")
	var map: Dictionary = MapData.load_map("res://assets/maps/lanternwood.txt")

	print("defence probe:")
	await _test_kit(MapData.load_map("res://assets/maps/library.txt"))

	await _stage("THE DEFENCE OF LANTERNWOOD")
	await _wait_frames(30)

	# --- 1/2. the staging
	_check("lanternwood loaded", current_scene.scene_file_path.ends_with("lanternwood.tscn"))
	_check("solo Fuji leads", party.roster.size() == 1 and party.leader_id == &"fuji")
	var fuji: Node2D = party.leader
	_check("she arrives with her tome", fuji.armed_tome())
	_check("she arrives with her darts", fuji.armed_darts())

	# --- 3. the field
	var foes := _enemies()
	_check("three enemies in the lanes (got %d)" % foes.size(), foes.size() == 3)
	_check("a HUD came with the fight",
		current_scene.get_node_or_null("HUD") != null
			or current_scene.find_child("HUD", false, false) != null)
	# Spawned on real anchors, not adrift: a slime on the wrong terrace aims its
	# 90px detect_range at a cliff face and the beat never resolves.
	var anchored := 0
	for f in foes:
		for a in ["slime_a", "slime_b", "slime_c"]:
			if (f as Node2D).position.distance_to(MapData.anchor_px(map, a)) < 2.0:
				anchored += 1
	_check("every enemy sits on its map anchor (%d/3)" % anchored, anchored == 3)
	_check("one of them is a bruiser",
		foes.any(func(f): return f.get("exp_value") == 30))

	# --- 3b. the gate is HELD while the lanes are full (2026-07-29). The fight
	# is staged a few cells from the south gate, so knockback plus a backpedal
	# used to end it on the overworld by accident, dropping the set-piece. Walk
	# her onto the exit and assert she is still in town.
	fuji.global_position = MapData.anchor_px(map, "exit_south")
	fuji.velocity = Vector2.ZERO
	await _wait_frames(12)
	_check("the gate refuses while something is in the lanes",
		current_scene.scene_file_path.ends_with("lanternwood.tscn"))
	# ...and off it again, or `body_entered` never re-fires when it reopens.
	fuji.global_position = MapData.anchor_px(map, "player_start")
	await _wait_frames(6)

	# --- 4. the second kill levels her
	var sheet = game.call("sheet", &"fuji")
	_check("she starts at level 1", sheet.level == 1)
	_kill(foes[0])
	await _wait_frames(4)
	_check("still level 1 after ONE kill", game.call("sheet", &"fuji").level == 1)
	_kill(foes[2])                                   # the other small one
	await _wait_frames(4)
	_check("LEVEL 2 on the second kill", game.call("sheet", &"fuji").level == 2)

	# --- 5. clearing the lanes
	_check("not yet defended", not game.call("flag", "town_defended"))
	_kill(foes[1])
	await _wait_frames(20)
	_check("town_defended once the lanes are clear", game.call("flag", "town_defended"))
	var drop: Node = null
	for n in current_scene.get_node("World").get_children():
		if n.get("item_id") != null:
			drop = n
	_check("a tonic is left in the snow", drop != null)

	# --- 6. picking it up
	if drop:
		_check("the satchel is empty before the walk-over",
			game.call("item_count", &"tonic") == 0)
		fuji.global_position = (drop as Node2D).global_position
		fuji.velocity = Vector2.ZERO
		await _wait_frames(12)
		_check("walking over it fills the satchel",
			game.call("item_count", &"tonic") >= 1)

	# --- 6b. ...and the gate opens again once they are. The refusal above is
	# only safe if it lifts, and it lifts on a marker that fires ONCE per entry
	# — hence the step-off above.
	fuji.global_position = MapData.anchor_px(map, "exit_south")
	fuji.velocity = Vector2.ZERO
	await _wait_frames(40)
	_check("the gate opens once the lanes are clear",
		current_scene.scene_file_path.ends_with("overworld.tscn"))

	# --- 7. a defended town stays quiet
	game.set("town_spawn", "")
	change_scene_to_file("res://scene/lanternwood.tscn")
	await _wait_frames(30)
	_check("re-entering a defended town spawns no new fight", _enemies().is_empty())

	print("defence probe: %s" % ("ALL PASS" if _fails == 0 else "%d FAILED" % _fails))
	quit(1 if _fails > 0 else 0)


# ---- the kit night (Act 1 beat 3a), the leg that ARMS her ---------------------------
# Without this the only way to arm Fuji is the dev menu, so the chain has to be
# proven completable: dose -> wand (TWO visits) -> a book, in the room's own
# furniture, ending on the flag the street reads.

var _last_press := 0


func _party_free() -> bool:
	var p: Node2D = party.leader
	return p != null and is_instance_valid(p) and p.is_physics_processing()


## Advance dialog by pressing attack every 250ms (past DialogBox's swallow
## window) until pred() holds or the budget dies. library_probe's helper.
func _mash_until(pred: Callable, max_frames: int) -> bool:
	for i in max_frames:
		if pred.call():
			Input.action_release("attack")
			return true
		var now := Time.get_ticks_msec()
		if now - _last_press > 250:
			_last_press = now
			Input.action_press("attack")
		elif now - _last_press > 120:
			Input.action_release("attack")
		await process_frame
	Input.action_release("attack")
	return false


## Park on a zone and interact. The DOUBLE PARK is not paranoia: `_mash_until`
## advances with ATTACK, and the press that lands on the frame control comes
## back is a real attack — an ARMED Fuji lunges out of the zone before the
## interact fires. She is unarmed for most of this leg and armed by the end of
## it, so the leg needs the dance either way.
func _interact_at(pos: Vector2) -> bool:
	await _wait_frames(20)
	var p: Node2D = party.leader
	p.velocity = Vector2.ZERO
	p.global_position = pos
	await _wait_frames(8)
	p.velocity = Vector2.ZERO
	p.global_position = pos
	await _wait_frames(10)
	Input.action_press("interact")
	await _wait_frames(4)
	Input.action_release("interact")
	await _wait_frames(20)
	var locked := not _party_free()
	var done: bool = await _mash_until(_party_free, 9000)
	# `locked` guards the false pass: without it _party_free is true from frame
	# one and every check below would pass for free.
	return locked and done


func _test_kit(lib: Dictionary) -> void:
	await _stage("THE KIT")
	await _wait_frames(30)
	await _mash_until(_party_free, 9000)
	_check("the library opened on the kit night",
		current_scene.scene_file_path.ends_with("library.tscn"))
	_check("she starts UNARMED", not party.leader.armed_tome()
		and not party.leader.armed_darts())

	# The book refuses before the dose — the beat has an order.
	await _interact_at(MapData.anchor_px(lib, "stack_b"))
	_check("no book before the dose", not game.call("flag", "fuji_tome_taken"))

	await _interact_at(MapData.anchor_px(lib, "stack_a"))
	_check("shelf three gives the dose", game.call("flag", "fuji_dose_found"))

	# The counter is the coffee counter in every phase but this one.
	var counter := MapData.bbox_rect(lib, "cC")
	var at := Vector2(counter.get_center().x, counter.end.y + 8.0)
	await _interact_at(at)
	_check("one visit does NOT finish the wand", not game.call("flag", "fuji_darts_made"))
	await _interact_at(at)
	_check("the second visit bores it out", game.call("flag", "fuji_darts_made"))
	_check("...and the darts are live", party.leader.armed_darts())

	# The first shelf she reaches for is the one she puts back.
	await _interact_at(MapData.anchor_px(lib, "stack_c"))
	_check("she puts the first one back", not game.call("flag", "fuji_tome_taken"))
	await _interact_at(MapData.anchor_px(lib, "stack_c"))
	_check("the second reach takes the book", game.call("flag", "fuji_tome_taken"))
	_check("...and the tome is live", party.leader.armed_tome())
	_check("the book she chose is remembered", game.get("fuji_tome") != &"")
	_check("...and it is in her WEAPON slot",
		game.call("sheet", &"fuji").equipped(Item.Kind.WEAPON) != null)
	_check("the kit is complete", game.call("flag", "fuji_kit_made"))


## Kill through HealthComponent rather than a synthetic hit: what is under test
## here is the beat's bookkeeping (EXP, the counter, the drop), not the damage
## pipeline, which rpg_probe already covers end to end.
func _kill(enemy: Node) -> void:
	var health = enemy.get_node("HealthComponent")
	health.take_damage(health.current_health)
