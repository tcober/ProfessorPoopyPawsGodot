class_name NPC
extends StaticBody2D

## Interact-to-talk villager (the first NPC entity, 2026-07-12). Stand in the
## TalkZone and press interact (E / Circle) to run the NPC's conversation
## through the scene's Theater. Interact is POLLED like every action in the
## project (the shot.gd gotcha).
##
## Sheets are one 48x48-cell ROW — [idle0, idle1, act0, act1, emote0, emote1]
## (frame_cols may stop at 2 or 4) — and the SpriteFrames build at runtime, so
## a new villager is a PNG plus exports: no .tres authoring. Anim names:
## idle_down (the Theater helpers' single-facing fallback), act (the NPC's
## business pose: casting, pointing, tinkering), emote (its big feeling).
## Cols 6-9 are OPTIONAL facings (2026-07-17, the bluff's from-behind
## staging): back x2 (frame_cols >= 8) and side x2 drawn facing LEFT
## (frame_cols >= 10; play_side(false) flips it right) — sheets without
## them are untouched, the play_* helpers no-op.
## The body is solid on the world layer and y-sorts in World at the party's
## feet convention (48-cell art, feet y=44 = node.y + 20).

signal talked(npc: NPC)

@export var display_name := ""
@export var sheet: Texture2D
@export var frame_cols := 6
@export var idle_fps := 1.6
@export_multiline var lines: PackedStringArray = []

var _player_in := false
var _busy := false

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D


func _ready() -> void:
	_build_frames()
	sprite.play("idle_down")
	$TalkZone.body_entered.connect(_on_zone.bind(true))
	$TalkZone.body_exited.connect(_on_zone.bind(false))


func _build_frames() -> void:
	assert(sheet != null, display_name + " NPC has no sheet")
	var f := SpriteFrames.new()
	var defs := {"idle_down": [0, 1], "act": [2, 3], "emote": [4, 5],
			"back": [6, 7], "side": [8, 9]}
	for anim: String in defs:
		var cols: Array = defs[anim]
		if cols[0] >= frame_cols:
			continue
		if anim != "default":
			f.add_animation(anim)
		f.set_animation_speed(anim, idle_fps)
		f.set_animation_loop(anim, true)
		for i: int in cols:
			if i < frame_cols:
				var at := AtlasTexture.new()
				at.atlas = sheet
				at.region = Rect2(i * 48, 0, 48, 48)
				f.add_frame(anim, at)
	f.remove_animation("default")
	sprite.sprite_frames = f


func _on_zone(body: Node2D, entering: bool) -> void:
	# leader only — a follower drifting through must not arm the prompt
	if body.is_in_group("player"):
		_player_in = entering


func _process(_delta: float) -> void:
	if _player_in and not _busy and lines.size() > 0 \
			and Input.is_action_just_pressed("interact") and not _cutscene():
		_talk()


## A locked party means a staged beat (or a minigame mashing E) is running —
## no NPC may open a nested conversation through it.
func _cutscene() -> bool:
	var players := get_tree().get_nodes_in_group("player")
	return players.is_empty() or not players[0].is_physics_processing()


func _talk() -> void:
	var theater: Theater = get_tree().get_first_node_in_group("theater")
	if theater == null:
		return
	_busy = true
	theater.lock_party()
	await theater.converse(display_name, lines)
	theater.unlock_party()
	talked.emit(self)
	_busy = false


# ---- cutscene poses ---------------------------------------------------------

func play_act() -> void:
	if sprite.sprite_frames.has_animation("act"):
		sprite.play("act")


func play_emote() -> void:
	if sprite.sprite_frames.has_animation("emote"):
		sprite.play("emote")


func play_idle() -> void:
	sprite.flip_h = false
	sprite.play("idle_down")


## Back to the camera (the bluff's facing-the-water staging).
func play_back() -> void:
	if sprite.sprite_frames.has_animation("back"):
		sprite.flip_h = false
		sprite.play("back")


## Profile. The cells face LEFT; right = false keeps that, true flips.
func play_side(right := false) -> void:
	if sprite.sprite_frames.has_animation("side"):
		sprite.flip_h = right
		sprite.play("side")
