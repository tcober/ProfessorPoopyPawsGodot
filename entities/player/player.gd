class_name Player
extends PartyMember

## Basil, the science cat. Movement/hop/hurt live in PartyMember; this is his
## kit: a laser gun fired in the facing direction — the bolt leaves the INSTANT
## the trigger is pulled and the recoil shoves him back like he can barely hold
## on. Beakers are the gun's magazines: pickups go into his coat as spares
## (max_beakers), and reloading (R, or pulling the trigger dry) plays the pour
## animation and empties one into the gun.

signal ammo_changed(current: int, max_ammo: int)
signal beakers_changed(current: int, max_beakers: int)

# Kit states (>= PartyMember.STATE_KIT).
const STATE_SHOOT := 2
const STATE_RELOAD := 3

## Laser gun. Fires the frame the trigger is pulled — no wind-up.
@export var max_ammo: int = 6
@export var fire_recover: float = 0.24   # control lock while the recoil slide plays out
@export var muzzle_offset: float = 16.0  # how far in front the bolt spawns (gun tip in the art)
@export var recoil_push: float = 240.0   # backward shove when the bolt leaves — barely held on
@export var max_beakers: int = 3         # spare magazines he can carry
@export var reload_time: float = 0.65    # beaker-pour animation lock (matches "reload" anim)
@export var reload_pour_at: float = 0.35 # seconds in when the juice lands (anim's stream frame)

const LaserBoltScene := preload("res://entities/projectiles/laser_bolt.tscn")
const MuzzleFlashScene := preload("res://entities/projectiles/muzzle_flash.tscn")

var ammo: int = 0
var beakers: int = 0

var _shoot_timer: float = 0.0
var _reload_timer: float = 0.0
var _poured: bool = false
var _recoil: Vector2 = Vector2.ZERO


func _ready() -> void:
	super()
	ammo = max_ammo
	beakers = 1                      # one spare mag in the coat to start
	ammo_changed.emit(ammo, max_ammo)
	beakers_changed.emit(beakers, max_beakers)


func _process_kit(delta: float) -> void:
	match state:
		STATE_SHOOT:
			# The bolt already left on the trigger frame; this is the kick —
			# he skids backward, barely holding on, while control is locked.
			velocity = _recoil
			_recoil = _recoil.move_toward(Vector2.ZERO, recoil_push * 4.5 * delta)
			_shoot_timer -= delta
			if _shoot_timer <= 0.0:
				state = STATE_MOVE
		STATE_RELOAD:
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
				state = STATE_MOVE


func _on_attack_intent() -> void:
	_try_fire()   # no airborne gate — he'll fire mid-hop


func _on_secondary_intent() -> void:
	_try_reload()


func _secondary_action() -> String:
	return "reload"


func _try_fire() -> void:
	if ammo <= 0:
		# Dry trigger pulls the fresh mag in (no-op if his coat is empty too).
		_try_reload()
		return
	# Everything lands on the trigger frame: bolt, flash, kick, recoil pose.
	ammo -= 1
	ammo_changed.emit(ammo, max_ammo)
	state = STATE_SHOOT
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
	if state != STATE_MOVE or _airborne:
		return
	if beakers <= 0 or ammo >= max_ammo:
		return
	state = STATE_RELOAD
	velocity = Vector2.ZERO
	facing = Vector2.DOWN   # he turns to the camera to pour
	_reload_timer = reload_time
	_poured = false
	sprite.play("reload")
	sprite.flip_h = false
