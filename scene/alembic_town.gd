extends Node2D

## Alembic Town, walkable at zone scale — the CT-Truce village the overworld's
## town icon opens into. Visible tiles are stamped at runtime from the
## generated layout (assets/_gen_tileset_town.py) onto two layers — Tiles
## under the player, TilesUpper over him (he passes behind rooflines and the
## hedge border) — with collision from the same assets/maps/town.txt grid.
## Marker positions come from the map's anchors: Basil's open door travels
## down to the lab (downstairs), the neighbor cottages and the barred Academy
## announce in the banner, the south lane exits to the overworld. The spawn
## anchor is routed through Game.town_spawn (read-and-clear; "" = the south
## entrance, where the overworld drops you).

const MAP_PATH := "res://assets/maps/town.txt"
const LAYOUT_PATH := "res://assets/tilesets/town_layout.txt"

## Return-spawn drop below the home door: a tile and a half for the 48px
## player, so leaving the cottage lands him clear of the door marker.
const ARRIVE_DROP := 24.0

var map: Dictionary

@onready var player: Player = $World/Player
@onready var locations: Node2D = $Locations
@onready var banner: Label = $UI/Banner
@onready var fade: ColorRect = $UI/Fade

var _entry_locked: bool = true
var _busy: bool = false
## Location ids the player is currently standing on; cleared on body_exited so
## a marker can't re-announce until he steps off and back onto it.
var _standing: Dictionary = {}


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	_clamp_camera()
	var spawn := Game.town_spawn
	Game.town_spawn = ""
	if spawn == "home":
		player.position = MapData.anchor_px(map, "home") + Vector2(0.0, ARRIVE_DROP)
	else:
		player.position = MapData.anchor_px(map, "player_start")
	for loc: OverworldLocation in locations.get_children():
		loc.position = MapData.anchor_px(map, loc.id)
		loc.body_entered.connect(_on_location_entered.bind(loc))
		loc.body_exited.connect(_on_location_exited.bind(loc))
	$ExitSouth.position = MapData.anchor_px(map, "exit_south")
	$ExitSouth.body_entered.connect(_on_exit_south)
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 0.0, 0.7)
	await get_tree().create_timer(0.8).timeout
	_entry_locked = false
	# A body that pushed into a marker during the entry fade already fired its
	# body_entered (swallowed by the lock) and won't re-fire — deliver it now.
	for loc: OverworldLocation in locations.get_children():
		if loc.overlaps_body(player):
			_on_location_entered(player, loc)


func _clamp_camera() -> void:
	var cam: Camera2D = player.get_node("Camera2D")
	var size := MapData.size_px(map)
	cam.limit_left = 0
	cam.limit_top = 0
	cam.limit_right = int(size.x)
	cam.limit_bottom = int(size.y)


func _on_location_entered(body: Node2D, loc: OverworldLocation) -> void:
	if not body is Player or _entry_locked or _busy:
		return
	if _standing.get(loc.id, false):
		return
	_standing[loc.id] = true
	if loc.target_scene != "":
		_travel(loc)
	else:
		_announce(loc)


func _on_location_exited(body: Node2D, loc: OverworldLocation) -> void:
	if body is Player:
		_standing[loc.id] = false


## Through Basil's open door, down to the lab.
func _travel(loc: OverworldLocation) -> void:
	_busy = true
	if loc.id == "home":
		Game.interior_spawn = "front_door"
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


## Out the south lane, back to the overworld at the town icon.
func _on_exit_south(body: Node) -> void:
	if body is Player and not _busy:
		_busy = true
		Game.overworld_spawn = "town"
		var tw := create_tween()
		tw.tween_property(fade, "modulate:a", 1.0, 0.5)
		await tw.finished
		get_tree().change_scene_to_file("res://scene/overworld.tscn")


func _show_banner(text: String, hold: float) -> void:
	banner.text = text
	var tw := create_tween()
	tw.tween_property(banner, "modulate:a", 1.0, 0.25)
	tw.tween_interval(hold)
	tw.tween_property(banner, "modulate:a", 0.0, 0.35)
	await tw.finished
