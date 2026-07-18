extends TravelScene

## Alembic Town on THESIS DAY — Prologue B (docs/DESIGN.md Story). One scene,
## four flag-driven phases dressed by a CanvasModulate tint (the tint law: one
## painting, never a repaint), routed by Game.town_thesis_phase:
##   plant    (night)   SEMI-PLAYABLE: the Academy stair -> the player's own
##                      walk home past Kitty's shuttered stall -> the doorstep
##                      bookend watch call -> Schweinler leaves the bag ->
##                      house_thesis
##   dash     (morning) the SQUELCH, the paw-print dash across town,
##                      Kitty's broken-axle stall cameo, reach the Academy ->
##                      hall (the dusk calls now play on the BLUFF —
##                      scene/bluff.gd "call1"/"call2" bracket the accident)
##   steps    (dusk)    out of the doctor's door onto the clinic steps —
##                      Ridley's blunt "perspective," the bowed head, then
##                      the night leaving (stick + knapsack, east) -> the
##                      closing cards and the hand-off to the adult build
## Rides the festival town's map + tiles (same era-frozen village); this is the
## same day the festival palette shows, just tinted by hour.

const MAP_PATH := "res://assets/maps/town_fest.txt"
const LAYOUT_PATH := "res://assets/tilesets/town_fest_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const FX_SHEET := preload("res://assets/prologue_fx.png")
const SHEET_SCHW := preload("res://assets/npc_schweinler_adult_gen.png")
const SHEET_BADGER := preload("res://assets/npc_badger_gen.png")
const SHEET_KITTY_ADULT := preload("res://assets/npc_kitty_adult_gen.png")

const FX_BAG := 10
const FX_PRINT := 11

const TINT_NIGHT := Color(0.42, 0.40, 0.66)
const TINT_MORNING := Color(0.98, 0.93, 0.86)
const TINT_DUSK := Color(0.74, 0.56, 0.66)

var phase := "plant"
var _print_accum := 0.0
var _last_print := Vector2.ZERO
var _dashing := false

@onready var theater: Theater = $Theater
@onready var tint: CanvasModulate = $Tint


func _player_node() -> Node2D:
	return Party.spawn($World, Vector2.ZERO)


func _map_path() -> String:
	return MAP_PATH


func _layout_path() -> String:
	return LAYOUT_PATH


func _place_player() -> void:
	phase = Game.town_thesis_phase
	Game.town_thesis_phase = ""
	if phase == "":
		phase = "plant"
	match phase:
		"dash":
			Party.place(MapData.anchor_px(map, "home") + Vector2(0.0, 24.0))
		"steps":
			Party.place(MapData.anchor_px(map, "cottage_e"))
		_:
			# plant opens at the Academy stair — Basil's been prepping the
			# hall; the walk home is the player's own (2026-07-16, the
			# night-before made playable)
			Party.place(MapData.anchor_px(map, "school") + Vector2(0.0, 24.0))


func _extra_setup() -> void:
	PropSpawner.build("res://assets/tilesets/town_fest_props.txt", map, $World)
	$ExitSouth.position = MapData.anchor_px(map, "exit_south")
	_wall_gate_mouth()
	Party.clamp_cameras(MapData.size_px(map))
	match phase:
		"plant": _phase_plant()
		"dash": _phase_dash()
		"steps": _phase_steps()


# ---- plant (night) ----------------------------------------------------------------

func _phase_plant() -> void:
	tint.color = TINT_NIGHT
	theater.lock_party()
	# the night before, PLAYABLE (2026-07-16): Basil has been prepping the
	# hall all evening; the walk home through the sleeping town is the
	# player's own, past Kitty's shuttered stall, down to the doorstep call
	theater.face(player, Vector2.DOWN)
	await theater.wait(ENTRY_FADE + 0.4)
	await theater.say("Basil", "Notes stacked. Chalk lined up. Diagrams pinned STRAIGHT. Nothing left to fuss with.")
	await theater.say("Basil", "Home. Sleep. Tomorrow I become a professor.")
	theater.close_dialog()
	_arm_stall_night()
	_show_banner("HOME - GET SOME SLEEP", BANNER_HOLD)
	await theater.walk_gate(MapData.anchor_px(map, "home") + Vector2(0.0, 26.0),
			Vector2(40.0, 24.0))
	# the bookend call (2026-07-16 Kitty thread): on his own doorstep, the
	# watch SHE MADE raised to his muzzle — the same look_watch gesture as
	# the bluff's first blink and the dusk calls, opposite emotional poles
	theater.face(player, Vector2.DOWN)
	player.sprite.play("look_watch")
	await theater.wait(0.5)
	await theater.say("Kitty", "Say it again. One more time. I want to hear it.")
	await theater.say("Basil", "...Tomorrow I present my thesis. Not one spark to my name, and they still have to hand me the robes.")
	await theater.say("Kitty", "Because you EARNED them. Every wiggle-fingers in that hall calls your work 'potions.' Let them. You and I know what it really is.")
	await theater.say("Basil", "Chemistry. Measured, repeatable, REAL. ...Say THAT part again tomorrow if I wobble.")
	await theater.say("Kitty", "Front row, center. Stall closes early. The whooping is PREPARED.")
	await theater.say("Basil", "Please don't whoop. ...The watch you made me says it's past midnight, you know.")
	await theater.say("Kitty", "That watch keeps PERFECT time. It's the cat wearing it who runs late. Bed! You'll be brilliant tomorrow - you always are, once you stop being scared.")
	await theater.say("Basil", "...Goodnight, Kitty.")
	theater.close_dialog()
	player.sprite.play("idle_down")
	theater.face(player, Vector2.UP)
	await theater.walk(player, MapData.anchor_px(map, "home") + Vector2(0.0, 12.0), 40.0)
	player.visible = false            # inside; the yard goes quiet
	await theater.wait(0.8)
	var schw: NPC = _npc("Schweinler", SHEET_SCHW, 6, MapData.anchor_px(map, "exit_south"))
	await theater.say("", "The town sleeps. A shape creeps up to Basil's door.")
	# theater walks are straight no-collision tweens — creep the LANES (up
	# the gate road, around the fountain's west ring, west down the main
	# lane), never the diagonal through the shop blocks
	await theater.walk_via(schw, [
			Vector2(440.0, 384.0),
			Vector2(408.0, 384.0),
			Vector2(408.0, 312.0),
			Vector2(168.0, 312.0),
			MapData.anchor_px(map, "home") + Vector2(0.0, 26.0)], 44.0)
	schw.play_idle()
	# the bag
	var bag := _fx_at(FX_BAG, MapData.anchor_px(map, "home") + Vector2(0.0, 18.0))
	await theater.say("Schweinler", "Heh heh heh. A little CONGRATULATIONS for the sparkless wonder and his little POTIONS.")
	schw.play_emote()
	await theater.say("Schweinler", "Enjoy your big lecture tomorrow, Basil. Oink - hahaha!")
	await theater.walk_via(schw, [
			Vector2(408.0, 312.0),
			Vector2(408.0, 384.0),
			Vector2(440.0, 384.0),
			MapData.anchor_px(map, "exit_south")], 60.0)
	schw.queue_free()
	bag.queue_free()
	theater.close_dialog()
	await theater.black(1.0)
	await theater.card("THE NEXT MORNING.", 1.8)
	get_tree().change_scene_to_file("res://scene/house_thesis.tscn")


# ---- dash (morning): the squelch, paw-prints, reach the school ---------------------

func _phase_dash() -> void:
	tint.color = TINT_MORNING
	theater.lock_party()
	theater.face(player, Vector2.DOWN)
	await theater.wait(ENTRY_FADE + 0.3)
	await theater.say("Basil", "The lecture! I OVERSLEPT! First lecture as a professor and I overslept!")
	# the squelch
	var bag := _fx_at(FX_BAG, player.global_position + Vector2(0.0, 10.0))
	await theater.wait(0.3)
	await theater.say("", "*SQUELCH.*")
	await theater.hop(player, 6.0)
	await theater.say("Basil", "...I do not have time to think about what that was.")
	await theater.say("Basil", "Gotta go gotta go GOTTA GO!")
	bag.queue_free()
	theater.close_dialog()
	_spawn_stall_kitty()
	_dashing = true
	theater.unlock_party()
	_show_banner("GET TO THE ACADEMY", BANNER_HOLD)
	# the Academy stair is the finish
	var goal := Area2D.new()
	goal.collision_layer = 0
	goal.collision_mask = 2
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(48, 16)
	shape.shape = rect
	goal.add_child(shape)
	goal.position = MapData.anchor_px(map, "school") + Vector2(0.0, 40.0)
	add_child(goal)
	goal.body_entered.connect(_on_reach_school)


func _on_reach_school(body: Node2D) -> void:
	if not body.is_in_group("player") or not _dashing:
		return
	_dashing = false
	theater.lock_party()
	await theater.say("Basil", "Made it. Okay. Deep breath. You are a professor. You belong here.")
	theater.close_dialog()
	await fade_out()
	get_tree().change_scene_to_file("res://scene/hall.tscn")


func _physics_process(_delta: float) -> void:
	# drop a fading paw-print trail behind Basil during the dash
	if not _dashing or not is_instance_valid(player):
		return
	if player.global_position.distance_to(_last_print) >= 14.0:
		_last_print = player.global_position
		_drop_print(player.global_position + Vector2(0.0, 8.0))


func _drop_print(pos: Vector2) -> void:
	var p := WorldFx.decal($World, FX_SHEET, FX_PRINT, pos)
	var tw := p.create_tween()
	tw.tween_interval(1.2)
	tw.tween_property(p, "modulate:a", 0.0, 1.4)
	tw.tween_callback(p.queue_free)


# ---- steps (dusk) + the leaving (night) --------------------------------------------
## The clinic-steps ending (2026-07-17): Basil gets six steps out of the
## doctor's door and folds onto the stoop. Ridley finds him there, says the
## blunt thing, and leaves — Basil barely speaks; the bowed head says it.
## Then the cut: the town's east lane at night, a stick and a knapsack, and
## he walks out of the story. Fully scripted on purpose — the user's agency
## spent itself at the sickroom door; this part just happens TO him.

func _phase_steps() -> void:
	tint.color = TINT_DUSK
	theater.lock_party()
	# out the doctor's door — the east neighbor cottage; he lands on the
	# door mouth, feet on the lane below the arch
	Party.place(MapData.anchor_px(map, "cottage_e"))
	player.sprite.play("sad")
	await theater.wait(ENTRY_FADE + 0.4)
	await theater.say("", "He makes it exactly six steps past the door.")
	theater.close_dialog()
	await theater.walk(player, MapData.anchor_px(map, "cottage_e") + Vector2(4.0, 14.0), 26.0)
	player.sprite.play("sit")             # down onto the clinic steps
	player.sprite.flip_h = false          # profile east, where the lane runs
	await theater.wait(1.6)
	# Ridley comes up the lane — the witness, still carrying it
	var badger: NPC = _npc("Ridley", SHEET_BADGER, 6, Vector2(430.0, 456.0))
	await theater.walk(badger, MapData.anchor_px(map, "cottage_e") + Vector2(38.0, 14.0), 44.0)
	await theater.say("Ridley", "Hey. Basil, right? I was there. On the road. I saw the whole thing.")
	await theater.say("Ridley", "The doctor won't say it plain, so: how is she?")
	await theater.say("Basil", "...")
	await theater.wait(0.6)
	await theater.say("Ridley", "That bad. ...You know what? Sitting out here like the sky fell on YOU - that's pretty selfish.")
	player.sprite.play("hurt")
	await theater.wait(0.4)
	player.sprite.play("sit")
	await theater.say("Ridley", "YOU weren't the one who got run over. SHE'S the one in the bed. And you're over here feeling sorry for YOURSELF?")
	await theater.say("Ridley", "...I'm just saying. Perspective. Anyway. Feel better!")
	theater.close_dialog()
	# he says his piece and walks off — nobody stops him
	await theater.walk(badger, Vector2(430.0, 456.0), 52.0)
	badger.queue_free()
	await theater.wait(0.8)
	await theater.say("Basil", "...")
	theater.close_dialog()
	player.sprite.play("bow_head")        # the slump past sad — no more words
	# night falls on him sitting there
	var tw := create_tween()
	tw.tween_property(tint, "color", TINT_NIGHT, 2.4)
	await tw.finished
	await theater.wait(1.2)
	# the pollable end-state for the probe (kept from the fountain phase)
	Game.set_flag("prologue_scolded")
	await theater.black(1.4)
	_leaving()


## The cut: the east lane at night. A stick, a knapsack, and out of town.
func _leaving() -> void:
	Party.place(Vector2(520.0, 312.0))    # the east lane, before the bridge
	player.sprite.play("knapsack")
	player.sprite.flip_h = false          # facing east — the way he'll walk
	await theater.clear(1.2)
	await theater.wait(1.8)               # the tableau holds: hitchhiker Basil
	player.sprite.play("knapsack_walk")
	var walk := create_tween()
	walk.tween_property(player, "global_position",
			Vector2(770.0, 312.0), 5.0)   # east, over the bridge, gone
	await theater.wait(3.4)
	await theater.black(1.6)
	if walk.is_running():
		walk.kill()
	await theater.card("The laughter followed him to the town line.  He did not go back.", 2.6)
	await theater.card("He stopped going anywhere at all.", 2.2)
	await theater.card("He kept the watch.", 1.8)
	await theater.card("YEARS LATER.", 2.0)
	Game.set_flag("prologue_done")
	Party.set_roster([&"basil", &"fuji"], &"basil")
	get_tree().change_scene_to_file("res://scene/house.tscn")


# ---- Kitty's stall (2026-07-16 Kitty thread) ---------------------------------------
## The fountain-rim stall is canonically HERS in the college era. Night
## before: shuttered, an optional pass-by line on the walk home. Thesis
## morning: she's wrestling a broken cart axle as Basil tears past — the
## mundane, maker-shaped reason the front-row promise breaks (she never
## sees the naming; the dusk call's "she didn't see it" hangs on this).

func _stall_center() -> Vector2:
	return MapData.bbox_rect(map, "m").get_center()


func _arm_stall_night() -> void:
	var zone := _stall_zone(40.0)
	zone.body_entered.connect(func(body: Node2D) -> void:
		if not body.is_in_group("player") or zone.get_meta("done", false) \
				or _busy:
			return
		zone.set_meta("done", true)
		theater.lock_party()
		await theater.say("Basil", "Her stall's shut up for the night. Good. Front row tomorrow, she said - she'd better be asleep too.")
		theater.close_dialog()
		theater.unlock_party())


func _spawn_stall_kitty() -> void:
	var kitty := _npc("Kitty", SHEET_KITTY_ADULT, 6,
			_stall_center() + Vector2(0.0, 20.0))
	kitty.play_act()                  # hunched over the axle
	var zone := _stall_zone(48.0)
	zone.body_entered.connect(func(body: Node2D) -> void:
		if not body.is_in_group("player") or zone.get_meta("done", false):
			return
		zone.set_meta("done", true)
		kitty.play_emote()
		_show_banner("KITTY: STUPID AXLE! GO GO GO - YOU'RE LATE!!", BANNER_HOLD))


func _stall_zone(radius: float) -> Area2D:
	var zone := Area2D.new()
	zone.collision_layer = 0
	zone.collision_mask = 2
	var shape := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = radius
	shape.shape = circle
	zone.add_child(shape)
	zone.position = _stall_center()
	zone.set_meta("done", false)
	add_child(zone)
	return zone


# ---- helpers ----------------------------------------------------------------------

## Same wall as town_fest's: the gate-mouth road runs to the map edge and
## the dash/call phases never wire the exit — without it a body can walk
## off the south edge into the void.
func _wall_gate_mouth() -> void:
	var wall := StaticBody2D.new()
	wall.collision_layer = 1
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(64.0, 8.0)
	shape.shape = rect
	wall.add_child(shape)
	wall.position = Vector2($ExitSouth.position.x, MapData.size_px(map).y + 4.0)
	add_child(wall)


func _npc(nm: String, sheet: Texture2D, cols: int, pos: Vector2) -> NPC:
	var npc: NPC = NPCScene.instantiate()
	npc.display_name = nm
	npc.sheet = sheet
	npc.frame_cols = cols
	npc.position = pos
	$World.add_child(npc)
	return npc


func _fx_at(cell: int, pos: Vector2) -> Sprite2D:
	# ground clutter (the bag) — a World decal so bodies pass in front of it
	return WorldFx.decal($World, FX_SHEET, cell, pos)
