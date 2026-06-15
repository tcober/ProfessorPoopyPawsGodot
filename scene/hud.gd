class_name HUD
extends CanvasLayer

## Heart row driven entirely by a HealthComponent's `health_changed` signal.
## HP is in half-hearts (2 per heart). Frames in hearts.png: full | half | empty.

const CELL := 16
const FRAME_FULL := 0
const FRAME_HALF := 1
const FRAME_EMPTY := 2

@export var heart_texture: Texture2D

@onready var container: HBoxContainer = $MarginContainer/Hearts


func bind_health(health: HealthComponent) -> void:
	health.health_changed.connect(_on_health_changed)
	_on_health_changed(health.current_health, health.max_health)


func _on_health_changed(current: int, max_health: int) -> void:
	var heart_count := int(ceil(max_health / 2.0))
	_ensure_heart_count(heart_count)
	var hearts := container.get_children()
	for i in heart_count:
		var hp_in_heart := current - i * 2
		var frame := FRAME_EMPTY
		if hp_in_heart >= 2:
			frame = FRAME_FULL
		elif hp_in_heart == 1:
			frame = FRAME_HALF
		_set_heart_frame(hearts[i] as TextureRect, frame)


func _ensure_heart_count(count: int) -> void:
	while container.get_child_count() < count:
		var rect := TextureRect.new()
		var atlas := AtlasTexture.new()
		atlas.atlas = heart_texture
		atlas.region = Rect2(0, 0, CELL, CELL)
		rect.texture = atlas
		rect.stretch_mode = TextureRect.STRETCH_KEEP
		container.add_child(rect)
	while container.get_child_count() > count:
		container.get_child(container.get_child_count() - 1).free()


func _set_heart_frame(rect: TextureRect, frame: int) -> void:
	var atlas := rect.texture as AtlasTexture
	atlas.region = Rect2(frame * CELL, 0, CELL, CELL)
