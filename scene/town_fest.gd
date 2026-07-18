extends TravelScene

## Alembic Town, FESTIVAL ERA — Prologue A "Sparkless" (docs/DESIGN.md Story).
## The same village grid as the drained present, decades younger: the Founding
## Festival fills the square, magic is casually everywhere, and kid Basil is
## the one cat who can't raise a spark. First entry arrives from the fest
## downstairs at Basil's home door (the home-start opening) and the town is
## FREE — the fountain-square teasing cutscene fires from a proximity zone
## when Basil first walks by the square. Then the chapter's wander rhythm
## (reworked 2026-07-15): three stinging villager talks → "I want to go
## home." → back through the FRONT DOOR to Mom downstairs, whose blessing
## by the hearth opens the south gate (the double-back — Mom stays home, no
## duplicate festival Mom). The goose steals Sage's ribbon mid-cutscene and
## hides in the orchard; finding it is a warmth beat that counts as a talk.

const MAP_PATH := "res://assets/maps/town_fest.txt"
const LAYOUT_PATH := "res://assets/tilesets/town_fest_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const FX_SHEET := preload("res://assets/prologue_fx.png")

const SHEET_SAGE := preload("res://assets/npc_sage_gen.png")
const SHEET_SCHW := preload("res://assets/npc_schweinler_gen.png")
const SHEET_SHEEP := preload("res://assets/npc_sheep_gen.png")
const SHEET_OWL := preload("res://assets/npc_owl_gen.png")
const SHEET_GOOSE := preload("res://assets/npc_goose_gen.png")
const SHEET_MOUSE := preload("res://assets/npc_mouse_gen.png")

## stings before Basil wants to go home
const GATE_TALKS := 3

var _talked := {}
var _gate_hinted := false
var _npcs := {}
## the bobbing square ribbons — the theft snatches one, so keep the refs
var _ribbons: Array[Sprite2D] = []
## the home-door re-entry stays disarmed while the from-downstairs arrival
## stands on it (it lands exactly on the door zone and must not bounce back)
var _home_armed := true

## Animated Tier-3 building sprites (water + smoke), cycled like the boiler.
var _anim_t := 0.0
var _animated: Array[Sprite2D] = []

@onready var theater: Theater = $Theater


func _process(delta: float) -> void:
	if _animated.is_empty():
		return
	_anim_t += delta
	var f := int(_anim_t / 0.18)
	for i in _animated.size():
		var s := _animated[i]
		s.frame = (f + i) % s.hframes


func _player_node() -> Node2D:
	return Party.spawn($World, Vector2.ZERO)


func _map_path() -> String:
	return MAP_PATH


func _layout_path() -> String:
	return LAYOUT_PATH


func _place_player() -> void:
	# First entry arrives from the fest downstairs at the home door; returns
	# from the meadow land at the south gate. ("festival" stays the fallback
	# for direct scene loads — old harness invocations.)
	var spawn := Game.town_spawn
	Game.town_spawn = ""
	if spawn == "home":
		# Land ON the door mouth — feet on the lane right under the arch (the
		# old tile-and-a-half drop read as appearing nowhere near the door).
		Party.place(MapData.anchor_px(map, "home"))
		_home_armed = false            # standing on the door zone; arm on exit
	elif Game.flag("prologue_festival_done"):
		Party.place(MapData.anchor_px(map, "player_start"))
	else:
		Party.place(MapData.anchor_px(map, "festival"))


func _extra_setup() -> void:
	PropSpawner.build("res://assets/tilesets/town_fest_props.txt", map, $World)
	for c in $World.get_children():
		if c is Sprite2D and (c as Sprite2D).hframes > 1:
			_animated.append(c)
	$ExitSouth.position = MapData.anchor_px(map, "exit_south")
	$ExitSouth.body_entered.connect(_on_exit_south)
	_wall_gate_mouth()
	_spawn_home_door()
	Party.clamp_cameras(MapData.size_px(map))
	_spawn_npcs()
	_spawn_goose()
	_spawn_ribbons()
	if not Game.flag("prologue_festival_done"):
		_spawn_fountain_zone()


## The gate-mouth road runs to the map's last row and the collision layer
## only stamps grid cells — when the exit refuses (gate closed), nothing
## stops a body walking off the south edge into the void. Wall it just
## past the edge; the ExitSouth zone fires well before it when open.
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


## Basil's own front door (the blessing double-back, 2026-07-15): while he
## wants to go home and the gate is still shut, stepping on the home door
## re-enters the fest downstairs where Mom waits by the hearth. Any other
## time it's a soft banner. The zone sits ON the door mouth (where the
## from-downstairs arrival lands), so it stays DISARMED until that body
## steps off it once (_home_armed — else the arrival bounces straight back).
func _spawn_home_door() -> void:
	var door := Area2D.new()
	door.collision_layer = 0
	door.collision_mask = 2
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(24.0, 16.0)
	shape.shape = rect
	door.add_child(shape)
	door.position = MapData.anchor_px(map, "home")
	add_child(door)
	door.body_exited.connect(func(body: Node2D) -> void:
		if body.is_in_group("player"):
			_home_armed = true)
	door.body_entered.connect(_on_home_door)


func _on_home_door(body: Node2D) -> void:
	if not body.is_in_group("player") or not _home_armed or _busy:
		return
	# once he's wanted home, the door stays open — Mom is inside baking for
	# the rest of the festival (post-blessing she has scoot-along lines)
	if Game.flag("prologue_want_home"):
		_busy = true
		Game.interior_spawn = "front_door"
		get_tree().change_scene_to_file.call_deferred("res://scene/downstairs_fest.tscn")
	else:
		_show_banner("HOME - MOM'S PIES NEED PEACE. THE FESTIVAL FIRST", BANNER_HOLD)


## The teasing beat fires from proximity, not scene entry (the home-start
## pacing pass): the town is free until Basil first walks by the square.
func _spawn_fountain_zone() -> void:
	var zone := Area2D.new()
	zone.collision_layer = 0
	zone.collision_mask = 2
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(96.0, 96.0)       # the road ring around the basin
	shape.shape = rect
	zone.add_child(shape)
	zone.position = Vector2(27.5 * 16.0, 21.5 * 16.0)   # the fountain's center
	add_child(zone)
	zone.body_entered.connect(func(body: Node2D) -> void:
		if body.is_in_group("player") and not Game.flag("prologue_festival_done"):
			zone.queue_free()
			_festival_cutscene())


# ---- the cast ---------------------------------------------------------------

func _spawn_npcs() -> void:
	var sage_lines := _sage_lines()
	var cast: Array = [
		{"anchor": "sage_pos", "name": "Sage", "sheet": SHEET_SAGE, "cols": 6,
			"lines": sage_lines},
		{"anchor": "schw_pos", "name": "Schweinler", "sheet": SHEET_SCHW, "cols": 6,
			"lines": PackedStringArray([
				"What are YOU looking at, Sparkless?",
				"My father says magic is BREEDING. And pigs of quality have LOADS of it.",
			])},
		{"anchor": "npc_sheep", "name": "Mrs. Flockhart", "sheet": SHEET_SHEEP, "cols": 6,
			"lines": PackedStringArray([
				"Basil, dear! Lovely festival, isn't it?",
				"Don't fret about the sparks. Everyone blooms eventually. My Wooliam didn't float his first ribbon till he was six.",
				"...You're ten? Oh. Oh dear. Well - wool over it, love!",
			])},
		{"anchor": "npc_owl", "name": "Professor Strix", "sheet": SHEET_OWL, "cols": 6,
			"lines": PackedStringArray([
				"Ah. The young Basil. I have read EVERY treatise on late-blooming magic. All nine of them.",
				"Chapter one is quite clear: some cats simply... don't. A fascinating case! May I take notes?",
			])},
		{"anchor": "npc_mouse", "name": "Pip", "sheet": SHEET_MOUSE, "cols": 6,
			"lines": PackedStringArray([
				"Basil! Wanna see MY spark? I learned it YESTERDAY and I'm only five!",
				"Oh... wait. Papa says I shouldn't show off in front of... um... I gotta go find Papa!",
			])},
	]
	for c: Dictionary in cast:
		var npc: NPC = NPCScene.instantiate()
		npc.display_name = c["name"]
		npc.sheet = c["sheet"]
		npc.frame_cols = c["cols"]
		npc.lines = c["lines"]
		npc.position = MapData.anchor_px(map, c["anchor"])
		npc.talked.connect(_on_npc_talked)
		$World.add_child(npc)
		_npcs[c["name"]] = npc


func _sage_lines() -> PackedStringArray:
	if Game.flag("prologue_ribbon_returned"):
		return PackedStringArray([
			"Best. Brother. Okay, SECOND best. I don't have another one, so you win by default.",
			"Honeycake's still coming. The BIG kind.",
		])
	if Game.flag("prologue_festival_done"):
		return PackedStringArray([
			"You're not REALLY mad, right? ...Basil?",
			"And the GOOSE! You SAW it - it looked me right in the eye and then it took my ribbon. Get it back and I'll forgive your sulking forever.",
		])
	return PackedStringArray(["Watch THIS!"])


## Three goose states (the theft rework, 2026-07-15): ribbon recovered — a
## dignified goose back on the lane; hidden — the thief tucked behind the
## orchard TreeCrown east of the river, just its head over the leaves (the
## y-sorted crown covers the body; the stolen ribbon floats as the tell);
## else — the pre-theft goose loitering on the lane, eyeing the ribbons
## (the theft itself runs inside the festival cutscene).
func _spawn_goose() -> void:
	var npc: NPC = NPCScene.instantiate()
	npc.display_name = "Goose"
	npc.sheet = SHEET_GOOSE
	npc.frame_cols = 6
	if Game.flag("prologue_ribbon"):
		npc.lines = PackedStringArray([
			"HONK.",
			"(It seems to respect you now. Or it is planning something.)",
		])
		npc.position = MapData.anchor_px(map, "npc_goose")
		npc.talked.connect(_on_npc_talked)
	elif Game.flag("prologue_goose_hidden"):
		npc.lines = PackedStringArray([
			"HONK?! (It nearly jumps out of its feathers.)",
		])
		# the anchor sits on the walkable bank cell (the anchor lint); the
		# goose itself tucks one step east, under the y-sorted crown
		npc.position = MapData.anchor_px(map, "goose_hide") + Vector2(16.0, 0.0)
		npc.talked.connect(_goose_startle)
		var carried := WorldFx.sheet_sprite(FX_SHEET, 0)
		carried.position = Vector2(7.0, -14.0)
		npc.add_child(carried)
		npc.set_meta("ribbon", carried)
	else:
		npc.lines = PackedStringArray([
			"HONK. (It is watching Sage's ribbons very, very closely.)",
		])
		npc.position = MapData.anchor_px(map, "npc_goose")
	$World.add_child(npc)
	_npcs["Goose"] = npc


## Sage's THREE levitated ribbons bobbing right over HER head — the casual
## living magic the whole prologue exists to take away later. Ownership must
## read on sight: her line counts three, the goose steals from this stack,
## and her "MY RIBBON!" needs no explaining. (They used to float over the
## square's center — nearer Schweinler than her — so the theft read
## backwards.) Airborne World FX: the origin sits on the ground under each
## ribbon (so depth sorts by the ground point) and the art floats via the
## sprite offset; the bob tweens the offset, never the origin.
func _spawn_ribbons() -> void:
	var over_sage := MapData.anchor_px(map, "sage_pos")
	var spots := [Vector2(-14, -58), Vector2(12, -72), Vector2(-2, -86)]
	for i in spots.size():
		var r := WorldFx.airborne($World, FX_SHEET, 1 if i % 2 else 0,
				over_sage + Vector2(spots[i].x, 0.0), -spots[i].y)
		var tw := r.create_tween().set_loops()
		tw.tween_property(r, "offset:y", r.offset.y - 5.0, 0.9 + 0.17 * i) \
				.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		tw.tween_property(r, "offset:y", r.offset.y, 0.9 + 0.17 * i) \
				.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		_ribbons.append(r)


## Road-ring route around the solid fountain: theater walks tween straight
## lines with physics off, so a scripted approach from the north or side
## roads must dog-leg via the ring corners or the body clips through the
## basin. Derived from the fountain's own footprint so map tweaks carry.
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


# ---- the festival beat --------------------------------------------------------

func _festival_cutscene() -> void:
	theater.lock_party()
	var sage: NPC = _npcs["Sage"]
	var schw: NPC = _npcs["Schweinler"]
	await theater.wait(0.4)                      # (fires mid-play, no entry fade)
	# the hail: Sage spots him and calls him over BEFORE the scripted walk —
	# without it, control just vanishes and Basil wanders off on his own
	sage.play_emote()
	await theater.say("Sage", "BASIL! HEY! Over HERE! You have GOT to see this!")
	theater.close_dialog()
	sage.play_act()
	await theater.wait(0.4)
	await theater.walk_via(player, _square_route(player.global_position,
			MapData.anchor_px(map, "basil_mark")), 50.0)
	theater.face(player, Vector2.LEFT)
	await theater.say("Sage", "Look-look-LOOK! Three ribbons at once! Basil, count them. THREE.")
	await theater.say("Basil", "I'm counting. Three. Incredible. The whole town is very impressed.")
	await theater.say("Sage", "Now YOU do one! Just a teensy spark. Ribbons basically float THEMSELVES.")
	await theater.wait(0.8)
	player.sprite.play("sad")
	await theater.wait(0.5)
	await theater.say("Basil", "...It doesn't work. You KNOW it doesn't work. It never works.")
	sage.play_emote()
	await theater.say("Sage", "Maybe you're holding your whiskers wrong?")
	theater.face(player, Vector2.RIGHT)
	schw.play_act()
	await theater.say("Schweinler", "HA! Did everyone hear? The BABY floats three, and big brother can't wiggle ONE.")
	schw.play_emote()
	await theater.hop(schw, 5.0)
	await theater.say("Schweinler", "Sparkless! SPARKLESS BASIL! Oink-hahaha!")
	sage.play_idle()
	await theater.say("Sage", "HEY. Only I get to tease him, mud-snout!")
	await theater.say("Schweinler", "See you at the recital, Sparkless. Oh wait - they don't LET you in.")
	schw.play_idle()
	await theater.wait(0.6)
	player.sprite.play("sad")
	await theater.say("Basil", "...I'm going for a walk.")
	theater.close_dialog()
	# ---- the goose theft (2026-07-15, still locked): it has been watching --
	await _goose_theft()
	Game.set_flag("prologue_festival_done")
	_npcs["Sage"].lines = _sage_lines()
	theater.unlock_party()
	await _show_banner("THE GOOSE FLED EAST - OVER THE BRIDGE", BANNER_HOLD)
	_show_banner("TALK TO THE TOWNSFOLK - E TO TALK", BANNER_HOLD)


## The goose waddles up to SAGE'S side, snatches the lowest of HER floating
## ribbons, and bolts over the bridge to hide behind the orchard tree. Raw
## position tweens (the goose sheet has no walk_* clips — emote IS the
## waddle pair) along the lanes, never through the blocks. Staging order is
## the readability pass (2026-07-17): announce the goose FIRST, walk it to
## the ribbon owner, one innocent beat, snatch, and Sage yells on sight —
## every step points at whose ribbon this is.
func _goose_theft() -> void:
	var goose: NPC = _npcs["Goose"]
	await theater.wait(0.5)
	await theater.say("", "...the goose. The goose has been WAITING.")
	theater.close_dialog()
	# waddle in: west down the lane, then south around the ring's WEST
	# corner, right up to Sage's elbow — hers are the ribbons it cased
	await _goose_run(goose, [
			Vector2(408.0, 312.0),
			Vector2(408.0, 392.0)], 62.0)
	await theater.wait(0.4)                # one innocent beat beside her
	await theater.hop(goose, 6.0)
	# the snatch: the lowest of Sage's ribbons zips into its beak — the SAME
	# fx cell rides the zip, the beak and the orchard hide-out (it used to
	# swap gold for magenta mid-flight)
	var rib: Sprite2D = _ribbons[0]
	var start := rib.global_position + Vector2(0.0, rib.offset.y)
	var cell := rib.frame
	rib.queue_free()                      # its bob tween dies with it
	var zip := WorldFx.sheet_sprite(FX_SHEET, cell)
	$World.add_child(zip)
	zip.global_position = start
	var tw := create_tween()
	tw.tween_property(zip, "global_position",
			goose.global_position + Vector2(7.0, -14.0), 0.3)
	await tw.finished
	zip.queue_free()
	var carried := WorldFx.sheet_sprite(FX_SHEET, cell)
	carried.position = Vector2(7.0, -14.0)
	goose.add_child(carried)
	(_npcs["Sage"] as NPC).play_emote()
	await theater.say("Sage", "HEY!! MY RIBBON! THE GOOSE HAS MY RIBBON!")
	# the getaway: up the west ring, east down the lane, over the bridge,
	# north along the bank, and into the orchard behind the tree
	await _goose_run(goose, [
			Vector2(408.0, 312.0),
			Vector2(728.0, 312.0),
			Vector2(760.0, 312.0),
			Vector2(760.0, 250.0),
			MapData.anchor_px(map, "goose_hide") + Vector2(16.0, 0.0)], 130.0)
	await theater.say("Sage", "It went over the BRIDGE! Basil, you're the fast one!")
	# respawn as the hidden orchard goose (the talkable startle state)
	Game.set_flag("prologue_goose_hidden")
	goose.queue_free()
	_npcs.erase("Goose")
	_spawn_goose()


## Chained straight tweens through lane waypoints, waddling all the way.
func _goose_run(goose: NPC, pts: Array, speed: float) -> void:
	goose.play_emote()
	var tw := create_tween()
	var from := goose.global_position
	for p: Vector2 in pts:
		tw.tween_property(goose, "global_position", p, from.distance_to(p) / speed)
		from = p
	await tw.finished
	goose.play_idle()


# ---- the wander rhythm: stings -> home to Mom -> the gate -------------------------

func _on_npc_talked(npc: NPC) -> void:
	if not Game.flag("prologue_festival_done"):
		return
	if npc.display_name == "Sage" and Game.flag("prologue_ribbon") \
			and not Game.flag("prologue_ribbon_returned"):
		# AWAIT it: if this Sage talk is also the third distinct talk, the
		# fall-through would start _want_home_line on the same DialogBox and
		# one advance press would resume BOTH pending say() awaits
		await _ribbon_return()
	_talked[npc.display_name] = true
	if _talked.size() >= GATE_TALKS and not Game.flag("prologue_want_home"):
		Game.set_flag("prologue_want_home")
		_want_home_line()


func _want_home_line() -> void:
	theater.lock_party()
	player.sprite.play("sad")
	await theater.say("Basil", "Everyone's very... helpful. I want to go home.")
	theater.close_dialog()
	theater.unlock_party()
	_show_banner("GO HOME - THE FRONT DOOR", BANNER_HOLD)


# ---- the orchard startle ----------------------------------------------------------

## Found behind the tree, the goose startles, then hands the ribbon over as
## if returning it was its own idea all along.
func _goose_startle(goose: NPC) -> void:
	if Game.flag("prologue_ribbon"):
		return
	theater.lock_party()
	await theater.hop(goose, 7.0)
	goose.play_act()                       # the honk pair
	await theater.say("Goose", "HONK!! ...honk. (...oh. It's you.)")
	await theater.say("Basil", "You. Feathery crime. I believe you have my sister's ribbon.")
	if goose.has_meta("ribbon"):
		(goose.get_meta("ribbon") as Sprite2D).queue_free()
		goose.remove_meta("ribbon")
	await theater.say("Goose", "(It sets the ribbon down with tremendous dignity, as if returning it was its own idea.)")
	await theater.say("Goose", "(It was just playing around.)")
	theater.close_dialog()
	goose.play_idle()
	goose.lines = PackedStringArray([
		"HONK.",
		"(It seems to respect you now. Or it is planning something.)",
	])
	Game.set_flag("prologue_ribbon")
	theater.unlock_party()
	_show_banner("RETURN THE RIBBON TO SAGE", BANNER_HOLD)


func _ribbon_return() -> void:
	theater.lock_party()
	var sage: NPC = _npcs["Sage"]
	sage.play_emote()
	await theater.say("Sage", "MY RIBBON! You caught the goose?! Nobody catches the goose!")
	player.sprite.play("happy")
	await theater.say("Basil", "Nobody had my motivation.")
	await theater.say("Sage", "Okay. New rule. Anyone who calls you Sparkless answers to ME.")
	theater.close_dialog()
	player.sprite.play("idle_down")
	Game.set_flag("prologue_ribbon_returned")
	sage.lines = _sage_lines()
	theater.unlock_party()


# ---- the south gate -------------------------------------------------------------

func _on_exit_south(body: Node) -> void:
	if not body.is_in_group("player") or _busy:
		return
	if not Game.flag("prologue_gate_open"):
		if not _gate_hinted:
			_gate_hinted = true
			_gate_hint()
		return
	_busy = true
	await fade_out()
	get_tree().change_scene_to_file("res://scene/meadow_fest.tscn")


func _gate_hint() -> void:
	theater.lock_party()
	if Game.flag("prologue_want_home"):
		await theater.say("Basil", "Not without telling Mom. She has EARS.")
	else:
		await theater.say("Basil", "Mom said stay in town for the festival. The festival says otherwise.")
	theater.close_dialog()
	theater.unlock_party()
