class_name HurtboxComponent
extends Area2D

## Receives hits from HitboxComponents and routes damage to a HealthComponent.
## Emits `hit` so the owning entity can react (knockback, flash, hurt state).

signal hit(damage: int, source: Node)

@export var health_component: HealthComponent
@export var invincible_time: float = 0.5

## The i-frame window as a deadline, not an awaited timer: a hurtbox freed
## mid-window (a slime splatting, a scene change) would resume a coroutine on
## a dead instance just to clear a flag nobody reads again.
var _invincible_until_ms: int = 0


func _ready() -> void:
	# Hand-authored .tscn files must mark node exports with
	# node_paths=PackedStringArray("health_component") on the node header or
	# the reference silently loads as null. Fall back to the conventional
	# sibling so a forgotten attribute degrades loudly-visibly, not silently.
	if health_component == null:
		health_component = get_node_or_null(^"../HealthComponent") as HealthComponent


func take_hit(damage: int, source: Node) -> void:
	if Time.get_ticks_msec() < _invincible_until_ms:
		return
	# Armed BEFORE the damage lands: a `hit` handler that swings back through
	# this same hurtbox in the same frame must not stack a second hit.
	if invincible_time > 0.0:
		_invincible_until_ms = Time.get_ticks_msec() + int(invincible_time * 1000.0)
	if health_component:
		health_component.take_damage(damage)
	hit.emit(damage, source)
