class_name OverworldLocation
extends Area2D

## A travel-map marker the overworld player can step onto. An empty `target_scene`
## means the spot is still locked and only announces itself with `locked_text`.

@export var id: String = ""
@export var display_name: String = ""
@export_file("*.tscn") var target_scene: String = ""
@export_multiline var locked_text: String = ""


func _ready() -> void:
	collision_layer = 0
	collision_mask = 2
