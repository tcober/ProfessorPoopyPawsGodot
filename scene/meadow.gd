extends Node2D

## Whisker Meadow, a painted scene: Ground and Overlay are single generated
## paintings (assets/_gen_scene_meadow.py); collision is an invisible
## TileMapLayer built at runtime from the same map file, so paint and physics
## agree by construction. Entities y-sort under World. Keeps exactly one beaker
## refill alive at a time — collecting it spawns a fresh one elsewhere.

const BeakerScene := preload("res://entities/pickups/beaker.tscn")

const MAP_PATH := "res://assets/maps/meadow.txt"
const TILE := 32

var map: Dictionary

@onready var player: Player = $World/Player
@onready var hud: HUD = $HUD
@onready var world: Node2D = $World


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	PaintedMap.build_collision(map, $Collision)
	player.position = MapData.anchor_px(map, "player_spawn")
	$ExitSouth.position = MapData.anchor_px(map, "exit_south")
	_clamp_camera()
	hud.bind_health(player.health)
	hud.bind_ammo(player)
	_track_beaker($World/Beaker)
	$ExitSouth.body_entered.connect(_on_exit_south)


func _clamp_camera() -> void:
	var cam: Camera2D = player.get_node("Camera2D")
	var size := MapData.size_px(map)
	cam.limit_left = 0
	cam.limit_top = 0
	cam.limit_right = int(size.x)
	cam.limit_bottom = int(size.y)


func _track_beaker(beaker: Beaker) -> void:
	beaker.collected.connect(_on_beaker_collected)


func _on_beaker_collected() -> void:
	var beaker := BeakerScene.instantiate()
	beaker.position = _random_spawn()
	world.add_child(beaker)
	_track_beaker(beaker)


func _random_spawn() -> Vector2:
	# Try a few spots so the new beaker doesn't drop on the player or in a solid.
	var size := MapData.size_px(map)
	var point := Vector2.ZERO
	for i in 20:
		point = Vector2(
			randf_range(TILE * 1.5, size.x - TILE * 1.5),
			randf_range(TILE * 1.5, size.y - TILE * 1.5)
		)
		var cell := Vector2i(point / TILE)
		if not MapData.is_solid(map, cell) and point.distance_to(player.global_position) > 96.0:
			return point
	return point


func _on_exit_south(body: Node) -> void:
	if body is Player:
		get_tree().change_scene_to_file("res://scene/overworld.tscn")
