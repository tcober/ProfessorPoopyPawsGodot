extends TravelScene

## Lanternwood, walkable at zone scale — Fuji's winter pine-forest hometown
## on the ice land (see TravelScene for the shared machinery). THE LIBRARY
## DOOR TRAVELS (2026-07-25): the hall on the north side of the square is
## where Fuji works, and its arch opens into scene/library.tscn. Every other
## door — Fuji's family home, the three snow-banked cabins — is still
## announce-only; the south gate lane exits to the overworld at Lanternwood's
## icon marker.
##
## Once the Ebb has happened (`ebb_done` — the story's current resting
## state: solo Fuji, stepped out of her library into the SAME night), the
## town dresses for it: a deep night tint the fire-lit windows and oil
## lanterns burn through — Lanternwood earns its name, honest flame owes
## magic nothing — and the neighbors are out in the snow comparing charms
## that all died at once.

const MAP_PATH := "res://assets/maps/lanternwood.txt"
const LAYOUT_PATH := "res://assets/tilesets/lanternwood_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const SHEET_HARE := preload("res://assets/npc_hare_gen.png")
const SHEET_BEAVER := preload("res://assets/npc_beaver_gen.png")
const SHEET_FOXKID := preload("res://assets/npc_foxkid_gen.png")

## The Ebb night's street register: a shade lighter than ebb.gd's cutscene
## indigo (snow bounces moonlight; the player still has to read the lanes)
## but deep enough that the additive window/lantern glow carries the town.
const NIGHT := Color(0.38, 0.4, 0.66)

## How many of the Ebb-night neighbours she has to ask before the library
## door opens onto the research beat (all three — the point of the gate is
## that the whole street tells her the same nothing).
const ASK_GATE := 3

## Ebb-night villagers already talked to, by name.
var _asked: Dictionary = {}


func _player_node() -> Node2D:
	return Party.spawn($World, Vector2.ZERO)   # placed for real in _place_player


func _map_path() -> String:
	return MAP_PATH


func _layout_path() -> String:
	return LAYOUT_PATH


func _place_player() -> void:
	var spawn := Game.town_spawn
	Game.town_spawn = ""
	if spawn == "library":
		# Land ON the door marker — feet on the lane right under the arch
		# (the door-mouth arrival doctrine). Now that the marker TRAVELS,
		# _standing is not cosmetic: without it, the body standing in the
		# zone at the end of the entry lock fires it and walks straight back
		# into the room it just left, forever.
		Party.place(MapData.anchor_px(map, "library"))
		_standing["library"] = true
	else:
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
	if Game.flag("ebb_done"):
		_ebb_night_town()


## Out the south gate lane, back to the overworld at the Lanternwood icon.
func _on_exit_south(body: Node) -> void:
	if body.is_in_group("player"):
		_exit_to_overworld("lanternwood")


## Through the library arch. The phase is ALWAYS named explicitly — "" is the
## boot default library.gd reads as the Ebb-night cutscene, and walking in
## the front door must never replay it. The research beat opens once the
## street has told her everything it can (every neighbour asked) and closes
## once she has the thesis.
func _on_travel(loc: OverworldLocation) -> void:
	if loc.id != "library":
		return
	Game.library_phase = "research" if Game.flag("asked_around") \
			and not Game.flag("thesis_found") else "open"


## The night the magic left, from the street: night falls over the snow
## (the fire-lit windows and oil lanterns burn straight through it) and the
## neighbors are out comparing notes. Interact-to-talk villagers — every
## line is about the sudden dead charms; nobody blames anybody (the Ebb has
## no author).
func _ebb_night_town() -> void:
	$Dim.color = NIGHT
	if Game.flag("thesis_found"):
		return                           # weeks on; the street went back in
	_villager("Bramble", SHEET_HARE, Vector2(440.0, 216.0), [
		"My warming-wand died mid-stir! I held it to my ear like a fool. Nothing. Not even a hum.",
		"Every charm on my washing line, cold as river stones. All at ONCE. What takes everything at once?",
	])
	_villager("Alder", SHEET_BEAVER, Vector2(264.0, 216.0), [
		"Sixty years my ember-charm kept the workshop warm. Tonight - pfft. A dead pebble.",
		"But look around you. The lanterns still burn. Honest oil, honest fire. Whatever left us didn't take THAT.",
	])
	_villager("Pip", SHEET_FOXKID, Vector2(360.0, 232.0), [
		"Did you FEEL it?! The ground went rrrRUMBLE and my glow-marble just... stopped.",
		"Papa says the magic's only hiding. It is NOT hiding. I checked under the ice. TWICE.",
	])


func _villager(nm: String, sheet: Texture2D, pos: Vector2, npc_lines: PackedStringArray) -> NPC:
	var npc: NPC = NPCScene.instantiate()
	npc.display_name = nm
	npc.sheet = sheet
	npc.frame_cols = 6
	npc.position = pos
	npc.lines = npc_lines
	npc.talked.connect(_on_villager_talked)
	$World.add_child(npc)
	return npc


## The street's own wander gate: once she has asked every neighbour and been
## told the same nothing three times over, the only place left to look is her
## own shelves — and the library door starts opening onto the research beat.
func _on_villager_talked(npc: NPC) -> void:
	_asked[npc.display_name] = true
	if _asked.size() >= ASK_GATE:
		Game.set_flag("asked_around")
