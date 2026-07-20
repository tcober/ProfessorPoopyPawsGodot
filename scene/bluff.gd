extends Node2D

## THE BLUFF — one headland, four beats (2026-07-18; docs/DESIGN.md Story).
## Staged FROM BEHIND (the 2026-07-17 restage): the sea + the sky band run
## across the NORTH, so the cast faces up-screen — backs to the camera,
## watching the water — and turns to PROFILE only to look at each other
## (Kitty's back/side NPC cells, the player's idle_up). The kiss is a
## composed two-cat sheet (bluff_kiss_gen: lean / KISS / after — two 48px
## bodies never read as one), swapped in over the hidden bodies. One
## windswept tree (Tier-3 prop) leans over the lip; the calls sit beneath
## it. Routed by Game.bluff_phase over one warm painting.
##
## THE HOUR (2026-07-18 sky pass): the top of the frame is a baked SKY
## overlay ($Sky — banded day or dusk art down to the horizon line, the
## water animating below it), the setting sun + its glint lane live on the
## additive $Glow (fading the glow IS the sunset), and $Stars is an
## additive starfield + moon that fades IN as night falls. _set_hour()
## snaps a phase's opening light; _fall_night() tweens all three with the
## CanvasModulate (the town_thesis nightfall idiom, aimed at the sky).
##   meet    (day)     from town_fest's south gate: Prologue A — kid Basil
##                     finds a girl cat wrestling a whirligig on the bluff.
##                     Gear/spring/crank fetch, the crank-up mash, the
##                     flight. Cards ("THREE SUMMERS LATER.") -> romance.
##   romance (sunset)  college Kitty summons Basil up here with the
##                     acceptance letter news — the watch gift. It EXPLODES
##                     on the handoff, the three pieces scatter across the
##                     SAME grass the whirligig parts did (on purpose), she
##                     re-tinkers it working, he plays look_watch for the
##                     FIRST time, the kiss — and the sun goes down while
##                     they watch, stars out. -> town_thesis "plant"
##   call1   (dusk)    from the hall's laugh-out: Basil sits on the lip and
##                     the light keeps leaving while KITTY calls to ask how
##                     it went; "I'm coming. Stay right there." -> accident
##   call2   (late)    her watch calls his — but the voice is Ridley's.
##                     Night completes ON the narration: he stays right
##                     there, and the stars come out. -> sickroom
## The SAME place on purpose: where everything began is where the bad news
## finds him. Semi-playable (walk/interact; no exits — the story leaves
## for you).

const MAP_PATH := "res://assets/maps/bluff.txt"
const LAYOUT_PATH := "res://assets/tilesets/bluff_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const FX_SHEET := preload("res://assets/prologue_fx.png")
const SHEET_KITTY := preload("res://assets/npc_kitty_adult_gen.png")
const SHEET_KITTY_KID := preload("res://assets/npc_kitty_gen.png")
const SHEET_KISS := preload("res://assets/bluff_kiss_gen.png")
const SKY_DUSK := preload("res://assets/tilesets/bluff_sky_dusk.png")
const SKY_DAY := preload("res://assets/tilesets/bluff_sky_day.png")

## fx strip cells (two-row sheet; WorldFx.sheet_sprite infers the rows)
const FX_SPARK0 := 2
const FX_SPARK1 := 3
const FX_GEAR := 4
const FX_SPRING := 5
const FX_CRANK := 6
const FX_WHIRL_DROOP := 7
const FX_WHIRL_SPIN0 := 8
const FX_POOF := 17
const FX_HEART := 19

const TINT_DAY := Color(1.02, 1.08, 1.28)      # the meet's bright afternoon —
                                               # a cool lift that blues the
                                               # baked indigo sea toward open
                                               # daylight water
const TINT_SUNSET := Color(1.0, 0.94, 0.88)    # the painting's own hour
const TINT_DUSK := Color(0.80, 0.64, 0.74)     # call1: the light going
const TINT_LATE := Color(0.68, 0.58, 0.74)     # call1's end / call2's open
const TINT_NIGHT := Color(0.54, 0.50, 0.74)    # gone

## Prologue A's whirligig recipe — gear on the treeline grass, spring out
## by the point, crank in the flowers. Anchors live in maps/bluff.txt.
const MEET_PARTS := {
	"gear": {"anchor": "part_gear", "cell": FX_GEAR,
		"line": "A brass gear, hiding in the grass by the treeline."},
	"spring": {"anchor": "part_spring", "cell": FX_SPRING,
		"line": "The spring! It sproinged ALL the way out to the point."},
	"crank": {"anchor": "part_crank", "cell": FX_CRANK,
		"line": "One wooden crank, snoozing in the flowers. Classic crank."},
}

## The exploded watch scatters into the whirligig recipe — Kitty keeps the
## recipes that work. Same anchors as MEET_PARTS, years later, on purpose.
const PARTS := {
	"gear": {"anchor": "part_gear", "cell": FX_GEAR,
		"line": "THE GEAR - IT ROLLED FOR THE TREELINE"},
	"spring": {"anchor": "part_spring", "cell": FX_SPRING,
		"line": "THE SPRING - SPROINGED HALFWAY TO THE POINT"},
	"crank": {"anchor": "part_crank", "cell": FX_CRANK,
		"line": "THE CRANK - IN THE FLOWERS. CLASSIC CRANK"},
}

var map: Dictionary
var player: Node2D
var phase := "romance"
var _busy_scene := false
var _flying := false
var _kitty: NPC
var _whirligig: Sprite2D
var _hint_tw: Tween
var _hour_tw: Tween

@onready var theater: Theater = $Theater


func _ready() -> void:
	phase = Game.bluff_phase
	Game.bluff_phase = ""
	if phase == "":
		phase = "romance"
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	PropSpawner.build("res://assets/tilesets/bluff_props.txt", map, $World)
	player = Party.spawn($World, MapData.anchor_px(map, "player_spawn"))
	Party.clamp_cameras(MapData.size_px(map))
	match phase:
		"meet": _phase_meet()
		"call1": _phase_call1()
		"call2": _phase_call2()
		_: _phase_romance()


# ---- the hour ---------------------------------------------------------------------

## Snap a phase's opening light: CanvasModulate + sun glow + stars + sky art.
func _set_hour(tint: Color, glow_a: float, stars_a: float, sky: Texture2D) -> void:
	$Dim.color = tint
	$Glow.modulate.a = glow_a
	$Stars.modulate.a = stars_a
	$Sky.texture = sky


## One tween of the hour, all layers in parallel (the town_thesis nightfall
## idiom, aimed at the sky): the tint cools, the sun lane goes out, the
## stars come up. Await it, or fire it un-awaited under a talky beat.
func _fall_night(tint: Color, glow_a: float, stars_a: float, dur: float) -> void:
	_hour_tw = create_tween().set_parallel(true)
	_hour_tw.tween_property($Dim, "color", tint, dur)
	_hour_tw.tween_property($Glow, "modulate:a", glow_a, dur)
	_hour_tw.tween_property($Stars, "modulate:a", stars_a, dur)
	await _hour_tw.finished


## The stars breathe once night is up — a soft alpha pulse reads as twinkle
## at this scale (the overlay is baked; the scene owns the shimmer). Waits
## out any running hour tween so the two never fight over the alpha.
func _twinkle() -> void:
	if _hour_tw and _hour_tw.is_running():
		await _hour_tw.finished
	var tw := create_tween().set_loops()
	tw.tween_property($Stars, "modulate:a", 0.8, 1.1) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tw.tween_property($Stars, "modulate:a", 1.0, 1.1) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)


# ---- meet (day): Prologue A — the whirligig, where everything begins ---------------

func _phase_meet() -> void:
	_set_hour(TINT_DAY, 0.12, 0.0, SKY_DAY)
	_spawn_kitty_kid()
	_spawn_whirligig()
	for part: String in MEET_PARTS:
		if not Game.flag("prologue_part_" + part):
			_spawn_part(part, MEET_PARTS, _on_meet_part_touched)
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


func _spawn_kitty_kid() -> void:
	_kitty = NPCScene.instantiate()
	_kitty.display_name = "Kitty"
	_kitty.sheet = SHEET_KITTY_KID
	_kitty.frame_cols = 6
	_kitty.lines = PackedStringArray([
		"The gear rolled for the treeline. The spring went SPROING toward the point.",
		"The crank? Honestly, no idea. Cranks are free spirits. Try the flowers.",
	]) if Game.flag("prologue_met_kitty") else PackedStringArray([])
	_kitty.position = MapData.anchor_px(map, "kitty_pos")
	$World.add_child(_kitty)          # _ready runs here, so the sprite is live
	if not _all_parts_found("prologue_part_"):
		_kitty.play_act()             # she starts hunched over the whirligig


func _spawn_whirligig() -> void:
	# sheet_sprite, not a raw hframes=16 Sprite2D: the fx sheet is two rows
	# now, and a bare hframes slice would cut 16x32 frames (8px off-center)
	_whirligig = WorldFx.sheet_sprite(FX_SHEET, FX_WHIRL_DROOP)
	_whirligig.position = MapData.anchor_px(map, "whirligig") + Vector2(0.0, -4.0)
	$World.add_child(_whirligig)


func _on_kitty_zone(body: Node2D) -> void:
	if body.is_in_group("player") and not Game.flag("prologue_met_kitty") \
			and not _busy_scene:
		_meet_kitty()
	elif body.is_in_group("player") and _all_parts_found("prologue_part_") \
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
	await theater.say("???", "Hey, you're the kid who can't do magic. From town.")
	player.sprite.play("sad")
	await theater.say("Basil", "...Yeah. That's me. Sorry. I'll go.")
	await theater.say("???", "Go? You've got PAWS, don't you?")
	await theater.say("Kitty", "Anyone can wiggle their fingers and float a ribbon. Try MAKING something. That's the good stuff.")
	await theater.say("Kitty", "Gear. Spring. Crank. Find the bits, and I'll show you the BEST thing on this bluff.")
	theater.close_dialog()
	Game.set_flag("prologue_met_kitty")
	_kitty.lines = PackedStringArray([
		"The gear rolled for the treeline. The spring went SPROING toward the point.",
		"The crank? Honestly, no idea. Cranks are free spirits. Try the flowers.",
	])
	theater.unlock_party()
	_show_hint("FIND THE GEAR, THE SPRING AND THE CRANK")
	_busy_scene = false


func _on_meet_part_touched(body: Node2D, part: String, area: Area2D) -> void:
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
	await theater.say("Basil", MEET_PARTS[part]["line"])
	theater.close_dialog()
	theater.unlock_party()
	var found := _parts_found("prologue_part_")
	if found < MEET_PARTS.size():
		_show_hint("%d OF %d PARTS" % [found, MEET_PARTS.size()])
	else:
		_show_hint("BRING THEM BACK TO KITTY")


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
	await theater.say("Kitty", "LOOK AT IT GO! No magic at all. Just brains and paws.")
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
	# Prologue A closes into the romance IN PLACE (2026-07-18, the meet
	# moved up here): the cards skip to the college years, the roster swaps
	# to basil_student, and the scene reloads itself in the sunset —
	# the acceptance-letter evening, the watch, the kiss — before its own
	# cards hand to thesis day.
	await theater.black(1.0)
	# one TIME card only (the 2026-07-18 card purge: commentary cards are
	# cut everywhere, cards may only say how much time passed)
	await theater.card("THREE SUMMERS LATER.", 2.0)
	Game.set_flag("prologue_whirligig_done")
	Party.set_roster([&"basil_student"])
	Game.bluff_phase = "romance"
	get_tree().change_scene_to_file("res://scene/bluff.tscn")


# ---- romance (sunset): the watch — explode, gather, fix, the kiss ------------------

func _phase_romance() -> void:
	_set_hour(TINT_SUNSET, 1.0, 0.0, SKY_DUSK)
	_spawn_kitty()
	_kitty.play_back()                     # she's watching the water when we open
	theater.lock_party()
	theater.face(player, Vector2.UP)
	await theater.wait(0.7)
	await theater.say("Basil", "Okay, I climbed your bluff. The letter's going to crease in this wind, you know.")
	theater.close_dialog()
	# she turns from the sunset and waves him up — announced, never mute
	_kitty.play_side()
	await theater.wait(0.3)
	_kitty.play_emote()
	await theater.say("Kitty", "It CAME? IT CAME. Get over here, Academy cat!")
	theater.close_dialog()
	var mark := MapData.anchor_px(map, "basil_mark")
	await theater.walk_via(player, [
			mark + Vector2(-64.0, 120.0),
			mark + Vector2(0.0, 36.0),
			mark], 55.0)
	# the two-backs shot: side by side at the lip, looking out over the drop
	theater.face(player, Vector2.UP)
	_kitty.play_back()
	await theater.wait(1.4)
	await theater.say("Kitty", "In on CRAFT alone. Wiggle-fingers: zero. Paws: ONE. I could BURST.")
	# she turns to him; he turns to her — every big line is said face to face
	_kitty.play_side()
	theater.face(player, Vector2.RIGHT)
	await theater.say("Kitty", "Which is why you're up here. I finished something. Three summers of something.")
	await theater.say("Kitty", "It's a watch. I made it. Academy cats cannot be late. It keeps PERFECT time.")
	await theater.say("Kitty", "Paw.")
	await theater.say("Basil", "What? Why?")
	await theater.say("Kitty", "PAW.")
	theater.close_dialog()
	await theater.wait(0.5)
	# ---- the handoff... and the mainspring's opinion of it
	var poof := WorldFx.airborne($World, FX_SHEET, FX_POOF,
			player.global_position + Vector2(6.0, 0.0), 30.0)
	await _scatter_parts()
	poof.queue_free()
	_kitty.play_idle()
	await theater.say("Kitty", "...")
	await theater.say("Basil", "It keeps perfect time.")
	await theater.say("Kitty", "The MAINSPRING was overwound, that's ALL. Nothing is lost that isn't lying in this grass.")
	await theater.say("Kitty", "Gear. Spring. Crank. Fetch, and I will PROVE it to you.")
	theater.close_dialog()
	_kitty.lines = PackedStringArray([
		"Gear, spring, crank. A headland this size can only hide them so well.",
		"Overwound. OVER-wound. The case is FINE.",
	])
	theater.unlock_party()
	_show_hint("GEAR - SPRING - CRANK. SOME RECIPES DON'T CHANGE.")


## The poof kicks the three pieces out across the headland: each icon flies
## from Basil's paws to its anchor, then becomes the meet-quest pickup idiom.
func _scatter_parts() -> void:
	var flights: Array = []
	for part: String in PARTS:
		var cfg: Dictionary = PARTS[part]
		var icon := WorldFx.sheet_sprite(FX_SHEET, cfg["cell"])
		$World.add_child(icon)
		icon.global_position = player.global_position + Vector2(6.0, -14.0)
		var tw := create_tween()
		tw.tween_property(icon, "global_position",
				MapData.anchor_px(map, cfg["anchor"]), 0.55) \
				.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		flights.append([tw, icon, part])
	await theater.wait(0.65)
	for f: Array in flights:
		(f[1] as Node).queue_free()
		_spawn_part(f[2], PARTS, _on_part_touched)


## The shared pickup idiom (meet quest + watch scatter): root Area2D for
## collision, decal icon + floating sparkle depth-sorted in $World.
func _spawn_part(part: String, parts: Dictionary, handler: Callable) -> void:
	var cfg: Dictionary = parts[part]
	var area := Area2D.new()
	area.collision_layer = 0
	area.collision_mask = 2
	area.position = MapData.anchor_px(map, cfg["anchor"])
	var shape := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 10.0
	shape.shape = circle
	area.add_child(shape)
	var icon := WorldFx.decal($World, FX_SHEET, cfg["cell"], area.position)
	area.set_meta("icon", icon)
	var spark := WorldFx.airborne($World, FX_SHEET, FX_SPARK0,
			area.position + Vector2(6.0, 0.0), 8.0)
	area.set_meta("spark", spark)
	var tw := spark.create_tween().set_loops()
	tw.tween_callback(func() -> void: spark.frame = FX_SPARK1).set_delay(0.4)
	tw.tween_callback(func() -> void: spark.frame = FX_SPARK0).set_delay(0.4)
	add_child(area)
	area.body_entered.connect(handler.bind(part, area))


func _on_part_touched(body: Node2D, part: String, area: Area2D) -> void:
	if not body.is_in_group("player") or Game.flag("prologue_wpart_" + part):
		return
	Game.set_flag("prologue_wpart_" + part)
	(area.get_meta("icon") as Node).queue_free()
	(area.get_meta("spark") as Node).queue_free()
	area.queue_free()
	if _all_parts_found("prologue_wpart_"):
		_kitty.lines = PackedStringArray([
			"Paw them over. CAREFULLY. Springs hold grudges.",
		])
		_show_hint("BRING THEM TO KITTY")
	else:
		_show_hint(PARTS[part]["line"])


func _parts_found(prefix: String) -> int:
	var n := 0
	for part: String in PARTS:
		if Game.flag(prefix + part):
			n += 1
	return n


func _all_parts_found(prefix: String) -> bool:
	return _parts_found(prefix) == PARTS.size()


func _spawn_kitty() -> void:
	_kitty = NPCScene.instantiate()
	_kitty.display_name = "Kitty"
	_kitty.sheet = SHEET_KITTY
	_kitty.frame_cols = 10                # cols 6-9: back x2 + side x2
	_kitty.position = MapData.anchor_px(map, "kitty_pos")
	_kitty.lines = PackedStringArray(["Sunset waits for nobody. Up here, QUICK."])
	_kitty.talked.connect(_on_kitty_talked)
	$World.add_child(_kitty)


## The talked handler AWAITS the beat it starts (the Sage ribbon lesson —
## one advance press must never resume two pending say() awaits).
func _on_kitty_talked(_npc: NPC) -> void:
	if _all_parts_found("prologue_wpart_") and not _busy_scene \
			and not Game.flag("prologue_watch_given"):
		await _refit_and_kiss()


func _refit_and_kiss() -> void:
	_busy_scene = true
	theater.lock_party()
	# he watches her paws work; she's over the pieces
	theater.face(player, Vector2.RIGHT)
	_kitty.play_act()
	await theater.say("Kitty", "Gear... spring... crank. And THIS time the mainspring gets some respect.")
	theater.close_dialog()
	# re-tinker sparkle over her paws while she sets it right
	var spark := WorldFx.airborne($World, FX_SHEET, FX_SPARK0,
			_kitty.position + Vector2(2.0, -2.0), 22.0)
	for i in 6:
		await theater.wait(0.22)
		spark.frame = FX_SPARK1 if spark.frame == FX_SPARK0 else FX_SPARK0
	spark.queue_free()
	_kitty.play_side()                    # she turns to him, holding it out
	await theater.say("Kitty", "Paw. ...It's safe. Probably. Paw anyway.")
	theater.close_dialog()
	# the watch on his wrist for the FIRST time — the raised-paw gesture
	# every later call beat repeats (player_frames `look_watch`)
	player.sprite.play("look_watch")
	await theater.wait(1.0)
	await theater.say("Basil", "It ticks. Kitty, the escapement alone - three summers? For me?")
	await theater.say("Kitty", "Every time you ran late I added a jewel to spite you. Does it still keep perfect time? PERFECT-er.")
	await theater.say("Basil", "...I'm never taking it off.")
	# the promise goes out over the water — she turns back to the sunset
	_kitty.play_back()
	await theater.say("Kitty", "I know. And when you're the one up FRONT in one of those big halls - because you WILL be -")
	await theater.say("Kitty", "- I'll be in the front row. Whooping.")
	_kitty.play_side()
	await theater.say("Basil", "Please don't whoop.")
	await theater.say("Kitty", "Whooping is a promise, professor.")
	theater.close_dialog()
	# ---- the kiss: she closes the gap, then the composed two-cat frames
	# take over from the hidden bodies (bluff_kiss_gen: lean / KISS / after)
	theater.face(player, Vector2.RIGHT)
	await theater.walk(_kitty, player.global_position + Vector2(18.0, 0.0), 30.0)
	_kitty.play_side()
	await theater.wait(0.4)
	var kiss := WorldFx.sheet_sprite(SHEET_KISS, 0, 3)
	kiss.position = Vector2(
			(player.global_position.x + _kitty.global_position.x) * 0.5,
			player.global_position.y)
	kiss.offset = Vector2(0.0, -24.0)     # 96px cell: art feet land on node.y + 20
	$World.add_child(kiss)
	player.sprite.visible = false
	_kitty.sprite.visible = false
	await theater.wait(0.8)               # the lean, the paw-hold
	kiss.frame = 1                        # THE KISS — the heart blooms over it
	var heart := WorldFx.airborne($World, FX_SHEET, FX_HEART,
			kiss.position + Vector2(0.0, 20.0), 44.0)
	var htw := heart.create_tween()
	htw.tween_property(heart, "offset:y", heart.offset.y - 8.0, 1.6) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	await theater.wait(2.0)
	heart.queue_free()
	kiss.frame = 2                        # the after: backs to the sun lane,
	await theater.wait(1.2)               # her head on his shoulder
	# ...and the sun goes down while they watch (2026-07-18): the whole
	# reason the scene faces the water. Sunset -> dusk -> the starfield —
	# held in silence (the narration purge: the two still silhouettes under
	# the stars ARE the line)
	await _fall_night(TINT_DUSK, 0.5, 0.55, 2.8)
	await _fall_night(TINT_NIGHT, 0.16, 1.0, 3.2)
	_twinkle()
	await theater.wait(2.6)
	Game.set_flag("prologue_watch_given")
	Game.set_flag("prologue_romance")
	await theater.black(1.6)
	await theater.card("YEARS LATER.", 2.0)
	Game.town_thesis_phase = "plant"
	get_tree().change_scene_to_file("res://scene/town_thesis.tscn")


# ---- call1 (dusk): she calls to ask how it went ------------------------------------

func _phase_call1() -> void:
	_set_hour(TINT_DUSK, 0.55, 0.0, SKY_DUSK)
	theater.lock_party()
	player.sprite.play("sad")
	await theater.wait(0.8)
	await theater.say("Basil", "Poopy Paws. They're all still laughing. I can hear it from here.")
	theater.close_dialog()
	# the walk to the lip is the player's own (the pacing law: agency, not cuts)
	_show_hint("THE EDGE OF THE BLUFF - SOMEWHERE NOBODY IS")
	await theater.walk_gate(MapData.anchor_px(map, "sit_spot"), Vector2(48.0, 32.0))
	await theater.walk(player, MapData.anchor_px(map, "sit_spot"), 40.0)
	# a long look out over the drop — back to the camera, under the tree
	theater.face(player, Vector2.UP)
	await theater.wait(1.2)
	player.sprite.play("sit")
	player.sprite.flip_h = false          # profile RIGHT, out over the point
	# the light keeps leaving while he sits there — un-awaited, the dusk
	# deepens under the whole call (first stars up by the end of it); a held
	# quiet beat while it drains, no narrator over it
	_fall_night(TINT_LATE, 0.40, 0.35, 9.0)
	await theater.wait(2.6)
	# the watch blinks — SHE calls HIM (she never saw the hall; a busted-axle
	# job at her wheel workshop did that — the excuse lands right here, the
	# only place it's ever told). He stands to answer: the same gesture she
	# taught him.
	await theater.wait(0.8)
	player.sprite.play("look_watch")
	await theater.wait(0.9)
	await theater.say("Kitty", "SO? Professor Basil. A stupid AXLE job ate my whole morning - I'm sorry, I ran the workshop right through your lecture. How'd it go? Did they whoop? Tell me somebody whooped.")
	await theater.say("Basil", "...")
	await theater.say("Kitty", "Basil?")
	await theater.say("Basil", "...The hall. Schweinler. I can't - Kitty, I can't even say it.")
	await theater.wait(0.6)
	await theater.say("Kitty", "...That bad, huh. Okay. Listen to me. I'm coming. Stay right there.")
	await theater.say("Basil", "Wait - it's nearly dark, the road - Kitty? ...She's already pedaling.")
	theater.close_dialog()
	player.sprite.play("sit")
	await theater.wait(1.4)
	await theater.black(1.0)
	# the accident is SHOWN — the side-view set-piece owns the flag
	get_tree().change_scene_to_file("res://scene/accident.tscn")


# ---- call2 (late): her watch calls his — with the wrong voice on it ----------------

func _phase_call2() -> void:
	# picks up where call1's falling light left off; the fall to FULL night
	# plays out ON SCREEN, held — the sky does the telling (the 2026-07-18
	# narration purge: no "the stars come out" box, the stars just come out)
	_set_hour(TINT_LATE, 0.40, 0.35, SKY_DUSK)
	theater.lock_party()
	# still where she told him to stay
	Party.place(MapData.anchor_px(map, "sit_spot"))
	player.sprite.play("sit")
	await _fall_night(TINT_NIGHT, 0.20, 1.0, 5.0)
	_twinkle()
	await theater.wait(1.0)
	await theater.say("Basil", "...Where is she?")
	await theater.wait(0.6)
	player.sprite.play("look_watch")
	await theater.wait(0.9)
	await theater.say("Basil", "Kitty! Finally - where ARE you, I was about to -")
	await theater.say("Ridley", "...Is this Basil? Your name's engraved on the little glass. I'm - there's been an accident. On the dusk road.")
	await theater.say("Ridley", "The doctor has her. The east cottage, by the fountain. You should... you should run.")
	theater.close_dialog()
	await theater.wait(0.5)
	# and he RUNS — a real bolt back down the headland the way he came (the
	# old beat played walk_side standing still), the cut catching him mid-run
	theater.walk(player, MapData.anchor_px(map, "player_spawn"), 130.0)
	await theater.wait(0.9)
	await theater.black(0.8)
	get_tree().change_scene_to_file("res://scene/sickroom.tscn")


# ---- helpers ----------------------------------------------------------------------

func _show_hint(text: String) -> void:
	var label: Label = $UI/Hint
	label.text = text
	label.modulate.a = 1.0
	# kill the previous fade or its interval expires mid-hold and yanks
	# THIS hint early — create_tween() never auto-kills prior tweens
	if _hint_tw:
		_hint_tw.kill()
	_hint_tw = create_tween()
	_hint_tw.tween_interval(2.4)
	_hint_tw.tween_property(label, "modulate:a", 0.0, 0.5)
