class_name Player
extends DirectionalBody2D

## The science cat. 8-way movement, 4-way facing (see DirectionalBody2D). Fires a
## laser gun in the facing direction — the bolt leaves the INSTANT the trigger is
## pulled and the recoil shoves him back like he can barely hold on. Beakers are
## the gun's magazines: pickups go into his coat as spares (max_beakers), and
## reloading (R, or pulling the trigger dry) plays the pour animation and empties
## one into the gun. Composes HealthComponent / HurtboxComponent.

signal ammo_changed(current: int, max_ammo: int)
signal beakers_changed(current: int, max_beakers: int)

enum State { MOVE, SHOOT, RELOAD, HURT }

@export var speed: float = 150.0
@export var knockback_speed: float = 130.0
@export var hurt_time: float = 0.3

## Laser gun. Fires the frame the trigger is pulled — no wind-up.
@export var max_ammo: int = 6
@export var fire_recover: float = 0.24   # control lock while the recoil slide plays out
@export var muzzle_offset: float = 16.0  # how far in front the bolt spawns (gun tip in the art)
@export var recoil_push: float = 240.0   # backward shove when the bolt leaves — barely held on
@export var max_beakers: int = 3         # spare magazines he can carry
@export var reload_time: float = 0.65    # beaker-pour animation lock (matches "reload" anim)
@export var reload_pour_at: float = 0.35 # seconds in when the juice lands (anim's stream frame)

## Hop: jumps straight up when standing, leaps in the held direction when moving, and
## can be steered a little mid-air (SNES-Zelda style). Dodges hits while airborne.
@export var jump_height: float = 26.0
@export var jump_time: float = 0.40
@export var jump_speed: float = 200.0    # forward leap speed while airborne
@export var air_steer: float = 110.0     # mid-air steering drift

const LaserBoltScene := preload("res://entities/projectiles/laser_bolt.tscn")
const MuzzleFlashScene := preload("res://entities/projectiles/muzzle_flash.tscn")

@onready var shadow: Sprite2D = $Shadow
@onready var hurtbox: HurtboxComponent = $HurtboxComponent
@onready var health: HealthComponent = $HealthComponent

var state: State = State.MOVE
var ammo: int = 0
var beakers: int = 0

var _knockback: Vector2 = Vector2.ZERO
var _shoot_timer: float = 0.0
var _reload_timer: float = 0.0
var _poured: bool = false
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
	beakers = 1                      # one spare mag in the coat to start
	ammo_changed.emit(ammo, max_ammo)
	beakers_changed.emit(beakers, max_beakers)
	hurtbox.hit.connect(_on_hurt)
	health.died.connect(_on_died)


func _physics_process(delta: float) -> void:
	match state:
		State.MOVE:
			_process_move()
		State.SHOOT:
			# The bolt already left on the trigger frame; this is the kick —
			# he skids backward, barely holding on, while control is locked.
			velocity = _recoil
			_recoil = _recoil.move_toward(Vector2.ZERO, recoil_push * 4.5 * delta)
			_shoot_timer -= delta
			if _shoot_timer <= 0.0:
				state = State.MOVE
		State.RELOAD:
			# Planted while he pours a beaker mag into the gun. The juice lands
			# partway through the anim — that's when the mag is actually spent.
			velocity = Vector2.ZERO
			_reload_timer -= delta
			if not _poured and _reload_timer <= reload_time - reload_pour_at:
				_poured = true
				beakers -= 1
				beakers_changed.emit(beakers, max_beakers)
				ammo = max_ammo
				ammo_changed.emit(ammo, max_ammo)
			if _reload_timer <= 0.0:
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
	elif Input.is_action_just_pressed("reload"):
		_try_reload()
	elif Input.is_action_just_pressed("jump") and not _airborne:
		_start_jump()


func _try_fire() -> void:
	if ammo <= 0:
		# Dry trigger pulls the fresh mag in (no-op if his coat is empty too).
		_try_reload()
		return
	# Everything lands on the trigger frame: bolt, flash, kick, recoil pose.
	ammo -= 1
	ammo_changed.emit(ammo, max_ammo)
	state = State.SHOOT
	_shoot_timer = fire_recover
	_recoil = -facing * recoil_push
	velocity = _recoil
	_spawn_bolt()
	_play_directional("shoot")


func _spawn_bolt() -> void:
	var bolt := LaserBoltScene.instantiate()
	bolt.direction = facing
	bolt.shooter = self
	get_parent().add_child(bolt)
	bolt.global_position = global_position + facing * muzzle_offset
	# Blast at the gun root.
	var flash := MuzzleFlashScene.instantiate()
	add_child(flash)
	if facing == Vector2.UP:
		# The up-view art holds the gun BEHIND his head — draw the flash there
		# too, before the sprite in child order (z_index would sink it under
		# the ground painting).
		move_child(flash, sprite.get_index())
	flash.position = facing * muzzle_offset
	flash.rotation = facing.angle()


func collect_beaker() -> bool:
	## A beaker is a spare magazine. False = paws full, leave it on the grass.
	if beakers >= max_beakers:
		return false
	beakers += 1
	beakers_changed.emit(beakers, max_beakers)
	return true


func _try_reload() -> void:
	# The pour is a planted ritual — no mid-hop reloads, nothing to load if the
	# mag is topped up or his coat is empty. (Empty-click feedback comes later.)
	if state != State.MOVE or _airborne:
		return
	if beakers <= 0 or ammo >= max_ammo:
		return
	state = State.RELOAD
	velocity = Vector2.ZERO
	facing = Vector2.DOWN   # he turns to the camera to pour
	_reload_timer = reload_time
	_poured = false
	sprite.play("reload")
	sprite.flip_h = false


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
	# He can't die (for now): the killing blow reads as a normal hit — the
	# hurt stagger plays and his hearts refill. Real death/respawn comes later.
	health.refill()
