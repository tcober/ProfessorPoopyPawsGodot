extends TravelScene

## Alembic Town on THESIS DAY — Prologue B (docs/DESIGN.md Story). One scene,
## four flag-driven phases dressed by a CanvasModulate tint (the tint law: one
## painting, never a repaint), routed by Game.town_thesis_phase:
##   plant    (night)   SEMI-PLAYABLE: the Academy stair -> the player's own
##                      walk home through the sleeping town -> the doorstep
##                      bookend watch call -> Schweinler leaves the bag ->
##                      house_thesis
##   dash     (morning) the step ONTO the bag is SHOWN, then the SQUELCH and
##                      the paw-print dash across town to the Academy ->
##                      hall (the dusk calls now play on the BLUFF —
##                      scene/bluff.gd "call1"/"call2" bracket the accident;
##                      Kitty is absent: her wheel workshop is off-screen,
##                      the busted-axle excuse lands in the bluff's call1)
##   steps    (dusk)    out of the doctor's door onto the clinic steps —
##                      Ridley's blunt "perspective," the bowed head, then
##                      the night leaving (the bindle tableau, the look-back,
##                      the south trudge out the gate) -> the
##                      closing cards and the hand-off to the adult build
## Rides the festival town's map + tiles (same era-frozen village); this is the
## same day the festival palette shows, just tinted by hour.

const MAP_PATH := "res://assets/maps/town_fest.txt"
const LAYOUT_PATH := "res://assets/tilesets/town_fest_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const FX_SHEET := preload("res://assets/prologue_fx.png")
const SHEET_SCHW := preload("res://assets/npc_schweinler_adult_gen.png")
const SHEET_BADGER := preload("res://assets/npc_badger_gen.png")

const FX_BAG := 10
const FX_PRINT := 11
## Where Schweinler leaves the bag and where Basil steps on it — ONE spot
## (the doorstep lane, just south of the door arch), relative to the "home"
## anchor: the morning bag must sit exactly where the night phase left it.
const BAG_OFF := Vector2(0.0, 38.0)

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
			# ON the door marker (the door-mouth convention) — the walk onto
			# the bag below needs the step south to be visible
			Party.place(MapData.anchor_px(map, "home"))
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
	# player's own, down to the doorstep call
	theater.face(player, Vector2.DOWN)
	await theater.wait(ENTRY_FADE + 0.4)
	await theater.say("Basil", "Notes stacked. Chalk lined up. Diagrams pinned STRAIGHT. Nothing left to fuss with.")
	await theater.say("Basil", "Home. Sleep. Tomorrow I become a professor.")
	theater.close_dialog()
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
	await theater.say("Basil", "...Tomorrow I present my thesis. Not one drop of magic to my name, and they still have to hand me the robes.")
	await theater.say("Kitty", "Because you EARNED them. Every wiggle-fingers in that hall calls your work 'potions.' Let them. You and I know what it really is.")
	await theater.say("Basil", "Chemistry. Measured, repeatable, REAL. ...Say THAT part again tomorrow if I wobble.")
	await theater.say("Kitty", "Front row, center. I'll shut the workshop early. The whooping is PREPARED.")
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
	# no narrator over the creep (the 2026-07-18 purge): the sleeping town
	# holds a quiet beat, then the shape slinks the lanes on its own
	await theater.wait(1.0)
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
	# the bag — dropped at BAG_OFF, right where the morning step will land
	var bag := _fx_at(FX_BAG, MapData.anchor_px(map, "home") + BAG_OFF)
	await theater.say("Schweinler", "Heh heh heh. A little CONGRATULATIONS for the no-magic wonder and his little POTIONS.")
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
	# the bag is already THERE — planted last night, waiting through the line
	var bag := _fx_at(FX_BAG, MapData.anchor_px(map, "home") + BAG_OFF)
	await theater.wait(ENTRY_FADE + 0.3)
	await theater.say("Basil", "The lecture! I OVERSLEPT! First lecture as a professor and I overslept!")
	# the step is SHOWN: he bolts south, straight onto it (the box stays OPEN
	# across the walk — the probe's dialog-closed predicate must not flip
	# before the squelch)
	await theater.walk(player, MapData.anchor_px(map, "home") + Vector2(0.0, 22.0), 72.0)
	# the squelch is PLAYED, not narrated (2026-07-18): the landing hop is
	# the flinch off the bag, and his own line names what his paw just learned
	await theater.hop(player, 6.0)
	await theater.say("Basil", "Ew. EW. Squishy. Why was that SQUISHY?!")
	await theater.say("Basil", "...I do not have time to think about what that was.")
	await theater.say("Basil", "Gotta go gotta go GOTTA GO!")
	theater.close_dialog()
	# the bag lingers a beat underfoot and fades, instead of blinking away
	var btw := bag.create_tween()
	btw.tween_interval(0.4)
	btw.tween_property(bag, "modulate:a", 0.0, 0.9)
	btw.tween_callback(bag.queue_free)
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
## Then the cut: the south gate at night — the knapsack, one look back at the
## town, the goodbye he owes nobody, and he walks out of the story. Fully
## scripted on purpose — the user's agency spent itself at the sickroom door;
## this part just happens TO him.

func _phase_steps() -> void:
	tint.color = TINT_DUSK
	theater.lock_party()
	# out the doctor's door — the east neighbor cottage; he lands on the
	# door mouth, feet on the lane below the arch
	Party.place(MapData.anchor_px(map, "cottage_e"))
	player.sprite.play("sad")
	await theater.wait(ENTRY_FADE + 0.4)
	# no "six steps" narrator (2026-07-18) — the six steps are just WALKED,
	# slow, and then his legs quit
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


## The cut: the south gate at night. A knapsack over his shoulder, one look
## back at the town (2026-07-18 — restaged from the east lane), and out.
func _leaving() -> void:
	Party.place(Vector2(440.0, 460.0))    # the central road, just inside the gate
	player.sprite.play("knapsack")
	player.sprite.flip_h = false          # profile: the held tableau
	await theater.clear(1.2)
	await theater.wait(1.8)               # the tableau holds: knapsack Basil
	# the look back: he turns to face the town he's leaving
	player.sprite.play("knapsack_back")
	player.sprite.flip_h = false
	await theater.wait(1.2)
	await theater.say("Basil", "...Goodbye.")
	await theater.say("Basil", "I would have loved being yours. Your chemist. Your neighbor. Anything.")
	await theater.say("Basil", "I wish I could have been welcome here.")
	theater.close_dialog()
	await theater.wait(1.0)
	# then he turns away and trudges out the lamp-flanked gate — the turn is a
	# beat of profile, then the SOUTH-facing trudge (2026-07-19: the walk used
	# to play the side clip while tweening south and read as a sideways glide)
	player.sprite.play("knapsack")
	player.sprite.flip_h = false
	await theater.wait(0.5)               # the turn: a profile flash...
	player.sprite.play("knapsack_walk_down")   # ...then face down the road
	var walk := create_tween()
	walk.tween_property(player, "global_position",
			Vector2(440.0, 545.0), 4.6)   # south, through the gate mouth, gone
	await theater.wait(2.8)
	await theater.black(1.6)
	if walk.is_running():
		walk.kill()
	# one TIME card only (the 2026-07-18 card purge — the hermit years and
	# the kept watch are shown by the adult build itself: the shut-in house,
	# the mantel whirligig, look_watch)
	await theater.card("YEARS LATER.", 2.0)
	Game.set_flag("prologue_done")
	Party.set_roster([&"basil", &"fuji"], &"basil")
	get_tree().change_scene_to_file("res://scene/house.tscn")


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
