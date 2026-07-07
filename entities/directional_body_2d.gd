class_name DirectionalBody2D
extends CharacterBody2D

## Base for the 8-way-moving, 4-way-facing bodies (the zone player and his chibi
## travel self): holds the facing vector and drives an AnimatedSprite2D by
## animation name — "<prefix>_up/_down/_side" with the side art flipped for left.
## Subclasses decide WHEN to move and which prefix to play; this decides how the
## facing reads and which clip shows.

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D

var facing: Vector2 = Vector2.DOWN


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
