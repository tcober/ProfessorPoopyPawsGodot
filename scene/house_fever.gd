extends Node2D

## The loft bedroom, THE FEVER — Prologue A0's first room (docs/DESIGN.md
## Story), before the festival ever happens. Kid Basil wakes in the cold
## pre-dawn because there is an adult voice downstairs at the wrong hour —
## the doctor's. Same loft as the festival sunrise and the thesis-day
## oversleep (reprise staging: one room, four eras now), but the curtains
## stay SHUT and the dawn glow stays down: the fever days are the one
## overcast stretch of the bright era. Twenty seconds, one line, control.
## The SW stairs descend to the fever downstairs, where Dr. Ciconia is on
## his way out.

const MAP_PATH := "res://assets/maps/house.txt"
const LAYOUT_PATH := "res://assets/tilesets/house_layout.txt"
const PROPS_PATH := "res://assets/tilesets/house_props.txt"
const FX_SHEET := preload("res://assets/prologue_fx.png")

const FX_ZZZ := 15

const DIM_SLEEP := Color(0.5, 0.48, 0.68)      # pre-dawn gloom, colder than
                                               # the festival morning's
const DIM_GREY := Color(0.72, 0.72, 0.82)      # overcast day through curtains

var map: Dictionary
var player: Node2D

@onready var theater: Theater = $Theater
@onready var dim: CanvasModulate = $Dim


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	PropSpawner.build(PROPS_PATH, map, $World)
	dim.color = DIM_SLEEP
	$Glow.modulate.a = 0.0
	# curtains drawn SHUT over the dormer window — and they stay shut: no
	# sunrise plays in this era (the house_fest idiom, minus the sun)
	var win := MapData.bbox_rect(map, "W")
	$Curtains.position = win.position
	$Curtains.frame = 0
	# asleep on the bed's walkable middle row (the house_fest spawn contract)
	var bed_row := MapData.bbox_rect(map, "b")
	player = Party.spawn($World, bed_row.get_center() + Vector2(0.0, -4.0))
	Party.clamp_cameras(MapData.view_size())
	player.sprite.play("sleep")
	Game.set_flag("prologue_fever")
	_wake_cutscene()


func _wake_cutscene() -> void:
	theater.lock_party()
	var zzz := WorldFx.airborne($World, FX_SHEET, FX_ZZZ,
			player.global_position + Vector2(8.0, 20.0), 30.0)
	await theater.wait(1.6)
	# eyes open — no sunrise. The house is TALKING, quietly, downstairs.
	zzz.queue_free()
	player.sprite.play("wake")
	var tw := create_tween()
	tw.tween_property(dim, "color", DIM_GREY, 0.9)
	await theater.wait(1.2)
	await theater.say("Basil", "...That's the doctor's voice.")
	theater.close_dialog()
	player.sprite.play("idle_down")
	theater.unlock_party()
	theater.hint("DOWNSTAIRS", 2.2)
	_wire_exit()


func _wire_exit() -> void:
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
		Game.interior_spawn = "stair_arrival"
		get_tree().change_scene_to_file.call_deferred("res://scene/downstairs_fever.tscn")
