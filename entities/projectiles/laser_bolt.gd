class_name LaserBolt
extends Area2D

## A single laser shot. Travels in `direction`, damages the first HurtboxComponent it
## hits, and frees itself on impact, on hitting a wall, or after `lifetime`.
## Collision mask = walls (1) + enemy hurtboxes (16); never hits the player.

@export var speed: float = 460.0
@export var damage: int = 2      # slimes have 6 HP -> three shots
@export var lifetime: float = 1.2

## Set by the shooter before adding to the tree.
var direction: Vector2 = Vector2.RIGHT
var shooter: Node = null

var _life_remaining: float = 0.0


func _ready() -> void:
	direction = direction.normalized()
	rotation = direction.angle()
	_life_remaining = lifetime
	area_entered.connect(_on_area_entered)
	body_entered.connect(_on_body_entered)


func _physics_process(delta: float) -> void:
	global_position += direction * speed * delta
	_life_remaining -= delta
	if _life_remaining <= 0.0:
		queue_free()


func _on_area_entered(area: Area2D) -> void:
	if area is HurtboxComponent:
		(area as HurtboxComponent).take_hit(damage, shooter)
		queue_free()


func _on_body_entered(_body: Node) -> void:
	# Hit a wall (only walls are in the mask).
	queue_free()
