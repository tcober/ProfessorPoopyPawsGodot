class_name DialogBox
extends CanvasLayer

## SNES-RPG dialog box: bordered panel, typewriter text, advance on attack/accept.
## Usage: `await dialog.say("BULLY: NICE PAWS, PROFESSOR.")` — resolves when the
## player dismisses the line. Pressing the button mid-type reveals the full line first.

signal advanced

const CHAR_TIME := 0.025

@onready var label: Label = $Panel/Text
@onready var arrow: Label = $Panel/Arrow

var _active: bool = false
var _tween: Tween


func _ready() -> void:
	visible = false


func say(text: String) -> void:
	visible = true
	_active = true
	arrow.visible = false
	label.text = text
	label.visible_characters = 0
	_tween = create_tween()
	_tween.tween_property(label, "visible_characters", text.length(), text.length() * CHAR_TIME)
	await _tween.finished
	arrow.visible = true
	await advanced
	visible = false
	_active = false


func _unhandled_input(event: InputEvent) -> void:
	if not _active:
		return
	if event.is_action_pressed("attack") or event.is_action_pressed("ui_accept"):
		get_viewport().set_input_as_handled()
		if _tween and _tween.is_running():
			_tween.custom_step(999.0)   # reveal the rest instantly
		else:
			advanced.emit()
