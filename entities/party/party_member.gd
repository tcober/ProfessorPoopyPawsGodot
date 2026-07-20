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

var member_id: StringName
var is_leader: bool = true   # a lone member in a one-off scene plays from keyboard
var state: int = STATE_MOVE
var intent := Intent.new()

var _knockback: Vector2 = Vector2.ZERO
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


func _on_hurt(_damage: int, source: Node) -> void:
	if source is Node2D:
		_knockback = (global_position - (source as Node2D).global_position).normalized() * knockback_speed
	else:
		_knockback = Vector2.ZERO
	_hurt_interrupt()
	state = STATE_HURT
	sprite.play("hurt")
	await get_tree().create_timer(hurt_time).timeout
	if state == STATE_HURT:
		state = STATE_MOVE


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
