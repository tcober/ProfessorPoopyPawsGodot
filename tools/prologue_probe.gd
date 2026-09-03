extends SceneTree

## Prologue A end-to-end probe (2026-07-12), in the party_probe tradition:
## drives the whole "Whirligig" chapter with synthesized POLLED input
## (actions only exist in the polled state — the shot.gd gotcha) and asserts
## the story flags flip in order:
##
##   home start (bedroom -> Mom gates the front door) -> the fountain
##   proximity trigger fires the teasing -> 3 villager talks open the gate ->
##   the BLUFF meet (2026-07-18: the meadow scene was cut — kid Basil meets
##   Kitty on the headland) -> 3 whirligig parts -> flight finale -> THE IDEA
##   (2026-07-25) -> the BREW back home (the workbench gate + the stir mash)
##   -> across town, where the south gate now REFUSES and the Academy door is
##   live -> the RECITAL (the aisle gate, four compound colours over the
##   house, the invitation) -> montage -> the same bluff reloads as the
##   SUNSET ROMANCE (the watch explodes, 3 pieces, the refit + the kiss) ->
##   Prologue B: plant's walk
##   home -> the dash -> the hall naming (auto walk-of-shame) -> bluff
##   call1 -> the accident (loop-and-land) -> bluff call2 -> the sickroom
##   verdict -> the clinic-steps scolding + the scripted leaving -> the Ebb
##   night (the mountain quake/crystal cutscene, skipped by the mash, then
##   the Lanternwood library's sync gag + dead-wand beat, which hands
##   control back IN the room and makes her walk out her own door) -> the
##   story rests on playable solo Fuji in lanternwood.tscn, the street out
##   comparing dead charms.
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
	# the front door opens onto THE BOUGHS since the 2026-08-23 split — the
	# festival is a rope ladder down
	var in_boughs := func() -> bool: return _scene_is("res://scene/canopy_fest.tscn")
	ok = await _mash_until(in_boughs, 900)
	_check("front door opens onto the festival boughs", ok)
	await _wait_frames(70)                # entry fade + lock
	var canopy_map: Dictionary = MapData.load_map("res://assets/maps/canopy_fest.txt")
	_player().global_position = MapData.anchor_px(canopy_map, "head1") + Vector2(8.0, 8.0)
	var in_town := func() -> bool: return _scene_is("res://scene/town_fest.tscn")
	ok = await _mash_until(in_town, 1500)
	_check("the ladder mouth descends into the festival town", ok)
	await _wait_frames(40)                # entry fade

	# ---- the fountain proximity trigger -> the teasing + the theft ----------
	# (the goose theft runs inside the festival cutscene now — budget covers
	# the take-off, the snatch, and the climb out over the rooftops)
	var town_map: Dictionary = MapData.load_map("res://assets/maps/town_fest.txt")
	_player().global_position = MapData.anchor_px(town_map, "basil_mark") + Vector2(0.0, -16.0)
	var festival_done := func() -> bool: return game.flag("prologue_festival_done")
	ok = await _mash_until(festival_done, 9000)
	_check("walking by the fountain fires the teasing", ok)
	await _wait_frames(30)

	# ---- the hidden goose, up the great tree — literally, since the split ----
	var npcs := {}
	for child in current_scene.get_node("World").get_children():
		if child is NPC:
			npcs[child.display_name] = child
	_check("festival cast spawned (5 villagers; the goose is treed)",
			npcs.size() == 5 and game.flag("prologue_goose_hidden"))
	# up tree 3 after it — the startle plays on its ring deck in canopy_fest
	_player().global_position = MapData.anchor_px(town_map, "top3") + Vector2(8.0, 8.0)
	ok = await _mash_until(in_boughs, 1500)
	_check("tree 3's mouth climbs to the boughs", ok)
	await _wait_frames(70)
	var boughs := current_scene
	var treed_goose: NPC = null
	for child in boughs.get_node("World").get_children():
		if child is NPC and child.display_name == "Goose":
			treed_goose = child
	var ribbon := func() -> bool: return game.flag("prologue_ribbon")
	ok = await _talk_to(treed_goose, boughs)
	ok = await _mash_until(ribbon, 1200)
	_check("the startled goose surrenders the ribbon", ok)
	await _wait_frames(20)
	# back down to the floor with the ribbon
	_player().global_position = MapData.anchor_px(canopy_map, "head3") + Vector2(8.0, 8.0)
	ok = await _mash_until(in_town, 1500)
	_check("the ladder returns the ribbon-bearer to the floor", ok)
	await _wait_frames(70)

	# ---- three stings, then the blessing double-back (Mom is DOWNSTAIRS) ----
	# (the town reloaded across the climb — rebind the scene and its cast)
	var town := current_scene
	var town_box_closed := func() -> bool: return not town.theater.dialog.visible
	npcs.clear()
	for child in town.get_node("World").get_children():
		if child is NPC:
			npcs[child.display_name] = child
	ok = await _talk_to(npcs["Sage"], town)
	_check("ribbon returned to Sage", game.flag("prologue_ribbon_returned"))
	await _talk_to(npcs["Mrs. Flockhart"], town)
	await _talk_to(npcs["Professor Strix"], town)
	ok = await _mash_until(town_box_closed, 1200)   # the want-home beat
	_check("three stings -> wants home, gate still shut",
			game.flag("prologue_want_home") and not game.flag("prologue_gate_open"))
	await _wait_frames(30)
	# the home door re-opens while he wants home — up tree 1 and press INTO it.
	# The zone hangs over the trunk face since 2026-08-22 (a press UP into the
	# door, so crossing the deck can't yank a body inside) — teleport a few px
	# into the face and let depenetration seat the body flush against it,
	# overlapping the raised zone (the zwalk seating idiom).
	_player().global_position = MapData.anchor_px(town_map, "top1") + Vector2(8.0, 8.0)
	ok = await _mash_until(in_boughs, 1500)
	_check("wanting home, tree 1's mouth climbs to the boughs", ok)
	await _wait_frames(70)
	_player().global_position = MapData.anchor_px(canopy_map, "home") + Vector2(8.0, -8.0)
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
	ok = await _mash_until(in_boughs, 900)
	_check("the front door returns to the boughs, gate open", ok)
	await _wait_frames(70)
	_player().global_position = MapData.anchor_px(canopy_map, "head1") + Vector2(8.0, 8.0)
	ok = await _mash_until(in_town, 1500)
	_check("...and the ladder puts him back on the floor", ok)
	await _wait_frames(40)

	# ---- south to the bluff meet (2026-07-18: the meadow was cut) -----------
	_player().global_position = MapData.anchor_px(town_map, "exit_south")
	var in_bluff := func() -> bool: return _scene_is("res://scene/bluff.tscn")
	ok = await _mash_until(in_bluff, 1200)
	_check("south gate travels to the bluff meet", ok)
	await _wait_frames(60)                # fade + lock

	# ---- meeting Kitty ------------------------------------------------------
	var bluff1 := current_scene
	var bluff_map: Dictionary = MapData.load_map("res://assets/maps/bluff.txt")
	_player().global_position = MapData.anchor_px(bluff_map, "kitty_pos") + Vector2(0.0, 40.0)
	var met_kitty := func() -> bool: return game.flag("prologue_met_kitty")
	ok = await _mash_until(met_kitty, 4000)
	_check("meeting Kitty starts the quest", ok)
	var box_closed := func() -> bool: return not bluff1.theater.dialog.visible
	ok = await _mash_until(box_closed, 1200)
	await _wait_frames(30)

	# ---- the three parts ----------------------------------------------------
	for part in ["gear", "spring", "crank"]:
		_player().global_position = MapData.anchor_px(bluff_map, "part_" + part)
		var found := func() -> bool: return game.flag("prologue_part_" + part)
		ok = await _mash_until(found, 900)
		_check("part found: " + part, ok)
		ok = await _mash_until(box_closed, 1200)
		await _wait_frames(20)

	# ---- the flight finale + THE IDEA -> his mother's kitchen ----------------
	_player().global_position = MapData.anchor_px(bluff_map, "kitty_pos") + Vector2(0.0, 40.0)
	var whirligig_done := func() -> bool: return game.flag("prologue_whirligig_done")
	ok = await _mash_until(whirligig_done, 9000)
	_check("Prologue A flight finale + the idea", ok)
	ok = await _mash_until(back_down, 2400)
	_check("the idea routes home to the fest downstairs", ok)
	await _wait_frames(40)

	# ==== THE BREW (2026-07-25) ===============================================
	# the workbench walk-gate, then the stir mash. The bench top is the map's
	# only `E` block and its pocket has one entrance, so the band is
	# unavoidable — derived from the map, never re-hardcoded.
	ok = await _mash_until(_party_free, 4000)
	_check("the brew beat hands over the walk to the bench", ok)
	_player().global_position = MapData.bbox_rect(down_map, "E").get_center()
	var potion := func() -> bool: return game.flag("prologue_potion_made")
	ok = await _mash_until(potion, 8000)
	_check("the stir mash brews the potion", ok)
	ok = await _mash_until(_party_free, 4000)
	_check("the brew hands control back", ok)
	await _wait_frames(20)

	# ---- out the front door, down the tree, across town, up to the Academy --
	_player().global_position = MapData.anchor_px(down_map, "exit_door")
	ok = await _mash_until(in_boughs, 1600)
	_check("the flask leaves by the front door", ok)
	await _wait_frames(70)
	_player().global_position = MapData.anchor_px(canopy_map, "head1") + Vector2(8.0, 8.0)
	ok = await _mash_until(in_town, 1500)
	_check("...and rides the ladder down with it", ok)
	await _wait_frames(70)                # entry fade + the entry lock
	# the south gate is SPENT now — it must refuse rather than replay the meet
	_player().global_position = MapData.anchor_px(town_map, "exit_south")
	await _wait_frames(60)
	_check("the spent south gate refuses", _scene_is("res://scene/town_fest.tscn"))
	ok = await _mash_until(_party_free, 2400)
	await _wait_frames(20)
	# the Academy door is LIVE: the same location node, flipped to travel. Land
	# ON the zone — a 16x12 rect centred on its anchor, NOT anchor+40, which is
	# town_thesis's separate dash GOAL area further down the plaza.
	_player().global_position = MapData.anchor_px(town_map, "school")
	var in_hall := func() -> bool: return _scene_is("res://scene/hall.tscn")
	ok = await _mash_until(in_hall, 4000)
	_check("the Academy door travels to the recital", ok)
	await _wait_frames(60)

	# ==== THE RECITAL =========================================================
	# the aisle gate, four colours, then the montage that used to live on the
	# bluff hands to the sunset romance.
	var hall_map: Dictionary = MapData.load_map("res://assets/maps/hall.txt")
	# gated on being in the HALL: _party_free alone is trivially true back in
	# the town we just left (the 2026-07-18 lesson about preds that are already
	# satisfied before the beat begins)
	var aisle_open := func() -> bool: return in_hall.call() and _party_free()
	ok = await _mash_until(aisle_open, 4000)
	_check("the recital hands over the walk up the aisle", ok)
	# the band across row 6 — the open strip south of the apron riser, the only
	# row touching it (the stage itself is a sealed region)
	var apron: Rect2 = MapData.bbox_rect(hall_map, "D")
	_player().global_position = Vector2(apron.get_center().x, apron.end.y + 8.0)
	var recital := func() -> bool: return game.flag("prologue_recital")
	ok = await _mash_until(recital, 16000)
	_check("the recital plays out (four colours, four bursts)", ok)
	ok = await _mash_until(in_bluff, 4000)
	_check("the recital hands off to the sunset romance", ok)
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
	# plant: the night-before lines -> the playable walk home -> up the tree
	# -> the doorstep call + the creep (both on the boughs since the split) ->
	# house_thesis
	ok = await _mash_until(_party_free, 3000)
	_check("the night-before hands over the walk home", ok)
	var in_boughs_night := func() -> bool: \
			return _scene_is("res://scene/canopy_thesis.tscn")
	_player().global_position = MapData.anchor_px(town_map, "top1") + Vector2(8.0, 8.0)
	ok = await _mash_until(in_boughs_night, 1500)
	_check("the walk home ends up tree 1's ladder", ok)
	await _wait_frames(70)
	# press the front door: the call, the quiet, the creep, the card
	_player().global_position = MapData.anchor_px(canopy_map, "home") + Vector2(8.0, -8.0)
	var in_wake := func() -> bool: return _scene_is("res://scene/house_thesis.tscn")
	ok = await _mash_until(in_wake, 9000)
	_check("the doorstep call + the creep -> the 8:57 wake-up", ok)
	await _wait_frames(30)

	# wake-up: mash through, then walk to the stair exit -> dash
	# (house_map was loaded for the home start — reuse it)
	var wake := current_scene
	var wake_closed := func() -> bool: return not wake.theater.dialog.visible
	ok = await _mash_until(wake_closed, 5000)     # the whole panic
	await _wait_frames(20)
	_player().global_position = MapData.anchor_px(house_map, "exit_door")
	# the morning opens ON THE DECK: the bag, the squelch, then the run drops
	# down the ladder and town_thesis's dash phase carries it to the Academy
	var in_dash := func() -> bool: return _scene_is("res://scene/canopy_thesis.tscn")
	ok = await _mash_until(in_dash, 1500)
	_check("wake-up -> the dash, on the deck", ok)
	await _wait_frames(40)

	# dash: mash the squelch beat on the deck, ride the mouth down, then run to
	# the school -> hall. End-state is _dashing, never dialog-invisible: the
	# box is also hidden through the opening entry-fade wait, which read as
	# "done" before the beat began.
	var deck := current_scene
	var deck_dashing := func() -> bool: return deck._dashing
	ok = await _mash_until(deck_dashing, 4000)    # squelch beat
	_check("the squelch hands over the run", ok)
	await _wait_frames(20)
	_player().global_position = MapData.anchor_px(canopy_map, "head1") + Vector2(8.0, 8.0)
	var in_ground_dash := func() -> bool: return _scene_is("res://scene/town_thesis.tscn")
	ok = await _mash_until(in_ground_dash, 1500)
	_check("the run drops to the floor mid-dash", ok)
	await _wait_frames(70)
	# The finish line's offset is READ OFF THE LIVE SCENE, never re-typed: this
	# was a hardcoded +40, the scene moved its goal to +24 in the Alembic rebuild
	# (the Academy became its own scene and `school` now names the north lane's
	# mouth), and a body parked 40px below the anchor has its collision box a
	# clear 10px under the rect — body_entered never fires and the dash hangs
	# with nothing in the log.
	var grun := current_scene
	_player().global_position = MapData.anchor_px(town_map, "school") + grun.DASH_GOAL_OFF
	ok = await _mash_until(in_hall, 5000)
	_check("dash -> the lecture hall", ok)
	await _wait_frames(40)

	# hall: Dean's welcome -> the walk-in gate -> the naming -> the AUTO walk
	# of shame (2026-07-17: his body gives up, not the player's) -> bluff
	# call1. The walk-in gate unlocks the party (the pollable state).
	ok = await _mash_until(_party_free, 2400)
	_check("the Dean's welcome hands over the walk-in", ok)
	# the walk-in gate is the band across the stage rows just west of the
	# podium (2026-07-18: the wing corridor is the only route onto the
	# stage) — land inside it, derived from the map, never re-hardcoded
	_player().global_position = Vector2(
			MapData.bbox_rect(hall_map, "L").position.x - 24.0,
			MapData.anchor_px(hall_map, "lectern_spot").y + 8.0)
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
	# sit, Ridley's blunt speech, the bowed head, night, then the leaving at
	# the south gate (the knapsack tableau, the look-back goodbye, the trudge
	# out the gate mouth) and the cards. Just mash the flags.
	var scolded := func() -> bool: return game.flag("prologue_scolded")
	ok = await _mash_until(scolded, 12000)
	_check("the scolding beat completes", ok)
	var prologue_done := func() -> bool: return game.flag("prologue_done")
	ok = await _mash_until(prologue_done, 12000)
	_check("the leaving completes the prologue", ok)

	# the Ebb night (2026-07-19): the leaving hands into scene/ebb.gd — the
	# mountain quake/crystal cutscene (the attack mash trips its polled skip
	# once armed) — then the Lanternwood library plays Fuji's dead-wand beat
	# onto the Ebb-night street (the adult build is ESC-skip-only now).
	var in_ebb := func() -> bool: return _scene_is("res://scene/ebb.tscn")
	ok = await _mash_until(in_ebb, 2500)
	_check("the leaving hands into the Ebb night", ok)
	var ebb_done := func() -> bool: return game.flag("ebb_done")
	ok = await _mash_until(ebb_done, 4000)
	_check("the Ebb plays (the mash skip fires)", ok)
	var in_library := func() -> bool: return _scene_is("res://scene/library.tscn")
	ok = await _mash_until(in_library, 4000)
	_check("the quake hands to the Lanternwood library", ok)
	# the story rests HERE now (2026-07-20): the dead-wand beat hands solo
	# Fuji the town — the same night, the street out comparing dead charms.
	# Since 2026-07-24 it hands CONTROL back in the room first (she has to
	# walk out and investigate), so this is a walk-gate like every other:
	# poll the unlock, then teleport to the door mouth. A mash alone would
	# hang here — attack only makes her swing her tome where she stands.
	var lib_map: Dictionary = MapData.load_map("res://assets/maps/library.txt")
	ok = await _mash_until(_party_free, 9000)
	_check("the dead-wand beat hands control back in the library", ok)
	_player().global_position = MapData.anchor_px(lib_map, "exit_door")
	var in_lanternwood := func() -> bool: return _scene_is("res://scene/lanternwood.tscn")
	ok = await _mash_until(in_lanternwood, 900)
	_check("Fuji walks out her own door into the town", ok)
	_check("solo Fuji roster", party.roster.size() == 1
			and party.roster[0] == &"fuji" and party.leader_id == &"fuji")
	await _wait_frames(40)               # entry fade settles; villagers cast
	_check("the Ebb-night street is peopled",
			current_scene.get_node("World").get_children().any(
					func(c: Node) -> bool: return c is NPC))

	print("prologue probe: %s" % ("ALL PASS" if _fails == 0 else "%d FAILED" % _fails))
	quit(1 if _fails > 0 else 0)
