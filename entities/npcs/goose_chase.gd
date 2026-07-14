class_name GooseChase
extends CharacterBody2D

## The ribbon thief (Prologue A pacing pass, 2026-07-12): the chaos goose,
## upgraded from a static NPC to a chase minigame. It waddles away whenever
## the leader closes in, honks and puts on a burst of speed each time it's
## caught, and after CATCHES_NEEDED catches it surrenders Sage's ribbon
## (`caught_all` — the scene runs the hand-back beat). A leash steers it home
## so it can't waddle out of the square; map collision handles the rest.
## Sheet: npc_goose_gen.png, one row x6 [idle x2, honk x2, WADDLE x2].

signal caught_all(goose: GooseChase)

const CATCHES_NEEDED := 3
const FLEE_RADIUS := 44.0
const FLEE_SPEED := 68.0
const BURST_SPEED := 130.0
const BURST_TIME := 0.7
const LEASH := 96.0            # max wander from home before steering back

@export var sheet: Texture2D

var catches := 0
var done := false
var _home := Vector2.ZERO
var _burst := 0.0
var _cooldown := 0.0           # ignore the catch zone briefly after a catch

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D


func _ready() -> void:
	_home = global_position
	_build_frames()
	sprite.play("idle")
	$CatchZone.body_entered.connect(_on_catch)


func _build_frames() -> void:
	var f := SpriteFrames.new()
	var defs := {"idle": [0, 1], "honk": [2, 3], "waddle": [4, 5]}
	for anim: String in defs:
		f.add_animation(anim)
		f.set_animation_speed(anim, 6.0 if anim == "waddle" else 2.0)
		f.set_animation_loop(anim, true)
		for i: int in defs[anim]:
			var at := AtlasTexture.new()
			at.atlas = sheet
			at.region = Rect2(i * 48, 0, 48, 48)
			f.add_frame(anim, at)
	f.remove_animation("default")
	sprite.sprite_frames = f


func _physics_process(delta: float) -> void:
	if done:
		velocity = Vector2.ZERO
		return
	_burst = maxf(0.0, _burst - delta)
	_cooldown = maxf(0.0, _cooldown - delta)
	var players := get_tree().get_nodes_in_group("player")
	var threat: Node2D = players[0] if players.size() > 0 else null
	var flee := Vector2.ZERO
	if threat != null:
		var d := global_position - threat.global_position
		if d.length() < FLEE_RADIUS or _burst > 0.0:
			# away from the cat, with a sideways wobble so it arcs
			flee = (d.normalized() + d.normalized().orthogonal() * 0.35).normalized()
	# the leash blends it back toward home so the chase stays in the square
	var homeward := _home - global_position
	if homeward.length() > LEASH:
		flee = (flee + homeward.normalized() * 1.4).normalized()
	if flee != Vector2.ZERO:
		velocity = flee * (BURST_SPEED if _burst > 0.0 else FLEE_SPEED)
		sprite.play("waddle")
		sprite.flip_h = velocity.x < 0.0
	else:
		velocity = Vector2.ZERO
		if sprite.animation == "waddle":
			sprite.play("idle")
	move_and_slide()


func _on_catch(body: Node2D) -> void:
	if done or _cooldown > 0.0 or not body.is_in_group("player"):
		return
	catches += 1
	_cooldown = 1.0
	_burst = BURST_TIME
	sprite.play("honk")
	var base := sprite.position.y
	var tw := create_tween()
	tw.tween_property(sprite, "position:y", base - 5.0, 0.12)
	tw.tween_property(sprite, "position:y", base, 0.12)
	if catches >= CATCHES_NEEDED:
		done = true
		caught_all.emit(self)


## After the hand-back beat the goose retires to dignified idling.
func settle() -> void:
	sprite.play("idle")
