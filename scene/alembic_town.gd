extends TravelScene

## Alembic Town, walkable at zone scale — the CT-Truce village the overworld's
## town icon opens into (see TravelScene for the shared machinery). Basil's open
## door travels down to the lab (downstairs); the neighbor cottages and the
## barred Academy announce in the banner; the south lane exits to the overworld.
## The spawn is routed through Game.town_spawn (read-and-clear; "" = the south
## entrance, where the overworld drops you). PARKED for now — see DESIGN.md.

const MAP_PATH := "res://assets/maps/town.txt"
const LAYOUT_PATH := "res://assets/tilesets/town_layout.txt"

## Return-spawn drop below the home door: a tile and a half for the 48px
## player, so leaving the cottage lands him clear of the door marker.
const ARRIVE_DROP := 24.0


func _player_node() -> Node2D:
	return Party.spawn($World, Vector2.ZERO)   # placed for real in _place_player


func _map_path() -> String:
	return MAP_PATH


func _layout_path() -> String:
	return LAYOUT_PATH


func _place_player() -> void:
	var spawn := Game.town_spawn
	Game.town_spawn = ""
	if spawn == "home":
		Party.place(MapData.anchor_px(map, "home") + Vector2(0.0, ARRIVE_DROP))
	else:
		Party.place(MapData.anchor_px(map, "player_start"))


func _extra_setup() -> void:
	$ExitSouth.position = MapData.anchor_px(map, "exit_south")
	$ExitSouth.body_entered.connect(_on_exit_south)
	Party.clamp_cameras(MapData.size_px(map))
	# TravelScene gates its markers on `body != player` — re-aim it when the
	# lead changes hands mid-town.
	Party.leader_changed.connect(_on_leader_changed)


func _on_leader_changed(leader: PartyMember) -> void:
	player = leader


## Through Basil's open door, down to the lab.
func _on_travel(loc: OverworldLocation) -> void:
	if loc.id == "home":
		Game.interior_spawn = "front_door"


## Out the south lane, back to the overworld at the town icon.
func _on_exit_south(body: Node) -> void:
	if body.is_in_group("player") and not _busy:
		_busy = true
		Game.overworld_spawn = "town"
		await fade_out()
		get_tree().change_scene_to_file("res://scene/overworld.tscn")
