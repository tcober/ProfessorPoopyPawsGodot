class_name HurtboxComponent
extends Area2D

## Receives hits from HitboxComponents and routes damage to a HealthComponent.
## Emits `hit` so the owning entity can react (knockback, flash, hurt state).
##
## `effect` is the optional status payload a compound bolt or a sleep dart rides
## in on — {"drowse": 1} / {"chill": 1} / {"burn": 4}. It is passed straight
## through to the `hit` signal; a StatusComponent on the victim is what reads
## it (see components/status_component.gd). Attacks that carry no status pass
## nothing and the whole layer stays out of their way.

signal hit(damage: int, source: Node, effect: Dictionary)

## Shared empty payload for the no-status path. A `= {}` default would allocate
## a fresh Dictionary on EVERY hit, and this is a projectile-heavy loop.
const NO_EFFECT: Dictionary = {}

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


func take_hit(damage: int, source: Node, effect: Dictionary = NO_EFFECT) -> void:
	if _invincible:
		return
	if health_component:
		health_component.take_damage(damage)
	hit.emit(damage, source, effect)
	if invincible_time > 0.0:
		_invincible = true
		await get_tree().create_timer(invincible_time).timeout
		_invincible = false
