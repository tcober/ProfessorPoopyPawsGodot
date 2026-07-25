extends SceneTree

## Behavioral probe for the status layer (sleep buildup / freeze / burn) and
## the compound gun. Drives a real slime in the real meadow rather than
## unit-testing the component in isolation, because the interesting failures
## are all wiring: a hit that doesn't carry its payload, a hitbox that never
## re-registers on wake, a burn tick swallowed by invincibility frames.
##
## Asserts:
##   1. one dart does NOT sleep a slime (the buildup has to be committed to),
##   2. the threshold'th dart does — body still, contact hitbox shape off,
##   3. a sleeper takes NORMAL damage and KEEPS sleeping (no wake-on-hit),
##   4. drowse DECAYS, so you can't chip something asleep one dart a minute,
##   5. it wakes on its own timer, and the contact hitbox comes back LIVE
##      even though it never stopped overlapping (the shape-vs-monitoring bug),
##   6. a bigger enemy needs more darts than a small one,
##   7. burn ticks land past the hurtbox's invincible_time gate,
##   8. chill slows, and stacks into a freeze.
##
## Must run WINDOWED (same GL note as tools/shot.gd):
##   /Applications/Godot.app/Contents/MacOS/Godot --path . --script tools/status_probe.gd

const DartScene := preload("res://entities/projectiles/blow_dart.tscn")

var _fails: Array[String] = []
var _checks := 0


func _initialize() -> void:
	_run()


func _run() -> void:
	Engine.max_fps = 60          # an occluded macOS window otherwise runs uncapped
	await process_frame
	change_scene_to_file("res://scene/meadow.tscn")
	await process_frame
	await process_frame

	# Strip the AI follower. Left alive it wanders over and kills the specimen
	# mid-await (the probe's first run crashed on a freed slime), and its
	# knockback drags the parked body around — neither is what's under test.
	var party := root.get_node("Party")
	for m in party.members:
		if m != party.leader:
			m.queue_free()
	await process_frame

	await _test_sleep_buildup()
	await _test_no_wake_on_hit()
	await _test_drowse_decay()
	await _test_wake_restores_contact_damage()
	await _test_bigger_resists()
	await _test_burn_beats_iframes()
	await _test_chill_and_freeze()
	_test_mixing_rules()
	await _test_compound_gun()
	await _test_loadout_survives_scene_change()

	print("")
	if _fails.is_empty():
		print("status_probe: OK (%d checks)" % _checks)
		quit(0)
	else:
		for f in _fails:
			print("FAIL: ", f)
		print("status_probe: %d/%d FAILED" % [_fails.size(), _checks])
		quit(1)


# --- helpers ------------------------------------------------------------------

func _check(ok: bool, what: String) -> void:
	_checks += 1
	if not ok:
		_fails.append(what)


## A fresh slime parked far from the party so nothing else touches it.
func _lone_slime(scene_path: String = "res://entities/enemies/slime.tscn") -> Node2D:
	var world: Node2D = current_scene.get_node("World")
	# Clear the field so stray slimes never wander into the specimen.
	for child in world.get_children():
		if child is Slime:
			child.queue_free()
	await process_frame
	var slime: Node2D = load(scene_path).instantiate()
	world.add_child(slime)
	slime.global_position = _party_leader().global_position + Vector2(220.0, 0.0)
	await process_frame
	await process_frame
	# Effectively unkillable by default (party_probe's trick): a specimen that
	# dies mid-await leaves every later assert reading a freed object. Tests
	# that measure damage set their own HP.
	var health = slime.get_node("HealthComponent")
	health.max_health = 99999
	health.current_health = 99999
	return slime


func _party_leader() -> Node2D:
	return root.get_node("Party").leader


## Autoloads are fetched by path, never by identifier: a --script tool compiles
## without the autoload names in scope (the same rule the narrative kit follows).
func _game() -> Node:
	return root.get_node("Game")


## Basil, duck-typed. Naming the `Player` CLASS here would drag player.gd into
## this tool's own compile — which happens before autoloads are registered, so
## its `Game.` references would fail to resolve and poison the whole run. Same
## hazard the narrative kit documents; the fix is to never name the type.
func _basil() -> Node2D:
	var leader := _party_leader()
	return leader if leader != null and leader.has_method("collect_beaker") else null


## Hit the slime's hurtbox directly — the projectile's own call, minus the
## travel time and the aim.
func _hit(slime: Node2D, damage: int, effect: Dictionary) -> void:
	var hurtbox = slime.get_node("HurtboxComponent")
	hurtbox._invincible = false            # skip the i-frame wait between probes
	hurtbox.take_hit(damage, _party_leader(), effect)
	await process_frame


func _wait(seconds: float) -> void:
	await create_timer(seconds).timeout


func _hitbox_live(slime: Node2D) -> bool:
	return not slime.get_node("Hitbox/CollisionShape2D").disabled


# --- the tests ----------------------------------------------------------------

func _test_sleep_buildup() -> void:
	var slime := await _lone_slime()
	var status = slime.get_node("StatusComponent")
	var threshold: int = status.drowse_threshold

	await _hit(slime, 1, {"drowse": 1})
	_check(not status.is_asleep(),
		"one dart slept a slime with threshold %d" % threshold)
	_check(_hitbox_live(slime), "contact hitbox died before the slime slept")

	for i in threshold - 1:
		await _hit(slime, 1, {"drowse": 1})
	_check(status.is_asleep(), "%d darts did not sleep the slime" % threshold)
	await process_frame
	await process_frame
	_check(not _hitbox_live(slime), "a sleeping slime can still deal contact damage")
	# Let the last dart's knockback bleed off first — a sleeper SLIDES when hit
	# (knockback outranks the disabled branch on purpose), so stillness is only
	# meaningful once the shove is spent.
	await _wait(0.5)
	_check(slime.velocity.length() < 1.0, "a sleeping slime is still moving")
	slime.queue_free()


func _test_no_wake_on_hit() -> void:
	var slime := await _lone_slime()
	var status = slime.get_node("StatusComponent")
	var health = slime.get_node("HealthComponent")
	for i in status.drowse_threshold:
		await _hit(slime, 0, {"drowse": 1})
	_check(status.is_asleep(), "setup: slime did not fall asleep")

	var before: int = health.current_health
	await _hit(slime, 2, {})
	_check(health.current_health == before - 2,
		"a sleeper took %d damage, expected 2" % (before - health.current_health))
	_check(status.is_asleep(), "the sleeper woke up when hit (it must not)")
	slime.queue_free()


func _test_drowse_decay() -> void:
	var slime := await _lone_slime()
	var status = slime.get_node("StatusComponent")
	await _hit(slime, 0, {"drowse": 1})
	var peak: float = status.drowse_ratio()
	_check(peak > 0.0, "one dart registered no drowse at all")
	# Long enough for drowse_decay to eat a full point.
	await _wait(1.0 / maxf(status.drowse_decay, 0.01) + 0.2)
	_check(status.drowse_ratio() < peak,
		"drowse never decayed — you could chip anything asleep given time")
	slime.queue_free()


func _test_wake_restores_contact_damage() -> void:
	var slime := await _lone_slime()
	var status = slime.get_node("StatusComponent")
	# Park it ON the leader so its hitbox and the player's hurtbox are
	# CONTINUOUSLY overlapping across the whole sleep. This is the exact shape
	# of the monitoring-vs-shape bug: re-enabling `monitoring` would not
	# re-scan an overlap that never ended, and the slime would wake harmless.
	slime.global_position = _party_leader().global_position
	for i in status.drowse_threshold:
		await _hit(slime, 0, {"drowse": 1})
	_check(status.is_asleep(), "setup: slime did not fall asleep")
	await _wait(status.sleep_time + 0.3)
	_check(not status.is_asleep(), "the slime never woke up")
	await process_frame
	await process_frame
	_check(_hitbox_live(slime),
		"woke overlapping the player but its contact hitbox stayed dead")
	slime.queue_free()


func _test_bigger_resists() -> void:
	var small := await _lone_slime()
	var small_threshold: int = small.get_node("StatusComponent").drowse_threshold
	small.queue_free()
	var big := await _lone_slime("res://entities/enemies/big_slime.tscn")
	var big_status = big.get_node("StatusComponent")
	_check(big_status.drowse_threshold > small_threshold,
		"the big slime (%d) does not resist more darts than the small one (%d)"
			% [big_status.drowse_threshold, small_threshold])

	# ...and it genuinely survives the small one's dose still awake.
	for i in small_threshold:
		await _hit(big, 0, {"drowse": 1})
	_check(not big_status.is_asleep(),
		"the big slime slept on the small slime's dart count")
	for i in big_status.drowse_threshold - small_threshold:
		await _hit(big, 0, {"drowse": 1})
	_check(big_status.is_asleep(), "the big slime never slept at its own threshold")
	big.queue_free()


func _test_burn_beats_iframes() -> void:
	var slime := await _lone_slime()
	var status = slime.get_node("StatusComponent")
	var health = slime.get_node("HealthComponent")
	health.max_health = 99
	health.current_health = 99
	var before: int = health.current_health
	await _hit(slime, 0, {"burn": 4})
	_check(status.is_burning(), "burn never applied")
	# Four ticks at burn_period, plus slack. The hurtbox's invincible_time
	# would swallow most of these if ticks went back through take_hit.
	await _wait(status.burn_period * 5.0)
	var dealt: int = before - health.current_health
	_check(dealt == 4, "burn dealt %d of 4 ticks (i-frames eating them?)" % dealt)
	_check(not status.is_burning(), "burn never expired")
	slime.queue_free()


## Every pair the mix menu can offer must resolve to a compound or to an
## explicit refusal — never to a silent nothing that eats two beakers.
func _test_mixing_rules() -> void:
	var base := Alchemy.make(Compound.Kind.BASE)
	var frost := Alchemy.make(Compound.Kind.FROST)
	var flame := Alchemy.make(Compound.Kind.FLAME)
	var plasma := Alchemy.make(Compound.Kind.PLASMA)

	# Rule 3, both orderings — it must not be reachable only one way round.
	var p1 := Alchemy.mix(flame, frost)
	var p2 := Alchemy.mix(frost, flame)
	_check(p1 != null and p1.kind == Compound.Kind.PLASMA, "flame+frost is not plasma")
	_check(p2 != null and p2.kind == Compound.Kind.PLASMA, "frost+flame is not plasma")

	# Rule 1: same kind concentrates — more potent, same magazine.
	var conc := Alchemy.mix(flame, flame)
	_check(conc != null and conc.potency > flame.potency, "flame+flame did not concentrate")
	_check(conc != null and conc.hit_damage() > flame.hit_damage(),
		"concentrating did not raise damage")
	_check(conc != null and conc.charges == flame.charges,
		"concentrating changed the magazine size")

	# Rule 2: green is the solvent — more shots, same punch.
	var dil := Alchemy.mix(base, flame)
	_check(dil != null and dil.kind == Compound.Kind.FLAME, "base+flame lost the flame")
	_check(dil != null and dil.charges > flame.charges, "diluting did not add charges")
	_check(dil != null and dil.hit_damage() == flame.hit_damage(),
		"diluting changed the damage")
	_check(Alchemy.mix(flame, base) != null, "dilution is not symmetric")

	# The BASE+BASE tie must resolve as concentrate, not dilute.
	var bb := Alchemy.mix(base, base)
	_check(bb != null and bb.potency > base.potency, "base+base did not concentrate")

	# Leftovers are refused explicitly, not silently.
	_check(Alchemy.mix(flame, plasma) == null, "flame+plasma should be inert")
	_check(Alchemy.mix(frost, plasma) == null, "frost+plasma should be inert")
	_check(Alchemy.refusal(flame, plasma) != "", "an inert pair gave no reason")

	# Mixing must never mutate its inputs — the menu previews before committing.
	_check(flame.potency == 1 and flame.charges == 6, "mix() mutated its arguments")


func _test_compound_gun() -> void:
	var player := _basil()
	if player == null:
		_check(false, "the meadow's leader is not Basil — cannot test the gun")
		return

	# Pouring a compound must retune the gun, not just refill it.
	var plasma := Alchemy.make(Compound.Kind.PLASMA)
	player.set("loaded", plasma)
	player.set("max_ammo", plasma.charges)
	_check(int(player.get("max_ammo")) == 3,
		"a plasma beaker did not give a 3-round magazine")

	# A bolt takes its whole character from the compound.
	var bolt: LaserBolt = load("res://entities/projectiles/laser_bolt.tscn").instantiate()
	bolt.apply_compound(plasma)
	_check(bolt.damage == plasma.hit_damage(), "the bolt ignored the compound's damage")
	_check(bolt.pierce, "the plasma bolt does not pierce")
	bolt.free()

	var flame_bolt: LaserBolt = load("res://entities/projectiles/laser_bolt.tscn").instantiate()
	flame_bolt.apply_compound(Alchemy.make(Compound.Kind.FLAME))
	_check(flame_bolt.effect.has("burn"), "the flame bolt carries no burn")
	_check(not flame_bolt.pierce, "the flame bolt should not pierce")
	# Short lifetime IS the range limit; if this grows, flame stops being a sprayer.
	_check(flame_bolt.speed * flame_bolt.lifetime < 100.0,
		"the flame bolt reaches %.0fpx — too far for a sprayer"
			% (flame_bolt.speed * flame_bolt.lifetime))
	flame_bolt.free()
	await process_frame


## The whole reason the loadout lives on Game: Party.spawn() rebuilds the body
## at every door, so a mixed compound held on the instance would evaporate.
func _test_loadout_survives_scene_change() -> void:
	_game().loaded = Alchemy.make(Compound.Kind.PLASMA)
	var carried: Array[Compound] = [Alchemy.make(Compound.Kind.FROST)]
	_game().spares = carried
	_game().ammo_left = 2

	change_scene_to_file("res://scene/meadow.tscn")
	await process_frame
	await process_frame
	await process_frame

	var player := _basil()
	_check(player != null, "lost Basil across the scene change")
	if player != null:
		var carried_loaded: Compound = player.get("loaded")
		var carried_spares: Array = player.get("beakers")
		var rounds := int(player.get("ammo"))
		_check(carried_loaded != null and carried_loaded.kind == Compound.Kind.PLASMA,
			"the loaded compound did not survive the scene change")
		_check(rounds == 2,
			"rounds reset to %d across a door (free plasma refill exploit)" % rounds)
		_check(carried_spares.size() == 1
				and (carried_spares[0] as Compound).kind == Compound.Kind.FROST,
			"the spare beakers did not survive the scene change")

	# reset_story() must blank all of it, or a backwards chapter jump carries a
	# late-game compound into a scene that predates the gun.
	_game().reset_story()
	_check(_game().loaded == null and _game().spares.is_empty() and _game().ammo_left == 0,
		"reset_story() left the gun loadout behind")


func _test_chill_and_freeze() -> void:
	var slime := await _lone_slime()
	var status = slime.get_node("StatusComponent")
	_check(is_equal_approx(status.move_scale(), 1.0), "an unchilled slime is slowed")
	await _hit(slime, 0, {"chill": 1})
	_check(status.move_scale() < 1.0, "one chill hit did not slow the slime")
	_check(not status.is_frozen(), "one chill hit froze the slime solid")
	for i in status.chill_threshold - 1:
		await _hit(slime, 0, {"chill": 1})
	_check(status.is_frozen(), "%d chill hits did not freeze" % status.chill_threshold)
	await process_frame
	await process_frame
	_check(not _hitbox_live(slime), "a frozen slime can still deal contact damage")
	await _wait(status.freeze_time + 0.3)
	_check(not status.is_frozen(), "the slime never thawed")
	slime.queue_free()
