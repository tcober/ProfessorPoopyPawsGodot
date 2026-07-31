extends TravelScene

## Alembic Town, walkable at zone scale — the Kakariko-style village the overworld's
## town icon opens into (see TravelScene for the shared machinery), and since
## 2026-07-30 a FOREST-FLOOR VILLAGE WITH FOUR GREAT TREES standing along its north
## edge. Each tree carries a round RING DECK near its crown, a door in its trunk and
## a rope ladder down to the floor; the ring is its own walkable stratum, joined to
## the ground by that ladder and by nothing else.
##
## THE CANOPY IS NOT A STREET. The previous build made it two continuous boardwalk
## storeys and the town rendered as horizontal stripes of plank and fascia — a lumber
## yard. What both references (FFXIV's Slitherbough, Endor) actually read from is the
## VOID between platforms, so the canopy is four islands and the town is the floor.
##
## Basil's open door travels down to the lab (downstairs); the shops, the cottages
## and the well announce in the banner; the south lane exits to the overworld. Two
## THE NORTH LANE GOES TO THE ACADEMY, which is its own scene (scene/academy.tscn)
## since 2026-07-30. The EAST mouth is authored in the grid and wired by nothing yet
## — Act 1 beat 5b — so it stays walled, because a road that runs to the map edge
## over cells collision never stamped is a walk into the void. The spawn is routed
## through Game.town_spawn (read-and-clear): "home" = Basil's door up his tree,
## "north" = back down the causeway from the Academy, "" = the south gate, where the
## overworld drops you.

const MAP_PATH := "res://assets/maps/town.txt"
const LAYOUT_PATH := "res://assets/tilesets/town_layout.txt"

@onready var theater: Theater = $Theater


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
		# Land ON the door marker — feet on the ring deck right under the arch
		# (the old tile-and-a-half drop read as appearing nowhere near the door).
		# _standing suppresses the marker until he steps off it once.
		Party.place(MapData.anchor_px(map, "home"))
		_standing["home"] = true
	elif spawn == "north":
		# back down the causeway from the Academy: land INSIDE the lane, a row
		# south of the mouth, so the walk-out zone is behind you and not under you
		Party.place(MapData.anchor_px(map, "exit_north") + Vector2(0.0, 32.0))
	else:
		Party.place(MapData.anchor_px(map, "player_start"))


func _extra_setup() -> void:
	# street furniture (well, lamps, stall, fountain) as y-sorted World entities;
	# the spawner front-loads them in child order so the party (spawned first by
	# TravelScene) still wins y-sort ties
	PropSpawner.build("res://assets/tilesets/town_props.txt", map, $World)
	_collect_animated()
	$ExitSouth.position = MapData.anchor_px(map, "exit_south")
	$ExitSouth.body_entered.connect(_on_exit_south)
	$ExitNorth.position = MapData.anchor_px(map, "exit_north")
	$ExitNorth.body_entered.connect(_on_exit_north)
	_wall_mouths()
	Party.clamp_cameras(MapData.size_px(map))
	# TravelScene gates its markers on `body != player` — re-aim it when the lead
	# changes hands mid-town.
	Party.leader_changed.connect(_on_leader_changed)


## Through Basil's own door, up his tree, down to the lab.
func _on_travel(loc: OverworldLocation) -> void:
	if loc.id == "home":
		Game.interior_spawn = "front_door"


## Out the south lane, back to the overworld at the town icon.
func _on_exit_south(body: Node) -> void:
	if body.is_in_group("player"):
		_exit_to_overworld("town")


## UP THE NORTH LANE TO THE ACADEMY (2026-07-30). The one exit in this town that
## does not go to the overworld: the college is its own scene now, one lane away,
## and this is the lane. The mouth is still walled past the trigger — the fade is
## several frames long and a body keeps walking through them.
func _on_exit_north(body: Node) -> void:
	if body.is_in_group("player"):
		await _leave_for("res://scene/academy.tscn")


## The same wall town_fest, town_thesis and lanternwood all put at their gate mouths
## (2026-07-29); TravelScene._wall is the shared body of it. It never bit at the south
## gate because the exit trigger happened to cover the whole 2-cell mouth — but the
## north and east mouths have no trigger at all yet, and the adult sandbox has no
## backstop and no refusal state, so without these the player walks off the collision
## grid into the void at two of the three exits.
func _wall_mouths() -> void:
	var size := MapData.size_px(map)
	_wall(Vector2($ExitSouth.position.x, size.y + 4.0), Vector2(64.0, 8.0))
	_wall(Vector2(MapData.anchor_px(map, "exit_north").x, -4.0), Vector2(64.0, 8.0))
	_wall(Vector2(size.x + 4.0, MapData.anchor_px(map, "exit_se").y),
			Vector2(8.0, 64.0))
