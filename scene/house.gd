extends Node2D

## Basil's house, the tile-based attic bedroom: visible tiles stamped at
## runtime from the generated layout (assets/_gen_tileset_house.py) onto two
## layers — Tiles under entities, TilesUpper over them (Basil passes behind
## the stairwell railing) — with collision from the same assets/maps/house.txt
## grid, so nothing can drift. Descending the stairs returns to the overworld
## at the home marker.

const MAP_PATH := "res://assets/maps/house.txt"
const LAYOUT_PATH := "res://assets/tilesets/house_layout.txt"

## Room dim (CanvasModulate): darker while the curtains are drawn, still dim
## when open — the window beam and pool carry the brightness.
const DIM_OPEN := Color(0.72, 0.7, 0.86)
const DIM_CLOSED := Color(0.62, 0.6, 0.8)

const PROPS_PATH := "res://assets/tilesets/house_props.txt"

var map: Dictionary
var curtains_open := false
var _near_window := false
var _curtain_busy := false

var player: DirectionalBody2D


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	# Spawn at the routed anchor (stair_top when climbing up from the
	# downstairs), else the default bedside boot spawn. Read-and-clear.
	# y-sorted furniture (desk, bed cover) from the generated manifest,
	# spawned before the party so bodies win y-sort ties
	PropSpawner.build(PROPS_PATH, map, $World)
	var spawn := Game.interior_spawn
	Game.interior_spawn = ""
	if spawn.is_empty() or not map.anchors.has(spawn):
		spawn = "player_spawn"
	player = Party.spawn($World, MapData.anchor_px(map, spawn))
	$ExitDoor.position = MapData.anchor_px(map, "exit_door")
	Party.clamp_cameras(MapData.view_size())
	$ExitDoor.body_entered.connect(_on_exit_door)
	# Curtain mechanic: the room wakes with the curtains drawn; standing at
	# the window (WindowZone) and pressing interact toggles them. Positions
	# derive from the map's W cells, so moving the window moves it all.
	var win := MapData.bbox_rect(map, "W")
	$Curtains.position = win.position
	$Curtains.frame = 0
	$Glow.modulate.a = 0.0
	$Dim.color = DIM_CLOSED
	$WindowZone.position = win.position + Vector2(win.size.x / 2.0, win.size.y + 14.0)
	$WindowZone.body_entered.connect(_on_window_zone.bind(true))
	$WindowZone.body_exited.connect(_on_window_zone.bind(false))


func _process(_delta: float) -> void:
	if _near_window and Input.is_action_just_pressed("interact"):
		_toggle_curtains()


func _on_window_zone(body: Node, entered: bool) -> void:
	if body.is_in_group("player"):
		_near_window = entered


## Slide the curtains open/closed through the half-open frame; the additive
## window beam and the room dim follow. (The fully open tied-back drapes are
## baked into the window tiles, so the sprite hides when open.)
func _toggle_curtains() -> void:
	if _curtain_busy:
		return
	_curtain_busy = true
	curtains_open = not curtains_open
	var tw := create_tween().set_parallel()
	if curtains_open:
		$Curtains.frame = 1
		tw.tween_property($Glow, "modulate:a", 1.0, 0.5)
		tw.tween_property($Dim, "color", DIM_OPEN, 0.5)
		await get_tree().create_timer(0.1).timeout
		if not is_inside_tree():
			return
		$Curtains.visible = false
	else:
		$Curtains.visible = true
		$Curtains.frame = 1
		tw.tween_property($Glow, "modulate:a", 0.0, 0.3)
		tw.tween_property($Dim, "color", DIM_CLOSED, 0.3)
		await get_tree().create_timer(0.1).timeout
		if not is_inside_tree():
			return
		$Curtains.frame = 0
	_curtain_busy = false


## Descending the loft stairs lands at their foot in the downstairs great room.
func _on_exit_door(body: Node) -> void:
	if body.is_in_group("player"):
		Game.interior_spawn = "stair_arrival"
		# Deferred: freeing the scene inside the Area2D callback is a physics error.
		get_tree().change_scene_to_file.call_deferred("res://scene/downstairs.tscn")
