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
	_fix_camera()
	$ExitDoor.body_entered.connect(_on_exit_door)
	$UpStair.body_entered.connect(_on_up_stair)
	_place_dressing()


## Animated dressing, positioned from the map so moving the feature chars
## moves it: the hearth fire overlay (under entities) and the free-standing
## boiler (a y-sorted World entity whose collision is the map's 'A' cells).
func _place_dressing() -> void:
	$Fire.position = _bbox_rect("H").position + FIRE_OFFSET
	var a := _bbox_rect("A")
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


## Pixel rect of a feature char's bbox in the map.
func _bbox_rect(ch: String) -> Rect2:
	var x0 := 1 << 20
	var y0 := 1 << 20
	var x1 := -1
	var y1 := -1
	for y in int(map.rows):
		var row: String = map.lines[y]
		for x in row.length():
			if row[x] == ch:
				x0 = mini(x0, x)
				y0 = mini(y0, y)
				x1 = maxi(x1, x)
				y1 = maxi(y1, y)
	return Rect2(x0 * 16.0, y0 * 16.0, (x1 - x0 + 1) * 16.0, (y1 - y0 + 1) * 16.0)


## The room is exactly one screen: clamp to the view (384x216), not the map
## (whose bottom rows are the stoop + void margin), so the camera never moves.
func _fix_camera() -> void:
	var cam: Camera2D = player.get_node("Camera2D")
	cam.limit_left = 0
	cam.limit_top = 0
	cam.limit_right = 384
	cam.limit_bottom = 216


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
