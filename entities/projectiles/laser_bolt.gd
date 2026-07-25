class_name LaserBolt
extends Area2D

## A single laser shot. Travels in `direction`, damages the first HurtboxComponent it
## hits, and frees itself on impact, on hitting a wall, or after `lifetime`.
## Collision mask = walls (1) + enemy hurtboxes (16); never hits the player.
##
## ONE scene serves every compound. Rather than a bolt scene per reagent, the
## shooter calls apply_compound() before adding it to the tree and the loaded
## chemistry sets the numbers, the status payload and the colour — the same
## pattern as `direction`/`shooter`, which are also poured in from outside.
## The defaults below are the plain green base reagent, so a bolt spawned
## without a compound behaves exactly as it always did.

@export var speed: float = 700.0
@export var damage: int = 2      # slimes have 4 HP -> two shots
@export var lifetime: float = 1.2

## Set by the shooter before adding to the tree.
var direction: Vector2 = Vector2.RIGHT
var shooter: Node = null

## Compound-driven. `pierce` keeps the bolt alive through a kill so plasma can
## skewer a line of slimes; `_struck` stops it double-hitting the same hurtbox
## on consecutive frames while it passes through.
var effect: Dictionary = {}
var pierce: bool = false
var spray: bool = false

var _life_remaining: float = 0.0
var _struck: Array[Area2D] = []
var _tint: Color = Color.WHITE

## How wide a spray gout swells to, and how far down it fades, over its life.
const SPRAY_FROM := 0.5
const SPRAY_TO := 1.7


func apply_compound(c: Compound) -> void:
	if c == null:
		return
	speed = c.speed
	damage = c.hit_damage()
	lifetime = c.lifetime
	effect = c.effect
	pierce = c.pierce
	spray = c.spray
	_tint = c.tint
	modulate = _tint


func _ready() -> void:
	direction = direction.normalized()
	rotation = direction.angle()
	_life_remaining = lifetime
	area_entered.connect(_on_area_entered)
	body_entered.connect(_on_body_entered)


func _physics_process(delta: float) -> void:
	global_position += direction * speed * delta
	_life_remaining -= delta
	if spray:
		# Swell and thin as it goes, so the short reach reads as a gout of
		# flame petering out rather than a laser blinking off mid-air.
		var t := 1.0 - clampf(_life_remaining / maxf(lifetime, 0.001), 0.0, 1.0)
		scale = Vector2.ONE * lerpf(SPRAY_FROM, SPRAY_TO, t)
		modulate = Color(_tint.r, _tint.g, _tint.b, 1.0 - t * 0.75)
	if _life_remaining <= 0.0:
		queue_free()


func _on_area_entered(area: Area2D) -> void:
	if area is HurtboxComponent:
		if area in _struck:
			return
		_struck.append(area)
		(area as HurtboxComponent).take_hit(damage, shooter, effect)
		if not pierce:
			queue_free()


func _on_body_entered(_body: Node) -> void:
	# Hit a wall (only walls are in the mask).
	queue_free()
