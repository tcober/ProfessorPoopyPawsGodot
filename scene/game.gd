extends Node

## Autoloaded as `Game`: state that survives scene changes. `overworld_spawn` names
## the OverworldLocation id the travel player appears at when the overworld loads.
## `interior_spawn` is the interior analog: the map anchor the next interior scene
## should spawn at. Interiors READ IT AND CLEAR IT ("" = use the scene's default),
## so a stale value can never teleport a later entry.

var overworld_spawn: String = "home"
var interior_spawn: String = ""
