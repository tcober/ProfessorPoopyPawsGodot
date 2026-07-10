class_name TravelScene
extends Node2D

## Shared driver for the CT-style walk-on-a-tiled-map scenes: the overworld
## travel layer and the walkable Alembic Town. Both stamp visible tiles from a
## generated layout onto Tiles (under the body) + TilesUpper (over it), take
## collision from the same map txt, and carry OverworldLocation markers that the
## body steps onto to travel or to read a locked-spot banner. Subclasses supply
## the player node, the map/layout paths, and where the body spawns; everything
## else — camera clamp, marker wiring, the entry fade, the announce/banner
## timing — lives here so the two scenes can't drift.

const ENTRY_FADE := 0.7      ## fade-from-black on arrival
const ENTRY_LOCK := 0.8      ## markers ignore the body until the fade settles
const TRAVEL_FADE := 0.5     ## fade-to-black when leaving through a marker
const BANNER_IN := 0.25
const BANNER_OUT := 0.35
const BANNER_HOLD := 1.6     ## how long a banner line rests before fading

var map: Dictionary
var player: Node2D

var _entry_locked := true
var _busy := false
## Marker ids the body is currently standing on; cleared on body_exited so a
## marker can't re-fire until the body steps off and back onto it.
var _standing: Dictionary = {}

@onready var locations: Node2D = $Locations
@onready var banner: Label = $UI/Banner
@onready var fade: ColorRect = $UI/Fade


func _ready() -> void:
	player = _player_node()
	map = MapData.load_map(_map_path())
	TiledMap.build(_layout_path(), {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	MapData.clamp_camera(player.get_node("Camera2D"), MapData.size_px(map))
	_wire_locations()
	_place_player()
	_extra_setup()
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 0.0, ENTRY_FADE)
	await get_tree().create_timer(ENTRY_LOCK).timeout
	_entry_locked = false
	# A body that pushed into a marker during the entry fade already fired its
	# body_entered (swallowed by the lock) and won't re-fire — deliver it now.
	for loc: OverworldLocation in locations.get_children():
		if loc.overlaps_body(player):
			_on_location_entered(player, loc)


func _wire_locations() -> void:
	for loc: OverworldLocation in locations.get_children():
		loc.position = MapData.anchor_px(map, loc.id)
		loc.body_entered.connect(_on_location_entered.bind(loc))
		loc.body_exited.connect(_on_location_exited.bind(loc))


func _on_location_entered(body: Node2D, loc: OverworldLocation) -> void:
	if body != player or _entry_locked or _busy:
		return
	if _standing.get(loc.id, false):
		return
	_standing[loc.id] = true
	if loc.target_scene != "":
		_travel(loc)
	else:
		_announce(loc)


func _on_location_exited(body: Node2D, loc: OverworldLocation) -> void:
	if body == player:
		_standing[loc.id] = false


func _travel(loc: OverworldLocation) -> void:
	_busy = true
	_on_travel(loc)
	_show_banner(loc.display_name, BANNER_HOLD)
	await fade_out()
	get_tree().change_scene_to_file(loc.target_scene)


func _announce(loc: OverworldLocation) -> void:
	_busy = true
	await _show_banner(loc.display_name, BANNER_HOLD)
	if loc.locked_text != "":
		await _show_banner(loc.locked_text, BANNER_HOLD)
	_busy = false


func _show_banner(text: String, hold: float) -> void:
	banner.text = text
	var tw := create_tween()
	tw.tween_property(banner, "modulate:a", 1.0, BANNER_IN)
	tw.tween_interval(hold)
	tw.tween_property(banner, "modulate:a", 0.0, BANNER_OUT)
	await tw.finished


## Fade to black; callers change scene once it resolves.
func fade_out() -> void:
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 1.0, TRAVEL_FADE)
	await tw.finished


# ---- subclass hooks --------------------------------------------------------

## The travel body this scene wires markers against (path differs per scene).
func _player_node() -> Node2D:
	assert(false, "TravelScene subclass must override _player_node()")
	return null

func _map_path() -> String:
	return ""

func _layout_path() -> String:
	return ""

## Put the body at its spawn (default anchor, or a routed return spawn).
func _place_player() -> void:
	pass

## Extra per-scene wiring (e.g. an exit zone) before the entry fade. Optional.
func _extra_setup() -> void:
	pass

## Per-scene spawn bookkeeping when leaving through a marker (records where to
## return). Optional.
func _on_travel(_loc: OverworldLocation) -> void:
	pass
