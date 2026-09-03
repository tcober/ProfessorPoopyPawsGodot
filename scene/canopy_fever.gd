extends CanopyScene

## THE BOUGHS, THE FEVER — Prologue A0's canopy. The boy's own deck on one
## grey day: out of the front door (the era's default spawn), down the ladder
## to the grey town, and back up at dusk. The same two tint phases as
## town_fever, keyed on the same flag, so the hour can never disagree between
## the storeys. The home door re-enters the fever downstairs.

const MAP_PATH := "res://assets/maps/canopy_fest.txt"
const LAYOUT_PATH := "res://assets/tilesets/canopy_fest_layout.txt"

const TINT_GREY := Color(0.68, 0.72, 0.84)
const TINT_DUSK := Color(0.74, 0.56, 0.66)

var _home_armed := true

@onready var tint: CanvasModulate = $Tint


func _map_path() -> String:
	return MAP_PATH


func _layout_path() -> String:
	return LAYOUT_PATH


func _props_path() -> String:
	return "res://assets/tilesets/canopy_fest_props.txt"


func _ground_scene() -> String:
	return "res://scene/town_fever.tscn"


func _extra_setup() -> void:
	super()
	var back := Game.flag("prologue_herbal_found")
	tint.color = TINT_DUSK if back else TINT_GREY
	$Glow.modulate.a = 1.0 if back else 0.45
	_spawn_home_door()


## Basil's own front door — back into the fever downstairs (the town_fever
## door, moved up the tree with the split).
func _spawn_home_door() -> void:
	var door := Area2D.new()
	door.collision_layer = 0
	door.collision_mask = 2
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(24.0, 8.0)
	shape.shape = rect
	shape.position = Vector2(8.0, -8.0)
	door.add_child(shape)
	door.position = MapData.anchor_px(map, "home")
	add_child(door)
	door.body_exited.connect(func(body: Node2D) -> void:
		if body.is_in_group("player"):
			_home_armed = true)
	door.body_entered.connect(func(body: Node2D) -> void:
		if not body.is_in_group("player") or not _home_armed or _busy:
			return
		_busy = true
		Game.interior_spawn = "front_door"
		await fade_out()
		get_tree().change_scene_to_file("res://scene/downstairs_fever.tscn"))
