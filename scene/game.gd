extends Node

## Autoloaded as `Game`: state that survives scene changes. `overworld_spawn` names
## the OverworldLocation id the travel player appears at when the overworld loads.
## `town_spawn` and `interior_spawn` are the zone analogs: the map anchor the next
## town/interior scene should spawn at. Both are READ AND CLEARED ("" = use the
## scene's default), so a stale value can never teleport a later entry.
## (`town_spawn` is only read by the PARKED alembic_town scene — the icon's
## gate mouth goes straight to the downstairs for now.)

var overworld_spawn: String = "town"
var town_spawn: String = ""
var interior_spawn: String = ""
