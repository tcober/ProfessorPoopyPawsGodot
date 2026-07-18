extends SceneTree

## Prologue A end-to-end probe (2026-07-12), in the party_probe tradition:
## drives the whole "Sparkless" chapter with synthesized POLLED input
## (actions only exist in the polled state — the shot.gd gotcha) and asserts
## the story flags flip in order:
##
##   home start (bedroom -> Mom gates the front door) -> the fountain
##   proximity trigger fires the teasing -> 3 villager talks open the gate ->
##   meadow -> meeting Kitty -> 3 whirligig parts -> flight finale ->
##   montage -> the SUNSET BLUFF romance (the watch explodes, 3 pieces, the
##   refit + the kiss, 2026-07-17) -> Prologue B: plant's walk home ->
##   the dash -> the hall naming (auto walk-of-shame) -> bluff call1 ->
##   the accident (loop-and-land) -> bluff call2 -> the sickroom verdict ->
##   the clinic-steps scolding + the scripted leaving -> hand-off to
##   house.tscn with the adult roster.
##
## Walk-gates are driven by TELEPORTING to the gate anchor; their pollable
## end-states are the party unlock (is_physics_processing) or a flag.
##
## Must run WINDOWED (the dummy rasterizer renders black, and wall-clock
## timers drive the dialog):
##   /Applications/Godot.app/Contents/MacOS/Godot --path . \
##       --script tools/prologue_probe.gd

var _fails := 0
var _last_press := 0

# autoloads aren't compile-time identifiers under --script; runtime lookup
# like party_probe does (assigned in _run — SceneTree has no @onready)
var game: Node
var party: Node


func _initialize() -> void:
	_run()


func _check(label: String, cond: bool) -> void:
	if cond:
		print("  ok    ", label)
	else:
		print("  FAIL  ", label)
		_fails += 1


## Advance dialog by pressing attack every 250ms (comfortably past the
## DialogBox swallow window) until pred() holds or the frame budget dies.
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


func _wait_frames(n: int) -> void:
	for i in n:
		await process_frame


func _scene_is(path: String) -> bool:
	return current_scene != null and current_scene.scene_file_path == path


## Stand at an NPC, press E, mash through the conversation (and any beat it
## chains into) until the box drops. Success is the NPC's own `talked`
## signal, and the opening press RETRIES: a staged beat racing the teleport
## (the downstairs door hint fired by the previous step's body_entered
## landing a physics tick late) can hold the party locked, eat the interact,
## and leave the mash closing the WRONG box.
func _talk_to(npc: NPC, scene: Node) -> bool:
	var talked := [false]
	var mark := func(_n: NPC) -> void: talked[0] = true
	npc.talked.connect(mark)
	var closed := func() -> bool: return not scene.theater.dialog.visible
	for attempt in 4:
		_player().global_position = npc.global_position + Vector2(0.0, 16.0)
		await _wait_frames(8)
		Input.action_press("interact")
		await _wait_frames(3)
		Input.action_release("interact")
		await _mash_until(closed, 2400)
		await _wait_frames(30)
		if talked[0]:
			npc.talked.disconnect(mark)
			return true
	npc.talked.disconnect(mark)
	return false


func _player() -> Node2D:
	var players := get_nodes_in_group("player")
	return players[0] if players.size() > 0 else null


## The pollable "party unlocked" end-state every phase gate shares (one
## home — four hand-copied lambdas drifted before the 2026-07-17 review).
func _party_free() -> bool:
	return _player() != null and _player().is_physics_processing()


func _run() -> void:
	await process_frame
	# an OCCLUDED macOS window runs UNCAPPED (~2000fps): frame budgets burn
	# in real seconds while the cutscenes' wall-clock timers don't advance
	# any faster — pin 60fps so budgets always track wall-clock (2026-07-16)
	Engine.max_fps = 60
	game = root.get_node("Game")
	party = root.get_node("Party")
	print("prologue probe:")
	var kid_roster: Array[StringName] = [&"kid_basil"]
	party.set_roster(kid_roster)

	# ---- the home start: bedroom -> downstairs -> Mom gates the door -------
	change_scene_to_file("res://scene/house_fest.tscn")
	await _wait_frames(5)
	_check("kid roster spawned solo in the fest bedroom",
			party.members.size() == 1 and party.leader is KidBasil
			and _scene_is("res://scene/house_fest.tscn"))
	var house_map: Dictionary = MapData.load_map("res://assets/maps/house.txt")
	# the sunrise wake-up holds the kid locked through the sigh — mash to
	# the unlock (the pollable end-state, the house_thesis wake idiom)
	var ok: bool = await _mash_until(_party_free, 3600)
	_check("the sunrise wake-up hands control back", ok)
	_player().global_position = MapData.anchor_px(house_map, "exit_door")
	var in_down := func() -> bool: return _scene_is("res://scene/downstairs_fest.tscn")
	ok = await _mash_until(in_down, 1200)
	_check("stairs descend to the fest downstairs", ok)
	await _wait_frames(20)
	var down := current_scene
	var down_map: Dictionary = MapData.load_map("res://assets/maps/downstairs.txt")
	# the front door is barred before Mom's good-morning
	var down_closed := func() -> bool: return not down.theater.dialog.visible
	_player().global_position = MapData.anchor_px(down_map, "exit_door")
	await _wait_frames(12)                # the hint beat fires
	await _mash_until(down_closed, 900)
	_check("front door is Mom-gated", in_down.call()
			and not game.flag("prologue_saw_mom"))
	var mom: NPC = null
	for child in down.get_node("World").get_children():
		if child is NPC:
			mom = child
	ok = await _talk_to(mom, down)
	_check("Mom's good-morning unlocks the door", game.flag("prologue_saw_mom"))
	_player().global_position = MapData.anchor_px(down_map, "exit_door")
	var in_town := func() -> bool: return _scene_is("res://scene/town_fest.tscn")
	ok = await _mash_until(in_town, 900)
	_check("front door opens into the festival town", ok)
	await _wait_frames(40)                # entry fade

	# ---- the fountain proximity trigger -> the teasing + the theft ----------
	# (the goose theft runs inside the festival cutscene now — budget covers
	# the waddle-in, the snatch, and the bridge getaway)
	var town_map: Dictionary = MapData.load_map("res://assets/maps/town_fest.txt")
	_player().global_position = MapData.anchor_px(town_map, "basil_mark") + Vector2(0.0, -16.0)
	var festival_done := func() -> bool: return game.flag("prologue_festival_done")
	ok = await _mash_until(festival_done, 9000)
	_check("walking by the fountain fires the teasing", ok)
	await _wait_frames(30)

	# ---- the hidden goose in the orchard ------------------------------------
	var town := current_scene
	var town_box_closed := func() -> bool: return not town.theater.dialog.visible
	var npcs := {}
	for child in town.get_node("World").get_children():
		if child is NPC:
			npcs[child.display_name] = child
	_check("festival cast spawned (5 villagers + the hidden goose)",
			npcs.size() == 6 and game.flag("prologue_goose_hidden"))
	var ribbon := func() -> bool: return game.flag("prologue_ribbon")
	ok = await _talk_to(npcs["Goose"], town)
	ok = await _mash_until(ribbon, 1200)
	_check("the startled goose surrenders the ribbon", ok)
	await _wait_frames(20)

	# ---- three stings, then the blessing double-back (Mom is DOWNSTAIRS) ----
	ok = await _talk_to(npcs["Sage"], town)
	_check("ribbon returned to Sage", game.flag("prologue_ribbon_returned"))
	await _talk_to(npcs["Mrs. Flockhart"], town)
	await _talk_to(npcs["Professor Strix"], town)
	ok = await _mash_until(town_box_closed, 1200)   # the want-home beat
	_check("three stings -> wants home, gate still shut",
			game.flag("prologue_want_home") and not game.flag("prologue_gate_open"))
	await _wait_frames(30)
	# the home door re-opens while he wants home: step on it -> downstairs
	# (the zone sits ON the door mouth since 2026-07-17 — no drop offset)
	_player().global_position = MapData.anchor_px(town_map, "home")
	var back_down := func() -> bool: return _scene_is("res://scene/downstairs_fest.tscn")
	ok = await _mash_until(back_down, 900)
	_check("the home door re-opens into the downstairs", ok)
	await _wait_frames(20)
	var down2 := current_scene
	var mom2: NPC = null
	for child in down2.get_node("World").get_children():
		if child is NPC:
			mom2 = child
	ok = await _talk_to(mom2, down2)
	_check("Mom's blessing opens the south gate", game.flag("prologue_gate_open"))
	await _wait_frames(20)
	_player().global_position = MapData.anchor_px(down_map, "exit_door")
	ok = await _mash_until(in_town, 900)
	_check("the front door returns to town, gate open", ok)
	await _wait_frames(40)

	# ---- south to the meadow ----------------------------------------------
	_player().global_position = MapData.anchor_px(town_map, "exit_south")
	var in_meadow := func() -> bool: return _scene_is("res://scene/meadow_fest.tscn")
	ok = await _mash_until(in_meadow, 1200)
	_check("south gate travels to the prologue meadow", ok)
	await _wait_frames(60)                # entry fade + lock

	# ---- meeting Kitty ------------------------------------------------------
	var meadow := current_scene
	var meadow_map: Dictionary = MapData.load_map("res://assets/maps/meadow.txt")
	_player().global_position = MapData.anchor_px(meadow_map, "kitty_pos") + Vector2(0.0, 40.0)
	var met_kitty := func() -> bool: return game.flag("prologue_met_kitty")
	ok = await _mash_until(met_kitty, 4000)
	_check("meeting Kitty starts the quest", ok)
	var box_closed := func() -> bool: return not meadow.theater.dialog.visible
	ok = await _mash_until(box_closed, 1200)
	await _wait_frames(30)

	# ---- the three parts ----------------------------------------------------
	for part in ["gear", "spring", "crank"]:
		_player().global_position = MapData.anchor_px(meadow_map, "part_" + part)
		var found := func() -> bool: return game.flag("prologue_part_" + part)
		ok = await _mash_until(found, 900)
		_check("part found: " + part, ok)
		ok = await _mash_until(box_closed, 1200)
		await _wait_frames(20)

	# ---- the flight finale + montage -> the sunset bluff ---------------------
	_player().global_position = MapData.anchor_px(meadow_map, "kitty_pos") + Vector2(0.0, 40.0)
	var sparkless_done := func() -> bool: return game.flag("prologue_sparkless_done")
	ok = await _mash_until(sparkless_done, 9000)
	_check("Prologue A flight finale + montage complete", ok)
	var in_bluff := func() -> bool: return _scene_is("res://scene/bluff.tscn")
	ok = await _mash_until(in_bluff, 1200)
	_check("A hands off to the sunset bluff", ok)
	_check("swapped to the student roster", party.roster.size() == 1
			and party.roster[0] == &"basil_student")
	await _wait_frames(30)

	# ==== THE BLUFF ROMANCE (2026-07-17) ======================================
	# mash the intro (the handoff EXPLODES mid-scene and scatters the three
	# pieces), gather them, then talk to Kitty for the refit + the kiss.
	# The intro's end-state is the party UNLOCK, never dialog-invisible: the
	# box is also invisible during the opening wait(), which reads as "done"
	# before the first line ever opens (the 2026-07-16 probe race).
	ok = await _mash_until(_party_free, 6000)
	_check("the exploded watch hands over the hunt", ok)
	await _wait_frames(20)
	# pieces by ANCHOR, never re-hardcoded pixels (the 2026-07-17 review)
	var bluff_map: Dictionary = MapData.load_map("res://assets/maps/bluff.txt")
	for part in ["gear", "spring", "crank"]:
		_player().global_position = MapData.anchor_px(bluff_map, "part_" + part)
		await _wait_frames(12)
	var parts_ok := func() -> bool: return game.flag("prologue_wpart_gear") \
			and game.flag("prologue_wpart_spring") and game.flag("prologue_wpart_crank")
	ok = await _mash_until(parts_ok, 600)
	_check("watch pieces gathered", ok)
	# the refit + the kiss: stand EAST of Kitty (open grass — south of her
	# is the cliff band), press E, mash to the flag — the scene frees itself
	# at the hand-off, so the end-state preds are the FLAG and the next
	# scene, never the (soon freed) theater
	var gift_done := func() -> bool: return game.flag("prologue_watch_given")
	_player().global_position = MapData.anchor_px(bluff_map, "kitty_pos") + Vector2(16.0, 0.0)
	await _wait_frames(8)
	for attempt in 4:
		Input.action_press("interact")
		await _wait_frames(3)
		Input.action_release("interact")
		ok = await _mash_until(gift_done, 3600)
		if ok:
			break
	_check("the refit + the kiss play", ok and game.flag("prologue_romance"))
	var in_thesis := func() -> bool: return _scene_is("res://scene/town_thesis.tscn")
	ok = await _mash_until(in_thesis, 1500)
	_check("the bluff hands off to thesis-day town (plant)", ok)
	await _wait_frames(40)

	# ==== PROLOGUE B ==========================================================
	# plant: the night-before lines -> the playable walk home -> the doorstep
	# call -> house_thesis
	ok = await _mash_until(_party_free, 3000)
	_check("the night-before hands over the walk home", ok)
	_player().global_position = MapData.anchor_px(town_map, "home") + Vector2(0.0, 26.0)
	var in_wake := func() -> bool: return _scene_is("res://scene/house_thesis.tscn")
	ok = await _mash_until(in_wake, 6000)
	_check("plant beat -> the 8:57 wake-up", ok)
	await _wait_frames(30)

	# wake-up: mash through, then walk to the stair exit -> dash
	# (house_map was loaded for the home start — reuse it)
	var wake := current_scene
	var wake_closed := func() -> bool: return not wake.theater.dialog.visible
	ok = await _mash_until(wake_closed, 5000)     # the whole panic
	await _wait_frames(20)
	_player().global_position = MapData.anchor_px(house_map, "exit_door")
	var in_dash := func() -> bool: return _scene_is("res://scene/town_thesis.tscn")
	ok = await _mash_until(in_dash, 1500)
	_check("wake-up -> the dash", ok)
	await _wait_frames(40)

	# dash: mash the squelch, then run to the school -> hall
	# (town_map was loaded earlier for the wander gate — reuse it)
	var dash := current_scene
	var dash_closed := func() -> bool: return not dash.theater.dialog.visible
	ok = await _mash_until(dash_closed, 4000)     # squelch beat
	await _wait_frames(20)
	# cross the puddles (stepping in clears them too) up to the school
	_player().global_position = MapData.anchor_px(town_map, "school") + Vector2(0.0, 40.0)
	var in_hall := func() -> bool: return _scene_is("res://scene/hall.tscn")
	ok = await _mash_until(in_hall, 5000)
	_check("dash -> the lecture hall", ok)
	await _wait_frames(40)

	# hall: Dean's welcome -> the walk-in gate -> the naming -> the AUTO walk
	# of shame (2026-07-17: his body gives up, not the player's) -> bluff
	# call1. The walk-in gate unlocks the party (the pollable state).
	ok = await _mash_until(_party_free, 2400)
	_check("the Dean's welcome hands over the walk-in", ok)
	# the walk-in gate is the full-width row below the benches (y 136), not
	# the podium point — land inside the band
	_player().global_position = Vector2(192.0, 136.0)
	var named := func() -> bool: return game.flag("prologue_named")
	ok = await _mash_until(named, 6000)
	_check("the naming beat completes", ok)
	# the slow scripted walk-out + card runs on its own; mash to the bluff
	ok = await _mash_until(in_bluff, 12000)
	_check("hall -> bluff call1 (the auto walk of shame)", ok)
	await _wait_frames(40)

	# call1: the sad lines -> the player's own walk to the lip (the gate) ->
	# sit -> her call -> the SHOWN accident -> bluff call2 (her watch, the
	# wrong voice) -> the sickroom. accident + call2 auto-run between mashes.
	ok = await _mash_until(_party_free, 4000)
	_check("call1 hands over the walk to the lip", ok)
	_player().global_position = MapData.anchor_px(bluff_map, "sit_spot")
	var in_sick := func() -> bool: return _scene_is("res://scene/sickroom.tscn")
	ok = await _mash_until(in_sick, 16000)
	_check("call1 + accident + call2 -> the sickroom", ok)
	_check("the accident happened on the way", game.flag("prologue_accident"))
	await _wait_frames(40)

	# sickroom: the doctor's invitation -> the walk to the bedside -> the
	# verdict -> the clinic-steps phase
	var sick_map: Dictionary = MapData.load_map("res://assets/maps/sickroom.txt")
	ok = await _mash_until(_party_free, 2400)
	_check("the doctor hands over the walk to the bedside", ok)
	_player().global_position = MapData.anchor_px(sick_map, "bedside")
	var in_steps := func() -> bool: return _scene_is("res://scene/town_thesis.tscn")
	ok = await _mash_until(in_steps, 7000)
	_check("the verdict -> the clinic steps", ok)
	await _wait_frames(40)

	# steps: fully scripted (the agency spent itself at the sickroom door) —
	# sit, Ridley's blunt speech, the bowed head, night, then the leaving
	# tableau (stick + knapsack, east) and the cards. Just mash the flags.
	var scolded := func() -> bool: return game.flag("prologue_scolded")
	ok = await _mash_until(scolded, 12000)
	_check("the scolding beat completes", ok)
	var prologue_done := func() -> bool: return game.flag("prologue_done")
	ok = await _mash_until(prologue_done, 12000)
	_check("the leaving completes the prologue", ok)
	var in_adult := func() -> bool: return _scene_is("res://scene/house.tscn")
	ok = await _mash_until(in_adult, 1500)
	_check("hand-off lands in the adult build (house.tscn)", ok)
	_check("adult roster restored", party.roster.size() == 2
			and party.roster[0] == &"basil" and party.roster[1] == &"fuji"
			and party.leader_id == &"basil")

	print("prologue probe: %s" % ("ALL PASS" if _fails == 0 else "%d FAILED" % _fails))
	quit(1 if _fails > 0 else 0)
