extends Node2D

## The loft bedroom, FESTIVAL MORNING — Prologue A's real first room. The
## chapter opens on a scripted SUNRISE (the 2026-07-15 narrative pass): kid
## Basil asleep in bed -> eyes open -> pads to the window -> the curtains
## slide apart and daylight floods in -> a small sigh -> control. Same loft
## the student oversleeps in on thesis day and the hermit haunts in the
## present (reprise staging: one room, three eras). Reuses the house
## tileset/map/props; the SW stairs descend to the fest downstairs where Mom
## gates the front door.

const MAP_PATH := "res://assets/maps/house.txt"
const LAYOUT_PATH := "res://assets/tilesets/house_layout.txt"
const PROPS_PATH := "res://assets/tilesets/house_props.txt"
const FX_SHEET := preload("res://assets/prologue_fx.png")

const FX_ZZZ := 15

const DIM_SLEEP := Color(0.55, 0.5, 0.72)      # pre-dawn gloom
const DIM_MORNING := Color(0.9, 0.86, 0.94)    # festival daylight, violet-cut

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
	# curtains drawn over the dormer window (position derives from the W
	# cells, the house.gd idiom — the open tied-back drapes are baked into
	# the window tiles, so the sprite hides once the cutscene opens them)
	var win := MapData.bbox_rect(map, "W")
	$Curtains.position = win.position
	$Curtains.frame = 0
	# asleep on the bed's walkable middle row, nudged 4px north so the
	# y-sorted quilt cover sorts over him (the house_thesis spawn contract)
	var bed_row := MapData.bbox_rect(map, "b")
	player = Party.spawn($World, bed_row.get_center() + Vector2(0.0, -4.0))
	Party.clamp_cameras(MapData.size_px(map))
	player.sprite.play("sleep")
	_sunrise_cutscene()


func _sunrise_cutscene() -> void:
	theater.lock_party()
	# sleeping Zs drift up, ground-anchored on his feet line so they sort in
	# front of the quilt cover
	var zzz := WorldFx.airborne($World, FX_SHEET, FX_ZZZ,
			player.global_position + Vector2(8.0, 20.0), 30.0)
	await theater.wait(1.4)
	# eyes open — dawn light starts creeping in
	zzz.queue_free()
	player.sprite.play("wake")
	await theater.wait(0.8)
	await theater.say("Basil", "...morning already?")
	theater.close_dialog()
	# pad out of bed and over to the window (dog-leg west off the bed row,
	# then up the rug — walk() is a no-collision tween, so the route stays
	# on open floor)
	player.sprite.play("idle_down")
	await theater.walk_via(player, [
			Vector2(208.0, 116.0),
			Vector2(184.0, 88.0)], 40.0)
	theater.face(player, Vector2.UP)
	await theater.wait(0.4)
	# the curtains slide apart — festival daylight floods the loft
	$Curtains.frame = 1
	var tw := create_tween().set_parallel()
	tw.tween_property($Glow, "modulate:a", 1.0, 0.9)
	tw.tween_property(dim, "color", DIM_MORNING, 0.9)
	await theater.wait(0.25)
	$Curtains.visible = false
	await theater.wait(0.9)
	# the sigh — the whole town will be at the festival. Everyone.
	theater.face(player, Vector2.DOWN)
	player.sprite.play("sigh")
	await theater.say("Basil", "*siiigh*... Founding Festival day. The WHOLE town will be out there.")
	await theater.say("Basil", "...the whole town.")
	theater.close_dialog()
	player.sprite.play("idle_down")
	theater.unlock_party()
	_show_hint("FESTIVAL MORNING - HEAD DOWNSTAIRS")
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
		get_tree().change_scene_to_file.call_deferred("res://scene/downstairs_fest.tscn")


func _show_hint(text: String) -> void:
	var label: Label = $UI/Hint
	label.text = text
	label.modulate.a = 1.0
	var tw := create_tween()
	tw.tween_interval(2.2)
	tw.tween_property(label, "modulate:a", 0.0, 0.5)
