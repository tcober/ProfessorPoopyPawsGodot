class_name BlowDart
extends Area2D

## A single blown dart. Travels in `direction`, damages the first
## HurtboxComponent it hits, and frees itself on impact, on hitting a wall,
## or after `lifetime`. Slower and lighter than the laser bolt — Fuji's poke.
## Collision mask = walls (1) + enemy hurtboxes (16); never hits the player.
##
## The damage is almost beside the point: the dart's job is the DROWSE it
## carries. Enough of them and the target drops asleep — harmless, still, and
## wide open to the tome. A bigger enemy just raises its own drowse_threshold,
## so it takes more darts.

@export var speed: float = 280.0
@export var damage: int = 1
@export var lifetime: float = 1.4
@export var drowse: int = 1

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
		(area as HurtboxComponent).take_hit(damage, shooter, {"drowse": drowse})
		queue_free()


func _on_body_entered(_body: Node) -> void:
	# Hit a wall (only walls are in the mask).
	queue_free()
