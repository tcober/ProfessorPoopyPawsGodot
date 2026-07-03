extends Node2D

## Chrono Trigger-style travel layer: a miniature continent painted from an ASCII map
## onto a TileMapLayer (water/forest/mountains solid via the tileset physics layer).
## Basil's chibi self walks between OverworldLocation markers — unlocked ones fade out
## into their zone scene, locked ones announce themselves in the bottom banner.

const TILE := 32

## Legend: '~' water · 's' sand · '.' grass · '-' path · '=' bridge · 'f' forest
## 'e' forest edge · 'h' hills · 'M' mountain · 'S' snow peak · 'r' river · 'c' cliff
## 'x' cracked earth · 't' dead tree · '*' crystal
const MAP: Array[String] = [
	"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~~~~~~~ssssss~~~~~~~~~~~~sssssss~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~~~~ss..................ffffffffffffffs~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~~s...MMSMMMMMMSMMMMMMMMffffffffffffffs~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~s...hMMMMMMMMMMMMMMMMMMffffffffffffffs~~~~~~~",
	"~~~~~~~~~~~~~~~~~~s....hMMMMMMMMMMMMMMMMMMffffffffffffffs~~~~~~~",
	"~~~~~~~~~~~~~~~~~~s....cMMMMMMMMMMMMMMMMMMffffffffffffffs~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~....cMMMMMMMMMMMMMMMMMMffffffffffffffs~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~s....ccccccccccccccrccceeeeeeeeeeeeees~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~~s.................r.................s~~~~~~~",
	"~~~~~~~~~~~~~~~~~~s...........-........r................s~~~~~~~",
	"~~~~~~~~~~~~~~~~~~sff.........-.........r......----.....s~~~~~~~",
	"~~~~~~~~~~~~~~~~~~see.........-.........r.....--........s~~~~~~~",
	"~~~~~~~~~~~~~~~~~~s...---------..........r...--.........s~~~~~~~",
	"~~~~~~~~~~~~~~~~~~s...-.......-..........r...-..........s~~~~~~~",
	"~~~~~~~~~~~~~~~~~~s..--.......------------=--.hxxxxxxxxhs~~~~~~~",
	"~~~~~~~~~~~~~~~~~~s..-....................r..hxxxtxxxxxxs~~~~~~~",
	"~~~~~~~~~~~~~~~~~s..--....................r.hxxxxxxxtxxxs~~~~~~~",
	"~~~~~~~~~~~~~~~~~s..-......................rhxxtxxxxxxxxs~~~~~~~",
	"~~~~~~~~~~~~~~~~s..--......................rxxxxxxxxxxtxs~~~~~~~",
	"~~~~~~~~~~~~~~~~s..-.......................rxxtxxxxxxxxxs~~~~~~~",
	"~~~~~~~~~~~~~~~s..--........................rxxxxxxtxxxxs~~~~~~~",
	"~~~~~~~~~~~~~~~s..-.........................rxxxx*xxxxxxs~~~~~~~",
	"~~~~~~~~~~~~~~s..--.........................rxxtxxxxxxxxs~~~~~~~",
	"~~~~~~~~~~~s....--.........................rxxxxxxxxxxxts~~~~~~~",
	"~~~~~~~~~ss....--..........................rxtxxxxxxxxxs~~~~~~~~",
	"~~~~~s.h......--...........................rxxxxxxxxxxs~~~~~~~~~",
	"~~~~ssh...-----.............................rxxxxxxxxxs~~~~~~~~~",
	"~~~~s..........h............................rxxxxxxxxs~~~~~~~~~~",
	"~~~~~ss.........ss....................s.....rxxxtxxss~~~~~~~~~~~",
	"~~~~~~ssss~~~~~~~~~~ssssss~~~~~~~sssss~~~sssrsss~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
	"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
]

## Atlas coords in assets/overworld_tiles.png (8x3 grid of 32x32 tiles).
const T_WATER := Vector2i(0, 0)
const T_WATER_SPARKLE := Vector2i(1, 0)
const T_SAND := Vector2i(2, 0)
const T_GRASS := Vector2i(3, 0)
const T_GRASS_DETAIL := Vector2i(4, 0)
const T_SCRUB := Vector2i(5, 0)
const T_PATH := Vector2i(6, 0)
const T_BRIDGE := Vector2i(7, 0)
const T_FOREST_A := Vector2i(0, 1)
const T_FOREST_B := Vector2i(1, 1)
const T_FOREST_EDGE := Vector2i(2, 1)
const T_HILLS := Vector2i(3, 1)
const T_MOUNTAIN := Vector2i(4, 1)
const T_MOUNTAIN_SNOW := Vector2i(5, 1)
const T_RIVER := Vector2i(6, 1)
const T_CLIFF := Vector2i(7, 1)
const T_CRACKED_A := Vector2i(0, 2)
const T_CRACKED_B := Vector2i(1, 2)
const T_DEAD_TREE := Vector2i(2, 2)
const T_CRYSTAL := Vector2i(3, 2)

@onready var player: OverworldPlayer = $OverworldPlayer
@onready var ground: TileMapLayer = $Ground
@onready var locations: Node2D = $Locations
@onready var banner: Label = $UI/Banner
@onready var fade: ColorRect = $UI/Fade

var _entry_locked: bool = true
var _busy: bool = false
## Location ids the player is currently standing on; cleared on body_exited so a
## marker can't re-announce until he steps off and back onto it.
var _standing: Dictionary = {}


func _ready() -> void:
	_paint_map()
	_clamp_camera()
	for loc: OverworldLocation in locations.get_children():
		loc.body_entered.connect(_on_location_entered.bind(loc))
		loc.body_exited.connect(_on_location_exited.bind(loc))
		if loc.id == Game.overworld_spawn:
			player.global_position = loc.global_position + Vector2(0, 52)
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 0.0, 0.7)
	await get_tree().create_timer(0.8).timeout
	_entry_locked = false


func _paint_map() -> void:
	for y in MAP.size():
		var row := MAP[y]
		assert(row.length() == MAP[0].length(), "MAP rows must all be the same width")
		for x in row.length():
			ground.set_cell(Vector2i(x, y), 0, _tile_for(row[x], x, y))


func _tile_for(ch: String, x: int, y: int) -> Vector2i:
	var h := _cell_hash(x, y)
	match ch:
		"~":
			return T_WATER_SPARKLE if h % 7 == 0 else T_WATER
		"s":
			return T_SAND
		"-":
			return T_PATH
		"=":
			return T_BRIDGE
		"f":
			# `h / 8` so the A/B mix uses higher hash bits, not a strict checkerboard.
			return T_FOREST_A if (h / 8) % 2 == 0 else T_FOREST_B
		"e":
			return T_FOREST_EDGE
		"h":
			return T_HILLS
		"M":
			return T_MOUNTAIN
		"S":
			return T_MOUNTAIN_SNOW
		"r":
			return T_RIVER
		"c":
			return T_CLIFF
		"x":
			return T_CRACKED_A if (h / 8) % 2 == 0 else T_CRACKED_B
		"t":
			return T_DEAD_TREE
		"*":
			return T_CRYSTAL
		_:
			if h % 14 == 0:
				return T_SCRUB
			if h % 8 == 0:
				return T_GRASS_DETAIL
			return T_GRASS


static func _cell_hash(x: int, y: int) -> int:
	return absi((x * 73856093) ^ (y * 19349663))


func _clamp_camera() -> void:
	var cam: Camera2D = player.get_node("Camera2D")
	cam.limit_left = 0
	cam.limit_top = 0
	cam.limit_right = MAP[0].length() * TILE
	cam.limit_bottom = MAP.size() * TILE


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
