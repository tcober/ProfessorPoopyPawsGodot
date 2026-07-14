extends Node

## Autoloaded as `Game`: state that survives scene changes. `overworld_spawn` names
## the OverworldLocation id the travel player appears at when the overworld loads.
## `town_spawn` and `interior_spawn` are the zone analogs: the map anchor the next
## town/interior scene should spawn at. Both are READ AND CLEARED ("" = use the
## scene's default), so a stale value can never teleport a later entry.
## (`town_spawn`: "home" = below Basil's door, "" = the town's south gate.)

var overworld_spawn: String = "town"
var town_spawn: String = ""
var interior_spawn: String = ""

## Story flags — set-once booleans that survive scene changes (no save system
## yet, so a run's story state lives and dies with the process). Prologue
## flags in use: prologue_festival_done, prologue_gate_open, prologue_done.
var flags: Dictionary = {}

## Which phase the thesis-day town scene (scene/town_thesis.gd) plays on entry
## ("plant" | "dash" | "call" | "fountain" | "leaving"), read-and-cleared like
## the spawn routers. "" = the scene's default (plant).
var town_thesis_phase: String = ""


func flag(flag_name: String) -> bool:
	return flags.get(flag_name, false)


func set_flag(flag_name: String) -> void:
	flags[flag_name] = true
