class_name HUD
extends CanvasLayer

## Heart row driven by a HealthComponent's `health_changed` signal, a laser-ammo
## pip row driven by the Player's `ammo_changed` signal, and a spare-magazine row
## (one beaker icon per spare mag) driven by `beakers_changed`.
## HP is in half-hearts (2 per heart). hearts.png frames: full | half | empty.
## ammo_pips.png frames: full | empty.

const CELL := 16
const FRAME_FULL := 0
const FRAME_HALF := 1
const FRAME_EMPTY := 2

const AMMO_CELL := 8
const AMMO_FULL := 0
const AMMO_EMPTY := 1

@export var heart_texture: Texture2D
@export var ammo_texture: Texture2D
@export var beaker_texture: Texture2D

@onready var container: HBoxContainer = $MarginContainer/Rows/Hearts
@onready var ammo_container: HBoxContainer = $MarginContainer/Rows/Ammo
@onready var mags_container: HBoxContainer = $MarginContainer/Rows/Mags


func bind_health(health: HealthComponent) -> void:
	health.health_changed.connect(_on_health_changed)
	_on_health_changed(health.current_health, health.max_health)


func bind_ammo(player: Player) -> void:
	player.ammo_changed.connect(_on_ammo_changed)
	player.beakers_changed.connect(_on_beakers_changed)
	_on_ammo_changed(player.ammo, player.max_ammo)
	_on_beakers_changed(player.beakers, player.max_beakers)


func _on_health_changed(current: int, max_health: int) -> void:
	var heart_count := int(ceil(max_health / 2.0))
	_ensure_count(container, heart_count, heart_texture, CELL)
	var hearts := container.get_children()
	for i in heart_count:
		var hp_in_heart := current - i * 2
		var frame := FRAME_EMPTY
		if hp_in_heart >= 2:
			frame = FRAME_FULL
		elif hp_in_heart == 1:
			frame = FRAME_HALF
		_set_frame(hearts[i] as TextureRect, frame, CELL)


func _on_ammo_changed(current: int, max_ammo: int) -> void:
	_ensure_count(ammo_container, max_ammo, ammo_texture, AMMO_CELL)
	var pips := ammo_container.get_children()
	for i in max_ammo:
		var frame := AMMO_FULL if i < current else AMMO_EMPTY
		_set_frame(pips[i] as TextureRect, frame, AMMO_CELL)


func _on_beakers_changed(current: int, _max_beakers: int) -> void:
	# Spares only — the loaded mag is the pip row. Plain icons, one per beaker.
	while mags_container.get_child_count() < current:
		var rect := TextureRect.new()
		rect.texture = beaker_texture
		rect.stretch_mode = TextureRect.STRETCH_KEEP
		mags_container.add_child(rect)
	while mags_container.get_child_count() > current:
		mags_container.get_child(mags_container.get_child_count() - 1).free()


func _ensure_count(box: HBoxContainer, count: int, tex: Texture2D, cell: int) -> void:
	while box.get_child_count() < count:
		var rect := TextureRect.new()
		var atlas := AtlasTexture.new()
		atlas.atlas = tex
		atlas.region = Rect2(0, 0, cell, cell)
		rect.texture = atlas
		rect.stretch_mode = TextureRect.STRETCH_KEEP
		box.add_child(rect)
	while box.get_child_count() > count:
		box.get_child(box.get_child_count() - 1).free()


func _set_frame(rect: TextureRect, frame: int, cell: int) -> void:
	var atlas := rect.texture as AtlasTexture
	atlas.region = Rect2(frame * cell, 0, cell, cell)
