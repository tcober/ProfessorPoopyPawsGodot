class_name PartyMember
extends DirectionalBody2D

## Shared chassis for the party's zone bodies (Basil, Fuji): 8-way movement,
## the hop, knockback/hurt, and the can't-die refill live here ONCE. Each
## physics frame the member gathers an Intent — from the keyboard when it is
## the leader, from its AIBrain child ("Brain") when it is following — and the
## same movement/attack code runs either way. Subclasses add their kit as
## states >= STATE_KIT behind _process_kit and the _on_*_intent hooks.
## The Party autoload owns leadership: it flips is_leader and keeps the
## "player" group (doors, exits, pickups) pointing at the leader only; every
## member sits in the "party" group (enemy targeting).

const STATE_MOVE := 0
const STATE_HURT := 1
const STATE_KIT := 2   # subclass kit states start here


## One frame of control, whoever the author: keyboard or brain.
class Intent:
	var move := Vector2.ZERO      # direction; length > 1 = AI catch-up sprint
	var face := Vector2.ZERO      # optional facing override (AI takes aim)
	var attack := false           # edge
	var secondary := false        # edge: Basil reload / Fuji dart
	var jump := false             # edge

	func clear() -> void:
		move = Vector2.ZERO
		face = Vector2.ZERO
		attack = false
		secondary = false
		jump = false


@export var speed: float = 150.0
@export var knockback_speed: float = 130.0
@export var hurt_time: float = 0.3

## Hop: jumps straight up when standing, leaps in the held direction when
## moving, and can be steered a little mid-air (SNES-Zelda style). Dodges
## hits while airborne. Followers never hop — brains don't set intent.jump.
@export var jump_height: float = 26.0
@export var jump_time: float = 0.40
@export var jump_speed: float = 200.0    # forward leap speed while airborne
@export var air_steer: float = 110.0     # mid-air steering drift

## AI catch-up sprint headroom: intent.move above unit length scales speed.
const MOVE_CLAMP := 1.3

## Walls, and only walls (bodies are on 2/4) — what a muzzle has to dodge.
const WALL_MASK := 1

## How far across the barrel line place_muzzle may slide a shot to find free
## air. 6px covers the worst case by construction: the bolt's 3px half-height
## plus the 2px the body's origin can sink into a solid cell. Wider than that
## and the shot would visibly leave the gun.
const MUZZLE_NUDGE := 6

var member_id: StringName
var is_leader: bool = true   # a lone member in a one-off scene plays from keyboard

## The body's OWN max HP, before any sheet is folded in — captured once, in
## _apply_sheet, straight off the .tscn export. The party menu needs it to
## recompute max HP when a +VIT hat is equipped mid-scene: without a clean
## baseline the only options are adding the delta (which drifts every time gear
## changes) or re-reading a value that already has VIT in it.
var base_max_health: int = 0
var state: int = STATE_MOVE
var intent := Intent.new()

var _knockback: Vector2 = Vector2.ZERO
var _hurt_timer: float = 0.0
var _jump_dir: Vector2 = Vector2.DOWN
var _airborne: bool = false
var _air_elapsed: float = 0.0
var _sprite_base_y: float = 0.0

@onready var shadow: Sprite2D = $Shadow
@onready var hurtbox: HurtboxComponent = $HurtboxComponent
@onready var health: HealthComponent = $HealthComponent
@onready var brain: Node = get_node_or_null("Brain")


func _ready() -> void:
	add_to_group("party")
	_sprite_base_y = sprite.position.y
	shadow.visible = false
	hurtbox.hit.connect(_on_hurt)
	health.died.connect(_on_died)
	_apply_sheet()


## Fold the member's CharacterSheet into this freshly-spawned body: VIT raises
## max HP, SPD raises move speed. Called from _ready, which is exactly late
## enough — children run _ready() first, so HealthComponent has already done its
## `current_health = max_health`, and the scene's own _ready (where HUD.bind_party
## runs) has not happened yet, so the HUD sizes its rows off the corrected max.
##
## THE ORDERING TRAP: assigning max_health alone does NOT re-emit
## health_changed, and the HUD sizes each heart row inside that handler. Refill
## in the same breath or the body spawns at the OLD max with a half-empty row.
func _apply_sheet() -> void:
	base_max_health = health.max_health
	var game := get_node_or_null(^"/root/Game")
	if game == null or member_id == &"":
		return                                   # bare scene or a --script probe
	var sheet: CharacterSheet = game.call("sheet", member_id)
	# A NEUTRAL sheet means "this body has no RPG layer" (kid Basil, the
	# student). Skip the writes entirely rather than applying zeroes: those
	# scenes carry their own tuned max_health exports, and a zero write would
	# silently retune prologue beats that have shipped since 2026-07-12.
	if sheet == null or sheet.neutral:
		return
	health.max_health = base_max_health + sheet.stat("vit")
	health.refill()
	speed *= 1.0 + minf(float(sheet.stat("spd")) / 40.0, StatBlock.SPD_CLAMP)


func _physics_process(delta: float) -> void:
	match state:
		STATE_MOVE:
			# Intent is only authored where it can be consumed — an edge fired
			# mid-swing/mid-hurt would be dropped (and a brain's attack
			# cooldown wasted with it); brains also shouldn't teleport a body
			# that's mid-knockback or mid-swing.
			_gather_intent()
			_process_move()
		STATE_HURT:
			velocity = _knockback
			_knockback = _knockback.move_toward(Vector2.ZERO, knockback_speed * 4.0 * delta)
			_hurt_timer -= delta
			if _hurt_timer <= 0.0:
				state = STATE_MOVE
		_:
			_process_kit(delta)
	_update_hop(delta)
	move_and_slide()


func is_airborne() -> bool:
	return _airborne


func _gather_intent() -> void:
	intent.clear()
	if is_leader:
		intent.move = Vector2(
			Input.get_axis("move_left", "move_right"),
			Input.get_axis("move_up", "move_down")
		).normalized()
		intent.attack = Input.is_action_just_pressed("attack")
		var secondary := _secondary_action()
		if secondary != "":
			intent.secondary = Input.is_action_just_pressed(secondary)
		intent.jump = Input.is_action_just_pressed("jump")
	elif brain != null:
		brain.think(get_physics_process_delta_time(), intent)


func _process_move() -> void:
	if _airborne:
		# Launch momentum plus a bit of mid-air steering with the held direction.
		# Clamped to the leap speed: steering turns or brakes the arc, but
		# holding the jump direction can't stack past jump_speed into a glide.
		var steer := intent.move.normalized() * air_steer if intent.move != Vector2.ZERO else Vector2.ZERO
		velocity = (_jump_dir * jump_speed + steer).limit_length(jump_speed)
	else:
		if intent.move != Vector2.ZERO:
			velocity = intent.move.limit_length(MOVE_CLAMP) * speed
			_update_facing(intent.move)
			_play_directional("walk")
		else:
			velocity = Vector2.ZERO
			_play_directional("idle")

	# A brain takes aim before it pulls the trigger.
	if intent.face != Vector2.ZERO:
		_update_facing(intent.face)

	if intent.attack:
		_on_attack_intent()
	elif intent.secondary:
		_on_secondary_intent()
	elif intent.jump and not _airborne:
		_start_jump()


func _start_jump() -> void:
	_airborne = true
	_air_elapsed = 0.0
	# Leap in the held direction; with no input held, hop straight up in place.
	_jump_dir = intent.move.normalized() if intent.move != Vector2.ZERO else Vector2.ZERO
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
	# Shadow shrinks with height, selling the hop.
	shadow.scale = Vector2.ONE * (1.0 - 0.45 * arc)


## `_effect` is the status payload the hit carried. Party members have no
## StatusComponent — nothing puts Basil or Fuji to sleep yet — so it is
## accepted and ignored rather than the signal being special-cased.
func _on_hurt(_damage: int, source: Node, _effect: Dictionary) -> void:
	if source is Node2D:
		_knockback = (global_position - (source as Node2D).global_position).normalized() * knockback_speed
	else:
		_knockback = Vector2.ZERO
	_hurt_interrupt()
	state = STATE_HURT
	# Counted down in _physics_process with every other kit timer, not awaited:
	# an awaited timer both resumes on a freed body (scene changes mid-stagger)
	# and lets an earlier hit's coroutine end a later hit's stagger early.
	_hurt_timer = hurt_time
	sprite.play("hurt")


func _on_died() -> void:
	# Party members can't die (for now): the killing blow reads as a normal
	# hit — the hurt stagger plays and the hearts refill. Real KO comes later.
	health.refill()


# ---- kit hooks (subclasses override) ----------------------------------------

## Runs the subclass's kit states (state >= STATE_KIT) each physics frame.
func _process_kit(_delta: float) -> void:
	pass


func _on_attack_intent() -> void:
	pass


func _on_secondary_intent() -> void:
	pass


## Input action polled into intent.secondary for the leader ("" = none).
func _secondary_action() -> String:
	return ""


## Called as a hit lands, before the hurt state — cancel live kit effects here.
func _hurt_interrupt() -> void:
	pass


## Place a freshly-instanced projectile at this body's muzzle, pulled clear of
## any wall it would otherwise be born inside.
##
## There are TWO independent ways a shot lands in rock, and they need different
## answers. The first pass only handled one of them.
##
##  1. ALONG the facing. The muzzle sits `offset` px in front of the ORIGIN and
##     the shot's collider reaches half its own length further — 25px for the
##     bolt — while the body's box hugs its FEET (12x8 at +6, top = origin+2)
##     and so stops ~10px short of a north wall. Fired at the rock, the bolt is
##     born well inside it and dies on its first physics step without moving.
##     ANSWER: ray the wall layer over the muzzle's reach; spawn at the last
##     point that fits.
##
##  2. ACROSS the facing. Pressed north, the box top IS the wall's edge, which
##     puts the body's ORIGIN 2px INSIDE the solid cell — and a bolt fired EAST
##     is centred on that origin, its 6px-tall collider straddling the boundary.
##     It dies having never left the barrel. This is the "I fire sideways and it
##     hits something invisible" case, and no amount of pulling back along the
##     facing touches it, because the overlap is sideways. ANSWER: test the
##     shot's REAL shape at its REAL spawn transform and nudge it perpendicular
##     until it is clear.
##
## Firing INTO a wall you are flush against still produces no shot: there is no
## free pixel to put one in, and the perpendicular search finds nothing because
## the wall spans the whole lane. That one is geometry, not a bug.
##
## The muzzle FLASH stays at the nominal offset throughout — it belongs to the
## gun, not to the bolt.
func place_muzzle(shot: Node2D, offset: float) -> void:
	var col := shot.get_node_or_null(^"CollisionShape2D") as CollisionShape2D
	if col == null or col.shape == null:
		shot.global_position = global_position + facing * offset
		return
	var space := get_world_2d().direct_space_state
	var half_len: float = col.shape.get_rect().size.x * 0.5

	# (1) along the facing
	var along := offset
	var ray := PhysicsRayQueryParameters2D.create(
			global_position, global_position + facing * (offset + half_len))
	ray.collision_mask = WALL_MASK
	var hit := space.intersect_ray(ray)
	if not hit.is_empty():
		along = maxf(global_position.distance_to(hit.position) - half_len - 1.0,
				0.0)
	var base := global_position + facing * along

	# (2) across it — first free lane within MUZZLE_NUDGE px, nearest first
	var perp := Vector2(-facing.y, facing.x)
	var query := PhysicsShapeQueryParameters2D.new()
	query.shape = col.shape
	query.collision_mask = WALL_MASK
	for step in MUZZLE_NUDGE + 1:
		for way in ([0.0] if step == 0 else [1.0, -1.0]):
			var spot: Vector2 = base + perp * (step * way)
			query.transform = Transform2D(facing.angle(), spot) * col.transform
			if space.intersect_shape(query, 1).is_empty():
				shot.global_position = spot
				return
	shot.global_position = base
