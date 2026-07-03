extends Node2D

## Opening scene, part 2 — PLAYABLE. Basil sprints the road to the Academy with poop
## on his paws (he leaves a fading trail of prints). A couple of slimes block the way:
## the player learns to fire and hop. Reaching the Academy doors starts the lecture.
##
## Painted scene: Ground/Overlay are single generated paintings
## (assets/_gen_scene_road.py); collision comes from assets/maps/road.txt.

const PRINT_TEX := preload("res://assets/props/paw_print.png")

const MAP_PATH := "res://assets/maps/road.txt"
const MAX_PRINTS := 26

var map: Dictionary

@onready var player: Player = $World/Player
@onready var hud: HUD = $HUD
@onready var prints: Node2D = $Prints
@onready var hint: Label = $UI/Hint

var _prints_left: int = MAX_PRINTS
var _last_print_pos: Vector2


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	PaintedMap.build_collision(map, $Collision)
	player.position = MapData.anchor_px(map, "player_spawn")
	$SchoolDoor.position = MapData.anchor_px(map, "school_door")
	var cam: Camera2D = player.get_node("Camera2D")
	var size := MapData.size_px(map)
	cam.limit_left = 0
	cam.limit_top = 0
	cam.limit_right = int(size.x)
	cam.limit_bottom = int(size.y)
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
	if _prints_left > 0 and player.global_position.distance_to(_last_print_pos) > 22.0:
		var p := Sprite2D.new()
		p.texture = PRINT_TEX
		p.position = player.global_position + Vector2(8 if _prints_left % 2 == 0 else -8, 36)
		p.modulate.a = 0.5 + 0.5 * float(_prints_left) / MAX_PRINTS
		prints.add_child(p)
		_last_print_pos = player.global_position
		_prints_left -= 1


func _on_school_door(body: Node) -> void:
	if body is Player:
		get_tree().change_scene_to_file("res://scene/intro_hall.tscn")


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_tree().change_scene_to_file("res://scene/overworld.tscn")
