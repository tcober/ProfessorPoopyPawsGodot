class_name Slime
extends CharacterBody2D

## Minimal chase enemy for the vertical slice. Chases the player when in range,
## deals contact damage via an always-on Hitbox, takes laser hits via its Hurtbox,
## and splats through a death animation when its HealthComponent dies.
##
## Movement is synced to the bounce animation: the slime only really travels while
## airborne (frames 2-4 of the walk cycle), so it hops instead of gliding.

@export var speed: float = 28.0
@export var detect_range: float = 90.0
@export var knockback_speed: float = 150.0
@export var knockback_friction: float = 600.0

## Walk-cycle frames where the slime is off the ground (see assets/_gen_slime_sprites.py).
const AIR_FIRST := 2
const AIR_LAST := 4
const AIR_BOOST := 2.1     # airborne speed multiplier...
const GROUND_DRAG := 0.1   # ...vs. barely creeping while grounded

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var health: HealthComponent = $HealthComponent
@onready var hurtbox: HurtboxComponent = $HurtboxComponent
@onready var hitbox: HitboxComponent = $Hitbox

var _player: Node2D
var _knockback: Vector2 = Vector2.ZERO
var _dying: bool = false


func _ready() -> void:
	health.died.connect(_on_died)
	hurtbox.hit.connect(_on_hit)
	_player = get_tree().get_first_node_in_group("player")
	sprite.play("walk_down")


func _physics_process(delta: float) -> void:
	if _dying:
		velocity = Vector2.ZERO
		return
	if _knockback != Vector2.ZERO:
		velocity = _knockback
		_knockback = _knockback.move_toward(Vector2.ZERO, knockback_friction * delta)
	elif _player and global_position.distance_to(_player.global_position) <= detect_range:
		var dir := (_player.global_position - global_position).normalized()
		var hop := AIR_BOOST if sprite.frame >= AIR_FIRST and sprite.frame <= AIR_LAST else GROUND_DRAG
		velocity = dir * speed * hop
		_face(dir)
	else:
		velocity = Vector2.ZERO
	move_and_slide()


func _face(dir: Vector2) -> void:
	if absf(dir.x) > absf(dir.y):
		_play_keeping_frame("walk_side")
		sprite.flip_h = dir.x < 0.0
	else:
		_play_keeping_frame("walk_up" if dir.y < 0.0 else "walk_down")


func _play_keeping_frame(anim: String) -> void:
	# Swap facing without restarting the bounce cycle mid-hop.
	if sprite.animation == anim:
		return
	var frame := sprite.frame
	var progress := sprite.frame_progress
	sprite.play(anim)
	sprite.set_frame_and_progress(frame, progress)


func _on_hit(_damage: int, source: Node) -> void:
	if source is Node2D:
		_knockback = (global_position - (source as Node2D).global_position).normalized() * knockback_speed
	# Brief white flash to telegraph the hit.
	sprite.modulate = Color(2.0, 2.0, 2.0)
	await get_tree().create_timer(0.08).timeout
	if is_instance_valid(sprite):
		sprite.modulate = Color.WHITE


func _on_died() -> void:
	_dying = true
	# Stop dealing/receiving damage while the splat plays out.
	hitbox.set_deferred("monitoring", false)
	hurtbox.set_deferred("monitorable", false)
	$CollisionShape2D.set_deferred("disabled", true)
	sprite.modulate = Color.WHITE
	sprite.play("death")
	await sprite.animation_finished
	queue_free()
