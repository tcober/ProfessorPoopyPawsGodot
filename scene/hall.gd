extends Node2D

## The Alembic Academy lecture hall — Prologue B "the naming" (docs/DESIGN.md
## Story). Basil delivers his re-enchantment thesis; Schweinler smells the
## bag on his paws and brands him "Professor Poopy Paws"; the gallery laughs;
## the cards fall. The emotional core of the prologue. Interior scene pattern
## (Tiles -> Collision -> y-sorted World -> TilesUpper), the cast are one-row
## NPC sprites posed by the Theater, then it hands to the town's dusk phase.

const MAP_PATH := "res://assets/maps/hall.txt"
const LAYOUT_PATH := "res://assets/tilesets/hall_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const SHEET_SCHW := preload("res://assets/npc_schweinler_adult_gen.png")
const SHEET_OWL := preload("res://assets/npc_owl_gen.png")
const SHEET_SHEEP := preload("res://assets/npc_sheep_gen.png")
const SHEET_MOUSE := preload("res://assets/npc_mouse_gen.png")
const SHEET_BADGER := preload("res://assets/npc_badger_gen.png")
const SHEET_STORK := preload("res://assets/npc_stork_gen.png")

var map: Dictionary
var player: Node2D
var _dean: NPC
var _schw: NPC
var _panel: Array[NPC] = []
var _audience: Array[NPC] = []

@onready var theater: Theater = $Theater


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	PropSpawner.build("res://assets/tilesets/hall_props.txt", map, $World)
	player = Party.spawn($World, MapData.anchor_px(map, "player_spawn"))
	Party.clamp_cameras(MapData.size_px(map))
	_spawn_cast()
	_naming_cutscene()


func _spawn_cast() -> void:
	# the judging panel behind the long stage-west desk — the Dean presides,
	# three faculty flank him; they stand on the stage row behind the desk so
	# the desktop plane hides their legs (the desk() entity idiom). All cast
	# sheets are 6 cols now (idle/act/EMOTE) — the gallery must really laugh.
	_dean = _npc("Dean Strix", SHEET_OWL, 6, "judge_1")
	_dean.play_act()                                   # a lecturing wing
	var jsheets := [SHEET_STORK, SHEET_BADGER, SHEET_SHEEP]
	for i in jsheets.size():
		_panel.append(_npc("", jsheets[i], 6, "judge_%d" % (i + 2)))
	_schw = _npc("Schweinler", SHEET_SCHW, 6, "schweinler_spot")
	# a PACKED gallery: three to a bench, twelve in all
	var sheets := [SHEET_SHEEP, SHEET_MOUSE, SHEET_BADGER]
	for i in 12:
		_audience.append(_npc("", sheets[i % 3], 6, "aud_%d" % (i + 1)))


func _npc(nm: String, sheet: Texture2D, cols: int, anchor: String) -> NPC:
	var npc: NPC = NPCScene.instantiate()
	npc.display_name = nm
	npc.sheet = sheet
	npc.frame_cols = cols
	npc.position = MapData.anchor_px(map, anchor)
	$World.add_child(npc)
	return npc


func _naming_cutscene() -> void:
	theater.lock_party()
	await theater.wait(0.6)
	theater.face(player, Vector2.UP)
	# the Dean's welcome is the summons; the walk to the stage is the
	# player's own (the pacing pass — control between every beat)
	await theater.say("Dean Strix", "...and so. No spark has ever stood at this podium. The work stood for itself instead - every measured drop of it. The floor is yours, Basil.")
	theater.close_dialog()
	# the gate is the full-width open row below the benches — every route
	# north crosses it (a point-gate at the podium is walkable around via
	# the side aisles); the last steps MOUNT THE STAGE from the east wing
	# (the front-center podium's own row is walled by desk + podium, so the
	# route loops around them — it reads as taking the stage stairs)
	await theater.walk_gate(Vector2(MapData.size_px(map).x * 0.5, 136.0),
			Vector2(MapData.size_px(map).x, 20.0))
	var podium_x := MapData.bbox_rect(map, "L").get_center().x
	var stage_y := MapData.anchor_px(map, "lectern_spot").y
	await theater.walk_via(player, [
			Vector2(168.0, 136.0),
			Vector2(168.0, 88.0),
			Vector2(248.0, 88.0),
			Vector2(248.0, stage_y),
			Vector2(podium_x, stage_y)], 55.0)
	theater.face(player, Vector2.DOWN)
	await theater.say("Basil", "Th-thank you, Dean. Esteemed faculty.")
	await theater.say("Basil", "My thesis is simple. Magic is not GONE where it seems absent. It is asleep. And what sleeps can be woken - measured, bottled, RE-KINDLED.")
	await theater.say("Basil", "You call my flasks 'potions.' They are chemistry. And chemistry does not need a spark to be TRUE.")
	await theater.wait(0.4)
	# Schweinler, from the gallery
	_schw.play_idle()
	await theater.say("Schweinler", "Hold on. HOLD ON. Does anyone else... smell that?")
	theater.face(player, Vector2.DOWN)
	await theater.say("Basil", "S-Schweinler? Smell wh-")
	_schw.play_act()
	await theater.say("Schweinler", "LOOK at his paws! He TRACKED it! All the way up onto the STAGE!")
	await theater.hop(_schw, 5.0)
	_schw.play_emote()
	await theater.say("Schweinler", "A brilliant lecture, everyone. From PROFESSOR... POOPY... PAWS!")
	# the gallery turns — every sheet has a real laugh pair now, and even
	# the panel cracks (that's the sting); hop ripples make the hall SHAKE
	for a in _audience:
		a.play_emote()
	for j in _panel:
		j.play_emote()
	_dean.play_emote()
	for i in 4:
		theater.hop(_audience[(i * 5) % _audience.size()], 4.0)
		await theater.wait(0.12)
	await theater.say("", "The whole hall laughs. Someone starts a chant.")
	await theater.say("Gallery", "Poopy Paws! POOPY PAWS! POOPY PAWS!")
	player.sprite.play("sad")
	await theater.wait(0.8)
	await theater.say("Basil", "...")
	theater.close_dialog()
	Game.set_flag("prologue_named")
	# the walk of shame is HIS OWN body giving up, not the player's (the
	# 2026-07-17 restage): he pouts, steps down off the stage and walks the
	# whole aisle SLOWLY while the gallery keeps laughing around him
	await theater.wait(0.6)
	await theater.walk_via(player, [
			Vector2(248.0, stage_y),
			Vector2(248.0, 88.0),
			Vector2(168.0, 88.0),
			Vector2(168.0, 136.0),
			MapData.anchor_px(map, "door")], 30.0)
	player.sprite.play("sad")
	await theater.wait(0.5)
	await theater.black(1.2)
	await theater.card("THE NAME STUCK.", 2.2)
	# dusk falls on the bluff — she calls to ask how it went
	Game.bluff_phase = "call1"
	get_tree().change_scene_to_file("res://scene/bluff.tscn")
