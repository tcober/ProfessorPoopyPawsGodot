class_name OverworldPlayer
extends DirectionalBody2D

## Basil's chibi travel-map self: 8-way movement, 4-way facing, no gun/hop/health
## (see DirectionalBody2D for facing + animation). Location triggers and scene
## changes are handled by the overworld scene.

@export var speed: float = 90.0


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
