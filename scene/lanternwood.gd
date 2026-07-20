extends TravelScene

## Lanternwood, walkable at zone scale — Fuji's winter pine-forest hometown
## on the ice land (see TravelScene for the shared machinery). Every door is
## announce-only for now: the library, Fuji's family home and the three
## snow-banked cabins read their banner lines; the south gate lane exits to
## the overworld at Lanternwood's icon marker.
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


## Animated Tier-3 props (multi-frame sheets — the five cabins' window
## flicker + woodsmoke); cycled in _process the way alembic town cycles its
## fountain and chimneys.
var _anim_t := 0.0
var _animated: Array[Sprite2D] = []


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
		# the Ebb-night arrival: she steps out of her own library door —
		# landed a step south of the announce zone so the banner waits for
		# her to turn back to it
		Party.place(MapData.anchor_px(map, "library") + Vector2(0.0, 18.0))
	else:
		Party.place(MapData.anchor_px(map, "player_start"))


func _extra_setup() -> void:
	# cabins, conifers and lamps as y-sorted World entities; the spawner
	# front-loads them in child order so the party (spawned first by
	# TravelScene) still wins y-sort ties
	PropSpawner.build("res://assets/tilesets/lanternwood_props.txt", map, $World)
	for c in $World.get_children():
		if c is Sprite2D and (c as Sprite2D).hframes > 1:
			_animated.append(c)
	$ExitSouth.position = MapData.anchor_px(map, "exit_south")
	$ExitSouth.body_entered.connect(_on_exit_south)
	Party.clamp_cameras(MapData.size_px(map))
	# TravelScene gates its markers on `body != player` — re-aim it when the
	# lead changes hands mid-town.
	Party.leader_changed.connect(_on_leader_changed)
	if Game.flag("ebb_done"):
		_ebb_night_town()


func _process(delta: float) -> void:
	if _animated.is_empty():
		return
	_anim_t += delta
	var f := int(_anim_t / 0.18)
	for i in _animated.size():          # per-cabin phase offset = looser, less mechanical
		var s := _animated[i]
		s.frame = (f + i) % s.hframes


func _on_leader_changed(leader: PartyMember) -> void:
	player = leader


## Out the south gate lane, back to the overworld at the Lanternwood icon.
func _on_exit_south(body: Node) -> void:
	if body.is_in_group("player") and not _busy:
		_busy = true
		Game.overworld_spawn = "lanternwood"
		await fade_out()
		get_tree().change_scene_to_file("res://scene/overworld.tscn")


## The night the magic left, from the street: night falls over the snow
## (the fire-lit windows and oil lanterns burn straight through it) and the
## neighbors are out comparing notes. Interact-to-talk villagers — every
## line is about the sudden dead charms; nobody blames anybody (the Ebb has
## no author).
func _ebb_night_town() -> void:
	$Dim.color = NIGHT
	# she just stepped OUT of this door — the day-state "bolted against the
	# cold" banner would contradict the scene she left seconds ago
	$Locations/Library.locked_text = "THE LAMPS STILL BURN. THE KETTLE NEVER GOT ITS COFFEE."
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
	$World.add_child(npc)
	return npc
