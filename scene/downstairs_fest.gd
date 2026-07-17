extends Node2D

## The great room, FESTIVAL MORNING — the second beat of the home-start
## opening (2026-07-12 pacing pass): Mom is at the hearth, and her good-morning
## is the front-door key (`prologue_saw_mom`). She STAYS home all festival
## (2026-07-15 — no duplicate festival Mom): after the three stings Basil
## doubles back through his own front door, and her blessing by the hearth
## is what opens the south gate (`prologue_gate_open`). Same map/tiles/props
## as the drained-era downstairs (the workshop corner has always been
## half-built — this family tinkers), brighter tint, fire and boiler alive.
## Out the front door lies the festival town at Basil's home door.

const MAP_PATH := "res://assets/maps/downstairs.txt"
const LAYOUT_PATH := "res://assets/tilesets/downstairs_layout.txt"
const PROPS_PATH := "res://assets/tilesets/downstairs_props.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const SHEET_MOM := preload("res://assets/npc_mom_gen.png")

const DIM_MORNING := Color(0.9, 0.85, 0.9)     # festival daylight indoors
const FIRE_OFFSET := Vector2(10.0, 20.0)       # see scene/downstairs.gd

var map: Dictionary
var player: Node2D
var _anim_t := 0.0
var _busy := false
var _mom: NPC
var _hint_tw: Tween

@onready var theater: Theater = $Theater


## Mom is home before the first leaving, and from the blessing double-back
## on she STAYS home — pies don't bake themselves, and vanishing right after
## her big scene read as a continuity hole.
func _mom_home() -> bool:
	return not Game.flag("prologue_left_home") or Game.flag("prologue_want_home")


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	PropSpawner.build(PROPS_PATH, map, $World)
	$Dim.color = DIM_MORNING
	var spawn := Game.interior_spawn
	Game.interior_spawn = ""
	if spawn.is_empty() or not map.anchors.has(spawn):
		spawn = "stair_arrival"
	player = Party.spawn($World, MapData.anchor_px(map, spawn))
	Party.clamp_cameras(MapData.view_size())
	$Fire.position = MapData.bbox_rect(map, "H").position + FIRE_OFFSET
	if _mom_home():
		_spawn_mom()
	$ExitDoor.position = MapData.anchor_px(map, "exit_door")
	$ExitDoor.body_entered.connect(_on_exit_door)
	if not Game.flag("prologue_saw_mom"):
		_show_hint("SAY GOOD MORNING TO MOM - E TO TALK")
	elif Game.flag("prologue_want_home") and not Game.flag("prologue_gate_open"):
		_show_hint("MOM'S BY THE HEARTH")


func _spawn_mom() -> void:
	_mom = NPCScene.instantiate()
	_mom.display_name = "Mom"
	_mom.sheet = SHEET_MOM
	_mom.frame_cols = 6
	if Game.flag("prologue_gate_open"):
		# post-blessing: she's still here, elbow-deep in pie
		_mom.lines = PackedStringArray([
			"Still here? The meadow won't sulk FOR you, sweetheart.",
			"Home before the lamps. And if that goose follows you, it is NOT staying for dinner.",
		])
	elif Game.flag("prologue_want_home"):
		# the double-back: he came home stung; her lines open the blessing
		_mom.lines = PackedStringArray([
			"Basil? Back already - and with a face like wet flour. Come here.",
		])
	else:
		_mom.lines = PackedStringArray([
			"There's my little tinkerer! Up with the birds for once.",
			"It's the Founding Festival, sweetheart. The WHOLE town's out - even the Academy has its window lit.",
			"Go see the ribbons. I'll be along when the pies are done. Scoot!",
		])
	# by the hearth, flour on her paws
	_mom.position = Vector2(4.0 * 16.0 + 8.0, 5.0 * 16.0 + 8.0)
	_mom.talked.connect(_on_mom_talked)
	$World.add_child(_mom)
	_mom.play_act()


func _on_mom_talked(_npc: NPC) -> void:
	if not Game.flag("prologue_saw_mom"):
		Game.set_flag("prologue_saw_mom")
		_show_hint("THE FESTIVAL AWAITS - OUT THE FRONT DOOR")
		return
	if Game.flag("prologue_want_home") and not Game.flag("prologue_gate_open"):
		_mom_blessing()


## Her blessing is the gate key: warmth first, permission second (ported
## from the festival-Mom beat when the blessing moved home, 2026-07-15).
func _mom_blessing() -> void:
	theater.lock_party()
	_mom.play_idle()
	await theater.say("Mom", "Oh, sweetheart. I heard about the square.")
	player.sprite.play("sad")
	await theater.say("Mom", "Listen to me. Sparks are common as dandelions.")
	_mom.play_emote()
	await theater.say("Mom", "You? You take things apart to see WHY. You put them back together BETTER. That is rarer than any ribbon trick.")
	await theater.say("Basil", "...You have to say that. You're my mom.")
	await theater.say("Mom", "And moms are always right. It's the law.")
	await theater.say("Mom", "Now scoot. Sulk somewhere sunny - the meadow's good for it. Out the south gate. Home before the lamps.")
	theater.close_dialog()
	player.sprite.play("idle_down")
	Game.set_flag("prologue_gate_open")
	theater.unlock_party()
	_show_hint("THE SOUTH GATE IS OPEN - THE MEADOW")


func _process(delta: float) -> void:
	# the room's little life (see scene/downstairs.gd)
	_anim_t += delta
	$Fire.frame = int(_anim_t / 0.16) % 3
	$World/Boiler.frame = int(_anim_t / 0.28) % 4


func _on_exit_door(body: Node) -> void:
	if not body.is_in_group("player") or _busy:
		return
	if not Game.flag("prologue_saw_mom"):
		_door_hint("Can't just LEAVE. Mom knows when I leave. Mom knows everything.")
		return
	# softlock guard: he came home FOR Mom — the door refuses until the
	# blessing opens the gate
	if Game.flag("prologue_want_home") and not Game.flag("prologue_gate_open"):
		_door_hint("No. I came home to talk to Mom. She's by the hearth.")
		return
	_busy = true
	Game.set_flag("prologue_left_home")
	Game.town_spawn = "home"
	get_tree().change_scene_to_file.call_deferred("res://scene/town_fest.tscn")


func _door_hint(line: String) -> void:
	_busy = true
	theater.lock_party()
	await theater.say("Basil", line)
	theater.close_dialog()
	theater.unlock_party()
	_busy = false


func _show_hint(text: String) -> void:
	var label: Label = $UI/Hint
	label.text = text
	label.modulate.a = 1.0
	# kill the previous fade or its interval expires mid-hold and yanks
	# THIS hint early — create_tween() never auto-kills prior tweens
	if _hint_tw:
		_hint_tw.kill()
	_hint_tw = create_tween()
	_hint_tw.tween_interval(2.4)
	_hint_tw.tween_property(label, "modulate:a", 0.0, 0.5)
