extends Node2D

## Basil's ground floor — the kitchen + lab great room between the loft
## bedroom and the outside world. Visible tiles stamped at runtime from the
## generated layout (assets/_gen_tileset_downstairs.py) onto two layers, with
## collision from the same assets/maps/downstairs.txt grid. Two ways in, two
## ways out: the top-center stair alcove climbs to the bedroom; the south
## front door opens onto the overworld at the town-icon gate mouth (the
## walkable Alembic Town scene is PARKED for now — see DESIGN.md). The spawn
## anchor is routed through Game.interior_spawn (read-and-clear; "" =
## front_door, the overworld-entry default).

const MAP_PATH := "res://assets/maps/downstairs.txt"
const LAYOUT_PATH := "res://assets/tilesets/downstairs_layout.txt"

## Cozy hearth-lit interior: dim everything (Basil included), let the fire
## and the doorway daylight carry the brightness.
const DIM := Color(0.74, 0.7, 0.84)

## Basil's feet sit at node.y + 20 (48px cell, feet baseline 44); y-sorted
## props must place their node at the same feet convention to sort true.
const PLAYER_FEET := 20.0

## Where the fire overlay sits inside the hearth bbox (the firebox opening
## in _interior_props.hearth: fx0=10, tongues from ~y20).
const FIRE_OFFSET := Vector2(10.0, 20.0)

var map: Dictionary
var _anim_t := 0.0

@onready var player: Player = $World/Player


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	var spawn := Game.interior_spawn
	Game.interior_spawn = ""
	if spawn.is_empty() or not map.anchors.has(spawn):
		spawn = "front_door"
	player.position = MapData.anchor_px(map, spawn)
	$ExitDoor.position = MapData.anchor_px(map, "exit_door")
	$UpStair.position = MapData.anchor_px(map, "exit_up")
	$Dim.color = DIM
	MapData.clamp_camera(player.get_node("Camera2D"), MapData.view_size())
	$ExitDoor.body_entered.connect(_on_exit_door)
	$UpStair.body_entered.connect(_on_up_stair)
	_place_dressing()


## Animated dressing, positioned from the map so moving the feature chars
## moves it: the hearth fire overlay (under entities) and the free-standing
## boiler (a y-sorted World entity whose collision is the map's 'A' cells).
func _place_dressing() -> void:
	$Fire.position = MapData.bbox_rect(map, "H").position + FIRE_OFFSET
	var a := MapData.bbox_rect(map, "A")
	var base_y := a.position.y + a.size.y
	var boiler: Sprite2D = $World/Boiler
	boiler.position = Vector2(a.position.x + a.size.x / 2.0, base_y - PLAYER_FEET)
	# sprite bottom sits exactly on the footprint's south edge
	boiler.offset = Vector2(0.0, base_y - boiler.texture.get_height() / 2.0 - boiler.position.y)


## The little life of the room: fire flicker, boiler shiver + steam leak.
func _process(delta: float) -> void:
	_anim_t += delta
	$Fire.frame = int(_anim_t / 0.16) % 3
	$World/Boiler.frame = int(_anim_t / 0.28) % 4


## Out the front door to the overworld, at the town icon's gate mouth.
func _on_exit_door(body: Node) -> void:
	if body is Player:
		Game.overworld_spawn = "town"
		# Deferred: freeing the scene inside the Area2D callback is a physics error.
		get_tree().change_scene_to_file.call_deferred("res://scene/overworld.tscn")


## Up the alcove stairs to the loft bedroom, arriving at the stair head.
func _on_up_stair(body: Node) -> void:
	if body is Player:
		Game.interior_spawn = "stair_top"
		# Deferred: freeing the scene inside the Area2D callback is a physics error.
		get_tree().change_scene_to_file.call_deferred("res://scene/house.tscn")
