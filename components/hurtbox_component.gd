class_name HurtboxComponent
extends Area2D

## Receives hits from HitboxComponents and routes damage to a HealthComponent.
## Emits `hit` so the owning entity can react (knockback, flash, hurt state).

signal hit(damage: int, source: Node)

@export var health_component: HealthComponent
@export var invincible_time: float = 0.5

var _invincible: bool = false


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
