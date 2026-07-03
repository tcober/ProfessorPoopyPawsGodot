class_name Cutscene
extends Node2D

## Base for scripted story scenes. Provides awaitable helpers (walk, say, fade, title
## cards) over plain AnimatedSprite2D actors, plus ESC to skip the whole intro.
## Scenes extend this, set `next_scene`/`skip_scene`, and await steps in `_play()`.

## Where this scene hands off when it finishes.
@export_file("*.tscn") var next_scene: String = "res://scene/overworld.tscn"
## Where ESC bails to (default: straight onto the travel map).
@export_file("*.tscn") var skip_scene: String = "res://scene/overworld.tscn"

@onready var dialog: DialogBox = $DialogBox
@onready var _fade_rect: ColorRect = $FadeLayer/Fade
@onready var _card_label: Label = $FadeLayer/Card

var _finished: bool = false


func _ready() -> void:
	_fade_rect.color = Color.BLACK
	_fade_rect.modulate.a = 1.0
	_card_label.visible = false
	_play.call_deferred()


## Override in the scene. End with `finish()`.
func _play() -> void:
	finish()


func finish() -> void:
	if _finished:
		return
	_finished = true
	get_tree().change_scene_to_file(next_scene)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_finished = true
		get_tree().change_scene_to_file(skip_scene)


# ---- awaitable helpers -------------------------------------------------------

func say(text: String) -> void:
	await dialog.say(text)


func wait(sec: float) -> void:
	await get_tree().create_timer(sec).timeout


func fade_in(dur: float = 0.7) -> void:
	var tw := create_tween()
	tw.tween_property(_fade_rect, "modulate:a", 0.0, dur)
	await tw.finished


func fade_out(dur: float = 0.7) -> void:
	var tw := create_tween()
	tw.tween_property(_fade_rect, "modulate:a", 1.0, dur)
	await tw.finished


## Black screen with centered text, then back to whatever fade state you set next.
func card(text: String, hold: float = 1.6) -> void:
	if _fade_rect.modulate.a < 1.0:
		await fade_out(0.5)
	_card_label.text = text
	_card_label.visible = true
	_card_label.modulate.a = 0.0
	var tw := create_tween()
	tw.tween_property(_card_label, "modulate:a", 1.0, 0.35)
	await tw.finished
	await wait(hold)
	var tw2 := create_tween()
	tw2.tween_property(_card_label, "modulate:a", 0.0, 0.35)
	await tw2.finished
	_card_label.visible = false


## Walk an AnimatedSprite2D actor to `to`, playing walk_* by direction, idling after.
func walk(actor: AnimatedSprite2D, to: Vector2, speed: float = 55.0) -> void:
	var delta := to - actor.position
	var suffix := "side"
	if absf(delta.x) <= absf(delta.y):
		suffix = "down" if delta.y > 0.0 else "up"
	actor.play("walk_" + suffix)
	actor.flip_h = suffix == "side" and delta.x < 0.0
	var tw := create_tween()
	tw.tween_property(actor, "position", to, delta.length() / speed)
	await tw.finished
	actor.play("idle_" + suffix)


## Quick vertical hop (surprise, laughter bounce...).
func hop(actor: Node2D, height: float = 5.0, dur: float = 0.22) -> void:
	var tw := create_tween()
	tw.tween_property(actor, "position:y", actor.position.y - height, dur * 0.5)
	tw.tween_property(actor, "position:y", actor.position.y, dur * 0.5)
	await tw.finished
