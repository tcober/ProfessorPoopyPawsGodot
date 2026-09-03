extends TravelScene

## Alembic Town, THE FEVER — Prologue A0 (docs/DESIGN.md Story). The
## festival town's own grid and paint, before the festival: one grey day,
## two flag-driven phases dressed by the Tint (the tint law — one painting,
## never a repaint):
##   out   (grey morning, not prologue_herbal_found) — the walk up the
##          north lane to the Academy. Two neighbours out, each about
##          their own small warm magic, neither about his mother.
##   back  (dusk, prologue_herbal_found) — the same lanes, and nothing
##          happens. Every window has a charm burning in it. No lines.
## The south and east mouths are walled (the fever day never leaves town);
## the School marker travels to the reading room, the home door back into
## the fever downstairs.

const MAP_PATH := "res://assets/maps/town_fest.txt"
const LAYOUT_PATH := "res://assets/tilesets/town_fest_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const SHEET_SHEEP := preload("res://assets/npc_sheep_gen.png")
const SHEET_OWL := preload("res://assets/npc_owl_gen.png")

const TINT_GREY := Color(0.68, 0.72, 0.84)
const TINT_DUSK := Color(0.74, 0.56, 0.66)

var _back := false

@onready var theater: Theater = $Theater
@onready var tint: CanvasModulate = $Tint


func _player_node() -> Node2D:
	return Party.spawn($World, Vector2.ZERO)


func _map_path() -> String:
	return MAP_PATH


func _layout_path() -> String:
	return LAYOUT_PATH


func _place_player() -> void:
	var spawn := Game.town_spawn
	Game.town_spawn = ""
	if not _place_on_rungs(spawn):
		if spawn == "school":
			# back out of the Academy's reading room, into the lane's mouth
			Party.place(MapData.anchor_px(map, "school") + Vector2(0.0, 24.0))
		else:
			# a direct load (dev menu / probe): the foot of Basil's own tree —
			# the front door and its "home" arrival live in canopy_fever now
			Party.place(MapData.anchor_px(map, "foot1"))
	_back = Game.flag("prologue_herbal_found")


func _extra_setup() -> void:
	PropSpawner.build("res://assets/tilesets/town_fest_props.txt", map, $World)
	_collect_animated()
	_wall_mouths()
	_wire_ladder_tops("res://scene/canopy_fever.tscn")
	Party.clamp_cameras(MapData.size_px(map))
	tint.color = TINT_DUSK if _back else TINT_GREY
	# the fest glow is the town's living charm-light; at dusk it is every
	# window in the town burning — which is the whole of the "back" phase
	$Glow.modulate.a = 1.0 if _back else 0.45
	var school: OverworldLocation = $Locations/School
	school.target_scene = "res://scene/academy_library.tscn"
	if not _back:
		_spawn_neighbours()
		_show_banner("THE ACADEMY - UP THE NORTH LANE", BANNER_HOLD)


## Two neighbours on the grey morning, at the foot of the north lane — ON
## the route from Basil's ladder to the Academy, because an ambient talkable
## the path never passes does not exist. Each is about their own small warm
## magic; neither mentions his mother, which is how a town this small says
## it knows.
func _spawn_neighbours() -> void:
	_villager("Mrs. Pell", SHEET_SHEEP, MapData.anchor_px(map, "fever_a"), [
		"Warming-charm in every loaf, dear. Take one up with you - warm to the bottom of the basket, all the way home.",
		"Off up the lane? Mind the wet.",
	])
	_villager("Lamplighter", SHEET_OWL, MapData.anchor_px(map, "fever_b"), [
		"Grey enough to want the lamps by NOON, this. Not that lighting them is any work. Wiggle, spark, done.",
		"Sixty lamps, son, and not one match in my coat. Never needed one in my life.",
	])


func _villager(nm: String, sheet: Texture2D, pos: Vector2,
		npc_lines: PackedStringArray) -> NPC:
	var npc: NPC = NPCScene.instantiate()
	npc.display_name = nm
	npc.sheet = sheet
	npc.frame_cols = 6
	npc.position = pos
	npc.lines = npc_lines
	$World.add_child(npc)
	return npc


## All three mouths are walled — the fever day never leaves town. The south
## gate gets an announce marker as well (a silent wall on the one tempting
## mouth reads as broken; a refusal out loud does not).
func _wall_mouths() -> void:
	var size := MapData.size_px(map)
	_wall(Vector2(MapData.anchor_px(map, "exit_south").x, size.y + 4.0),
			Vector2(64.0, 8.0))
	_wall(Vector2(MapData.anchor_px(map, "exit_north").x, -4.0), Vector2(64.0, 8.0))
	_wall(Vector2(size.x + 4.0, MapData.anchor_px(map, "exit_se").y),
			Vector2(8.0, 64.0))


## (Basil's front door moved up the tree with the 2026-08-23 split — it lives
## in canopy_fever.gd now, same latch, same trunk-face zone.)
