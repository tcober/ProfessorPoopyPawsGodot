extends Node

## Autoloaded as `Game`: state that survives scene changes. `overworld_spawn` names
## the OverworldLocation id the travel player appears at when the overworld loads.
## `town_spawn` and `interior_spawn` are the zone analogs: the map anchor the next
## town/interior scene should spawn at. Both are READ AND CLEARED ("" = use the
## scene's default), so a stale value can never teleport a later entry.
## (`town_spawn`: "home" = below Basil's door in Alembic Town, "library" =
## Fuji's library door in Lanternwood (the Ebb-night arrival), "" = the
## town's south gate.)

var overworld_spawn: String = "town"
var town_spawn: String = ""
var interior_spawn: String = ""

## Story flags — set-once booleans that survive scene changes (no save system
## yet, so a run's story state lives and dies with the process). Prologue
## flags in use: prologue_festival_done, prologue_gate_open, prologue_done.
var flags: Dictionary = {}

## Which phase the thesis-day town scene (scene/town_thesis.gd) plays on entry
## ("plant" | "dash" | "steps"), read-and-cleared like the spawn routers.
## "" = the scene's default (plant).
var town_thesis_phase: String = ""

## Which beat the sunset bluff (scene/bluff.gd) plays on entry — the SAME
## headland hosts Prologue A's whirligig meet, the romance and both thesis-day
## calls, on purpose (the place their love began is where the bad news finds
## him). Read-and-cleared; "" = "romance". ("meet" | "romance" | "call1" | "call2")
var bluff_phase: String = ""

## Basil's gun loadout: what is poured into the gun right now, and the spare
## beakers in his coat. Lives HERE rather than on the body because Party.spawn()
## rebuilds every member from scratch on each scene load — anything held on the
## Player instance (ammo, HP) resets at every door. The compound you mixed has
## to outlive the walk to the meadow, so it lives with the rest of the
## run-scoped state. Cleared by reset_story() like everything else.
var loaded: Compound = null
var spares: Array[Compound] = []
var ammo_left: int = 0

## Which beat the Lanternwood library (scene/library.gd) plays on entry —
## Fuji's little reading room in her snow-town. "ebb" (the default for now)
## = the Ebb-night wand-coffee beat, her first appearance; Act 1's playable
## research phase will reuse the same room. Read-and-cleared.
var library_phase: String = ""


func flag(flag_name: String) -> bool:
	return flags.get(flag_name, false)


func set_flag(flag_name: String) -> void:
	flags[flag_name] = true


## Wipe story state back to a fresh boot. set_flag() is one-way (there is no
## unset), so the dev chapter selector calls this before staging a beat —
## otherwise a BACKWARDS jump carries a later chapter's flags into an earlier
## scene and mis-dresses it (entering town_fest with prologue_festival_done
## already set skips the fountain cutscene you came to look at).
func reset_story() -> void:
	flags.clear()
	# "town", not "" — the declared default. overworld.gd matches this against
	# location ids and silently strands the chibi at player_start on no match.
	overworld_spawn = "town"
	town_spawn = ""
	interior_spawn = ""
	town_thesis_phase = ""
	bluff_phase = ""
	library_phase = ""
	# Blank, not "a fresh green beaker": the Player fills these on _ready when
	# it finds them empty, so a backwards chapter jump can't carry a late-game
	# plasma decoction into a scene that predates the gun.
	loaded = null
	spares = []
	ammo_left = 0
