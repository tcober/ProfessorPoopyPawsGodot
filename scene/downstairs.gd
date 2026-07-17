extends Node2D

## Basil's ground floor — the kitchen + lab great room between the loft
## bedroom and the outside world. Visible tiles stamped at runtime from the
## generated layout (assets/_gen_tileset_downstairs.py) onto two layers, with
## collision from the same assets/maps/downstairs.txt grid. Two ways in, two
## ways out: the top-center stair alcove climbs to the bedroom; the south
## front door opens into walkable Alembic Town, just below the cottage door
## (Game.town_spawn = "home"). The spawn anchor is routed through
## Game.interior_spawn (read-and-clear; "" = front_door, the town-entry
## default).

const MAP_PATH := "res://assets/maps/downstairs.txt"
const LAYOUT_PATH := "res://assets/tilesets/downstairs_layout.txt"

## Cozy hearth-lit interior: dim everything (Basil included), let the fire
## and the doorway daylight carry the brightness.
const DIM := Color(0.74, 0.7, 0.84)

const PROPS_PATH := "res://assets/tilesets/downstairs_props.txt"

## The whirligig (2026-07-16 Kitty thread): the prologue's first-friend
## machine, kept all these years on the hearth MANTEL — the same fx-sheet
## frames the meadow finale flew. The fire's draft stirs the rotor now and
## then; a relic, not magic. A plain $World sprite, not airborne(): it's a
## wall-band object over solid hearth cells — its key (40) sits north of any
## reachable body key, so a body pressed to the hearth face always occludes
## it, same as the baked mantel clutter beside it.
const FX_SHEET := preload("res://assets/prologue_fx.png")
const FX_WHIRL_DROOP := 7
const FX_WHIRL_SPIN0 := 8
## Offset from the hearth H-bbox origin to the mantel perch (between the
## baked candle and trinket box) — derived like $Fire so a map edit that
## moves the hearth carries the whirligig with the rest of the mantel art.
const WHIRL_OFFSET := Vector2(16.0, 8.0)
const WHIRL_STIR_PERIOD := 7.0
const WHIRL_STIR_LEN := 0.6

## Where the fire overlay sits inside the hearth bbox (the firebox opening
## in _interior_props.hearth: fx0=10, tongues from ~y20).
const FIRE_OFFSET := Vector2(10.0, 20.0)

var map: Dictionary
var _anim_t := 0.0
var _whirl: Sprite2D

var player: DirectionalBody2D


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	# y-sorted furniture (boiler, table, armchair, workbench) from the
	# generated manifest, spawned before the party so bodies win y-sort ties
	PropSpawner.build(PROPS_PATH, map, $World)
	# the whirligig relic on the mantel (machine feet at cell bottom, so the
	# center rides 8px above the plank line)
	_whirl = WorldFx.sheet_sprite(FX_SHEET, FX_WHIRL_DROOP)
	_whirl.position = MapData.bbox_rect(map, "H").position + WHIRL_OFFSET
	$World.add_child(_whirl)
	var spawn := Game.interior_spawn
	Game.interior_spawn = ""
	if spawn.is_empty() or not map.anchors.has(spawn):
		spawn = "front_door"
	player = Party.spawn($World, MapData.anchor_px(map, spawn))
	$ExitDoor.position = MapData.anchor_px(map, "exit_door")
	$UpStair.position = MapData.anchor_px(map, "exit_up")
	$Dim.color = DIM
	Party.clamp_cameras(MapData.view_size())
	$ExitDoor.body_entered.connect(_on_exit_door)
	$UpStair.body_entered.connect(_on_up_stair)
	# the hearth fire overlay (under entities), positioned from the map so
	# moving the feature chars moves it
	$Fire.position = MapData.bbox_rect(map, "H").position + FIRE_OFFSET


## The little life of the room: fire flicker, boiler shiver + steam leak.
func _process(delta: float) -> void:
	_anim_t += delta
	$Fire.frame = int(_anim_t / 0.16) % 3
	$World/Boiler.frame = int(_anim_t / 0.28) % 4
	# the drooped rotor stirs in the hearth draft for a beat every few seconds
	if fmod(_anim_t, WHIRL_STIR_PERIOD) > WHIRL_STIR_PERIOD - WHIRL_STIR_LEN:
		_whirl.frame = FX_WHIRL_SPIN0 + int(_anim_t / 0.12) % 2
	else:
		_whirl.frame = FX_WHIRL_DROOP


## Out the front door into Alembic Town, arriving just below the cottage door.
func _on_exit_door(body: Node) -> void:
	if body.is_in_group("player"):
		Game.town_spawn = "home"
		# Deferred: freeing the scene inside the Area2D callback is a physics error.
		get_tree().change_scene_to_file.call_deferred("res://scene/alembic_town.tscn")


## Up the alcove stairs to the loft bedroom, arriving at the stair head.
func _on_up_stair(body: Node) -> void:
	if body.is_in_group("player"):
		Game.interior_spawn = "stair_top"
		# Deferred: freeing the scene inside the Area2D callback is a physics error.
		get_tree().change_scene_to_file.call_deferred("res://scene/house.tscn")
