extends TravelScene

## Whisker Meadow, FESTIVAL ERA — Prologue A's second half (docs/DESIGN.md
## Story): the same meadow map as the combat zone, decades earlier and SAFE —
## no slimes, no beakers, no HUD. Kid Basil comes here to pout and finds a
## girl cat wrestling a hand-cranked whirligig. The fetch-quest (gear on the
## beach, spring in the flowers, crank by the boulders) teaches the
## explore/interact loop; the flight cutscene ends the chapter and the montage
## cards hand the game off to the adult build ("YEARS LATER.").
##
## Rides TravelScene for the entry fade / banner / camera plumbing with an
## empty Locations set; quest state lives in Game.flags so leaving mid-quest
## and coming back keeps progress.

const MAP_PATH := "res://assets/maps/meadow.txt"
const LAYOUT_PATH := "res://assets/tilesets/meadow_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const FX_SHEET := preload("res://assets/prologue_fx.png")
const SHEET_KITTY := preload("res://assets/npc_kitty_gen.png")

## fx strip cells (prologue_fx.png is a 16-wide grid, TWO rows since the
## accident set-piece — always slice it via WorldFx.sheet_sprite, which
## infers vframes from the sheet height)
const FX_SPARK0 := 2
const FX_SPARK1 := 3
const FX_GEAR := 4
const FX_SPRING := 5
const FX_CRANK := 6
const FX_WHIRL_DROOP := 7
const FX_WHIRL_SPIN0 := 8

const PARTS := {
	"gear": {"anchor": "part_gear", "cell": FX_GEAR,
		"line": "A brass gear, snoozing in the wet sand."},
	"spring": {"anchor": "part_spring", "cell": FX_SPRING,
		"line": "The spring! It bounced ALL the way out here."},
	"crank": {"anchor": "part_crank", "cell": FX_CRANK,
		"line": "One wooden crank, hiding by the boulders. Classic crank."},
}

var _kitty: NPC
var _whirligig: Sprite2D
var _busy_scene := false
var _flying := false

@onready var theater: Theater = $Theater


func _player_node() -> Node2D:
	return Party.spawn($World, Vector2.ZERO)


func _map_path() -> String:
	return MAP_PATH


func _layout_path() -> String:
	return LAYOUT_PATH


func _place_player() -> void:
	Party.place(MapData.anchor_px(map, "enter_south"))


func _extra_setup() -> void:
	$ExitSouth.position = MapData.anchor_px(map, "exit_south")
	$ExitSouth.body_entered.connect(_on_exit_south)
	Party.clamp_cameras(MapData.size_px(map))
	_spawn_kitty()
	_spawn_whirligig()
	for part: String in PARTS:
		if not Game.flag("prologue_part_" + part):
			_spawn_part(part)
	# the meeting trigger: a wide zone around Kitty's work spot
	var zone := Area2D.new()
	zone.collision_layer = 0
	zone.collision_mask = 2
	var shape := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 52.0
	shape.shape = circle
	zone.add_child(shape)
	zone.position = _kitty.position
	add_child(zone)
	zone.body_entered.connect(_on_kitty_zone)


# ---- the cast ----------------------------------------------------------------

func _spawn_kitty() -> void:
	_kitty = NPCScene.instantiate()
	_kitty.display_name = "Kitty"
	_kitty.sheet = SHEET_KITTY
	_kitty.frame_cols = 6
	_kitty.lines = PackedStringArray([
		"The gear likes the beach. The spring went SPROING toward the flowers.",
		"The crank? Honestly, no idea. Cranks are free spirits. Try the boulders.",
	]) if Game.flag("prologue_met_kitty") else PackedStringArray([])
	_kitty.position = MapData.anchor_px(map, "kitty_pos")
	$World.add_child(_kitty)          # _ready runs here, so the sprite is live
	if not _all_parts_found():
		_kitty.play_act()             # she starts hunched over the whirligig


func _spawn_whirligig() -> void:
	# sheet_sprite, not a raw hframes=16 Sprite2D: the fx sheet is two rows
	# now, and a bare hframes slice would cut 16x32 frames (8px off-center)
	_whirligig = WorldFx.sheet_sprite(FX_SHEET, FX_WHIRL_DROOP)
	_whirligig.position = MapData.anchor_px(map, "whirligig") + Vector2(0.0, -4.0)
	$World.add_child(_whirligig)


func _spawn_part(part: String) -> void:
	var cfg: Dictionary = PARTS[part]
	var area := Area2D.new()
	area.collision_layer = 0
	area.collision_mask = 2
	area.position = MapData.anchor_px(map, cfg["anchor"])
	var shape := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 10.0
	shape.shape = circle
	area.add_child(shape)
	# the part icon is a ground decal and the sparkle floats over it — both
	# depth-sort with bodies in $World (the whirligig treatment); the Area2D
	# stays root, collision-only
	var icon := WorldFx.decal($World, FX_SHEET, cfg["cell"], area.position)
	area.set_meta("icon", icon)
	var spark := WorldFx.airborne($World, FX_SHEET, FX_SPARK0,
			area.position + Vector2(6.0, 0.0), 8.0)
	area.set_meta("spark", spark)
	var tw := spark.create_tween().set_loops()
	tw.tween_callback(func() -> void: spark.frame = FX_SPARK1).set_delay(0.4)
	tw.tween_callback(func() -> void: spark.frame = FX_SPARK0).set_delay(0.4)
	add_child(area)
	area.body_entered.connect(_on_part_touched.bind(part, area))


# ---- quest flow ---------------------------------------------------------------

func _on_kitty_zone(body: Node2D) -> void:
	if body.is_in_group("player") and not Game.flag("prologue_met_kitty") \
			and not _busy_scene:
		_meet_kitty()
	elif body.is_in_group("player") and _all_parts_found() \
			and Game.flag("prologue_met_kitty") and not _busy_scene and not _flying:
		_flight_finale()


func _meet_kitty() -> void:
	_busy_scene = true
	theater.lock_party()
	await theater.walk(player, _kitty.position + Vector2(-26.0, 12.0), 55.0)
	theater.face(player, Vector2.RIGHT)
	await theater.say("???", "Stupid. Stubborn. WING-NUT.")
	await theater.say("Basil", "...Are you talking to me?")
	await theater.say("???", "To the whirligig. It ate its crank AGAIN. And the gear rolled off. And the spring went sproing. Somewhere.")
	_kitty.play_idle()
	await theater.say("???", "Hey, you're the sparkless kid. From town.")
	player.sprite.play("sad")
	await theater.say("Basil", "...Yeah. That's me. Sorry. I'll go.")
	await theater.say("???", "Go? You've got PAWS, don't you?")
	await theater.say("Kitty", "Anyone can wiggle their fingers and float a ribbon. Try MAKING something. That's the good stuff.")
	await theater.say("Kitty", "Gear. Spring. Crank. Find the bits, and I'll show you the BEST thing in this meadow.")
	theater.close_dialog()
	Game.set_flag("prologue_met_kitty")
	_kitty.lines = PackedStringArray([
		"The gear likes the beach. The spring went SPROING toward the flowers.",
		"The crank? Honestly, no idea. Cranks are free spirits. Try the boulders.",
	])
	theater.unlock_party()
	_show_banner("FIND THE GEAR, THE SPRING AND THE CRANK", BANNER_HOLD)
	_busy_scene = false


func _on_part_touched(body: Node2D, part: String, area: Area2D) -> void:
	if not body.is_in_group("player") or Game.flag("prologue_part_" + part) \
			or not Game.flag("prologue_met_kitty"):
		return
	Game.set_flag("prologue_part_" + part)
	(area.get_meta("icon") as Node).queue_free()
	(area.get_meta("spark") as Node).queue_free()
	area.queue_free()
	_part_line(part)


func _part_line(part: String) -> void:
	theater.lock_party()
	await theater.say("Basil", PARTS[part]["line"])
	theater.close_dialog()
	theater.unlock_party()
	var found := _parts_found()
	if found < PARTS.size():
		_show_banner("%d OF %d PARTS" % [found, PARTS.size()], BANNER_HOLD)
	else:
		_show_banner("BRING THEM BACK TO KITTY", BANNER_HOLD)


func _parts_found() -> int:
	var n := 0
	for part: String in PARTS:
		if Game.flag("prologue_part_" + part):
			n += 1
	return n


func _all_parts_found() -> bool:
	return _parts_found() == PARTS.size()


# ---- the flight ------------------------------------------------------------------

func _flight_finale() -> void:
	_busy_scene = true
	_flying = true
	theater.lock_party()
	await theater.walk(player, _kitty.position + Vector2(-26.0, 12.0), 55.0)
	theater.face(player, Vector2.RIGHT)
	await theater.say("Kitty", "Gear. Spring. Crank. You found ALL of it. You're hired.")
	_kitty.play_act()
	await theater.wait(1.4)
	_kitty.play_idle()
	await theater.say("Kitty", "Okay. Deep breath. Grab the crank and WIND!")
	theater.close_dialog()
	await _crank_minigame()
	_whirligig.frame = FX_WHIRL_SPIN0
	_spin_whirligig()
	var tw := create_tween()
	tw.tween_property(_whirligig, "position:y", _whirligig.position.y - 30.0, 1.2) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	await tw.finished
	_orbit_whirligig()
	_kitty.play_emote()
	player.sprite.play("happy")
	await theater.say("Kitty", "LOOK AT IT GO! No magic. No sparks. Just brains and paws.")
	await theater.say("Basil", "It flies. It actually - we MADE that. It's FLYING!")
	await theater.say("Kitty", "'Course it flies. I'm Kitty. Kitty Cool. And you're Basil-who-found-the-spring.")
	await theater.say("Kitty", "Same time tomorrow? The next one's gonna be TWICE as big.")
	await theater.say("Basil", "Yeah. Yeah!")
	theater.close_dialog()
	await theater.wait(1.2)
	await _montage_and_handoff()


## The crank-up mash (2026-07-12 pacing pass): E presses wind the crank, the
## meter decays a little between presses, and the rotor wakes with the fill.
## The party stays locked, so the mashed E can't leak into NPC talks (npc.gd
## refuses conversations while a body is physics-frozen).
func _crank_minigame() -> void:
	var back := ColorRect.new()
	back.offset_left = 128.0
	back.offset_top = 120.0
	back.offset_right = 256.0
	back.offset_bottom = 134.0
	back.color = Color(0.055, 0.04, 0.115, 0.9)
	var fill_rect := ColorRect.new()
	fill_rect.offset_left = 130.0
	fill_rect.offset_top = 122.0
	fill_rect.offset_right = 130.0
	fill_rect.offset_bottom = 132.0
	fill_rect.color = Color(0.91, 0.74, 0.38)
	var label := Label.new()
	label.text = "CRANK IT! MASH E"
	label.offset_left = 128.0
	label.offset_top = 106.0
	label.offset_right = 256.0
	label.offset_bottom = 118.0
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.add_theme_font_override("font", preload("res://assets/font/pixel_font.fnt"))
	label.add_theme_font_size_override("font_size", 8)
	label.add_theme_color_override("font_shadow_color", Color.BLACK)
	for node in [back, fill_rect, label]:
		$UI.add_child(node)
	var fill := 0.0
	var rotor_t := 0.0
	var was_down := false
	while fill < 1.0:
		var delta := get_process_delta_time()
		# level-edge detection, NOT is_action_just_pressed: this coroutine
		# resumes on the tree's process_frame signal, which can run before
		# the same-frame press lands — a just_pressed edge would be missed
		# every time (found by the prologue probe, 2026-07-12)
		var down := Input.is_action_pressed("interact") \
				or Input.is_action_pressed("attack")
		if down and not was_down:
			fill = minf(1.0, fill + 0.09)
			if fill >= 1.0:
				break     # full NOW — the decay below must never gnaw it back
		was_down = down
		fill = maxf(0.0, fill - delta * 0.05)
		fill_rect.offset_right = 130.0 + 124.0 * fill
		# the rotor wakes with the fill: dead below a nudge, then flickering
		# faster and faster
		rotor_t += delta
		if fill < 0.12:
			_whirligig.frame = FX_WHIRL_DROOP
		elif rotor_t >= 0.30 - 0.24 * fill:
			rotor_t = 0.0
			_whirligig.frame = FX_WHIRL_SPIN0 if _whirligig.frame != FX_WHIRL_SPIN0 \
					else FX_WHIRL_SPIN0 + 1
		await get_tree().process_frame
	fill_rect.offset_right = 254.0
	for node in [back, fill_rect, label]:
		node.queue_free()


## Rotor flicker while the whirligig is airborne (scene-lifetime loop).
func _spin_whirligig() -> void:
	while _flying and is_instance_valid(_whirligig):
		_whirligig.frame = FX_WHIRL_SPIN0 if _whirligig.frame != FX_WHIRL_SPIN0 \
				else FX_WHIRL_SPIN0 + 1
		await get_tree().create_timer(0.09).timeout


func _orbit_whirligig() -> void:
	var c := _whirligig.position
	var tw := create_tween().set_loops()
	tw.tween_property(_whirligig, "position", c + Vector2(24.0, -8.0), 0.9) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tw.tween_property(_whirligig, "position", c + Vector2(0.0, 6.0), 0.9) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tw.tween_property(_whirligig, "position", c + Vector2(-24.0, -8.0), 0.9) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tw.tween_property(_whirligig, "position", c, 0.9) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)


func _montage_and_handoff() -> void:
	# Prologue A closes and B ("Professor Poopy Paws") opens: the montage
	# skips the intervening years, swaps to the college-age body (basil_student
	# — no gun, the laser is still years away), and drops into thesis-day town
	# at its first phase, the night Schweinler plants the bag.
	await theater.black(1.0)
	await theater.card("They built things all summer.", 1.8)
	await theater.card("Then all the summers after that.", 1.8)
	await theater.card("A water wheel. A message kite. A potion that fizzed EXACTLY on purpose.", 2.4)
	await theater.card("The Academy took him for potion-craft.  Kitty kissed him at the gate.", 2.4)
	await theater.card("YEARS LATER.", 2.0)
	Game.set_flag("prologue_sparkless_done")
	Party.set_roster([&"basil_student"])
	Game.town_thesis_phase = "plant"
	get_tree().change_scene_to_file("res://scene/town_thesis.tscn")


# ---- exits -------------------------------------------------------------------------

func _on_exit_south(body: Node) -> void:
	if body.is_in_group("player") and not _busy and not _busy_scene:
		_busy = true
		get_tree().change_scene_to_file.call_deferred("res://scene/town_fest.tscn")
