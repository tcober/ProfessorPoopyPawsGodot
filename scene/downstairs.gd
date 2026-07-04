extends Node2D

## Basil's ground floor — the kitchen + lab great room between the loft
## bedroom and the outside world. Visible tiles stamped at runtime from the
## generated layout (assets/_gen_tileset_downstairs.py) onto two layers, with
## collision from the same assets/maps/downstairs.txt grid. Two ways in, two
## ways out: the top-center stair alcove climbs to the bedroom; the south
## front door opens onto the overworld at the home marker. The spawn anchor
## is routed through Game.interior_spawn (read-and-clear; "" = front_door,
## the overworld-entry default).

const MAP_PATH := "res://assets/maps/downstairs.txt"
const LAYOUT_PATH := "res://assets/tilesets/downstairs_layout.txt"

## Cozy hearth-lit interior: dim everything (Basil included), let the fire
## and the doorway daylight carry the brightness.
const DIM := Color(0.74, 0.7, 0.84)

var map: Dictionary

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
	_fix_camera()
	$ExitDoor.body_entered.connect(_on_exit_door)
	$UpStair.body_entered.connect(_on_up_stair)


## The room is exactly one screen: clamp to the view (384x216), not the map
## (whose bottom rows are the stoop + void margin), so the camera never moves.
func _fix_camera() -> void:
	var cam: Camera2D = player.get_node("Camera2D")
	cam.limit_left = 0
	cam.limit_top = 0
	cam.limit_right = 384
	cam.limit_bottom = 216


## Out the front door to the overworld, at the home marker.
func _on_exit_door(body: Node) -> void:
	if body is Player:
		Game.overworld_spawn = "home"
		# Deferred: freeing the scene inside the Area2D callback is a physics error.
		get_tree().change_scene_to_file.call_deferred("res://scene/overworld.tscn")


## Up the alcove stairs to the loft bedroom, arriving at the stair head.
func _on_up_stair(body: Node) -> void:
	if body is Player:
		Game.interior_spawn = "stair_top"
		# Deferred: freeing the scene inside the Area2D callback is a physics error.
		get_tree().change_scene_to_file.call_deferred("res://scene/house.tscn")
