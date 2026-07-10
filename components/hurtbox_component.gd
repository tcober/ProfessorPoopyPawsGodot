class_name HurtboxComponent
extends Area2D

## Receives hits from HitboxComponents and routes damage to a HealthComponent.
## Emits `hit` so the owning entity can react (knockback, flash, hurt state).

signal hit(damage: int, source: Node)

@export var health_component: HealthComponent
@export var invincible_time: float = 0.5

var _invincible: bool = false


func _ready() -> void:
	# Hand-authored .tscn files must mark node exports with
	# node_paths=PackedStringArray("health_component") on the node header or
	# the reference silently loads as null. Fall back to the conventional
	# sibling so a forgotten attribute degrades loudly-visibly, not silently.
	if health_component == null:
		health_component = get_node_or_null(^"../HealthComponent") as HealthComponent


func take_hit(damage: int, source: Node) -> void:
	if _invincible:
		return
	if health_component:
		health_component.take_damage(damage)
	hit.emit(damage, source)
	if invincible_time > 0.0:
		_invincible = true
		await get_tree().create_timer(invincible_time).timeout
		_invincible = false
