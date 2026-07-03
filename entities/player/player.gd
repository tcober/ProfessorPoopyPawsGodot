class_name Player
extends CharacterBody2D

## The science cat. 8-way movement, 4-way facing. Fires a laser gun in the facing
## direction (single shot per press) and refills its charges from beaker pickups.
## Composes HealthComponent / HurtboxComponent and drives an AnimatedSprite2D by
## animation name so a real sprite sheet swaps in with no code change.

signal ammo_changed(current: int, max_ammo: int)

enum State { MOVE, SHOOT, HURT }

@export var speed: float = 150.0
@export var knockback_speed: float = 130.0
@export var hurt_time: float = 0.3

## Laser gun.
@export var max_ammo: int = 6
@export var fire_windup: float = 0.12    # gun-raise time before the bolt actually fires
@export var fire_recover: float = 0.20   # planted "settle" time after the shot
@export var muzzle_offset: float = 16.0  # how far in front the bolt spawns (gun tip in the art)
@export var recoil_push: float = 165.0   # backward shove when the bolt leaves — it KICKS

## Hop: jumps straight up when standing, leaps in the held direction when moving, and
## can be steered a little mid-air (SNES-Zelda style). Dodges hits while airborne.
@export var jump_height: float = 26.0
@export var jump_time: float = 0.40
@export var jump_speed: float = 200.0    # forward leap speed while airborne
@export var air_steer: float = 110.0     # mid-air steering drift

const LaserBoltScene := preload("res://entities/projectiles/laser_bolt.tscn")
const MuzzleFlashScene := preload("res://entities/projectiles/muzzle_flash.tscn")

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var shadow: Sprite2D = $Shadow
@onready var hurtbox: HurtboxComponent = $HurtboxComponent
@onready var health: HealthComponent = $HealthComponent

var state: State = State.MOVE
var facing: Vector2 = Vector2.DOWN
var ammo: int = 0

var _knockback: Vector2 = Vector2.ZERO
var _shoot_timer: float = 0.0
var _fired: bool = false
var _recoil: Vector2 = Vector2.ZERO
var _jump_dir: Vector2 = Vector2.DOWN
var _airborne: bool = false
var _air_elapsed: float = 0.0
var _sprite_base_y: float = 0.0


func _ready() -> void:
	add_to_group("player")
	_sprite_base_y = sprite.position.y
	shadow.visible = false
	ammo = max_ammo
	ammo_changed.emit(ammo, max_ammo)
	hurtbox.hit.connect(_on_hurt)
	health.died.connect(_on_died)


func _physics_process(delta: float) -> void:
	match state:
		State.MOVE:
			_process_move()
		State.SHOOT:
			# The shot shoves him backward; a slower bleed-off lets the slide read.
			velocity = _recoil
			_recoil = _recoil.move_toward(Vector2.ZERO, recoil_push * 4.5 * delta)
			_shoot_timer -= delta
			# Wind-up first; the bolt leaves once the gun is raised.
			if not _fired and _shoot_timer <= fire_recover:
				_fire_bolt()
			if _shoot_timer <= 0.0:
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

	if Input.is_action_just_pressed("attack"):
		_try_fire()
	elif Input.is_action_just_pressed("jump") and not _airborne:
		_start_jump()


func _try_fire() -> void:
	if ammo <= 0:
		# Out of charges — needs a beaker refill. (Empty-click feedback comes later.)
		return
	# Start the shoot pose now; the bolt fires after the wind-up (see _physics_process).
	state = State.SHOOT
	_fired = false
	_shoot_timer = fire_windup + fire_recover
	velocity = Vector2.ZERO
	_play_directional("shoot")


func _fire_bolt() -> void:
	_fired = true
	ammo -= 1
	ammo_changed.emit(ammo, max_ammo)
	_recoil = -facing * recoil_push
	_spawn_bolt()


func _spawn_bolt() -> void:
	var bolt := LaserBoltScene.instantiate()
	bolt.direction = facing
	bolt.shooter = self
	get_parent().add_child(bolt)
	bolt.global_position = global_position + facing * muzzle_offset
	# Blast at the gun root.
	var flash := MuzzleFlashScene.instantiate()
	add_child(flash)
	flash.position = facing * muzzle_offset
	flash.rotation = facing.angle()


func refill_ammo(amount: int) -> void:
	ammo = mini(ammo + amount, max_ammo)
	ammo_changed.emit(ammo, max_ammo)


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
	# Shadow shrinks as he rises, selling the height.
	shadow.scale = Vector2.ONE * (1.0 - 0.45 * arc)


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
