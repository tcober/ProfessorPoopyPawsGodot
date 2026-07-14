extends Node2D

## The loft bedroom, FESTIVAL MORNING — Prologue A's real first room (the
## 2026-07-12 pacing pass: the chapter opens at HOME, playable from the first
## frame — no locked cutscene). Kid Basil wakes in the same loft the student
## oversleeps in on thesis day and the hermit haunts in the present (reprise
## staging: one room, three eras). Reuses the house tileset/map/props with a
## bright festival-morning tint. The SW stairs descend to the fest downstairs
## where Mom gates the front door.

const MAP_PATH := "res://assets/maps/house.txt"
const LAYOUT_PATH := "res://assets/tilesets/house_layout.txt"
const PROPS_PATH := "res://assets/tilesets/house_props.txt"

const DIM_MORNING := Color(0.9, 0.86, 0.94)    # festival daylight, violet-cut

var map: Dictionary
var player: Node2D


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	PropSpawner.build(PROPS_PATH, map, $World)
	$Dim.color = DIM_MORNING
	player = Party.spawn($World, MapData.anchor_px(map, "player_spawn"))
	Party.clamp_cameras(MapData.size_px(map))
	_show_hint("FESTIVAL MORNING - HEAD DOWNSTAIRS")
	var exit := Area2D.new()
	exit.collision_layer = 0
	exit.collision_mask = 2
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(24, 16)
	shape.shape = rect
	exit.add_child(shape)
	exit.position = MapData.anchor_px(map, "exit_door")
	add_child(exit)
	exit.body_entered.connect(_on_exit)


func _on_exit(body: Node) -> void:
	if body.is_in_group("player"):
		Game.interior_spawn = "stair_arrival"
		get_tree().change_scene_to_file.call_deferred("res://scene/downstairs_fest.tscn")


func _show_hint(text: String) -> void:
	var label: Label = $UI/Hint
	label.text = text
	label.modulate.a = 1.0
	var tw := create_tween()
	tw.tween_interval(2.2)
	tw.tween_property(label, "modulate:a", 0.0, 0.5)
