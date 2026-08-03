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
			_process_move(delta)
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


func _process_move(delta: float) -> void:
	if _airborne:
		# Launch momentum plus a bit of mid-air steering with the held direction.
		# Clamped to the leap speed: steering turns or brakes the arc, but
		# holding the jump direction can't stack past jump_speed into a glide.
		var steer := intent.move.normalized() * air_steer if intent.move != Vector2.ZERO else Vector2.ZERO
		velocity = (_jump_dir * jump_speed + steer).limit_length(jump_speed)
	elif _on_ladder():
		_climb(delta)
	elif intent.move != Vector2.ZERO:
		velocity = intent.move.limit_length(MOVE_CLAMP) * speed
		_funnel(delta)
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
	# You do not hop off a rope ladder thirty feet up. The lane below owns the
	# body's x while it climbs and the hop does not, so a leap from the rungs
	# would drift sideways for 0.4s and then snap back on landing.
	elif intent.jump and not _airborne and not _on_ladder():
		_start_jump()


## A ROPE LADDER IS ONE LANE WIDE AND YOU ARE ON IT OR OFF IT (2026-08-02).
##
## The rungs are two cells across — 32px, against a 12px collision box — so
## "walk normally, play the climb clip" left twenty pixels of side-to-side slop on
## every ladder in the game. A body could stroll up at an angle, hug one stile the
## whole way, or shuffle sideways while the climb animation insisted it was holding
## on with both paws: a wide plank with a picture of a ladder on it.
##
## So the ladder DRIVES the body while the body is on it — vertical only, pinned to
## the run's own centre line. There is no state to enter or leave and no marker,
## zone or scene wiring anywhere: put your feet on a `ropeladder` cell and the lane
## owns you, take them off and it doesn't. That is the same contract _on_ladder()
## already had for the climb ART, now extended to the movement it was drawn for.
func _climb(delta: float) -> void:
	# The SIGN of the held direction, never its normalized component: on a one-lane
	# climb a diagonal press is simply "up", and taking .y off a normalized vector
	# would climb at 71% speed for a reason the player cannot see.
	var dir := signf(intent.move.y)
	# The lane is PULLED, not snapped — stepping on from the ground below slides
	# the body into the middle of the rungs over a frame or two instead of popping
	# it there. Dividing by delta makes that pull exact: it arrives on the centre
	# line and stops dead, with none of the residual creep a proportional gain
	# leaves behind.
	var lane := MapData.terrain_run_center_x(_scene_map(), global_position + FOOT_OFFSET)
	velocity = Vector2(clampf((lane - global_position.x) / maxf(delta, 0.0001),
			-speed, speed), dir * speed)
	# The clip is gated on the SpriteFrames actually carrying it: `play()` on a
	# missing animation is an error every physics frame plus a frozen pose, so a
	# sheet without the row falls back to the walk it had before — wrong-looking but
	# playable, the right failure for a body that wanders onto a ladder in a scene
	# nobody staged. Every playable body carries the row (kid Basil's sheet grew it
	# on 2026-07-30; the student rides player_frames.tres and always had it), so the
	# gate is insurance for the next sheet, not a live fallback.
	if not sprite.sprite_frames.has_animation("climb_up"):
		_update_facing(Vector2.UP)
		_play_directional("walk" if dir != 0.0 else "idle")
		return
	# The climb is BACK-VIEW ONLY and has no side or down variant, because you
	# always face the ladder. It is played by name rather than through
	# _play_directional, and the facing is forced so nothing can flip it to a
	# walk_side — which used to happen, and read as a cat sliding up the rungs.
	facing = Vector2.UP
	sprite.flip_h = false
	sprite.play("climb_up")
	# Standing still on the rungs holds the climb's first frame rather than
	# dropping to an idle, which would read as letting go.
	if dir == 0.0:
		sprite.pause()


## THE MOUTH IS NARROWER THAN THE LADDER, so the lane reaches one cell out.
##
## A rope ladder runs down INSIDE the trunk's four columns — it has to, or you could
## step sideways off rung eight onto ground thirty feet below — which leaves the two
## rung cells with solid timber either side. A 12px-wide body therefore only fits
## through the middle 20px of that 32px pair, and walking at the foot of a great tree
## six pixels off centre does not start a climb: it stops you dead against bark, with
## the rungs plainly visible beside you and nothing to tell you why.
##
## So a body stepping TOWARD a rung cell from the one directly above or below it is
## slid into the mouth on the way. Both halves of that sentence are load-bearing, and
## together they are why this cannot leak onto open ground — where every map is one
## long horizontal run of the same terrain and a stray pull would drag every body to
## the middle of it:
##
##  - it needs a vertical press, so walking east-west past a ladder foot never fires;
##  - the cell it tests is the one the body's OWN feet are about to enter, so the body
##    is already standing over a rung column by the time it can fire at all.
func _funnel(delta: float) -> void:
	var dir := signf(intent.move.y)
	if dir == 0.0:
		return
	var m := _scene_map()
	if m.is_empty():
		return
	var ahead := global_position + FOOT_OFFSET + Vector2(0.0, dir * 16.0)
	if MapData.terrain_at_px(m, ahead) != "ropeladder":
		return
	velocity.x = clampf(
			(MapData.terrain_run_center_x(m, ahead) - global_position.x)
			/ maxf(delta, 0.0001), -speed, speed)


## The scene's map, cached on first use — _on_ladder runs twice a physics frame per
## member — and re-resolved whenever the scene changes, because Party.spawn()
## rebuilds every body at every scene change but the member itself outlives the
## lookup.
var _ladder_scene: Node = null
var _ladder_map: Dictionary = {}


## ASKED OF THE FEET, NOT THE ORIGIN, and that asymmetry is the whole bug this
## comment exists for. A body's origin sits ~10px ABOVE its collision box's bottom
## edge, so climbing UP the origin crosses onto a ladder cell a good half-cell before
## the feet do, and climbing DOWN it hangs on the cell above for that same half-cell.
## The result reads exactly the way it was reported: "sorta works when you start from
## the bottom, but from the top it just looks like the character is walking."
##
## The box's own bottom is `origin + 10` (12x8 centred at +6), so +8 is a pixel or two
## inside the cell the feet are actually standing on, whichever way the body entered
## it. Anything that asks the map where a body IS wants this offset, not the origin.
const FOOT_OFFSET := Vector2(0.0, 8.0)


## Is this body standing on a rope-ladder cell?
##
## Asked of the MAP, not of a collision layer or a marker Area2D, for the same
## reason every other geometry question in this codebase is: the map txt is the one
## source both paint and physics come from, so a ladder that moves in the grid moves
## here too with no scene edit.
##
## Scenes with no `map` (the cutscene stages, the meadow's own loader) simply answer
## false, which is why _scene_map duck-types the property instead of requiring
## TravelScene.
func _on_ladder() -> bool:
	var m := _scene_map()
	if m.is_empty():
		return false
	return MapData.terrain_at_px(m, global_position + FOOT_OFFSET) == "ropeladder"


## The current scene's parsed map, or {} for a scene that has none.
func _scene_map() -> Dictionary:
	var scn := get_tree().current_scene
	if scn == null:
		return {}
	if scn != _ladder_scene:
		_ladder_scene = scn
		var m: Variant = scn.get("map")
		_ladder_map = m if m is Dictionary else {}
	return _ladder_map


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
