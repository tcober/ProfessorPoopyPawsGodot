extends Node2D

## THE DOCTOR'S OFFICE — Prologue B "the verdict" (docs/DESIGN.md Story).
## The front room of the east neighbor cottage in town (the door banners
## name it — one village, one doctor), rebuilt 2026-07-16 as a small dense
## diorama on the loft-bedroom recipe. Kitty survives the crash but her
## memory is gone; the stork doctor delivers the verdict; Basil sits at the
## bedside and she looks at him like a kind stranger. Then he leaves, and
## the town's clinic-steps phase closes the chapter. Interior pattern; Kitty is
## the npc_kitty_bed sprite propped at the pillow, the doctor an npc_stork
## sprite, both posed by the Theater.
##
## THE STAGE, NOT THE SCRIPT. This file builds the room and casts it; the beat
## itself — every word anybody says — lives in scene/sickroom_dialogue.gd, which
## extends this and is the script sickroom.tscn actually carries. Splitting on
## `_play_beat()` is the same hook idiom TravelScene already uses for
## `_place_player` / `_extra_setup`, and the path-form `extends` means no new
## class_name and so no re-import.

const MAP_PATH := "res://assets/maps/sickroom.txt"
const LAYOUT_PATH := "res://assets/tilesets/sickroom_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const SHEET_KITTY := preload("res://assets/npc_kitty_bed_gen.png")
const SHEET_STORK := preload("res://assets/npc_stork_gen.png")
const SHEET_KITTYMOM := preload("res://assets/npc_kittymom_gen.png")

var map: Dictionary
var player: Node2D
var _kitty: NPC
var _doctor: NPC

@onready var theater: Theater = $Theater


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	PropSpawner.build("res://assets/tilesets/sickroom_props.txt", map, $World)
	player = Party.spawn($World, MapData.anchor_px(map, "player_spawn"))
	Party.clamp_cameras(MapData.size_px(map))
	_spawn_cast()
	_play_beat()


func _spawn_cast() -> void:
	# Kitty in the bed: her sprite sits at the pillow; the frame cols are the
	# rest/vacant/polite trio (frame_cols=6 = [rest x2, vacant x2, polite x2]).
	# +8 centers her on the 4-cell bed's pillow (the anchor is the west
	# walk cell); -14 sets her head ON the pillow volume with the gown
	# meeting the folded sheet — the 2026-07-16 small-room geometry
	_kitty = _make_npc("Kitty", SHEET_KITTY,
			MapData.anchor_px(map, "kitty_bed") + Vector2(8.0, -14.0))
	_kitty.sprite.play("act")             # 'vacant' pair = act (cols 2-3)
	_doctor = _make_npc("Dr. Ciconia", SHEET_STORK,
			MapData.anchor_px(map, "doctor_spot"))


## All three of this room's sheets stay at SIX columns, and none of them is a
## sheet waiting on facings (the 2026-07-29 back/side pass deliberately skipped
## them): kitty_bed remaps cells 2-5 to rest/vacant/polite, so cells 6-9 would
## mean something else again on it, and the stork and Kitty's mother never move
## further than one tween across a room they both face the camera in — the whole
## verdict is played front-first, which is the point of it. face_dir() therefore
## falls back to idle_down for every direction here, and the ONE profile tell in
## the scene stays hand-rolled: the mother's flip_h below.
func _make_npc(nm: String, sheet: Texture2D, pos: Vector2) -> NPC:
	var npc: NPC = NPCScene.instantiate()
	npc.display_name = nm
	npc.sheet = sheet
	npc.frame_cols = 6
	npc.position = pos
	$World.add_child(npc)
	return npc

## The beat this room plays once it is built. Overridden in sickroom_dialogue.gd;
## a stub here so the base can call it and so the room still loads (empty) if the
## script is ever detached.
func _play_beat() -> void:
	pass
