extends TravelScene

## Alembic Town, FESTIVAL ERA — Prologue A "Sparkless" (docs/DESIGN.md Story).
## The same village grid as the drained present, decades younger: the Founding
## Festival fills the square, magic is casually everywhere, and kid Basil is
## the one cat who can't raise a spark. First entry arrives from the fest
## downstairs at Basil's home door (the home-start opening) and the town is
## FREE — the fountain-square teasing cutscene fires from a proximity zone
## when Basil first walks by the square. Then the chapter's wander rhythm
## (the 2026-07-12 pacing pass): three stinging villager talks → "I want to
## go home." → MOM's blessing by the cottage opens the south gate. The goose
## is a chase minigame (it stole Sage's ribbon); returning the ribbon is a
## warmth beat that counts as a talk.

const MAP_PATH := "res://assets/maps/town_fest.txt"
const LAYOUT_PATH := "res://assets/tilesets/town_fest_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const GooseChaseScene := preload("res://entities/npcs/goose_chase.tscn")
const FX_SHEET := preload("res://assets/prologue_fx.png")

const SHEET_SAGE := preload("res://assets/npc_sage_gen.png")
const SHEET_SCHW := preload("res://assets/npc_schweinler_gen.png")
const SHEET_SHEEP := preload("res://assets/npc_sheep_gen.png")
const SHEET_OWL := preload("res://assets/npc_owl_gen.png")
const SHEET_GOOSE := preload("res://assets/npc_goose_gen.png")
const SHEET_MOUSE := preload("res://assets/npc_mouse_gen.png")
const SHEET_MOM := preload("res://assets/npc_mom_gen.png")

## stings before Basil wants to go home (Mom doesn't count — she's not a sting)
const GATE_TALKS := 3

var _talked := {}
var _gate_hinted := false
var _npcs := {}
var _goose: GooseChase

@onready var theater: Theater = $Theater


func _player_node() -> Node2D:
	return Party.spawn($World, Vector2.ZERO)


func _map_path() -> String:
	return MAP_PATH


func _layout_path() -> String:
	return LAYOUT_PATH


const ARRIVE_DROP := 24.0


func _place_player() -> void:
	# First entry arrives from the fest downstairs at the home door; returns
	# from the meadow land at the south gate. ("festival" stays the fallback
	# for direct scene loads — old harness invocations.)
	var spawn := Game.town_spawn
	Game.town_spawn = ""
	if spawn == "home":
		Party.place(MapData.anchor_px(map, "home") + Vector2(0.0, ARRIVE_DROP))
	elif Game.flag("prologue_festival_done"):
		Party.place(MapData.anchor_px(map, "player_start"))
	else:
		Party.place(MapData.anchor_px(map, "festival"))


func _extra_setup() -> void:
	PropSpawner.build("res://assets/tilesets/town_fest_props.txt", map, $World)
	$ExitSouth.position = MapData.anchor_px(map, "exit_south")
	$ExitSouth.body_entered.connect(_on_exit_south)
	_wall_gate_mouth()
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
		{"anchor": "mom_pos", "name": "Mom", "sheet": SHEET_MOM, "cols": 6,
			"lines": PackedStringArray([
				"Enjoying the festival, sweetheart?",
				"Stay where I can hear the fountain, alright? And no climbing the well. Again.",
			])},
		{"anchor": "npc_sheep", "name": "Mrs. Flockhart", "sheet": SHEET_SHEEP, "cols": 4,
			"lines": PackedStringArray([
				"Basil, dear! Lovely festival, isn't it?",
				"Don't fret about the sparks. Everyone blooms eventually. My Wooliam didn't float his first ribbon till he was six.",
				"...You're ten? Oh. Oh dear. Well - wool over it, love!",
			])},
		{"anchor": "npc_owl", "name": "Professor Strix", "sheet": SHEET_OWL, "cols": 4,
			"lines": PackedStringArray([
				"Ah. The young Basil. I have read EVERY treatise on late-blooming magic. All nine of them.",
				"Chapter one is quite clear: some cats simply... don't. A fascinating case! May I take notes?",
			])},
		{"anchor": "npc_mouse", "name": "Pip", "sheet": SHEET_MOUSE, "cols": 4,
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
	if _npcs["Mom"] != null:
		(_npcs["Mom"] as NPC).play_act()   # dusting flour off her paws


func _sage_lines() -> PackedStringArray:
	if Game.flag("prologue_ribbon_returned"):
		return PackedStringArray([
			"Best. Brother. Okay, SECOND best. I don't have another one, so you win by default.",
			"Honeycake's still coming. The BIG kind.",
		])
	if Game.flag("prologue_festival_done"):
		return PackedStringArray([
			"You're not REALLY mad, right? ...Basil?",
			"Also! That HORRIBLE goose stole my third ribbon. MY ribbon! Get it back and I'll forgive your sulking forever.",
		])
	return PackedStringArray(["Watch THIS!"])


func _spawn_goose() -> void:
	if Game.flag("prologue_ribbon"):
		# already caught — a dignified, stationary goose with a grudge
		var npc: NPC = NPCScene.instantiate()
		npc.display_name = "Goose"
		npc.sheet = SHEET_GOOSE
		npc.frame_cols = 6
		npc.lines = PackedStringArray([
			"HONK.",
			"(It seems to respect you now. Or it is planning something.)",
		])
		npc.position = MapData.anchor_px(map, "npc_goose")
		npc.talked.connect(_on_npc_talked)
		$World.add_child(npc)
		_npcs["Goose"] = npc
		return
	_goose = GooseChaseScene.instantiate()
	_goose.sheet = SHEET_GOOSE
	_goose.position = MapData.anchor_px(map, "npc_goose")
	_goose.caught_all.connect(_on_goose_caught)
	$World.add_child(_goose)


## Levitated festival ribbons bobbing over the fountain square — the casual
## living magic the whole prologue exists to take away later. Airborne World
## FX: the origin sits on the square under each ribbon (so depth sorts by the
## ground point) and the art floats via the sprite offset; the bob tweens the
## offset, never the origin.
func _spawn_ribbons() -> void:
	var square := MapData.anchor_px(map, "basil_mark")
	var spots := [Vector2(-26, -70), Vector2(22, -84), Vector2(-6, -96),
			Vector2(38, -62), Vector2(-42, -88)]
	for i in spots.size():
		var r := WorldFx.airborne($World, FX_SHEET, 1 if i % 2 else 0,
				square + Vector2(spots[i].x, 0.0), -spots[i].y)
		var tw := r.create_tween().set_loops()
		tw.tween_property(r, "offset:y", r.offset.y - 5.0, 0.9 + 0.17 * i) \
				.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		tw.tween_property(r, "offset:y", r.offset.y, 0.9 + 0.17 * i) \
				.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)


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
	sage.play_act()
	await theater.wait(0.8)                      # let the square breathe first
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
	Game.set_flag("prologue_festival_done")
	_npcs["Sage"].lines = _sage_lines()
	theater.unlock_party()
	_show_banner("TALK TO THE TOWNSFOLK - E TO TALK", BANNER_HOLD)


# ---- the wander rhythm: stings -> Mom -> the gate --------------------------------

func _on_npc_talked(npc: NPC) -> void:
	if not Game.flag("prologue_festival_done"):
		return
	if npc.display_name == "Mom":
		if Game.flag("prologue_want_home") and not Game.flag("prologue_gate_open"):
			_mom_blessing()
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
	_show_banner("FIND MOM - SHE'S BY THE COTTAGE", BANNER_HOLD)


## Her blessing is the gate key: warmth first, permission second.
func _mom_blessing() -> void:
	theater.lock_party()
	var mom: NPC = _npcs["Mom"]
	mom.play_idle()
	await theater.say("Mom", "Oh, sweetheart. I heard about the square.")
	player.sprite.play("sad")
	await theater.say("Mom", "Listen to me. Sparks are common as dandelions.")
	mom.play_emote()
	await theater.say("Mom", "You? You take things apart to see WHY. You put them back together BETTER. That is rarer than any ribbon trick.")
	await theater.say("Basil", "...You have to say that. You're my mom.")
	await theater.say("Mom", "And moms are always right. It's the law.")
	await theater.say("Mom", "Now scoot. Sulk somewhere sunny - the meadow's good for it. Home before the lamps.")
	theater.close_dialog()
	player.sprite.play("idle_down")
	Game.set_flag("prologue_gate_open")
	theater.unlock_party()
	_show_banner("THE SOUTH GATE IS OPEN", BANNER_HOLD)


# ---- the goose chase --------------------------------------------------------------

func _on_goose_caught(goose: GooseChase) -> void:
	theater.lock_party()
	await theater.say("Goose", "HONK!! HONK HONK HONK.")
	await theater.say("Basil", "Gotcha! Hand it over, you feathery crime.")
	await theater.say("Goose", "(It surrenders the ribbon with tremendous dignity.)")
	theater.close_dialog()
	goose.settle()
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
