extends Node2D

## Vertical-slice meadow: an ASCII map painted onto a TileMapLayer (hedge border is
## solid via the tileset's physics layer), a camera clamped to the room, slimes, and a
## HUD bound to the player's HealthComponent. Keeps exactly one beaker refill alive at
## a time — collecting it spawns a fresh one elsewhere in the room.

const BeakerScene := preload("res://entities/pickups/beaker.tscn")

const TILE := 16

## Legend: '#' hedge (solid) · '.' grass · '-' dirt path · 'f' flowers · 'r' rock
const MAP: Array[String] = [
	"################################################",
	"#..............................................#",
	"#..f....................f...........f..........#",
	"#.....................r................r.......#",
	"#....--------------------------................#",
	"#...-..........................----............#",
	"#...-..............................--..........#",
	"#..f-....r...........f...............-....f....#",
	"#...-.................................-........#",
	"#...-.........f.......................-...f....#",
	"#....--............r..................-........#",
	"#......-...............f.............-.....r...#",
	"#.r.....-............................-.........#",
	"#........-...........r..............--....f....#",
	"#..f......-........................-...........#",
	"#..........--......f..............-............#",
	"#....f........-..................--......r.....#",
	"#..............------------------..............#",
	"#..f..........f..........f..............f......#",
	"#.......r........................r.............#",
	"#...........f.........f..................f.....#",
	"#......................................r.......#",
	"#..............f...............................#",
	"######################....######################",
]

## Tileset atlas coords (see assets/_gen_tileset.py).
const T_GRASS := Vector2i(0, 0)
const T_TUFT := Vector2i(1, 0)
const T_FLOWERS := Vector2i(2, 0)
const T_PATH := Vector2i(3, 0)
const T_HEDGE_A := Vector2i(0, 1)
const T_HEDGE_B := Vector2i(1, 1)
const T_ROCK := Vector2i(2, 1)

## Beaker spawn bounds, kept inside the hedge border.
const SPAWN_MIN := Vector2(28, 28)
const SPAWN_MAX := Vector2(740, 356)

@onready var player: Player = $Player
@onready var hud: HUD = $HUD
@onready var ground: TileMapLayer = $Ground


func _ready() -> void:
	_paint_map()
	_clamp_camera()
	hud.bind_health(player.health)
	hud.bind_ammo(player)
	_track_beaker($Beaker)
	$ExitSouth.body_entered.connect(_on_exit_south)


func _paint_map() -> void:
	for y in MAP.size():
		var row := MAP[y]
		assert(row.length() == MAP[0].length(), "MAP rows must all be the same width")
		for x in row.length():
			ground.set_cell(Vector2i(x, y), 0, _tile_for(row[x], x, y))


func _tile_for(ch: String, x: int, y: int) -> Vector2i:
	match ch:
		"#":
			return T_HEDGE_B if _cell_hash(x, y) % 4 == 0 else T_HEDGE_A
		"-":
			return T_PATH
		"f":
			return T_FLOWERS
		"r":
			return T_ROCK
		_:
			return T_TUFT if _cell_hash(x, y) % 10 < 3 else T_GRASS


static func _cell_hash(x: int, y: int) -> int:
	return absi((x * 73856093) ^ (y * 19349663))


func _clamp_camera() -> void:
	var cam: Camera2D = player.get_node("Camera2D")
	cam.limit_left = 0
	cam.limit_top = 0
	cam.limit_right = MAP[0].length() * TILE
	cam.limit_bottom = MAP.size() * TILE


func _track_beaker(beaker: Beaker) -> void:
	beaker.collected.connect(_on_beaker_collected)


func _on_beaker_collected() -> void:
	var beaker := BeakerScene.instantiate()
	beaker.position = _random_spawn()
	add_child(beaker)
	_track_beaker(beaker)


func _random_spawn() -> Vector2:
	# Try a few spots so the new beaker doesn't drop right on the player or in a hedge.
	var point := Vector2.ZERO
	for i in 20:
		point = Vector2(
			randf_range(SPAWN_MIN.x, SPAWN_MAX.x),
			randf_range(SPAWN_MIN.y, SPAWN_MAX.y)
		)
		var cell := ground.local_to_map(point)
		var solid := ground.get_cell_atlas_coords(cell) in [T_HEDGE_A, T_HEDGE_B]
		if not solid and point.distance_to(player.global_position) > 48.0:
			return point
	return point


func _on_exit_south(body: Node) -> void:
	if body is Player:
		get_tree().change_scene_to_file("res://scene/overworld.tscn")
