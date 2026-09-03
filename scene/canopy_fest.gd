extends CanopyScene

## THE BOUGHS, FESTIVAL ERA — Prologue A's canopy. Two beats live up here:
##
##  - BASIL'S FRONT DOOR (the blessing double-back): while he wants to go home
##    and the gate is shut, the door re-enters the fest downstairs where Mom
##    waits by the hearth; any other time it's a soft banner. Ported from the
##    pre-split town_fest verbatim — the zone hangs over the trunk face, the
##    arrival stays armed, and the announce-only Home location is freed the
##    moment the door goes live (two zones on one anchor is the softlock).
##
##  - THE GOOSE, TREED (A4): with the ribbon stolen and unrecovered, the thief
##    is round the back of tree 3's trunk on its ring deck — reachable by that
##    tree's rope ladder and nothing else, which is the whole beat: the one
##    cat in town who can't do magic gets the ribbon back by CLIMBING. The
##    theft itself plays on the ground (town_fest._goose_theft) and exits up
##    this tree's own ladder line.

const MAP_PATH := "res://assets/maps/canopy_fest.txt"
const LAYOUT_PATH := "res://assets/tilesets/canopy_fest_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const FX_SHEET := preload("res://assets/prologue_fx.png")
const SHEET_GOOSE := preload("res://assets/npc_goose_gen.png")

## the home-door re-entry stays disarmed while the from-downstairs arrival
## stands on it (the pre-split town_fest latch)
var _home_armed := true

@onready var theater: Theater = $Theater


func _map_path() -> String:
	return MAP_PATH


func _layout_path() -> String:
	return LAYOUT_PATH


func _props_path() -> String:
	return "res://assets/tilesets/canopy_fest_props.txt"


func _ground_scene() -> String:
	return "res://scene/town_fest.tscn"


func _extra_setup() -> void:
	super()
	_spawn_home_door()
	if Game.flag("prologue_want_home"):
		_free_home_location()
	_spawn_goose()


## Basil's own front door (the blessing double-back — see town_fest's history).
func _spawn_home_door() -> void:
	var door := Area2D.new()
	door.collision_layer = 0
	door.collision_mask = 2
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(24.0, 8.0)
	shape.shape = rect
	shape.position = Vector2(8.0, -8.0)
	door.add_child(shape)
	door.position = MapData.anchor_px(map, "home")
	add_child(door)
	door.body_exited.connect(func(body: Node2D) -> void:
		if body.is_in_group("player"):
			_home_armed = true)
	door.body_entered.connect(_on_home_door)


func _on_home_door(body: Node2D) -> void:
	if not body.is_in_group("player") or not _home_armed or _busy:
		return
	if Game.flag("prologue_want_home"):
		_busy = true
		Game.interior_spawn = "front_door"
		get_tree().change_scene_to_file.call_deferred("res://scene/downstairs_fest.tscn")
	else:
		_show_banner("HOME - MOM'S PIES NEED PEACE. THE FESTIVAL FIRST", BANNER_HOLD)


## Once he wants home, the code door above owns the anchor — the announce-only
## location sharing it must GO (the 2026-07-18 probe softlock).
func _free_home_location() -> void:
	var loc := $Locations.get_node_or_null("Home")
	if loc:
		loc.queue_free()


## The treed goose — only while the ribbon is stolen and unrecovered. Its
## dignified return to the square is town_fest's business.
func _spawn_goose() -> void:
	if not Game.flag("prologue_goose_hidden") or Game.flag("prologue_ribbon"):
		return
	var npc: NPC = NPCScene.instantiate()
	npc.display_name = "Goose"
	npc.sheet = SHEET_GOOSE
	npc.frame_cols = 6
	npc.lines = PackedStringArray([
		"HONK?! (It nearly jumps out of its feathers.)",
	])
	npc.position = MapData.anchor_px(map, "goose_hide")
	npc.talked.connect(_goose_startle)
	var carried := WorldFx.sheet_sprite(FX_SHEET, 0)
	carried.position = Vector2(7.0, -14.0)
	npc.add_child(carried)
	npc.set_meta("ribbon", carried)
	$World.add_child(npc)


## Found round the back of the trunk, thirty feet up somebody else's tree, the
## goose startles and then hands the ribbon over as if returning it was its own
## idea all along. Basil counts the rungs, because Basil counts things.
func _goose_startle(goose: NPC) -> void:
	if Game.flag("prologue_ribbon"):
		return
	theater.lock_party()
	await theater.hop(goose, 7.0)
	goose.play_act()                       # the honk pair
	await theater.say("Goose", "HONK!! ...honk. (...oh. It's you.)")
	await theater.say("Basil", "You. Feathery crime. Do you have ANY idea how many rungs that was?")
	await theater.say("Basil", "Forty-one. I counted. Hand it over.")
	if goose.has_meta("ribbon"):
		(goose.get_meta("ribbon") as Sprite2D).queue_free()
		goose.remove_meta("ribbon")
	await theater.say("Goose", "(It sets the ribbon down with tremendous dignity, as if returning it was its own idea.)")
	await theater.say("Goose", "(It was just playing around.)")
	theater.close_dialog()
	goose.play_idle()
	goose.lines = PackedStringArray([
		"HONK.",
		"(It seems to respect you now. Or it is planning something.)",
	])
	Game.set_flag("prologue_ribbon")
	theater.unlock_party()
	_show_banner("RETURN THE RIBBON TO SAGE - DOWN THE LADDER", BANNER_HOLD)
