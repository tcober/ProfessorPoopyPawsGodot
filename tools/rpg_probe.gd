extends SceneTree

## Behavioral probe for the RPG layer: levels, the EXP curve, the five stats,
## the four equipment slots, the satchel, and the stat-driven damage pipeline.
##
## Like status_probe, this drives the REAL meadow with a REAL slime rather than
## unit-testing resources in isolation, because every interesting failure in
## this layer is wiring: a sheet applied after HealthComponent already latched
## its max, a stat multiplier that silently never reaches the hurtbox, a
## reset_story that forgets one of the two new dictionaries.
##
## Asserts:
##   1. the EXP curve's edges — first rung, cap, and exp_at() accumulation,
##   2. grant_exp levels once per rung and can carry several rungs at once,
##   3. growth tables apply, and Basil and Fuji do NOT converge,
##   4. prologue bodies get a NEUTRAL sheet and their max_health is untouched,
##   5. a sheet's VIT reaches the live body's max HP on spawn,
##   6. equip/unequip round-trips through the satchel and moves stat totals,
##   7. MIGHT scales damage OUT and GUARD reduces damage IN, floored at 1,
##   8. a kill grants EXP to EVERY roster member, not just the killer,
##   9. sheets and satchel survive a scene change but NOT reset_story().
##
## Must run WINDOWED (the GL Compatibility renderer draws black headless):
##   /Applications/Godot.app/Contents/MacOS/Godot --path . --script tools/rpg_probe.gd

var _fails: Array[String] = []
var _checks := 0


func _initialize() -> void:
	_run()


func _run() -> void:
	Engine.max_fps = 60          # an occluded macOS window otherwise runs uncapped
	await process_frame

	# The pure-data tests need no scene at all, so they run before the load.
	_test_curve()
	_test_growth()
	_test_neutral_sheets()
	_test_items_table()

	change_scene_to_file("res://scene/meadow.tscn")
	await process_frame
	await process_frame

	# Strip the AI follower for the damage tests: left alive it wanders over and
	# kills the specimen mid-await, and its knockback drags the parked body.
	var party := root.get_node("Party")
	for m in party.members:
		if m != party.leader:
			m.queue_free()
	await process_frame

	await _test_vit_reaches_the_body()
	await _test_equipment()
	await _test_might_and_guard()
	await _test_kill_grants_whole_roster()
	await _test_persistence()

	print("")
	if _fails.is_empty():
		print("rpg_probe: OK (%d checks)" % _checks)
		quit(0)
	else:
		for f in _fails:
			print("FAIL: ", f)
		print("rpg_probe: %d/%d FAILED" % [_fails.size(), _checks])
		quit(1)


# --- helpers --------------------------------------------------------------------------

func _check(ok: bool, what: String) -> void:
	_checks += 1
	if not ok:
		_fails.append(what)


## Autoloads by path, never by identifier: a --script tool compiles before the
## autoloads are registered, so a bare `Game.` would fail to resolve.
func _game() -> Node:
	return root.get_node("Game")


func _leader() -> Node2D:
	return root.get_node("Party").leader


## A fresh slime parked clear of the party, with the HP the caller wants.
func _lone_slime(hp: int) -> Node2D:
	var world: Node2D = current_scene.get_node("World")
	for child in world.get_children():
		if child is Slime:
			child.queue_free()
	await process_frame
	var slime: Node2D = load("res://entities/enemies/slime.tscn").instantiate()
	world.add_child(slime)
	slime.global_position = _leader().global_position + Vector2(240.0, 0.0)
	await process_frame
	await process_frame
	var health = slime.get_node("HealthComponent")
	health.max_health = hp
	health.current_health = hp
	return slime


## Hit a hurtbox directly, bypassing the i-frame gate so successive synthetic
## hits all land (status_probe's idiom).
func _hit(target: Node2D, damage: int, source: Node) -> int:
	var hurtbox = target.get_node("HurtboxComponent")
	var health = target.get_node("HealthComponent")
	hurtbox._invincible_until_ms = 0
	var before: int = health.current_health
	hurtbox.take_hit(damage, source)
	await process_frame
	return before - health.current_health


# --- 1. the curve ---------------------------------------------------------------------

func _test_curve() -> void:
	_check(StatBlock.exp_to_next(1) == 20, "first rung is not 20 (2 slimes at 10 EXP)")
	_check(StatBlock.exp_to_next(StatBlock.MAX_LEVEL) == 0, "cap does not report 0 to next")
	_check(StatBlock.exp_to_next(999) == 0, "past-cap level does not report 0")
	_check(StatBlock.exp_at(1) == 0, "level 1 should require no banked EXP")
	_check(StatBlock.exp_at(2) == 20, "exp_at(2) should equal the first rung")
	_check(StatBlock.exp_at(3) == 20 + StatBlock.exp_to_next(2), "exp_at does not accumulate")

	# level_progress must never divide by zero at the cap — the classic "1/0" bar.
	var capped := CharacterSheet.make(&"fuji", StatBlock.MAX_LEVEL)
	var p := StatBlock.level_progress(capped)
	_check(p.y > 0, "level_progress returns a zero denominator at cap")

	# One rung at a time, and several at once.
	var s := StatBlock.fresh(&"fuji")
	_check(StatBlock.grant_exp(s, 19) == 0, "levelled early (19 < 20)")
	_check(StatBlock.grant_exp(s, 1) == 1, "did not level exactly on the rung")
	_check(s.level == 2, "level is not 2 after the first rung")
	var big := StatBlock.fresh(&"fuji")
	_check(StatBlock.grant_exp(big, 10000) >= 5, "a huge grant did not carry several levels")
	_check(big.level <= StatBlock.MAX_LEVEL, "levelled past the cap")


# --- 2. growth ------------------------------------------------------------------------

func _test_growth() -> void:
	var f := CharacterSheet.make(&"fuji", 20)
	var b := CharacterSheet.make(&"basil", 20)
	StatBlock.apply_growth(f)
	StatBlock.apply_growth(b)
	_check(f.stat("vit") > b.stat("vit"), "Fuji should out-VIT Basil at 20")
	_check(b.stat("mig") > f.stat("mig"), "Basil should out-MIG Fuji at 20")
	_check(f.base != b.base, "the two level-20 sheets converged — the swap stops mattering")
	# Growth is a TABLE, so re-applying must be idempotent rather than additive.
	var before: Dictionary = f.base.duplicate()
	StatBlock.apply_growth(f)
	_check(f.base == before, "apply_growth accumulates instead of assigning")
	# Level growth grants no SPD anywhere — the AI brains are tuned to 150px/s.
	for lvl in range(1, StatBlock.MAX_LEVEL + 1):
		var s := CharacterSheet.make(&"fuji", lvl)
		StatBlock.apply_growth(s)
		if s.base["spd"] != 0:
			_check(false, "level %d grants SPD; the brains are tuned to a fixed speed" % lvl)
			break


# --- 3. neutral sheets ----------------------------------------------------------------

func _test_neutral_sheets() -> void:
	for id in StatBlock.SHEETLESS:
		var s := StatBlock.fresh(id)
		_check(s.neutral, "%s should get a NEUTRAL sheet (no combat in the prologue)" % id)
		_check(StatBlock.grant_exp(s, 500) == 0, "%s levelled — it has no growth table" % id)
	_check(StatBlock.fresh(&"nobody_at_all").neutral, "an unknown id must degrade to neutral")


# --- 4. the item table ----------------------------------------------------------------

func _test_items_table() -> void:
	var tonic := Items.get_item(Items.TONIC)
	_check(tonic != null, "the tonic is missing from the table")
	_check(tonic.heal > 0, "the tonic heals nothing")
	_check(Items.get_item(&"no_such_item") == null, "an unknown id should be null, not an error")
	_check(Items.get_item(&"") == null, "the empty id should be null")
	# Every gear item must declare a real slot and only real stats.
	for it in Items.all():
		if it.is_gear():
			_check(Item.SLOTS.has(it.kind), "%s has a kind that is not an equip slot" % it.id)
		for stat: String in it.worn:
			_check(CharacterSheet.STATS.has(stat),
				"%s grants unknown stat %s" % [it.id, stat])
	# Fuji's books are hers; Basil cannot wear them.
	var primer := Items.get_item(&"primer")
	_check(primer.usable_by(&"fuji"), "Fuji cannot hold her own primer")
	_check(not primer.usable_by(&"basil"), "Basil can hold a book he has no kit for")
	_check(Items.get_item(&"earflaps").usable_by(&"basil"), "an unrestricted hat refused a user")


# --- 5. VIT reaches the body ----------------------------------------------------------

func _test_vit_reaches_the_body() -> void:
	var game := _game()
	game.call("reset_story")
	var sheet = game.call("sheet", &"fuji")
	sheet.level = 10
	StatBlock.apply_growth(sheet)
	var vit: int = sheet.stat("vit")
	_check(vit > 0, "a level-10 Fuji has no VIT to test with")

	# Respawn the party so _apply_sheet runs against the new sheet.
	root.get_node("Party").call("set_roster", [&"fuji"] as Array[StringName], &"fuji")
	change_scene_to_file("res://scene/meadow.tscn")
	await process_frame
	await process_frame
	await process_frame
	var body := _leader()
	var health = body.get_node("HealthComponent")
	_check(health.max_health == body.base_max_health + vit,
		"VIT did not reach max_health (got %d, want %d + %d)"
			% [health.max_health, body.base_max_health, vit])
	# THE ORDERING TRAP: assigning max_health does not re-emit health_changed, so
	# a body that spawned at the old max would show a half-empty heart row.
	_check(health.current_health == health.max_health,
		"the body spawned below its own max — _apply_sheet forgot to refill")


# --- 6. equipment ---------------------------------------------------------------------

func _test_equipment() -> void:
	var game := _game()
	game.call("reset_story")
	var sheet = game.call("sheet", &"fuji")
	var base_grd: int = sheet.stat("grd")

	game.call("add_item", &"oilskin", 1)
	_check(game.call("item_count", &"oilskin") == 1, "the satchel did not take the apron")

	var apron := Items.get_item(&"oilskin")
	sheet.equip(Item.Kind.BODY, &"oilskin")
	game.call("take_item", &"oilskin")
	_check(sheet.stat("grd") == base_grd + int(apron.worn["grd"]),
		"equipping the apron did not move GUARD")
	_check(game.call("item_count", &"oilskin") == 0,
		"the apron is worn AND still in the satchel — it can be worn twice")
	_check(sheet.equipped(Item.Kind.BODY) != null, "the body slot reads empty while worn")

	var removed = sheet.unequip(Item.Kind.BODY)
	game.call("add_item", removed.id)
	_check(sheet.stat("grd") == base_grd, "un-equipping did not give GUARD back")
	_check(game.call("item_count", &"oilskin") == 1, "the apron did not return to the satchel")
	_check(sheet.equipped(Item.Kind.BODY) == null, "the body slot still reads worn")

	# The four slots are independent — a hat must not evict a shirt.
	sheet.equip(Item.Kind.HEAD, &"earflaps")
	sheet.equip(Item.Kind.BODY, &"oilskin")
	_check(sheet.equipped(Item.Kind.HEAD) != null and sheet.equipped(Item.Kind.BODY) != null,
		"two different slots are sharing one entry")


# --- 7. might and guard ---------------------------------------------------------------

func _test_might_and_guard() -> void:
	var game := _game()
	game.call("reset_story")
	root.get_node("Party").call("set_roster", [&"fuji"] as Array[StringName], &"fuji")
	change_scene_to_file("res://scene/meadow.tscn")
	await process_frame
	await process_frame
	for m in root.get_node("Party").members:
		if m != root.get_node("Party").leader:
			m.queue_free()
	await process_frame

	var fuji := _leader()
	var sheet = game.call("sheet", &"fuji")

	# --- MIGHT scales damage OUT.
	sheet.base["mig"] = 0
	var slime := await _lone_slime(9999)
	var flat: int = await _hit(slime, 10, fuji)
	_check(flat == 10, "MIG 0 should be a pass-through (got %d of 10)" % flat)

	sheet.base["mig"] = 12                       # +100% at MIG_DIV 12
	var scaled: int = await _hit(slime, 10, fuji)
	_check(scaled == 20, "MIG 12 should double a 10 (got %d)" % scaled)
	sheet.base["mig"] = 0

	# --- a projectile's SHOOTER is what carries the stat, not the projectile.
	var dart = load("res://entities/projectiles/blow_dart.tscn").instantiate()
	current_scene.get_node("World").add_child(dart)
	dart.shooter = fuji
	sheet.base["mig"] = 12
	var via_dart: int = await _hit(slime, 10, dart)
	_check(via_dart == 20, "a dart did not inherit its shooter's MIGHT (got %d)" % via_dart)
	sheet.base["mig"] = 0
	dart.queue_free()
	slime.queue_free()
	await process_frame

	# --- GUARD reduces damage IN, and can never reach zero.
	sheet.base["grd"] = 0
	var health = fuji.get_node("HealthComponent")
	health.max_health = 200
	health.current_health = 200
	var raw: int = await _hit(fuji, 8, null)
	_check(raw == 8, "GRD 0 should be a pass-through (got %d of 8)" % raw)

	sheet.base["grd"] = 8                        # -1 at GRD_DIV 8
	var shaved: int = await _hit(fuji, 8, null)
	_check(shaved == 7, "GRD 8 should shave exactly 1 (got %d)" % shaved)

	sheet.base["grd"] = 400                      # absurd on purpose
	var floored: int = await _hit(fuji, 2, null)
	_check(floored == 1, "GUARD reached zero — an untouchable party is a dead loop")
	sheet.base["grd"] = 0


# --- 8. a kill pays the whole roster --------------------------------------------------

func _test_kill_grants_whole_roster() -> void:
	var game := _game()
	game.call("reset_story")
	root.get_node("Party").call("set_roster",
		[&"basil", &"fuji"] as Array[StringName], &"basil")
	change_scene_to_file("res://scene/meadow.tscn")
	await process_frame
	await process_frame

	var before_b: int = game.call("sheet", &"basil").exp_total
	var before_f: int = game.call("sheet", &"fuji").exp_total
	game.call("grant_kill", 10)
	_check(game.call("sheet", &"basil").exp_total == before_b + 10, "the leader got no EXP")
	_check(game.call("sheet", &"fuji").exp_total == before_f + 10,
		"the FOLLOWER got no EXP — everyone in the roster is paid in full")

	# Two ten-EXP slimes is exactly one level, which is what the first street
	# fight is tuned around.
	game.call("reset_story")
	var slime_exp: int = load("res://entities/enemies/slime.tscn").instantiate().exp_value
	game.call("grant_kill", slime_exp)
	_check(game.call("sheet", &"fuji").level == 1, "levelled on the FIRST slime")
	game.call("grant_kill", slime_exp)
	_check(game.call("sheet", &"fuji").level == 2, "did not level on the SECOND slime")


# --- 9. persistence -------------------------------------------------------------------

func _test_persistence() -> void:
	var game := _game()
	game.call("reset_story")
	var sheet = game.call("sheet", &"fuji")
	sheet.level = 7
	game.call("add_item", Items.TONIC, 2)
	game.set("fuji_tome", &"primer")

	# Survives a door...
	change_scene_to_file("res://scene/meadow.tscn")
	await process_frame
	await process_frame
	_check(game.call("sheet", &"fuji").level == 7, "the sheet did not survive a scene change")
	_check(game.call("item_count", Items.TONIC) == 2, "the satchel did not survive a door")

	# ...but a backwards chapter jump wipes it, or a level-18 Fuji turns up in
	# the prologue holding a brass-bound ledger.
	game.call("reset_story")
	_check(game.call("sheet", &"fuji").level == 1, "reset_story did not clear sheets")
	_check(game.call("item_count", Items.TONIC) == 0, "reset_story did not clear the satchel")
	_check(game.get("fuji_tome") == &"", "reset_story did not clear fuji_tome")
