class_name AIBrain
extends Node

## The follower's controller — a "Brain" child of each PartyMember scene that
## fills the member's Intent when it isn't the leader (SoM-style). Three moods:
## FOLLOW the leader (hysteresis so it doesn't jitter at the stop line, a
## sprint when left behind), ENGAGE a LATCHED enemy while leashed to the
## leader, and RETURN — the decisive break-off when the leader walks away from
## a fight: run all the way home before even looking at enemies again. Every
## boundary here is a two-threshold band (stop/resume, acquire/hold,
## leash/break) because any single-threshold edge reads as frame twitching —
## Basil's own recoil skid (~30px) crosses a lone 70px line every shot. The
## catch-up teleport only fires OFF-SCREEN — measured against the live camera,
## limits and smoothing included — and lands a step behind the leader after a
## shape sweep proves the step is walkable (else on the leader itself), so it
## never pops inside the view and never embeds in a wall. Kit subclasses
## decide HOW to fight in _combat(); this class decides WHEN. Brains only
## author movement and attack edges — never intent.jump; followers don't hop.

enum Mood { FOLLOW, ENGAGE, RETURN }

@export var follow_distance: float = 34.0  # close enough — stop here
@export var follow_resume: float = 44.0    # ...and don't restart until this far
@export var boost_at: float = 56.0         # beyond this, sprint to catch up
@export var catchup_boost: float = 1.25    # sprint = intent.move above unit length
## Must stay <= the SMALLEST view half-extent + offscreen_margin (216/108 + 24
## on the 384x216 view = 132 vertically), or a wall-stuck follower can sit
## invisible in the gap and never come home.
@export var teleport_at: float = 130.0
@export var offscreen_margin: float = 24.0 # past the view edge by this = truly gone
@export var detect_range: float = 70.0     # ACQUIRE radius — how far fights start
## HOLD radius for the latched target — must clear detect_range + Basil's
## ~30px recoil skid, and sit above his fire_range so kiting works.
@export var drop_range: float = 140.0
@export var leash_range: float = 96.0      # may ENGAGE while this close to the leader
@export var leash_break: float = 128.0     # engaged past this — break off and RETURN
@export var rejoin_at: float = 48.0        # RETURN ends this close; combat may resume
@export var attack_cooldown: float = 0.8

var member: PartyMember
var _mood := Mood.FOLLOW
var _target: Node2D = null
var _cool: float = 0.0
var _moving: bool = false   # follow hysteresis state


func _ready() -> void:
	member = get_parent() as PartyMember


func _physics_process(delta: float) -> void:
	# Unconditional decay: the member skips think() during kit/hurt states,
	# and pausing the cooldown through every swing stretched the follower's
	# attack cadence by the whole animation length.
	_cool = maxf(_cool - delta, 0.0)


## Forget everything mood-transient. Party calls this on leader swaps so a
## member never resumes a stale RETURN/ENGAGE from before a stint in the lead.
func reset() -> void:
	_mood = Mood.FOLLOW
	_target = null
	_moving = false


func think(_delta: float, intent: PartyMember.Intent) -> void:
	var leader: PartyMember = Party.leader
	if not is_instance_valid(leader) or leader == member:
		return
	var to_leader := leader.global_position - member.global_position
	var dist := to_leader.length()
	if dist > teleport_at and _off_screen():
		_teleport_home(leader)
		return
	match _mood:
		Mood.FOLLOW:
			var target := _nearest_enemy(detect_range)
			if target != null and dist <= leash_range:
				_mood = Mood.ENGAGE
				_target = target       # latch — held to drop_range, not detect
				_combat(target, intent)
			else:
				_follow(to_leader, intent)
		Mood.ENGAGE:
			if not _latch_valid():
				_target = _nearest_enemy(drop_range)
			if _target == null:
				_mood = Mood.FOLLOW
				_follow(to_leader, intent)
			elif dist > leash_break:
				_mood = Mood.RETURN
				_target = null
				_follow(to_leader, intent)
			else:
				_combat(_target, intent)
		Mood.RETURN:
			if dist <= rejoin_at:
				_mood = Mood.FOLLOW
			_follow(to_leader, intent)


## The latched target survives until it dies (slimes leave "enemies" as the
## splat starts) or breaks clear of drop_range — recoil skids and slime hops
## across the acquire line don't shake it.
func _latch_valid() -> bool:
	return is_instance_valid(_target) and _target.is_in_group("enemies") \
			and member.global_position.distance_to(_target.global_position) <= drop_range


func _follow(to_leader: Vector2, intent: PartyMember.Intent) -> void:
	var dist := to_leader.length()
	if _moving:
		if dist <= follow_distance:
			_moving = false
			return
	elif dist < follow_resume:
		return
	_moving = true
	var boost := catchup_boost if dist > boost_at else 1.0
	intent.move = to_leader.normalized() * boost


## Abandoned out of sight — reappear a step behind the leader. The member's
## own shape is swept from the leader's spot (walkable by construction —
## party bodies don't collide with each other) toward the landing; a wall
## behind the leader means landing ON the leader instead of inside/through it.
func _teleport_home(leader: PartyMember) -> void:
	var back := -leader.facing * follow_distance
	var landing := leader.global_position + back
	if member.test_move(Transform2D(0.0, leader.global_position), back):
		landing = leader.global_position
	member.global_position = landing
	member.velocity = Vector2.ZERO
	reset()


## True when the member sits outside the live camera's view (plus margin).
## Measured from the camera's actual screen center — limits and smoothing
## included — so a clamped corner camera still counts correctly.
func _off_screen() -> bool:
	var cam := member.get_viewport().get_camera_2d()
	if cam == null:
		return true
	var half := MapData.view_size() * 0.5 + Vector2.ONE * offscreen_margin
	var d := (member.global_position - cam.get_screen_center_position()).abs()
	return d.x > half.x or d.y > half.y


func _nearest_enemy(radius: float) -> Node2D:
	var best: Node2D = null
	var best_d := radius
	for e in get_tree().get_nodes_in_group("enemies"):
		var d := member.global_position.distance_to((e as Node2D).global_position)
		if d <= best_d:
			best_d = d
			best = e
	return best


# ---- kit hook ----------------------------------------------------------------

## Fight `target` by authoring intent — override per kit.
func _combat(_target_node: Node2D, _intent: PartyMember.Intent) -> void:
	pass
