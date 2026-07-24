extends TravelScene

## Lanternwood, walkable at zone scale — Fuji's winter pine-forest hometown
## on the ice land (see TravelScene for the shared machinery). Every door is
## announce-only for now: the library, Fuji's family home and the three
## snow-banked cabins read their banner lines; the south gate lane exits to
## the overworld at Lanternwood's icon marker.

const MAP_PATH := "res://assets/maps/lanternwood.txt"
const LAYOUT_PATH := "res://assets/tilesets/lanternwood_layout.txt"


func _player_node() -> Node2D:
	return Party.spawn($World, Vector2.ZERO)   # placed for real in _place_player


func _map_path() -> String:
	return MAP_PATH


func _layout_path() -> String:
	return LAYOUT_PATH


func _place_player() -> void:
	Party.place(MapData.anchor_px(map, "player_start"))


func _extra_setup() -> void:
	# cabins, conifers and lamps as y-sorted World entities; the spawner
	# front-loads them in child order so the party (spawned first by
	# TravelScene) still wins y-sort ties
	PropSpawner.build("res://assets/tilesets/lanternwood_props.txt", map, $World)
	_collect_animated()
	$ExitSouth.position = MapData.anchor_px(map, "exit_south")
	$ExitSouth.body_entered.connect(_on_exit_south)
	Party.clamp_cameras(MapData.size_px(map))
	# TravelScene gates its markers on `body != player` — re-aim it when the
	# lead changes hands mid-town.
	Party.leader_changed.connect(_on_leader_changed)


## Out the south gate lane, back to the overworld at the Lanternwood icon.
func _on_exit_south(body: Node) -> void:
	if body.is_in_group("player"):
		_exit_to_overworld("lanternwood")
