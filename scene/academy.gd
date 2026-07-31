extends TravelScene

## THE ALEMBIC ACADEMY, walkable — the precinct north of Alembic Town, and its own
## scene since 2026-07-30 (see TravelScene for the shared machinery).
##
## IT USED TO BE A BUILDING IN THE TOWN GRID. Alembic's rebuild as a forest-floor
## village put four great trees along its north edge and had no room left for a
## college on a cliff, and the college was the more interesting thing to lose the
## compromise on: as one 14x9 landmark at the top of a town it could only ever be a
## facade you walked up to. Given its own 64x48 grid it can be what it is — a walled
## precinct you approach along an axis, gate by gate. Read assets/maps/academy.txt's
## header for the composition.
##
## Everything here is announce-only in the drained present, deliberately. The gates
## are barred, and Prologue B's naming plays inside the lecture hall (scene/hall.tscn),
## which is entered from `town_fest`'s own School marker and never through here — so
## nothing in this scene can break a chapter that has shipped.
##
## THE SOUTH LANE IS THE ONLY WAY IN OR OUT, and it runs back to Alembic Town's north
## mouth. Game.town_spawn = "north" is what the town reads to put the player back in
## its own lane rather than at the south gate.

const MAP_PATH := "res://assets/maps/academy.txt"
const LAYOUT_PATH := "res://assets/tilesets/academy_layout.txt"

@onready var theater: Theater = $Theater


func _player_node() -> Node2D:
	return Party.spawn($World, Vector2.ZERO)   # placed for real in _place_player


func _map_path() -> String:
	return MAP_PATH


func _layout_path() -> String:
	return LAYOUT_PATH


func _place_player() -> void:
	Party.place(MapData.anchor_px(map, "player_start"))


func _extra_setup() -> void:
	PropSpawner.build("res://assets/tilesets/academy_props.txt", map, $World)
	_collect_animated()
	$ExitSouth.position = MapData.anchor_px(map, "exit_south")
	$ExitSouth.body_entered.connect(_on_exit_south)
	_wall_mouth()
	Party.clamp_cameras(MapData.size_px(map))
	Party.leader_changed.connect(_on_leader_changed)


## Back down the causeway to Alembic Town, arriving in ITS north lane.
##
## NOT _exit_to_overworld: this precinct's neighbour is the town, not the map, so it
## goes through TravelScene._leave_for and sets the town's OWN router instead.
##
## `_busy` is checked here as well as inside _leave_for for the same reason
## _exit_to_overworld checks it: the router write below must not happen on a refused
## exit. A marker banner also holds `_busy`, and a stale "north" would misroute the
## NEXT arrival in Alembic Town.
func _on_exit_south(body: Node) -> void:
	if not body.is_in_group("player") or _busy:
		return
	Game.town_spawn = "north"
	await _leave_for("res://scene/alembic_town.tscn")


## The same wall every gate mouth in this project gets (2026-07-29) —
## TravelScene._wall is the shared body of it, and its doc is why.
func _wall_mouth() -> void:
	_wall(Vector2($ExitSouth.position.x, MapData.size_px(map).y + 4.0),
			Vector2(64.0, 8.0))
