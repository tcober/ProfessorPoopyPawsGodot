extends Node2D

## The great room, FESTIVAL MORNING — the second beat of the home-start
## opening (2026-07-12 pacing pass): Mom is at the hearth, and her good-morning
## is the front-door key (`prologue_saw_mom`). Same map/tiles/props as the
## drained-era downstairs (the workshop corner has always been half-built —
## this family tinkers), brighter tint, fire and boiler alive. Out the front
## door lies the festival town at Basil's home door.

const MAP_PATH := "res://assets/maps/downstairs.txt"
const LAYOUT_PATH := "res://assets/tilesets/downstairs_layout.txt"
const PROPS_PATH := "res://assets/tilesets/downstairs_props.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const SHEET_MOM := preload("res://assets/npc_mom_gen.png")

const DIM_MORNING := Color(0.9, 0.85, 0.9)     # festival daylight indoors
const FIRE_OFFSET := Vector2(10.0, 20.0)       # see scene/downstairs.gd

var map: Dictionary
var player: Node2D
var _anim_t := 0.0
var _busy := false

@onready var theater: Theater = $Theater


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	PropSpawner.build(PROPS_PATH, map, $World)
	$Dim.color = DIM_MORNING
	var spawn := Game.interior_spawn
	Game.interior_spawn = ""
	if spawn.is_empty() or not map.anchors.has(spawn):
		spawn = "stair_arrival"
	player = Party.spawn($World, MapData.anchor_px(map, spawn))
	Party.clamp_cameras(MapData.view_size())
	$Fire.position = MapData.bbox_rect(map, "H").position + FIRE_OFFSET
	_spawn_mom()
	$ExitDoor.position = MapData.anchor_px(map, "exit_door")
	$ExitDoor.body_entered.connect(_on_exit_door)
	if not Game.flag("prologue_saw_mom"):
		_show_hint("SAY GOOD MORNING TO MOM - E TO TALK")


func _spawn_mom() -> void:
	var mom: NPC = NPCScene.instantiate()
	mom.display_name = "Mom"
	mom.sheet = SHEET_MOM
	mom.frame_cols = 6
	mom.lines = PackedStringArray([
		"There's my little tinkerer! Up with the birds for once.",
		"It's the Founding Festival, sweetheart. The WHOLE town's out - even the Academy has its window lit.",
		"Go see the ribbons. I'll be along when the pies are done. Scoot!",
	])
	# by the hearth, flour on her paws
	mom.position = Vector2(4.0 * 16.0 + 8.0, 5.0 * 16.0 + 8.0)
	mom.talked.connect(_on_mom_talked)
	$World.add_child(mom)
	mom.play_act()


func _on_mom_talked(_npc: NPC) -> void:
	if not Game.flag("prologue_saw_mom"):
		Game.set_flag("prologue_saw_mom")
		_show_hint("THE FESTIVAL AWAITS - OUT THE FRONT DOOR")


func _process(delta: float) -> void:
	# the room's little life (see scene/downstairs.gd)
	_anim_t += delta
	$Fire.frame = int(_anim_t / 0.16) % 3
	$World/Boiler.frame = int(_anim_t / 0.28) % 4


func _on_exit_door(body: Node) -> void:
	if not body.is_in_group("player") or _busy:
		return
	if not Game.flag("prologue_saw_mom"):
		_door_hint()
		return
	_busy = true
	Game.town_spawn = "home"
	get_tree().change_scene_to_file.call_deferred("res://scene/town_fest.tscn")


func _door_hint() -> void:
	_busy = true
	theater.lock_party()
	await theater.say("Basil", "Can't just LEAVE. Mom knows when I leave. Mom knows everything.")
	theater.close_dialog()
	theater.unlock_party()
	_busy = false


func _show_hint(text: String) -> void:
	var label: Label = $UI/Hint
	label.text = text
	label.modulate.a = 1.0
	var tw := create_tween()
	tw.tween_interval(2.4)
	tw.tween_property(label, "modulate:a", 0.0, 0.5)
