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

const HUDScene := preload("res://scene/hud.tscn")
const SlimeScene := preload("res://entities/enemies/slime.tscn")
const BigSlimeScene := preload("res://entities/enemies/big_slime.tscn")
const PickupScene := preload("res://entities/pickups/item_pickup.tscn")

## The map anchors the defence spawns at. Explicit, never random: the town is
## FIVE TERRACES now, and a random spawn lands as often as not on the wrong
## ledge, where a slime's 90px detect_range is aimed uselessly at a cliff face.
const DEFENCE_SPAWNS := ["slime_a", "slime_b", "slime_c"]

## The Ebb night's street register: a shade lighter than ebb.gd's cutscene
## indigo (snow bounces moonlight; the player still has to read the lanes)
## but deep enough that the additive window/lantern glow carries the town.
# Retuned UP 2026-07-28 with the Narshe palette. This is a CanvasModulate, i.e.
# a multiply over art that is now dark to begin with — at the old 0.38 the
# terraced street went unreadably black. The tint's job is still to say "night";
# the fire-lit windows and oil lanterns burn through it either way.
const NIGHT := Color(0.58, 0.6, 0.8)

## How many of the Ebb-night neighbours she has to ask before the library
## door opens onto the research beat (all three — the point of the gate is
## that the whole street tells her the same nothing).
const ASK_GATE := 3

## Ebb-night villagers already talked to, by name.
var _asked: Dictionary = {}

## The scene's own Theater (an instanced theater.tscn in lanternwood.tscn).
## TravelScene doesn't expose one — it has no cutscenes of its own — so this is
## declared here, the way every other scene with a Theater does it.
@onready var theater: Theater = $Theater

## Slimes still standing in the street. Counted DOWN rather than respawned:
## the meadow is an endless field and its refill loop is right for that, but a
## defence has to be winnable or the beat never ends.
var _alive := 0
var _hud: CanvasLayer = null


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
	if _defence_due():
		_start_defence()


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
	_villager("Bramble", SHEET_HARE, MapData.anchor_px(map, "villager_a"), [
		"My warming-wand died mid-stir! I held it to my ear like a fool. Nothing. Not even a hum.",
		"Every charm on my washing line, cold as river stones. All at ONCE. What takes everything at once?",
	])
	_villager("Alder", SHEET_BEAVER, MapData.anchor_px(map, "villager_b"), [
		"Sixty years my ember-charm kept the workshop warm. Tonight - pfft. A dead pebble.",
		"But look around you. The lanterns still burn. Honest oil, honest fire. Whatever left us didn't take THAT.",
	])
	_villager("Pip", SHEET_FOXKID, MapData.anchor_px(map, "villager_c"), [
		"Did you FEEL it?! The ground went rrrRUMBLE and my glow-marble just... stopped.",
		"Papa says the magic's only hiding. It is NOT hiding. I checked under the ice. TWICE.",
	])


# ---- THE DEFENCE OF LANTERNWOOD (Act 1, 2026-07-28) ---------------------------------
# The first real fight in the game, and it is Fuji's alone. She comes back out of
# her own library with a kit she built that afternoon and the street is not empty
# any more — curdled magic has pooled in the lanes the way it has everywhere
# else since the Ebb, except this is HER lane. Three slimes, no respawns, a level
# on the second kill, and a tonic left in the snow when it is over.
#
# Staged in the STREET rather than out on a road somewhere on purpose: a town
# turning dangerous is a stronger beat than a road being dangerous, it costs no
# new zone, and it puts the terraces to work — she fights UP them.

## Armed, the Ebb has happened, and nobody has cleared the lanes yet.
func _defence_due() -> bool:
	return Game.flag("fuji_kit_made") and not Game.flag("town_defended")


func _start_defence() -> void:
	# The HUD lives in meadow.tscn, not here, because this scene is a town nine
	# times out of ten. Instance it for the fight and let it go with the scene.
	# Its CanvasLayer defaults to layer 1, correctly under UI (10), Theater (15)
	# and the dialog box (20).
	_hud = HUDScene.instantiate()
	add_child(_hud)
	_hud.bind_party(Party.members)

	for i in DEFENCE_SPAWNS.size():
		var anchor: String = DEFENCE_SPAWNS[i]
		# One bruiser in the set so the drowse threshold has something to say:
		# a BigSlime needs five darts where a small one needs two.
		var scene: PackedScene = BigSlimeScene if i == 1 else SlimeScene
		var slime := scene.instantiate()
		slime.position = MapData.anchor_px(map, anchor)
		$World.add_child(slime)
		slime.died.connect(_on_defender_kill)
		_alive += 1

	Game.levelled.connect(_on_levelled)
	theater.hint("SOMETHING IS IN THE LANES.", 3.0)


## `died` fires mid-physics, from inside the slime's own signal handler — do the
## bookkeeping deferred so the beat's closing walk-through never runs while the
## physics server is still mid-step.
func _on_defender_kill() -> void:
	_alive -= 1
	if _alive <= 0:
		_finish_defence.call_deferred()


func _finish_defence() -> void:
	Game.set_flag("town_defended")
	# The reward is left in the snow rather than granted invisibly: a line
	# saying "you got a tonic" is a notification, an object on the ground is a
	# thing you walk over and pick up, and the second one is a game.
	var drop := PickupScene.instantiate()
	drop.item_id = Items.TONIC
	drop.count = 2
	drop.position = MapData.anchor_px(map, DEFENCE_SPAWNS[0])
	$World.add_child(drop)
	theater.hint("THE LANES ARE CLEAR.   SOMETHING GLINTS IN THE SNOW.", 3.4)


## Levelling is toasted through the Theater, not the HUD: every scene in the
## game has a Theater and only combat zones have a HUD, so a HUD toast would
## simply not exist in most of the places a level can now be earned.
func _on_levelled(member_id: StringName, level: int) -> void:
	theater.hint("%s REACHED LEVEL %d." % [String(member_id).to_upper(), level], 2.6)


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
