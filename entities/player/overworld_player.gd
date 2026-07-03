class_name OverworldPlayer
extends CharacterBody2D

## Basil's chibi travel-map self: 8-way movement and 4-way facing only — no gun, hop,
## or health. Location triggers and scene changes are handled by the overworld scene.

@export var speed: float = 180.0

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D

var facing: Vector2 = Vector2.DOWN


func _physics_process(_delta: float) -> void:
	var input := Vector2(
		Input.get_axis("move_left", "move_right"),
		Input.get_axis("move_up", "move_down")
	)
	if input != Vector2.ZERO:
		input = input.normalized()
		velocity = input * speed
		_update_facing(input)
		_play_directional("walk")
	else:
		velocity = Vector2.ZERO
		_play_directional("idle")
	move_and_slide()


func _update_facing(dir: Vector2) -> void:
	if absf(dir.x) > absf(dir.y):
		facing = Vector2.RIGHT if dir.x > 0.0 else Vector2.LEFT
	else:
		facing = Vector2.DOWN if dir.y > 0.0 else Vector2.UP


func _facing_suffix() -> String:
	if facing == Vector2.UP:
		return "up"
	elif facing == Vector2.DOWN:
		return "down"
	return "side"


func _play_directional(prefix: String) -> void:
	sprite.play(prefix + "_" + _facing_suffix())
	sprite.flip_h = facing == Vector2.LEFT
