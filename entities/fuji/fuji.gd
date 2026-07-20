class_name Fuji
extends PartyMember

## Fuji, the librarian cat. Movement/hop/hurt live in PartyMember; this is her
## kit: the tome — a two-paw overhead swing whose BookHitbox opens only around
## the impact frame — and a reed blow-pipe whose dart leaves on the puff frame
## (no ammo; the planted pose is the cost).

# Kit states (>= PartyMember.STATE_KIT).
const STATE_BOOK := 2
const STATE_DART := 3

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

const BlowDartScene := preload("res://entities/projectiles/blow_dart.tscn")

var _book_timer: float = 0.0
var _dart_timer: float = 0.0
var _darted: bool = false
var _lunge: Vector2 = Vector2.ZERO

@onready var book_hitbox: HitboxComponent = $BookHitbox
@onready var book_shape: CollisionShape2D = $BookHitbox/CollisionShape2D


func _process_kit(delta: float) -> void:
	match state:
		STATE_BOOK:
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
				state = STATE_MOVE
		STATE_DART:
			# Planted while she raises the pipe and puffs — the dart leaves on
			# the puff frame, at the pipe-tip contract.
			velocity = Vector2.ZERO
			_dart_timer -= delta
			if not _darted and _dart_timer <= dart_time - dart_spawn_at:
				_darted = true
				_spawn_dart()
			if _dart_timer <= 0.0:
				state = STATE_MOVE


func _on_attack_intent() -> void:
	if not _airborne:
		_start_book()


func _on_secondary_intent() -> void:
	if not _airborne:
		_start_dart()


func _secondary_action() -> String:
	return "dart"


func _hurt_interrupt() -> void:
	# A hit mid-swing closes the book before the stagger takes over.
	book_shape.set_deferred("disabled", true)


func _start_book() -> void:
	state = STATE_BOOK
	_book_timer = book_time
	_lunge = facing * book_lunge
	velocity = _lunge
	book_hitbox.position = facing * book_reach
	_play_directional("book")


func _start_dart() -> void:
	state = STATE_DART
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
