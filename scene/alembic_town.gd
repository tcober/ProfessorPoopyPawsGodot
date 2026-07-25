extends TravelScene

## Alembic Town, walkable at zone scale — the Kakariko-style village the
## overworld's town icon opens into (see TravelScene for the shared machinery).
## Basil's open door travels down to the lab (downstairs); the shops, inn,
## neighbor cottages and the terrace's barred Academy announce in the banner;
## the south lane exits to the overworld. The spawn is routed through
## Game.town_spawn (read-and-clear; "home" = below Basil's door for the
## downstairs front door, "" = the south gate, where the overworld drops you).

const MAP_PATH := "res://assets/maps/town.txt"
const LAYOUT_PATH := "res://assets/tilesets/town_layout.txt"


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
		# Land ON the door marker — feet on the lane right under the arch
		# (the old tile-and-a-half drop read as appearing nowhere near the
		# door). _standing suppresses the marker until he steps off it once.
		Party.place(MapData.anchor_px(map, "home"))
		_standing["home"] = true
	else:
		Party.place(MapData.anchor_px(map, "player_start"))


func _extra_setup() -> void:
	# street furniture (well, lamps, stall, fountain) as y-sorted World
	# entities; the spawner front-loads them in child order so the party
	# (spawned first by TravelScene) still wins y-sort ties
	PropSpawner.build("res://assets/tilesets/town_props.txt", map, $World)
	_collect_animated()
	$ExitSouth.position = MapData.anchor_px(map, "exit_south")
	$ExitSouth.body_entered.connect(_on_exit_south)
	Party.clamp_cameras(MapData.size_px(map))
	# TravelScene gates its markers on `body != player` — re-aim it when the
	# lead changes hands mid-town.
	Party.leader_changed.connect(_on_leader_changed)


## Through Basil's open door, down to the lab.
func _on_travel(loc: OverworldLocation) -> void:
	if loc.id == "home":
		Game.interior_spawn = "front_door"


## Out the south lane, back to the overworld at the town icon.
func _on_exit_south(body: Node) -> void:
	if body.is_in_group("player"):
		_exit_to_overworld("town")
