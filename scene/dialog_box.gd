class_name DialogBox
extends CanvasLayer

## The SNES dialog box, built fresh 2026-07-12 (the deleted kit is NOT
## recovered): a bottom panel with a brass bevel, a name plate riding the top
## edge, a typewriter reveal and a blinking ▼ advance arrow. Mixed-case text —
## the lowercase glyph set shipped with this box (assets/_pixfont.py).
## All input is POLLED (the shot.gd synthesized-press gotcha): attack /
## interact / ui_accept advance; a press mid-type reveals the full line.
## say() resolves when the player advances past the line; the box stays open
## between lines of one conversation — close() drops it.

signal advanced

const CHAR_TIME := 0.025
## Swallow the press that opened the conversation (the NPC's interact poll and
## this box poll the same frame — without the grace window the first line
## skips instantly).
const SWALLOW_MS := 140

var _typing := false
var _awaiting := false
var _reveal := 0.0
var _accept_after := 0

@onready var text: Label = $Text
@onready var name_label: Label = $NameLabel
@onready var name_plate: ColorRect = $NamePlate
@onready var arrow: Label = $Arrow


func _ready() -> void:
	visible = false
	# the arrow blinks forever; visibility gates whether it shows
	var tw := create_tween().set_loops()
	tw.tween_property(arrow, "modulate:a", 0.2, 0.35)
	tw.tween_property(arrow, "modulate:a", 1.0, 0.35)


## One line; resolves when the player advances past it.
func say(speaker: String, line: String) -> void:
	visible = true
	_set_speaker(speaker)
	text.text = line
	text.visible_characters = 0
	_reveal = 0.0
	_typing = true
	_awaiting = true
	arrow.visible = false
	_accept_after = Time.get_ticks_msec() + SWALLOW_MS
	await advanced


## A whole one-speaker conversation, then the box drops.
func converse(speaker: String, conversation: PackedStringArray) -> void:
	for line in conversation:
		await say(speaker, line)
	close()


func close() -> void:
	visible = false
	_typing = false
	_awaiting = false


func _process(delta: float) -> void:
	if not visible:
		return
	if _typing:
		_reveal += delta
		text.visible_characters = int(_reveal / CHAR_TIME)
		if text.visible_characters >= text.text.length():
			_finish_typing()
	if not _awaiting or Time.get_ticks_msec() < _accept_after:
		return
	if Input.is_action_just_pressed("attack") \
			or Input.is_action_just_pressed("interact") \
			or Input.is_action_just_pressed("ui_accept"):
		if _typing:
			_finish_typing()
		else:
			_awaiting = false
			advanced.emit()


func _finish_typing() -> void:
	_typing = false
	text.visible_characters = -1
	arrow.visible = true


func _set_speaker(speaker: String) -> void:
	var show := speaker != ""
	name_plate.visible = show
	name_label.visible = show
	if show:
		name_label.text = speaker
		# plate hugs the name: monospace advance 6 + 5px padding each side
		name_plate.offset_right = name_plate.offset_left + speaker.length() * 6 + 10
