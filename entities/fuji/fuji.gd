class_name Fuji
extends DirectionalBody2D

## The librarian cat. 8-way movement, 4-way facing (see DirectionalBody2D).
## Fights with her tome — a two-paw overhead swing whose BookHitbox opens only
## around the impact frame — and a reed blow-pipe whose dart leaves on the
## puff frame (no ammo; the planted pose is the cost). Hops like Basil.
## Composes HealthComponent / HurtboxComponent.

enum State { MOVE, BOOK, DART, HURT }

@export var speed: float = 150.0
@export var knockback_speed: float = 130.0
@export var hurt_time: float = 0.3

## Tome swing. Timings track book_* in fuji_frames.tres: 6 frames at 16fps
## with the impact frame held 2 ticks (7/16s total).
@export var book_time: float = 0.44
@export var book_active_from: float = 0.16  # hitbox opens on the strike frame
@export var book_active_to: float = 0.32    # ...and closes after the impact hold
@export var book_reach: float = 12.0        # hitbox center along the facing
@export var book_lunge: float = 90.0        # forward press that sells the swing

## Blow-pipe. Timings track dart_* in fuji_frames.tres: 4 frames at 12fps
## with the puff held 2 ticks (5/12s total).
@export var dart_time: float = 0.42
@export var dart_spawn_at: float = 0.17     # the puff frame — the dart leaves here
@export var muzzle_offset: float = 19.0     # pipe tip in the art (longer than Basil's gun)

## Hop: jumps straight up when standing, leaps in the held direction when
## moving, air-steerable, dodges hits while airborne (same feel as Basil).
@export var jump_height: float = 26.0
@export var jump_time: float = 0.40
@export var jump_speed: float = 200.0
@export var air_steer: float = 110.0

const BlowDartScene := preload("res://entities/projectiles/blow_dart.tscn")

@onready var shadow: Sprite2D = $Shadow
@onready var hurtbox: HurtboxComponent = $HurtboxComponent
@onready var health: HealthComponent = $HealthComponent
@onready var book_hitbox: HitboxComponent = $BookHitbox
@onready var book_shape: CollisionShape2D = $BookHitbox/CollisionShape2D

var state: State = State.MOVE

var _knockback: Vector2 = Vector2.ZERO
var _book_timer: float = 0.0
var _dart_timer: float = 0.0
var _darted: bool = false
var _lunge: Vector2 = Vector2.ZERO
var _jump_dir: Vector2 = Vector2.DOWN
var _airborne: bool = false
var _air_elapsed: float = 0.0
var _sprite_base_y: float = 0.0


func _ready() -> void:
	add_to_group("player")
	_sprite_base_y = sprite.position.y
	shadow.visible = false
	hurtbox.hit.connect(_on_hurt)
	health.died.connect(_on_died)


func _physics_process(delta: float) -> void:
	match state:
		State.MOVE:
			_process_move()
		State.BOOK:
			# The swing carries her forward a step; the hitbox is live only
			# through the strike-and-impact window. Monitoring stays ON — the
			# SHAPE toggles, so already-overlapping hurtboxes register as new
			# pairs (a monitoring flip doesn't re-scan existing overlaps).
			velocity = _lunge
			_lunge = _lunge.move_toward(Vector2.ZERO, book_lunge * 3.0 * delta)
			_book_timer -= delta
			var elapsed := book_time - _book_timer
			var live := elapsed >= book_active_from and elapsed <= book_active_to
			if book_shape.disabled == live:
				book_shape.set_deferred("disabled", not live)
			if _book_timer <= 0.0:
				book_shape.set_deferred("disabled", true)
				state = State.MOVE
		State.DART:
			# Planted while she raises the pipe and puffs — the dart leaves on
			# the puff frame, at the pipe-tip contract.
			velocity = Vector2.ZERO
			_dart_timer -= delta
			if not _darted and _dart_timer <= dart_time - dart_spawn_at:
				_darted = true
				_spawn_dart()
			if _dart_timer <= 0.0:
				state = State.MOVE
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
	if _airborne:
		# Launch momentum plus a bit of mid-air steering with the held direction.
		var steer := input.normalized() * air_steer if input != Vector2.ZERO else Vector2.ZERO
		velocity = _jump_dir * jump_speed + steer
	else:
		if input != Vector2.ZERO:
			input = input.normalized()
			velocity = input * speed
			_update_facing(input)
			_play_directional("walk")
		else:
			velocity = Vector2.ZERO
			_play_directional("idle")

	if Input.is_action_just_pressed("attack") and not _airborne:
		_start_book()
	elif Input.is_action_just_pressed("dart") and not _airborne:
		_start_dart()
	elif Input.is_action_just_pressed("jump") and not _airborne:
		_start_jump()


func _start_book() -> void:
	state = State.BOOK
	_book_timer = book_time
	_lunge = facing * book_lunge
	velocity = _lunge
	book_hitbox.position = facing * book_reach
	_play_directional("book")


func _start_dart() -> void:
	state = State.DART
	velocity = Vector2.ZERO
	_dart_timer = dart_time
	_darted = false
	_play_directional("dart")


func _spawn_dart() -> void:
	var dart := BlowDartScene.instantiate()
	dart.direction = facing
	dart.shooter = self
	get_parent().add_child(dart)
	dart.global_position = global_position + facing * muzzle_offset


func _start_jump() -> void:
	_airborne = true
	_air_elapsed = 0.0
	# Leap in the held direction; with no input held, hop straight up in place.
	var input := Vector2(
		Input.get_axis("move_left", "move_right"),
		Input.get_axis("move_up", "move_down")
	)
	_jump_dir = input.normalized() if input != Vector2.ZERO else Vector2.ZERO
	# Drop a ground shadow so the hop reads; the sprite rises away from it.
	shadow.visible = true
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
		shadow.visible = false
		shadow.scale = Vector2.ONE
		hurtbox.set_deferred("monitorable", true)
		return
	# Parabolic arc, peaks at t = 0.5.
	var arc := 4.0 * t * (1.0 - t)   # 0 -> 1 -> 0
	sprite.position.y = _sprite_base_y - jump_height * arc
	# Shadow shrinks as she rises, selling the height.
	shadow.scale = Vector2.ONE * (1.0 - 0.45 * arc)


func _on_hurt(_damage: int, source: Node) -> void:
	if source is Node2D:
		_knockback = (global_position - (source as Node2D).global_position).normalized() * knockback_speed
	else:
		_knockback = Vector2.ZERO
	book_shape.set_deferred("disabled", true)
	state = State.HURT
	sprite.play("hurt")
	await get_tree().create_timer(hurt_time).timeout
	if state == State.HURT:
		state = State.MOVE


func _on_died() -> void:
	# She can't die (for now): the killing blow reads as a normal hit — the
	# hurt stagger plays and her hearts refill. Real death/respawn comes later.
	health.refill()
