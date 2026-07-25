extends Node2D

## The 8:57 wake-up — Prologue B (docs/DESIGN.md Story). Basil oversleeps on
## thesis morning; Dr. Feathers the bird will not shut up; the clock says 8:57
## and the lecture is at nine. Reuses the loft bedroom tileset/map/props (it
## IS his room) with a dawn-dim CanvasModulate that brightens as he bolts up.
## Basil spawns asleep on the bed (only his head shows over the y-sorted quilt
## cover — the bed_parts read); after the panic he hops out and the door cuts
## straight to the dash phase in town.

const MAP_PATH := "res://assets/maps/house.txt"
const LAYOUT_PATH := "res://assets/tilesets/house_layout.txt"
const PROPS_PATH := "res://assets/tilesets/house_props.txt"
const FX_SHEET := preload("res://assets/prologue_fx.png")

const FX_BIRD0 := 12
const FX_BIRD1 := 13
const FX_ZZZ := 15

const DIM_SLEEP := Color(0.55, 0.5, 0.72)      # pre-dawn gloom
const DIM_AWAKE := Color(0.86, 0.83, 0.96)     # daylight floods in

var map: Dictionary
var player: Node2D
var _bird: Sprite2D
var _hint_tw: Tween

@onready var theater: Theater = $Theater
@onready var dim: CanvasModulate = $Dim


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	PropSpawner.build(PROPS_PATH, map, $World)
	dim.color = DIM_SLEEP
	# spawn on the bed's walkable middle row — the quilt cover (a y-sorted
	# World prop) sorts OVER him, so only his head shows on the pillow.
	# The 4px north nudge keeps his sort-Y strictly under the cover's
	# baseline origin (bbox("bB").end.y − base_inset − PLAYER_FEET = 119;
	# the row center alone is 120 and he'd draw over the quilt).
	var bed_row := MapData.bbox_rect(map, "b")
	player = Party.spawn($World, bed_row.get_center() + Vector2(0.0, -4.0))
	# one-screen diorama: pin the camera (view_size), matching house.gd and the
	# downstairs scenes — the 24x14 map is 8px taller than the view, and
	# size_px would give this the only follow-drift among the loft's three eras
	Party.clamp_cameras(MapData.view_size())
	player.sprite.play("idle_down")
	_spawn_bird()
	_wake_cutscene()


func _spawn_bird() -> void:
	# perched on the window sill high on the north wall — a World sprite so
	# it lives on the same canvas as the bodies it heckles
	var win := MapData.bbox_rect(map, "W")
	var sill := Vector2(win.get_center().x + 10.0, win.position.y + 8.0)
	_bird = WorldFx.airborne($World, FX_SHEET, FX_BIRD0, sill, 0.0)


func _flap() -> void:
	# quick wing flaps while Dr. Feathers is on screen
	for i in 12:
		if not is_instance_valid(_bird):
			return
		_bird.frame = FX_BIRD1 if _bird.frame == FX_BIRD0 else FX_BIRD0
		await get_tree().create_timer(0.18).timeout


func _wake_cutscene() -> void:
	theater.lock_party()
	# sleeping Zs drift up — ground-anchored on his feet line so they sort
	# in FRONT of the quilt cover he sleeps under
	var zzz := WorldFx.airborne($World, FX_SHEET, FX_ZZZ,
			player.global_position + Vector2(8.0, 20.0), 30.0)
	await theater.wait(0.8)
	await theater.say("Basil", "Zzz... mm. Tenure... acceptance speech... zzz...")
	_flap()
	await theater.say("Dr. Feathers", "TWEET! TWEET! TWEET!")
	await theater.say("Basil", "Mnnh. Five more minutes, Dr. Feathers.")
	await theater.say("Dr. Feathers", "TWEET!! TWEET!! TWEET!!")
	zzz.queue_free()
	await theater.say("Basil", "...Wait. Birds. Morning birds. Why is it so BRIGHT?")
	# he bolts upright — daylight snaps in
	var tw := create_tween()
	tw.tween_property(dim, "color", DIM_AWAKE, 0.4)
	await tw.finished
	await theater.say("Basil", "The clock. Where's the clock. Clock clock clock-")
	await theater.say("Basil", "EIGHT FIFTY-SEVEN?!")
	await theater.say("Basil", "The alarm never went off. The lecture is at NINE.")
	await theater.say("Basil", "No no no no no no NO!")
	theater.close_dialog()
	# hop out of bed, then hand control over to reach the stairs
	player.sprite.play("idle_down")
	await theater.hop(player, 8.0)
	theater.unlock_party()
	_show_hint("GET DOWNSTAIRS - THE SW STAIRS")
	# wire the stair exit (reuse the house exit anchor)
	var exit := Area2D.new()
	exit.collision_layer = 0
	exit.collision_mask = 2
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(24, 16)
	shape.shape = rect
	exit.add_child(shape)
	exit.position = MapData.anchor_px(map, "exit_door")
	add_child(exit)
	exit.body_entered.connect(_on_exit)


func _on_exit(body: Node) -> void:
	if body.is_in_group("player"):
		Game.town_thesis_phase = "dash"
		get_tree().change_scene_to_file.call_deferred("res://scene/town_thesis.tscn")


func _show_hint(text: String) -> void:
	var label: Label = $UI/Hint
	label.text = text
	label.modulate.a = 1.0
	# kill the previous fade or its interval expires mid-hold and yanks
	# THIS hint early — create_tween() never auto-kills prior tweens
	if _hint_tw:
		_hint_tw.kill()
	_hint_tw = create_tween()
	_hint_tw.tween_interval(2.2)
	_hint_tw.tween_property(label, "modulate:a", 0.0, 0.5)
