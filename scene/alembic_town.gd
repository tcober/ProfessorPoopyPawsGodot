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

const NPCScene := preload("res://entities/npcs/npc.tscn")
const SHEET_BADGER := preload("res://assets/npc_badger_gen.png")
const SHEET_MOUSE := preload("res://assets/npc_mouse_gen.png")
const SHEET_SHEEP := preload("res://assets/npc_sheep_gen.png")
const SHEET_STORK := preload("res://assets/npc_stork_gen.png")
const SHEET_FOXKID := preload("res://assets/npc_foxkid_gen.png")

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
		# The zone itself hangs OVER the trunk face now (a press UP into the
		# door, never a stroll across the deck's through-row), so the latch
		# only matters while an exit-hold keeps the body pressed against it;
		# TravelScene resyncs it from the real overlap when the entry lock lifts.
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
	_townsfolk()
	$ExitSouth.position = MapData.anchor_px(map, "exit_south")
	_wire_exit($ExitSouth, _on_exit_south)
	$ExitNorth.position = MapData.anchor_px(map, "exit_north")
	_wire_exit($ExitNorth, _on_exit_north)
	_wall_mouths()
	Party.clamp_cameras(MapData.size_px(map))
	# TravelScene gates its markers on `body != player` — re-aim it when the lead
	# changes hands mid-town.
	Party.leader_changed.connect(_on_leader_changed)


## THE TOWN AFTER THE EBB — five people standing outside five shut doors.
##
## Every building in this town was already written as REFUSED: the grindstone
## sits cold, the tonics glint on a dark sill, no beds tonight. That was the
## whole of it — an 80x56 clearing with a shop name on each door and nobody in
## it, which reads as a set rather than as a place people gave up on. A drained
## town is not an EMPTY town. It is a town where everyone is outside, because
## there is nothing to go in for.
##
## They are the layer DESIGN.md beat 4 calls "the generic townsfolk who exist to
## fail her first" — so this is deliberately NOT that beat and sets no flag. The
## two who actually answer Fuji are his sister and his mother, and both need
## sheets that do not exist yet (`npc_sage_gen` is the KID, `npc_mom_gen` the
## kid-era mother). What these five carry is the register and the setup:
##
##  - the innkeeper says he remembers every face that ever took a room — which is
##    what makes him the one worth asking later — WITHOUT the answer. The "went
##    east, past the meadow" line is beat 4's payoff and stays unspent.
##  - the mouse at THE CRACKED FLASK plants Sage's own secret before she appears:
##    half those bottles were charm-work and half were just boiling things
##    properly, and nobody remembers which half. That is the thesis, in a queue.
##  - the kid has the cruel name and NOT the man. "Professor Poopy Paws" survives
##    here as a bogeyman with a machine that eats the magic out of things — the
##    theme's cleanest statement, told as gossip by somebody who has no idea it
##    is about a person, to a player who may well BE him.
##
## The stork is the one piece of standing canon reused: the door already says the
## old stork retired years ago and nobody came after. He is still here. He
## retired because a charm could close a wound faster than he could, and the
## charms have stopped.
func _townsfolk() -> void:
	# Roam boxes are authored against the grid and verified clear — every cell
	# walkable, none of them a walk-behind crown, all >= 2 cells wide (the
	# one-cell-lane rule: a villager is a solid StaticBody2D and a body in a
	# one-cell lane is a wall). Each box also EXCLUDES its own shop's door
	# approach, so no wanderer can ever park itself on a door.
	_folk("Hob", SHEET_BADGER, 10, "folk_smith", [
		"Grindstone turns fine. Wheel's fine, arm's fine. It's the EDGE that won't take any more.",
		"Sharpened the same blade Tuesday and Wednesday. Something's gone out of the steel, and it isn't rust.",
	], Rect2i(14, 32, 5, 3))
	_folk("A Waiting Customer", SHEET_MOUSE, 8, "folk_flask", [
		"She's not opening. I've knocked. I've waited. I've knocked again in a way I thought was polite.",
		"Half those bottles were charm-work and half were just boiling things properly. Nobody left in this town remembers which half.",
	], Rect2i(43, 32, 5, 3))
	_folk("The Innkeeper", SHEET_SHEEP, 8, "folk_inn", [
		"Hearth's banked. Beds are aired. Nobody's come up that road in a season.",
		"I remember every face that ever took a room off me. It's the only skill I've got left and there's nobody to spend it on.",
	], Rect2i(47, 51, 5, 3))
	_folk("The Old Stork", SHEET_STORK, 6, "folk_doctor", [
		"I shut that door when a charm could close a wound in the time it takes to say so. Made me redundant, I thought. I was relieved.",
		"...I have been standing out here three weeks working out whether I still remember how to do it the slow way.",
	], Rect2i(62, 43, 5, 3))
	_folk("A Kid", SHEET_FOXKID, 10, "folk_kid", [
		"Mum says if I'm not in by dark, Professor Poopy Paws'll get me.",
		"He's not REAL. He's a story. He's got a machine that eats the magic out of things, and that's where it all went.",
	], Rect2i(8, 43, 5, 3))


## One townsperson on a map anchor, with an authored roam box. `cols` is the
## sheet's real column count: 6 and 8 column sheets are legacy but legal — npc.gd
## builds only the clips whose columns exist, so the stork simply never turns and
## the mouse has a back but no profile. They wander only if their sheet can walk
## (rows 1-3), which npc.gd gates on the PNG's HEIGHT, so a 48px sheet stands
## still and stays correct rather than sliding.
func _folk(nm: String, sheet: Texture2D, cols: int, anchor: String,
		npc_lines: PackedStringArray, roam: Rect2i) -> NPC:
	var npc: NPC = NPCScene.instantiate()
	npc.display_name = nm
	npc.sheet = sheet
	npc.frame_cols = cols
	npc.position = MapData.anchor_px(map, anchor)
	npc.lines = npc_lines
	npc.wander_cells = roam
	npc.wander = sheet.get_height() >= 4 * 48
	npc.bind_map(map)
	$World.add_child(npc)
	return npc


## Through Basil's own door, up his tree, down to the lab.
func _on_travel(loc: OverworldLocation) -> void:
	if loc.id == "home":
		Game.interior_spawn = "front_door"


## Out the south lane, back to the overworld at the town icon.
func _on_exit_south(body: Node) -> void:
	if _exit_ok(body):
		_exit_to_overworld("town")


## UP THE NORTH LANE TO THE ACADEMY (2026-07-30). The one exit in this town that
## does not go to the overworld: the college is its own scene now, one lane away,
## and this is the lane. The mouth is still walled past the trigger — the fade is
## several frames long and a body keeps walking through them.
func _on_exit_north(body: Node) -> void:
	if not _exit_ok(body):
		return
	_busy = true
	await fade_out()
	get_tree().change_scene_to_file("res://scene/academy.tscn")


## The same wall town_fest, town_thesis and lanternwood all put at their gate mouths
## (2026-07-29): a mouth road runs to the map's last row and the collision layer only
## stamps grid cells, so past the mouth there is nothing. It never bit at the south
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
