extends Node2D

## Whisker Meadow, a tiled combat zone on the shared overworld tile kit
## (assets/_gen_tileset_meadow.py): Tiles/TilesUpper are stamped from the
## generated layout; collision is an invisible TileMapLayer built at runtime
## from the same map file, so tiles and physics agree by construction.
## Entities y-sort under World. Keeps exactly one beaker refill alive at a
## time — collecting it spawns a fresh one elsewhere — and keeps the slime
## population topped up: each kill respawns one elsewhere.

const BeakerScene := preload("res://entities/pickups/beaker.tscn")
const SlimeScene := preload("res://entities/enemies/slime.tscn")

const MAP_PATH := "res://assets/maps/meadow.txt"
const LAYOUT_PATH := "res://assets/tilesets/meadow_layout.txt"
const TILE := 16

var map: Dictionary

@onready var player: DirectionalBody2D = $World/Player
@onready var hud: HUD = $HUD
@onready var world: Node2D = $World


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	player.position = MapData.anchor_px(map, "player_spawn")
	$ExitSouth.position = MapData.anchor_px(map, "exit_south")
	MapData.clamp_camera(player.get_node("Camera2D"), MapData.size_px(map))
	hud.bind_health(player.get_node("HealthComponent") as HealthComponent)
	if player is Player:
		# Gun-cat plumbing: ammo pips, spare mags, and the beaker refill.
		hud.bind_ammo(player as Player)
		_track_beaker($World/Beaker)
	else:
		# Fuji fights with tome + darts — the beaker refill has no meaning.
		$World/Beaker.queue_free()
	for child in world.get_children():
		if child is Slime:
			_track_slime(child)
	$ExitSouth.body_entered.connect(_on_exit_south)


func _track_beaker(beaker: Beaker) -> void:
	beaker.collected.connect(_on_beaker_collected)


func _on_beaker_collected() -> void:
	var beaker := BeakerScene.instantiate()
	beaker.position = _random_spawn()
	world.add_child(beaker)
	_track_beaker(beaker)


func _track_slime(slime: Slime) -> void:
	slime.died.connect(_on_slime_died)


func _on_slime_died() -> void:
	# Deferred: died fires mid-physics; adding a body during a callback is unsafe.
	_spawn_slime.call_deferred()


func _spawn_slime() -> void:
	var slime := SlimeScene.instantiate()
	slime.position = _random_spawn()
	world.add_child(slime)
	_track_slime(slime)


func _random_spawn() -> Vector2:
	# Try a few spots so the respawn doesn't drop on the player or in a solid.
	var size := MapData.size_px(map)
	var point := Vector2.ZERO
	for i in 20:
		point = Vector2(
			randf_range(TILE * 1.5, size.x - TILE * 1.5),
			randf_range(TILE * 1.5, size.y - TILE * 1.5)
		)
		var cell := Vector2i(point / TILE)
		if not MapData.is_solid(map, cell) and point.distance_to(player.global_position) > 48.0:
			return point
	return point


func _on_exit_south(body: Node) -> void:
	if body.is_in_group("player"):
		# Return to the meadow's own icon on the overworld (explicit, not relying
		# on the value the overworld wrote on the way in).
		Game.overworld_spawn = "meadow"
		# Deferred: freeing the scene inside the Area2D callback is a physics error.
		get_tree().change_scene_to_file.call_deferred("res://scene/overworld.tscn")
