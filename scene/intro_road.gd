extends Node2D

## Opening scene, part 2 — PLAYABLE. Basil sprints the road to the Academy with poop
## on his paws (he leaves a fading trail of prints). A couple of slimes block the way:
## the player learns to fire and hop. Reaching the Academy doors starts the lecture.

const PRINT_TEX := preload("res://assets/props/paw_print.png")

const TILE := 16
## Legend: '#' hedge (solid) · '.' grass · '-' dirt path · 'f' flowers · 'r' rock
const MAP: Array[String] = [
	"################################################################################",
	"#..............................................................................#",
	"#..f..........f...............r......f................f........................#",
	"#....r.................f..........................r............f...............#",
	"#..........f..................................f.......................f........#",
	"#.....................r................f.......................................#",
	"#..f...........f...............................................r...............#",
	"#.........r.....................f.....................f........................#",
	"#...............................................f..............................#",
	"#......f..............r........................................................#",
	"#...............................................................f..............#",
	"#------------------------------------------------------------------------------#",
	"#------------------------------------------------------------------------------#",
	"#.....f........r...............................f...............................#",
	"#..........................f.......................................r...........#",
	"#...r..............f..............r..................f.........................#",
	"#.f..........................f.................................................#",
	"#.....................f..................r.....................f...............#",
	"#..........r...................................................................#",
	"#..f...................................f.............r..........f..............#",
	"#..............f...............................................................#",
	"#.......................................................f......................#",
	"################################################################################",
]

const T_GRASS := Vector2i(0, 0)
const T_TUFT := Vector2i(1, 0)
const T_FLOWERS := Vector2i(2, 0)
const T_PATH := Vector2i(3, 0)
const T_HEDGE_A := Vector2i(0, 1)
const T_HEDGE_B := Vector2i(1, 1)
const T_ROCK := Vector2i(2, 1)

const MAX_PRINTS := 26

@onready var player: Player = $Player
@onready var hud: HUD = $HUD
@onready var ground: TileMapLayer = $Ground
@onready var prints: Node2D = $Prints
@onready var hint: Label = $UI/Hint

var _prints_left: int = MAX_PRINTS
var _last_print_pos: Vector2


func _ready() -> void:
	_paint_map()
	var cam: Camera2D = player.get_node("Camera2D")
	cam.limit_left = 0
	cam.limit_top = 0
	cam.limit_right = MAP[0].length() * TILE
	cam.limit_bottom = MAP.size() * TILE
	hud.bind_health(player.health)
	hud.bind_ammo(player)
	_last_print_pos = player.global_position
	$SchoolDoor.body_entered.connect(_on_school_door)
	# The hint hangs around for a bit, then fades.
	var tw := create_tween()
	tw.tween_interval(6.0)
	tw.tween_property(hint, "modulate:a", 0.0, 1.2)


func _physics_process(_delta: float) -> void:
	# Poopy paw prints trail behind him until they (mostly) wear off.
	if _prints_left > 0 and player.global_position.distance_to(_last_print_pos) > 11.0:
		var p := Sprite2D.new()
		p.texture = PRINT_TEX
		p.position = player.global_position + Vector2(4 if _prints_left % 2 == 0 else -4, 18)
		p.modulate.a = 0.5 + 0.5 * float(_prints_left) / MAX_PRINTS
		prints.add_child(p)
		_last_print_pos = player.global_position
		_prints_left -= 1


func _paint_map() -> void:
	for y in MAP.size():
		var row := MAP[y]
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


func _on_school_door(body: Node) -> void:
	if body is Player:
		get_tree().change_scene_to_file("res://scene/intro_hall.tscn")


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_tree().change_scene_to_file("res://scene/overworld.tscn")
