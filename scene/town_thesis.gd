extends TravelScene

## Alembic Town on THESIS DAY — Prologue B (docs/DESIGN.md Story). One scene,
## four flag-driven phases dressed by a CanvasModulate tint (the tint law: one
## painting, never a repaint), routed by Game.town_thesis_phase:
##   plant    (night)   SEMI-PLAYABLE: the Academy stair -> the player's own
##                      walk home past Kitty's shuttered stall -> the doorstep
##                      bookend watch call -> Schweinler leaves the bag ->
##                      house_thesis
##   dash     (morning) the SQUELCH, the hop-the-puddles run, paw-print trail,
##                      Kitty's broken-axle stall cameo, reach the Academy ->
##                      hall
##   call     (dusk)    the shuttered stall, the call to Kitty, then the SHOWN
##                      accident (scene/accident.tscn) -> sickroom
##   fountain (dusk)    the classmate's cruelty, then the night leaving -> the
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
const FX_WATCH := 16               # row 2 of the fx sheet (the watch call)

const TINT_NIGHT := Color(0.42, 0.40, 0.66)
const TINT_MORNING := Color(0.98, 0.93, 0.86)
const TINT_DUSK := Color(0.74, 0.56, 0.66)

const PUDDLES := ["puddle_1", "puddle_2", "puddle_3"]

var phase := "plant"
var _print_accum := 0.0
var _last_print := Vector2.ZERO
var _puddles_cleared := 0
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
		"call", "fountain":
			Party.place(MapData.anchor_px(map, "school") + Vector2(0.0, 24.0))
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
		"call": _phase_call()
		"fountain": _phase_fountain()


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
	# watch SHE MADE blinking on his wrist — the same fx and the same
	# gesture as the dusk call after the naming, opposite emotional poles
	theater.face(player, Vector2.DOWN)
	var watch := WorldFx.airborne($World, FX_SHEET, 0,
			player.global_position + Vector2(10.0, 4.0), 36.0)
	watch.frame = FX_WATCH
	await theater.wait(0.5)
	await theater.say("Kitty", "Say it again. One more time. I want to hear it.")
	await theater.say("Basil", "...Tomorrow I present my thesis. As the youngest professor the Academy has ever made.")
	await theater.say("Kitty", "HA! There he is. Stall closes early tomorrow. Front row, center. The whooping is PREPARED.")
	await theater.say("Basil", "Please don't whoop. ...The watch you made me says it's past midnight, you know.")
	await theater.say("Kitty", "That watch keeps PERFECT time. It's the cat wearing it who runs late. Bed! You'll be brilliant tomorrow - you always are, once you stop being scared.")
	await theater.say("Basil", "...Goodnight, Kitty.")
	theater.close_dialog()
	watch.queue_free()
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
	await theater.say("Schweinler", "Heh heh heh. A little CONGRATULATIONS for Mr. Youngest-Professor-Ever.")
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


# ---- dash (morning): the squelch, puddles, paw-prints, reach the school ------------

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
	_spawn_puddles()
	_spawn_stall_kitty()
	_dashing = true
	theater.unlock_party()
	_show_banner("GET TO THE ACADEMY - K/SHIFT TO HOP THE PUDDLES", BANNER_HOLD)
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


func _spawn_puddles() -> void:
	for name in PUDDLES:
		var area := Area2D.new()
		area.collision_layer = 0
		area.collision_mask = 2
		area.position = MapData.anchor_px(map, name)
		var shape := CollisionShape2D.new()
		var circle := CircleShape2D.new()
		circle.radius = 11.0
		shape.shape = circle
		area.add_child(shape)
		# the splash icon depth-sorts with bodies; the Area2D itself is
		# collision-only and can stay on the root
		var icon := WorldFx.decal($World, FX_SHEET, 14, area.position)
		area.set_meta("icon", icon)
		area.set_meta("cleared", false)
		add_child(area)
		area.body_entered.connect(_on_puddle.bind(area))


func _on_puddle(body: Node2D, area: Area2D) -> void:
	if not body.is_in_group("player") or area.get_meta("cleared"):
		return
	if body.is_airborne():
		area.set_meta("cleared", true)
		_puddles_cleared += 1
		var icon := area.get_meta("icon") as Sprite2D
		icon.modulate.a = 0.35        # a hopped-over splash mark
	else:
		# stepped in it — a brief stumble
		area.set_meta("cleared", true)
		_puddles_cleared += 1
		_stumble()


func _stumble() -> void:
	if not _dashing:
		return
	_dashing = false
	theater.lock_party()
	player.sprite.play("hurt")
	await theater.say("Basil", "GAH - cold cold cold! My good lecture socks!")
	theater.close_dialog()
	player.sprite.play("idle_down")
	theater.unlock_party()
	_dashing = true


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


# ---- call (dusk): the call to Kitty, the accident over black ----------------------

func _phase_call() -> void:
	tint.color = TINT_DUSK
	theater.lock_party()
	theater.face(player, Vector2.DOWN)
	player.sprite.play("sad")
	await theater.wait(ENTRY_FADE + 0.4)
	await theater.say("Basil", "Poopy Paws. They're all still laughing. I can hear it from here.")
	await theater.say("Basil", "...Kitty. I need to hear Kitty. She always knows what to say.")
	theater.close_dialog()
	# down the grand stair to the square, at the player's pace — the gate is
	# the square itself (the fest cutscene's zone: the ring roads on every
	# side; a point-gate is walkable around), then the last steps to the old
	# post stand-mark are staged around the basin's west ring
	_show_banner("THE FOUNTAIN SQUARE - SOMEWHERE QUIET TO CALL HER", BANNER_HOLD)
	var basin := MapData.bbox_rect(map, "oO")
	await theater.walk_gate(basin.get_center(), Vector2(96.0, 96.0))
	await theater.walk_via(player, _post_route(player.global_position), 50.0)
	# the stall is two tiles away, shuttered — WHY he calls instead of
	# walking over, and why she has to take the dusk road to reach him
	await theater.say("Basil", "Her stall's shut. She never made it to the hall today. ...Good. Good. She didn't see it.")
	# the watch call (2026-07-15): comms on his wrist — the watch face
	# blinks awake over him while the connection hunts for her
	theater.face(player, Vector2.DOWN)
	var watch := WorldFx.airborne($World, FX_SHEET, 0,
			player.global_position + Vector2(10.0, 4.0), 36.0)
	watch.frame = FX_WATCH
	await theater.wait(0.5)
	# the bookend rhyme: "that watch keeps PERFECT time," the night before
	await theater.say("Basil", "Pick up. Come on. You built this thing and it has never once failed - pick UP.")
	await theater.say("Basil", "Kitty. It's me. It's bad. The lecture, Schweinler, the whole hall - please pick up.")
	await theater.say("Kitty", "Oh no... that asshole. I'm coming! Stay where you are!")
	await theater.say("Basil", "Wait - it's nearly dark, don't take the road - Kitty? ...She's already pedaling.")
	theater.close_dialog()
	watch.queue_free()
	await theater.black(1.0)
	# the accident is SHOWN now — the side-view set-piece owns the flag
	get_tree().change_scene_to_file("res://scene/accident.tscn")


# ---- fountain (dusk) + the leaving (night) ----------------------------------------

func _phase_fountain() -> void:
	tint.color = TINT_DUSK
	theater.lock_party()
	player.sprite.play("sad")
	var badger: NPC = _npc("Ridley", SHEET_BADGER, 4,
			MapData.anchor_px(map, "classmate_pos"))
	await theater.wait(ENTRY_FADE + 0.4)
	# the long walk down to the square is the player's own (the pacing pass);
	# the gate is the square itself, then the last steps to the rim are
	# staged around the basin
	_show_banner("THE FOUNTAIN SQUARE", BANNER_HOLD)
	await theater.walk_gate(MapData.bbox_rect(map, "oO").get_center(), Vector2(96.0, 96.0))
	await theater.walk_via(player, _square_route(player.global_position,
			MapData.anchor_px(map, "festival")), 46.0)
	await theater.say("", "Basil sits at the fountain until the sky goes violet. A classmate finds him.")
	await theater.say("Ridley", "Hey. Basil, right? Rough day, huh. Heard about the lecture. AND the... y'know.")
	await theater.say("Ridley", "So what's eating you? You've been staring at that water for an hour.")
	await theater.say("Basil", "She doesn't know me. Kitty. She woke up and she looked right through me. The doctor says it's permanent.")
	await theater.say("Basil", "And they're STILL laughing about the name. I lost everything today. In one day.")
	await theater.wait(0.5)
	await theater.say("Ridley", "Wow. You know what? That's pretty selfish.")
	player.sprite.play("hurt")
	await theater.say("Ridley", "YOU weren't the one who got run over. SHE'S the one in the bed. And you're over here feeling sorry for YOURSELF?")
	await theater.say("Ridley", "...I'm just saying. Perspective. Anyway. Feel better!")
	badger.queue_free()
	await theater.wait(0.8)
	await theater.say("Basil", "...")
	theater.close_dialog()
	# night falls; the leaving
	var tw := create_tween()
	tw.tween_property(tint, "color", TINT_NIGHT, 2.0)
	await tw.finished
	await theater.say("Basil", "...He's right. What kind of person makes this about himself.")
	await theater.say("Basil", "I can't be here. I can't be ANYWHERE people are.")
	theater.close_dialog()
	_show_banner("LEAVE TOWN - THE SOUTH GATE", BANNER_HOLD)
	$ExitSouth.body_entered.connect(_on_leave)
	# the pollable end-state for the probe: this phase unlocks twice (the
	# walk-gate and here), so is_physics_processing() alone is ambiguous
	Game.set_flag("prologue_scolded")
	theater.unlock_party()


func _on_leave(body: Node) -> void:
	if not body.is_in_group("player") or _busy:
		return
	_busy = true
	theater.lock_party()
	await theater.black(1.5)
	await theater.card("He took a stick and a knapsack, and he walked east.", 2.4)
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


## Road-ring route around the solid fountain (same rule as town_fest's:
## theater walks are straight no-collision tweens; dog-leg the ring).
func _square_route(from: Vector2, to: Vector2) -> Array:
	var basin := MapData.bbox_rect(map, "oO")
	var west := from.x < basin.get_center().x
	var ring_x := basin.position.x - 8.0 if west else basin.end.x + 8.0
	var pts := []
	if from.y < basin.position.y + 16.0:
		pts.append(Vector2(ring_x, basin.position.y - 8.0))
		pts.append(Vector2(ring_x, basin.end.y + 8.0))
	elif from.y < basin.end.y + 8.0:
		pts.append(Vector2(ring_x, basin.end.y + 8.0))
	pts.append(to)
	return pts


## Ring route to the watch-call stand mark (the old `post` anchor) on the
## basin's WEST ring: unlike the south-side targets _square_route serves,
## east/south arrivals must loop under the basin to the west road first.
func _post_route(from: Vector2) -> Array:
	var basin := MapData.bbox_rect(map, "oO")
	var w := basin.position.x - 8.0
	var e := basin.end.x + 8.0
	var n := basin.position.y - 8.0
	var s := basin.end.y + 8.0
	var pts := []
	if from.x > basin.get_center().x and from.y >= basin.position.y + 16.0:
		pts.append(Vector2(e, s))
		pts.append(Vector2(w, s))
	elif from.y >= s:
		pts.append(Vector2(w, s))
	elif from.y < basin.position.y + 16.0:
		pts.append(Vector2(w, n))
	pts.append(MapData.anchor_px(map, "post"))
	return pts


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
