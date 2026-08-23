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

## The Star Fox voice: one syllable-blip as every BLIP_EVERY-th character
## lands. Punctuation and spaces stay silent, so the rhythm follows the words
## and a "..." line says nothing at all.
const BLIP_EVERY := 3
const BLIP_SILENT := " .,!?-'\";:()"

var _typing := false
var _awaiting := false
var _reveal := 0.0
var _accept_after := 0
var _speaker := ""
var _blip_gate := 0

## Looked up by PATH, never the autoload identifier — this box is part of the
## narrative kit, and --script probes must be able to compile it cold.
@onready var _sfx: Node = get_node_or_null(^"/root/Sfx")

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
	_blip_gate = 0
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
	# A say() still parked on `advanced` would hang its whole cutscene — the
	# beat's remaining awaits would never run and the party would stay locked.
	# Dropping the box resolves the line instead.
	if _awaiting:
		_awaiting = false
		advanced.emit()


func _process(delta: float) -> void:
	if not visible:
		return
	if _typing:
		_reveal += delta
		text.visible_characters = int(_reveal / CHAR_TIME)
		_blip()
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
			if _sfx:
				_sfx.talk_advance()
			advanced.emit()


## One voice syllable per few landed characters, in the speaker's own pitch
## (Sfx.VOICES). A press that reveals the whole line goes through
## _finish_typing, so a skipped line never machine-guns its backlog of blips.
func _blip() -> void:
	if _sfx == null:
		return
	var vis := mini(text.visible_characters, text.text.length())
	if vis <= _blip_gate or vis <= 0:
		return
	if BLIP_SILENT.contains(text.text[vis - 1]):
		return
	_blip_gate = vis + BLIP_EVERY - 1
	_sfx.talk_blip(_speaker)


func _finish_typing() -> void:
	_typing = false
	text.visible_characters = -1
	arrow.visible = true


func _set_speaker(speaker: String) -> void:
	_speaker = speaker
	var named := speaker != ""
	name_plate.visible = named
	name_label.visible = named
	if named:
		name_label.text = speaker
		# plate hugs the name: monospace advance 6 + 5px padding each side
		name_plate.offset_right = name_plate.offset_left + speaker.length() * 6 + 10
