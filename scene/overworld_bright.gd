extends "res://scene/overworld.gd"

## The PRE-EBB continent — the byte-locked twin of the overworld (same grid
## and anchors, bright era palette, the big mountain still wearing its snow
## summit instead of the crystal). Exists for the Ebb event scene's assets,
## screenshots, and future pre-Ebb story beats; nothing in the live flow
## routes here.


func _map_path() -> String:
	return "res://assets/maps/overworld_bright.txt"


func _layout_path() -> String:
	return "res://assets/tilesets/overworld_bright_layout.txt"
