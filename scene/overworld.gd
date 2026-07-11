extends TravelScene

## Chrono Trigger-style travel layer over a TILED continent (see TravelScene for
## the shared machinery). Markers take their positions from the map's anchors —
## one source of truth for geography. Towns are CT-faithful cluster ICONS:
## stepping on Alembic Town's gate mouth fades straight into Basil's downstairs
## (the walkable town scene, alembic_town.tscn, is PARKED — see DESIGN.md); the
## meadow marker fades into the meadow zone. Locked spots announce in the banner.

const MAP_PATH := "res://assets/maps/overworld.txt"
const LAYOUT_PATH := "res://assets/tilesets/overworld_layout.txt"

## Return-spawn drop below a marker: one tile and a hair, so arriving from a
## zone lands the chibi on the walkable cell just south of the marker (door
## mouths sit IN a building's door cell) without re-triggering it.
const ARRIVE_DROP := 18.0


func _player_node() -> Node2D:
	return $OverworldPlayer


func _map_path() -> String:
	return MAP_PATH


func _layout_path() -> String:
	return LAYOUT_PATH


## The party travels as ONE chibi (CT/SoM convention) — whoever leads is the
## one walking the map. Both chibi scenes share overworld_player.gd; only the
## SpriteFrames differ, so the swap is a frames repoint.
const FUJI_CHIBI_FRAMES := "res://entities/player/overworld_fuji_frames.tres"


func _place_player() -> void:
	if Party.leader_id == &"fuji":
		var chibi_sprite := player.get_node("AnimatedSprite2D") as AnimatedSprite2D
		chibi_sprite.sprite_frames = load(FUJI_CHIBI_FRAMES)
	player.global_position = MapData.anchor_px(map, "player_start")
	for loc: OverworldLocation in locations.get_children():
		if loc.id == Game.overworld_spawn:
			player.global_position = loc.global_position + Vector2(0.0, ARRIVE_DROP)


func _on_travel(loc: OverworldLocation) -> void:
	Game.overworld_spawn = loc.id
