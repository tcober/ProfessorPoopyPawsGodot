class_name Slime
extends CharacterBody2D

## Minimal chase enemy for the vertical slice. Chases the nearest party member
## in range (leader or AI follower alike — SoM pressure on the whole party),
## deals contact damage via an always-on Hitbox, takes laser hits via its Hurtbox,
## and splats through a death animation when its HealthComponent dies. Sits in
## the "enemies" group so party brains can target it; leaves the group on death.
##
## Movement is synced to the bounce animation: the slime only really travels while
## airborne (frames 2-4 of the walk cycle), so it hops instead of gliding.
##
## Statuses live in the composed StatusComponent. While it reports disabled
## (asleep from Fuji's darts, or frozen by a frost compound) the slime goes
## still and STOPS DEALING CONTACT DAMAGE — but it still takes normal damage and
## still gets shoved by knockback, so a sleeper slides when you hit it.

## Emitted when the slime dies (as the explosion starts, before it frees itself).
signal died

@export var speed: float = 28.0
@export var detect_range: float = 90.0
@export var knockback_speed: float = 150.0
@export var knockback_friction: float = 600.0

## Walk-cycle frames where the slime is off the ground (see assets/_gen_slime_sprites.py).
const AIR_FIRST := 2
const AIR_LAST := 4
const AIR_BOOST := 2.1     # airborne speed multiplier...
const GROUND_DRAG := 0.1   # ...vs. barely creeping while grounded
const SQUASH_FRAME := 1    # the flattest cell of the walk cycle (see the generator)

## Status tells. Every one of these BOOSTS a channel rather than pulling the
## others down: a multiply that only subtracts drags a saturated body toward
## gray or olive, which is the exact mud the palette doctrine bans (the first
## pass at these read as a dead gray slime and a khaki one).
##
## Sleep barely tints at all on purpose. The Zs and the stopped bounce already
## say "asleep", and a violet sleep wash was invisible on the violet BigSlime
## anyway — a tell that only works on one enemy is not a tell.
const ASLEEP_TINT := Color(0.88, 0.88, 1.02)    # a breath cooler, nothing more
const FROZEN_TINT := Color(0.70, 0.98, 1.30)    # rime: blue UP, not green down
const BURNING_TINT := Color(1.45, 0.92, 0.72)   # ember: hot and bright, never khaki

## The sleeping-Zs bubble. Cell 15 of the FROZEN row 0 of the shared fx sheet —
## drawn for the prologue and never used until now, so sleep costs no new art.
const FX_SHEET := preload("res://assets/prologue_fx.png")
const FX_ZZZ := 15

## How high the Zs float above the dome — a taller body needs a taller lift.
## Measured to sit just off the dome's crown: the fx cell is itself 16px tall
## and draws centred, so this is roughly (dome height / 2) + 6, not the full
## body height, or the Zs detach and read as belonging to nothing.
@export var zzz_lift: float = 12.0

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var health: HealthComponent = $HealthComponent
@onready var hurtbox: HurtboxComponent = $HurtboxComponent
@onready var hitbox: HitboxComponent = $Hitbox
@onready var status: StatusComponent = $StatusComponent
@onready var hitbox_shape: CollisionShape2D = $Hitbox/CollisionShape2D

var _knockback: Vector2 = Vector2.ZERO
var _dying: bool = false
var _flashing: bool = false
var _zzz: Sprite2D = null
var _zzz_t: float = 0.0


func _ready() -> void:
	health.died.connect(_on_died)
	hurtbox.hit.connect(_on_hit)
	status.disabled_changed.connect(_on_disabled_changed)
	add_to_group("enemies")
	sprite.play("walk_down")


func _physics_process(delta: float) -> void:
	if _dying:
		velocity = Vector2.ZERO
		return
	var target := _nearest_party()
	if _knockback != Vector2.ZERO:
		# Above the disabled check on purpose: a hit still shoves a sleeper,
		# so it slides instead of taking the blow like a rock.
		velocity = _knockback
		_knockback = _knockback.move_toward(Vector2.ZERO, knockback_friction * delta)
	elif status.is_disabled():
		velocity = Vector2.ZERO
	elif target and global_position.distance_to(target.global_position) <= detect_range:
		var dir := (target.global_position - global_position).normalized()
		var hop := AIR_BOOST if sprite.frame >= AIR_FIRST and sprite.frame <= AIR_LAST else GROUND_DRAG
		velocity = dir * speed * hop * status.move_scale()
		_face(dir)
	else:
		velocity = Vector2.ZERO
	move_and_slide()
	# Burn has no end-signal (it just runs out of ticks), so the tell is
	# reconciled every frame rather than only on status transitions.
	if not _flashing:
		_refresh_tint()
	if _zzz != null:
		# Slow drift so the Zs breathe instead of sitting there as a decal.
		_zzz_t += delta
		_zzz.offset.y = -zzz_lift - sin(_zzz_t * 2.2) * 2.0
		_zzz.modulate.a = 0.75 + 0.25 * sin(_zzz_t * 2.2)


## Re-picked every frame so pressure follows whoever wanders closest.
func _nearest_party() -> Node2D:
	var best: Node2D = null
	var best_d := INF
	for m in get_tree().get_nodes_in_group("party"):
		var d := global_position.distance_to((m as Node2D).global_position)
		if d < best_d:
			best_d = d
			best = m
	return best


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


func _on_hit(_damage: int, source: Node, effect: Dictionary) -> void:
	if source is Node2D:
		_knockback = (global_position - (source as Node2D).global_position).normalized() * knockback_speed
	status.apply(effect)
	# Brief white flash to telegraph the hit.
	_flashing = true
	sprite.modulate = Color(2.0, 2.0, 2.0)
	await get_tree().create_timer(0.08).timeout
	_flashing = false
	if is_instance_valid(sprite) and not _dying:
		_refresh_tint()


## Sleep and freeze both stop the body dealing contact damage. The Hitbox's
## SHAPE is what toggles, never `monitoring`: flipping monitoring back on does
## not re-scan areas that are ALREADY overlapping, so a slime that woke up while
## still touching the player would never re-register and would stay harmless
## forever. (The same reason Fuji's BookHitbox toggles its shape.) `_on_died`
## can get away with `monitoring = false` only because it frees the node.
func _on_disabled_changed(is_disabled: bool) -> void:
	if _dying:
		return
	hitbox_shape.set_deferred("disabled", is_disabled)
	if is_disabled:
		# Stop the bounce ON the squash frame rather than wherever the cycle
		# happened to be — the flattest pose in the walk row, so the body reads
		# as slumped instead of hovering mid-hop with the lights out.
		sprite.set_frame_and_progress(SQUASH_FRAME, 0.0)
		sprite.pause()
	else:
		sprite.play()
	_refresh_tint()
	_sync_zzz()


## The Zs ride as a CHILD of the body rather than a loose World fx, so they
## follow a sleeper that gets knocked sliding. A child sprite y-sorts with its
## parent, which is what the airborne-fx rule wants anyway: ground-anchored
## origin, art lifted by `offset` alone.
func _sync_zzz() -> void:
	var want := status.is_asleep() and not _dying
	if want and _zzz == null:
		_zzz = WorldFx.sheet_sprite(FX_SHEET, FX_ZZZ)
		_zzz.offset = Vector2(0.0, -zzz_lift)
		_zzz_t = 0.0
		add_child(_zzz)
	elif not want and _zzz != null:
		_zzz.queue_free()
		_zzz = null


## Status colour, so the flash restore never wipes an active ailment's tell.
func _refresh_tint() -> void:
	if status.is_frozen():
		sprite.modulate = FROZEN_TINT
	elif status.is_asleep():
		sprite.modulate = ASLEEP_TINT
	elif status.is_burning():
		sprite.modulate = BURNING_TINT
	else:
		sprite.modulate = Color.WHITE


func _on_died() -> void:
	_dying = true
	_sync_zzz()                    # a slime killed in its sleep drops the Zs
	remove_from_group("enemies")   # party brains stop targeting the splat
	died.emit()
	# Stop dealing/receiving damage while the splat plays out.
	hitbox.set_deferred("monitoring", false)
	hurtbox.set_deferred("monitorable", false)
	$CollisionShape2D.set_deferred("disabled", true)
	sprite.modulate = Color.WHITE
	sprite.play("death")
	await sprite.animation_finished
	queue_free()
