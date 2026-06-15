class_name Slime
extends CharacterBody2D

## Minimal chase enemy for the vertical slice. Chases the player when in range,
## deals contact damage via an always-on Hitbox, takes sword hits via its Hurtbox,
## and frees itself when its HealthComponent dies.

@export var speed: float = 28.0
@export var detect_range: float = 90.0
@export var knockback_speed: float = 150.0
@export var knockback_friction: float = 600.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var health: HealthComponent = $HealthComponent
@onready var hurtbox: HurtboxComponent = $HurtboxComponent

var _player: Node2D
var _knockback: Vector2 = Vector2.ZERO


func _ready() -> void:
	health.died.connect(_on_died)
	hurtbox.hit.connect(_on_hit)
	_player = get_tree().get_first_node_in_group("player")


func _physics_process(delta: float) -> void:
	if _knockback != Vector2.ZERO:
		velocity = _knockback
		_knockback = _knockback.move_toward(Vector2.ZERO, knockback_friction * delta)
	elif _player and global_position.distance_to(_player.global_position) <= detect_range:
		var dir := (_player.global_position - global_position).normalized()
		velocity = dir * speed
	else:
		velocity = Vector2.ZERO
	move_and_slide()


func _on_hit(_damage: int, source: Node) -> void:
	if source is Node2D:
		_knockback = (global_position - (source as Node2D).global_position).normalized() * knockback_speed
	# Brief white flash to telegraph the hit.
	sprite.modulate = Color(2.0, 2.0, 2.0)
	await get_tree().create_timer(0.08).timeout
	if is_instance_valid(sprite):
		sprite.modulate = Color.WHITE


func _on_died() -> void:
	queue_free()
