extends Node2D

## THE LANTERNWOOD LIBRARY — Fuji's little reading room in her snow town,
## and her first appearance. Phase "ebb" (the default, and the only beat the
## room knows yet) is the Ebb night from HER side of the world: closing
## time, one more chapter, wand-made coffee — the sparks fly but keep
## missing the kettle, the ground shakes, she steadies herself... and the
## next flick of the wand makes NOTHING. No spark at all. Act 1's playable
## research phase will reuse this same room later (Game.library_phase).
##
## Partyless like the accident: Fuji is an NPC sprite posed by the Theater,
## the camera is the scene's own, and every beat auto-runs on tweens/waits
## or advances on attack (probe-passable).

const MAP_PATH := "res://assets/maps/library.txt"
const LAYOUT_PATH := "res://assets/tilesets/library_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const SHEET_FUJI := preload("res://assets/npc_fuji_gen.png")
const FX_SHEET := preload("res://assets/prologue_fx.png")

const FX_POOF := 17
const FX_SPARK_A := 20               # the Ebb-night magic motes (row 1)
const FX_SPARK_B := 21

## The wand's bead tip while the act cells play flipped west (the kettle
## sits one tuck-cell west of her): offset from the NPC node origin — the
## unflipped cell's tip sits at ~(43, 5) of the 48px cell, mirrored.
const WAND_TIP := Vector2(-20.0, -19.0)

const QUAKE_TIME := 2.4              # her local share of the mountain's quake
const QUAKE_AMP_LO := 1.0
const QUAKE_AMP_HI := 4.0
const QUAKE_STEP := 0.04

var map: Dictionary
var _fuji: NPC
var _anim_t := 0.0
var _spark_mat := CanvasItemMaterial.new()

@onready var theater: Theater = $Theater


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	PropSpawner.build("res://assets/tilesets/library_props.txt", map, $World)
	# the hearth fire overlay, positioned from the map like downstairs
	$Fire.position = MapData.bbox_rect(map, "H").position + Vector2(10.0, 20.0)
	$Camera2D.position = MapData.size_px(map) * 0.5
	$Camera2D.make_current()
	_spark_mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	var phase := Game.library_phase
	Game.library_phase = ""
	# "ebb" is the room's only beat so far; later phases branch here
	if phase == "" or phase == "ebb":
		_spawn_fuji()
		_ebb_night()


func _process(delta: float) -> void:
	_anim_t += delta
	$Fire.frame = int(_anim_t / 0.16) % 3


func _spawn_fuji() -> void:
	_fuji = NPCScene.instantiate()
	_fuji.display_name = "Fuji"
	_fuji.sheet = SHEET_FUJI
	_fuji.frame_cols = 10
	# the east tuck cell: she stands AT the counter, the kettle one cell west
	_fuji.position = MapData.anchor_px(map, "kettle") + Vector2(16.0, 0.0)
	$World.add_child(_fuji)
	_fuji.play_side(false)           # profile, facing west over the kettle


func _ebb_night() -> void:
	theater.fade.modulate.a = 1.0    # born black; the room fades in
	await theater.wait(0.4)
	await theater.clear(1.2)
	await theater.wait(0.8)
	await theater.say("Fuji", "One more chapter, then bed. ...Which means coffee.")
	theater.close_dialog()
	# ---- cast one: the wand WORKS — it just has opinions about aim
	await theater.wait(0.4)
	await _cast(4, 2)
	await theater.say("Fuji", "Ah - no - the KETTLE, not the floorboards-")
	theater.close_dialog()
	# ---- cast two: worse. The mess is winning.
	await theater.wait(0.3)
	await _cast(5, 1)
	theater.hop(_fuji, 4.0)
	await theater.say("Fuji", "Oh, come ON. Heat the water. It's barely even a spell.")
	theater.close_dialog()
	# ---- the QUAKE — the mountain's moment, felt from her floor
	await theater.wait(0.6)
	_fuji.play_emote()               # ears flat, shoulders up
	await _quake()
	await theater.wait(1.2)          # the stillness after
	_fuji.play_idle()
	await theater.wait(0.7)
	await theater.say("Fuji", "...That was scary.")
	await theater.say("Fuji", "...Everything seems okay, though? Nothing even fell.")
	await theater.say("Fuji", "Where was I. Coffee.")
	theater.close_dialog()
	# ---- cast three: NOTHING. No spark at all.
	await theater.wait(0.5)
	_fuji.sprite.flip_h = true
	_fuji.sprite.play("act")
	await theater.wait(1.5)
	_fuji.sprite.stop()              # she flicks it again -
	_fuji.sprite.play("act")
	await theater.wait(1.5)
	_fuji.play_idle()                # - and lowers it, looking at it
	await theater.wait(2.2)          # the held silent beat
	await theater.black(1.6)
	Game.set_flag("ebb_done")
	# the story stays with HER: solo Fuji steps out into her street — the
	# SAME night (no card: no time passes between her floor and the town),
	# where the whole neighborhood is out comparing dead charms
	Party.set_roster([&"fuji"], &"fuji")
	Game.town_spawn = "library"
	get_tree().change_scene_to_file("res://scene/lanternwood.tscn")


## One wand attempt: `n` sparks off the bead, `hits` of them reaching the
## kettle (a bright blink on the spout), the rest going wide and popping
## into little poofs on the floorboards — the mess.
func _cast(n: int, hits: int) -> void:
	_fuji.sprite.flip_h = true
	_fuji.sprite.play("act")
	await theater.wait(0.35)
	var tip := _fuji.global_position + WAND_TIP
	var kettle := MapData.anchor_px(map, "kettle") + Vector2(0.0, -4.0)
	# jitter AWAY from the counter (cells 8-9 x 6-7): an offset that lands a
	# poof inside its footprint gets swallowed by the y-sorted counter art
	var wilds: Array[Vector2] = [
		MapData.anchor_px(map, "mess_a"), MapData.anchor_px(map, "mess_b"),
		MapData.anchor_px(map, "mess_a") + Vector2(-10.0, 6.0),
		MapData.anchor_px(map, "mess_b") + Vector2(12.0, 4.0),
		MapData.anchor_px(map, "mess_a") + Vector2(-8.0, 10.0),
	]
	for i in n:
		var to_kettle := i < hits
		var target := kettle if to_kettle else wilds[i % wilds.size()]
		_launch_spark(tip, target, to_kettle)
		await theater.wait(0.22)
	await theater.wait(0.6)
	_fuji.sprite.flip_h = false
	_fuji.play_side(false)           # back to the profile at the counter


## One spark: a mote off the bead arcing to its landing — kettle hits blink
## out; wild ones pop a poof decal that fades from the floor.
func _launch_spark(from: Vector2, to: Vector2, hit: bool) -> void:
	var s := WorldFx.sheet_sprite(FX_SHEET, FX_SPARK_A if hit else FX_SPARK_B)
	s.material = _spark_mat
	s.position = from
	$World.add_child(s)
	var tw := s.create_tween()
	tw.tween_property(s, "position", to, 0.4) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tw.tween_callback(func() -> void:
		if not hit:
			var p := WorldFx.decal($World, FX_SHEET, FX_POOF, to)
			var fade_tw := p.create_tween()
			fade_tw.tween_property(p, "modulate:a", 0.0, 0.5)
			fade_tw.tween_callback(p.queue_free)
		s.queue_free())


## Her floor's share of the earthquake — the same escalating camera jitter
## the mountain scene rolls, wall-clock throughout.
func _quake() -> void:
	var start := Time.get_ticks_msec()
	while true:
		var t := float(Time.get_ticks_msec() - start) / 1000.0
		if t >= QUAKE_TIME:
			break
		var amp := lerpf(QUAKE_AMP_LO, QUAKE_AMP_HI, t / QUAKE_TIME)
		$Camera2D.offset = Vector2(randf_range(-amp, amp), randf_range(-amp, amp))
		await get_tree().create_timer(QUAKE_STEP).timeout
	$Camera2D.offset = Vector2.ZERO
