extends CanopyScene

## THE BOUGHS, DRAINED PRESENT — the canopy over Alembic Town, where the
## households actually live: four ring decks, three neighbours' doors that
## announce and one that opens (Basil's — the hermit is the one cat in town
## who stopped coming down). The Home marker travels to the lab downstairs;
## the ladders hand the climb to alembic_town below.

const MAP_PATH := "res://assets/maps/canopy.txt"
const LAYOUT_PATH := "res://assets/tilesets/canopy_layout.txt"


func _map_path() -> String:
	return MAP_PATH


func _layout_path() -> String:
	return LAYOUT_PATH


func _props_path() -> String:
	return "res://assets/tilesets/canopy_props.txt"


func _ground_scene() -> String:
	return "res://scene/alembic_town.tscn"


## Through Basil's own door, down to the lab.
func _on_travel(loc: OverworldLocation) -> void:
	if loc.id == "home":
		Game.interior_spawn = "front_door"
