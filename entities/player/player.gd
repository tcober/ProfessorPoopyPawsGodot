class_name Player
extends CharacterBody2D

## The science cat. 8-way movement, 4-way facing, directional sword swing.
## Composes HealthComponent / HurtboxComponent / HitboxComponent and drives an
## AnimatedSprite2D by animation name so a real sprite sheet swaps in with no code change.

enum State { MOVE, ATTACK, HURT }

@export var speed: float = 115.0
@export var knockback_speed: float = 130.0
@export var hurt_time: float = 0.3

## Hop: a short cosmetic jump that briefly lifts the cat and dodges hits mid-air.
@export var jump_height: float = 9.0
@export var jump_time: float = 0.42

## How far in front of the cat the sword hitbox sits, in pixels.
const HITBOX_OFFSET := 12.0

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var hitbox: HitboxComponent = $Hitbox
@onready var hitbox_shape: CollisionShape2D = $Hitbox/CollisionShape2D
@onready var hurtbox: HurtboxComponent = $HurtboxComponent
@onready var health: HealthComponent = $HealthComponent

var state: State = State.MOVE
var facing: Vector2 = Vector2.DOWN
var _knockback: Vector2 = Vector2.ZERO
var _airborne: bool = false
var _air_elapsed: float = 0.0
var _sprite_base_y: float = 0.0


func _ready() -> void:
	add_to_group("player")
	_sprite_base_y = sprite.position.y
	_set_hitbox_enabled(false)
	hurtbox.hit.connect(_on_hurt)
	health.died.connect(_on_died)
	sprite.animation_finished.connect(_on_animation_finished)


func _physics_process(delta: float) -> void:
	match state:
		State.MOVE:
			_process_move()
		State.ATTACK:
			velocity = Vector2.ZERO
		State.HURT:
			velocity = _knockback
			_knockback = _knockback.move_toward(Vector2.ZERO, knockback_speed * 4.0 * delta)
	_update_hop(delta)
	move_and_slide()


func _process_move() -> void:
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

	if Input.is_action_just_pressed("attack"):
		_start_attack()
	elif Input.is_action_just_pressed("jump") and not _airborne:
		_start_jump()


func _start_jump() -> void:
	_airborne = true
	_air_elapsed = 0.0
	# Lift the hurtbox out of reach so a well-timed hop dodges an attack.
	hurtbox.set_deferred("monitorable", false)


func _update_hop(delta: float) -> void:
	if not _airborne:
		return
	_air_elapsed += delta
	var t := _air_elapsed / jump_time
	if t >= 1.0:
		_airborne = false
		sprite.position.y = _sprite_base_y
		hurtbox.set_deferred("monitorable", true)
		return
	# Parabolic arc, peaks at t = 0.5.
	sprite.position.y = _sprite_base_y - 4.0 * jump_height * t * (1.0 - t)


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


func _start_attack() -> void:
	state = State.ATTACK
	velocity = Vector2.ZERO
	_play_directional("attack")
	hitbox.position = facing * HITBOX_OFFSET
	_set_hitbox_enabled(true)


func _set_hitbox_enabled(enabled: bool) -> void:
	hitbox.monitoring = enabled
	hitbox_shape.set_deferred("disabled", not enabled)


func _on_animation_finished() -> void:
	if state == State.ATTACK:
		_set_hitbox_enabled(false)
		state = State.MOVE


func _on_hurt(_damage: int, source: Node) -> void:
	if source is Node2D:
		_knockback = (global_position - (source as Node2D).global_position).normalized() * knockback_speed
	else:
		_knockback = Vector2.ZERO
	state = State.HURT
	sprite.play("hurt")
	await get_tree().create_timer(hurt_time).timeout
	if state == State.HURT:
		state = State.MOVE


func _on_died() -> void:
	set_physics_process(false)
	sprite.play("hurt")
	# Death/respawn flow comes later; for the slice we just stop the cat.
