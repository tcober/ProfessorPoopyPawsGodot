extends Node2D

## THE WORKSHOP INTERLUDE — the evening the Academy letter came (2026-07-16,
## the Kitty thread made playable; docs/DESIGN.md Story, between Prologue A
## and B). Three summers after the whirligig, college-age Kitty has taken
## over the workshop corner of Basil's great room; he bursts in with the
## acceptance letter and she won't hear it until he fetches her three parts
## — gear, spring, crank, the whirligig recipe on purpose — because the
## build she's finishing IS his watch. The gift plays on-screen (the watch
## fx blinks on his wrist for the first time), she plants the front-row
## promise, and the outro cards hand to thesis day. Same map/tiles/props as
## the drained-era downstairs, tinted to lamplit evening (the tint law).
## Semi-playable: walk/interact only, the exit door refuses until the gift.

const MAP_PATH := "res://assets/maps/downstairs.txt"
const LAYOUT_PATH := "res://assets/tilesets/downstairs_layout.txt"
const PROPS_PATH := "res://assets/tilesets/downstairs_props.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const FX_SHEET := preload("res://assets/prologue_fx.png")
const SHEET_KITTY := preload("res://assets/npc_kitty_adult_gen.png")

const DIM_EVENING := Color(0.88, 0.76, 0.74)   # honey-rose lamplight
const FIRE_OFFSET := Vector2(10.0, 20.0)       # see scene/downstairs.gd

## fx strip cells (always sliced via WorldFx.sheet_sprite — two-row sheet)
const FX_SPARK0 := 2
const FX_SPARK1 := 3
const FX_WATCH := 16

## The watch wants the whirligig's parts — Kitty keeps the recipes that
## work. Positions are named anchors in maps/downstairs.txt (the meadow's
## convention): the map is SHARED with the drained-era downstairs, so a
## furniture edit there must carry these spots — never hardcode pixels a
## txt edit can strand (the 2026-07-17 review).
const PARTS := {
	"gear": {"anchor": "part_gear", "cell": 4,
		"line": "THE GEAR - BY THE BOILER, WHERE GEARS FEEL SAFE"},
	"spring": {"anchor": "part_spring", "cell": 5,
		"line": "THE SPRING - IT SPROINGED INTO THE KITCHEN AGAIN"},
	"crank": {"anchor": "part_crank", "cell": 6,
		"line": "THE CRANK - UNDER THE TABLE. CLASSIC CRANK"},
}

var map: Dictionary
var player: Node2D
var _anim_t := 0.0
var _busy := false
var _busy_scene := false
var _kitty: NPC
var _hint_tw: Tween

@onready var theater: Theater = $Theater


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	PropSpawner.build(PROPS_PATH, map, $World)
	$Dim.color = DIM_EVENING
	player = Party.spawn($World, MapData.anchor_px(map, "front_door"))
	Party.clamp_cameras(MapData.view_size())
	$Fire.position = MapData.bbox_rect(map, "H").position + FIRE_OFFSET
	_spawn_kitty()
	$ExitDoor.position = MapData.anchor_px(map, "exit_door")
	$ExitDoor.body_entered.connect(_on_exit_door)
	_intro()


func _spawn_kitty() -> void:
	_kitty = NPCScene.instantiate()
	_kitty.display_name = "Kitty"
	_kitty.sheet = SHEET_KITTY
	_kitty.frame_cols = 6
	# behind the KITCHEN TABLE (the counter-walk T row), not the workbench:
	# the lab corner's E row is a one-cell alley boxed by armchair/boiler/
	# bench — a solid NPC in it wedges anyone who follows (the 2026-07-16
	# room-to-move lesson). The table sits in open floor with three clear
	# sides; the kitty_pos anchor lands her feet on the walkable T row and
	# the y-sorted tabletop hides her hem — the family table. Again.
	_kitty.position = MapData.anchor_px(map, "kitty_pos")
	_kitty.talked.connect(_on_kitty_talked)
	$World.add_child(_kitty)
	_kitty.play_act()                 # hunched over the build from frame one


func _intro() -> void:
	theater.lock_party()
	theater.face(player, Vector2.UP)
	await theater.wait(0.7)
	await theater.say("Basil", "KITTY. Kitty. It came. The seal and the ribbon and everything - IT CAME.")
	await theater.say("Kitty", "Letter or no letter, this hinge won't set itself. Paws first, news second.")
	await theater.say("Kitty", "Gear. Spring. Crank. They're SOMEWHERE in this room. Fetch, and you can read me anything you like.")
	await theater.say("Basil", "You do know this is the biggest news of my entire life.")
	await theater.say("Kitty", "Second biggest. You'll see. GO.")
	theater.close_dialog()
	_kitty.lines = PackedStringArray([
		"Gear, spring, crank. A room this size can only hide them so well.",
		"The hinge and I are having a DISAGREEMENT. Fetch faster.",
	])
	# parts spawn BEFORE the unlock: the unlock is the phase's pollable
	# end-state (the probe idiom), so everything it implies must exist first
	for part: String in PARTS:
		_spawn_part(part)
	theater.unlock_party()
	_show_hint("GEAR - SPRING - CRANK. SOME RECIPES DON'T CHANGE.")


## The meadow quest's pickup idiom: root Area2D for collision, decal icon +
## floating sparkle depth-sorted in $World.
func _spawn_part(part: String) -> void:
	var cfg: Dictionary = PARTS[part]
	var area := Area2D.new()
	area.collision_layer = 0
	area.collision_mask = 2
	area.position = MapData.anchor_px(map, cfg["anchor"])
	var shape := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 10.0
	shape.shape = circle
	area.add_child(shape)
	var icon := WorldFx.decal($World, FX_SHEET, cfg["cell"], area.position)
	area.set_meta("icon", icon)
	var spark := WorldFx.airborne($World, FX_SHEET, FX_SPARK0,
			area.position + Vector2(6.0, 0.0), 8.0)
	area.set_meta("spark", spark)
	var tw := spark.create_tween().set_loops()
	tw.tween_callback(func() -> void: spark.frame = FX_SPARK1).set_delay(0.4)
	tw.tween_callback(func() -> void: spark.frame = FX_SPARK0).set_delay(0.4)
	add_child(area)
	area.body_entered.connect(_on_part_touched.bind(part, area))


func _on_part_touched(body: Node2D, part: String, area: Area2D) -> void:
	if not body.is_in_group("player") or Game.flag("prologue_wpart_" + part):
		return
	Game.set_flag("prologue_wpart_" + part)
	(area.get_meta("icon") as Node).queue_free()
	(area.get_meta("spark") as Node).queue_free()
	area.queue_free()
	if _all_parts_found():
		_kitty.lines = PackedStringArray([
			"Paw them over. CAREFULLY. Springs hold grudges.",
		])
		_show_hint("BRING THEM TO KITTY")
	else:
		_show_hint(PARTS[part]["line"])


func _all_parts_found() -> bool:
	for part: String in PARTS:
		if not Game.flag("prologue_wpart_" + part):
			return false
	return true


## The talked handler AWAITS the beat it starts (the Sage ribbon lesson —
## one advance press must never resume two pending say() awaits).
func _on_kitty_talked(_npc: NPC) -> void:
	if _all_parts_found() and not _busy_scene \
			and not Game.flag("prologue_watch_given"):
		await _gift()


func _gift() -> void:
	_busy_scene = true
	theater.lock_party()
	_kitty.play_act()
	await theater.say("Kitty", "Gear... spring... crank. And the case I finished LAST week...")
	theater.close_dialog()
	# assembly sparkle over the tabletop while she snaps it together
	var spark := WorldFx.airborne($World, FX_SHEET, FX_SPARK0,
			_kitty.position + Vector2(8.0, 6.0), 26.0)
	for i in 4:
		await theater.wait(0.22)
		spark.frame = FX_SPARK1 if spark.frame == FX_SPARK0 else FX_SPARK0
	spark.queue_free()
	_kitty.play_idle()
	await theater.say("Kitty", "Done. Paw.")
	await theater.say("Basil", "What? Why?")
	await theater.say("Kitty", "PAW.")
	# the watch blinks awake on his wrist for the FIRST time — the same fx
	# and the same gesture as both of thesis day's calls
	var watch := WorldFx.airborne($World, FX_SHEET, 0,
			player.global_position + Vector2(10.0, 4.0), 36.0)
	watch.frame = FX_WATCH
	await theater.wait(0.8)
	await theater.say("Kitty", "It's a watch. I made it. You're an Academy cat now - and Academy cats cannot be late.")
	await theater.say("Basil", "You BUILT this? It ticks. Kitty, the escapement alone - how long did -")
	await theater.say("Kitty", "Three summers. Every time you ran late I added a jewel to spite you. It keeps PERFECT time.")
	_kitty.play_emote()
	await theater.say("Kitty", "WHOO! Youngest cat ever admitted on CRAFT. Wiggle-fingers: zero. Paws: ONE.")
	player.sprite.play("idle_down")
	await theater.say("Basil", "...I'm never taking it off.")
	await theater.say("Kitty", "I know. And someday, when you're the one up FRONT in one of those big halls - because you WILL be -")
	await theater.say("Kitty", "- I'll be in the front row. Whooping.")
	await theater.say("Basil", "Please don't whoop.")
	await theater.say("Kitty", "Whooping is a promise, professor. Now go tell your mom. Go on - you'll be brilliant.")
	theater.close_dialog()
	watch.queue_free()
	Game.set_flag("prologue_watch_given")
	await theater.black(1.2)
	await theater.card("He was still late, most days.  He never took the watch off.", 2.6)
	await theater.card("She kissed him at the Academy gate on his first day.", 2.4)
	await theater.card("YEARS LATER.", 2.0)
	Game.town_thesis_phase = "plant"
	get_tree().change_scene_to_file("res://scene/town_thesis.tscn")


func _process(delta: float) -> void:
	# the room's little life (see scene/downstairs.gd)
	_anim_t += delta
	$Fire.frame = int(_anim_t / 0.16) % 3
	$World/Boiler.frame = int(_anim_t / 0.28) % 4


func _on_exit_door(body: Node) -> void:
	if not body.is_in_group("player") or _busy or _busy_scene:
		return
	# the refusal tracks the objective: hunting parts vs. delivering them
	if _all_parts_found():
		_door_hint("Not now. She has the parts. Whatever she's finishing over there, I want to SEE it.")
	else:
		_door_hint("Leave? She'd never let me hear the end of it. The parts are IN here somewhere.")


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
