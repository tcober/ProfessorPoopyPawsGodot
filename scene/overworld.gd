extends Node2D

## Chrono Trigger-style travel layer over a painted continent: Ground/Overlay are
## single generated paintings (assets/_gen_scene_overworld.py); collision is an
## invisible TileMapLayer built from the same map file (sea/forest/mountain/river
## solid), and the location markers take their positions from the map's anchors —
## one source of truth for geography. Basil's chibi self walks between
## OverworldLocation markers: unlocked ones fade out into their zone scene,
## locked ones announce themselves in the bottom banner.

const MAP_PATH := "res://assets/maps/overworld.txt"

var map: Dictionary

@onready var player: OverworldPlayer = $OverworldPlayer
@onready var locations: Node2D = $Locations
@onready var banner: Label = $UI/Banner
@onready var fade: ColorRect = $UI/Fade

var _entry_locked: bool = true
var _busy: bool = false
## Location ids the player is currently standing on; cleared on body_exited so a
## marker can't re-announce until he steps off and back onto it.
var _standing: Dictionary = {}


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	PaintedMap.build_collision(map, $Collision)
	_clamp_camera()
	player.global_position = MapData.anchor_px(map, "player_start")
	for loc: OverworldLocation in locations.get_children():
		loc.position = MapData.anchor_px(map, loc.id)
		loc.body_entered.connect(_on_location_entered.bind(loc))
		loc.body_exited.connect(_on_location_exited.bind(loc))
		if loc.id == Game.overworld_spawn:
			player.global_position = loc.global_position + Vector2(0, 52)
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 0.0, 0.7)
	await get_tree().create_timer(0.8).timeout
	_entry_locked = false


func _clamp_camera() -> void:
	var cam: Camera2D = player.get_node("Camera2D")
	var size := MapData.size_px(map)
	cam.limit_left = 0
	cam.limit_top = 0
	cam.limit_right = int(size.x)
	cam.limit_bottom = int(size.y)


func _on_location_entered(body: Node2D, loc: OverworldLocation) -> void:
	if not body is OverworldPlayer or _entry_locked or _busy:
		return
	if _standing.get(loc.id, false):
		return
	_standing[loc.id] = true
	if loc.target_scene != "":
		_travel(loc)
	else:
		_announce(loc)


func _on_location_exited(body: Node2D, loc: OverworldLocation) -> void:
	if body is OverworldPlayer:
		_standing[loc.id] = false


func _travel(loc: OverworldLocation) -> void:
	_busy = true
	Game.overworld_spawn = loc.id
	_show_banner(loc.display_name, 1.6)
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 1.0, 0.5)
	await tw.finished
	get_tree().change_scene_to_file(loc.target_scene)


func _announce(loc: OverworldLocation) -> void:
	_busy = true
	await _show_banner(loc.display_name, 1.6)
	if loc.locked_text != "":
		await _show_banner(loc.locked_text, 1.6)
	_busy = false


func _show_banner(text: String, hold: float) -> void:
	banner.text = text
	var tw := create_tween()
	tw.tween_property(banner, "modulate:a", 1.0, 0.25)
	tw.tween_interval(hold)
	tw.tween_property(banner, "modulate:a", 0.0, 0.35)
	await tw.finished
