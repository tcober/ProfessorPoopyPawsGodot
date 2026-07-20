extends Node2D

## THE EBB (the Act 1 opener) — the night the world's magic drains, staged
## over the overworld's big mountain. A PURE cutscene: no player, no party,
## no collision. Both era layouts are stamped on entry (bright pair visible,
## drained pair hidden), the camera holds on the summit under a deep-indigo
## night, the ground shakes, and ONE white flash swaps the bright world for
## the drained one — the palette drain and the summit-crystal ignition land
## on the same cut. Then the SPARKS: loose magic streaming home to the
## summit from every edge of the sky — twinkling motes drifting in on bowed
## firefly paths the crystal's pull slowly wins, shedding trails, drunk in
## soft blooms at the chisel tip — and a held silence. No dialog boxes,
## no cards (the narration purge — the mountain does the talking).
## ui_accept/ui_cancel/attack skips (polled LEVEL-detect + latch, the
## crank-mash gotcha) straight to the flag + fade + handoff.

const FX_SHEET := preload("res://assets/prologue_fx.png")
const FX_SPARK_A := 20               # row-1 spark cells, alternated
const FX_SPARK_B := 21

const NEXT_SCENE := "res://scene/library.tscn"

const FADE_IN := 1.0                 # fade from black onto the bright summit
const HOLD_OPEN := 1.2               # the held beat before anything moves
const QUAKE_TIME := 2.2              # escalating jitter window
const QUAKE_AMP_LO := 1.0            # px, quake start
const QUAKE_AMP_HI := 4.0            # px, quake peak
const QUAKE_STEP := 0.04             # s between jitter nudges (wall-clock)
const FLASH_IN := 0.12               # white slam up...
const FLASH_OUT := 0.5               # ...and the slow reveal back down
const HOLD_DRAINED := 0.8            # the dead world sits a moment
const SPARK_COUNT := 26
const SPARK_GAP := 0.19              # stagger: 26 spawns ~= 5s of stream,
                                     # ~6 motes alive at once
const SPARK_SETTLE := 1.3            # let the last motes land
const HOLD_SILENT := 1.5             # the held SILENT beat before the cut
const FADE_OUT := 1.2
const SKIP_ARM := 1.0                # the skip poll goes live after this

const NIGHT_TINT := Color(0.32, 0.32, 0.58)      # deep indigo
const SPARK_TINT := Color(0.88, 0.78, 1.0)       # violet-white motes

## Hand-varied spawn points just outside the 384x216 camera rect
## (half-extents 192x108), relative to the camera center.
const SPARK_OFFS: Array[Vector2] = [
	Vector2(-206.0, -74.0), Vector2(148.0, -122.0), Vector2(210.0, -18.0),
	Vector2(-64.0, -126.0), Vector2(-214.0, 52.0), Vector2(202.0, 96.0),
	Vector2(30.0, 124.0), Vector2(-150.0, 120.0), Vector2(214.0, -88.0),
	Vector2(-198.0, -10.0), Vector2(96.0, -120.0), Vector2(-30.0, 122.0),
	Vector2(206.0, 44.0), Vector2(-118.0, -124.0),
]

var _summit := Vector2.ZERO          # the 'B' bbox center (the camera's home)
var _tip := Vector2.ZERO             # the crystal's chisel tip (the sparks'
                                     # true home — the generator's blaze
                                     # point, B + (112, 10))
var _cam_center := Vector2.ZERO      # summit nudged 8px south
var _finished := false
var _skip_armed := false
var _press_latch := false
var _spark_mat := CanvasItemMaterial.new()

@onready var camera: Camera2D = $Camera2D
@onready var glow_drained: Sprite2D = $GlowDrained
@onready var flash: ColorRect = $UI/Flash
@onready var fade: ColorRect = $UI/Fade


func _ready() -> void:
	TiledMap.build("res://assets/tilesets/overworld_bright_layout.txt",
			{"lower": $TilesBright, "upper": $TilesBrightUpper})
	TiledMap.build("res://assets/tilesets/overworld_layout.txt",
			{"lower": $TilesDrained, "upper": $TilesDrainedUpper})
	# the summit: pixel center of the big mountain's 'B' block — the cells
	# are solid, so no anchor can live there; the bbox IS the address
	var map := MapData.load_map("res://assets/maps/overworld_bright.txt")
	var b_rect := MapData.bbox_rect(map, "B")
	_summit = b_rect.get_center()
	_tip = b_rect.position + Vector2(112.0, 10.0)
	_cam_center = _summit + Vector2(0.0, 8.0)
	camera.position = _cam_center
	camera.make_current()
	_spark_mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	get_tree().create_timer(SKIP_ARM).timeout.connect(
			func() -> void: _skip_armed = true)
	_run()


func _process(_delta: float) -> void:
	# POLLED level-detect + latch (the crank-mash gotcha: a frame signal can
	# beat a same-frame press, and shot.gd's synthesized presses exist only
	# in the polled Input state — never is_action_just_pressed here)
	var pressed := Input.is_action_pressed("ui_accept") \
			or Input.is_action_pressed("ui_cancel") \
			or Input.is_action_pressed("attack")
	if pressed and not _press_latch and _skip_armed:
		_finish()
	_press_latch = pressed


func _run() -> void:
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 0.0, FADE_IN)
	await tw.finished
	await _hold(HOLD_OPEN)
	if _finished:
		return
	await _quake()
	if _finished:
		return
	# the flash: the whole drain lands inside one blink of white
	var up := create_tween()
	up.tween_property(flash, "modulate:a", 1.0, FLASH_IN)
	await up.finished
	if _finished:
		return
	_swap()
	var down := create_tween()
	down.tween_property(flash, "modulate:a", 0.0, FLASH_OUT)
	await down.finished
	await _hold(HOLD_DRAINED)
	if _finished:
		return
	await _spark_stream()
	if _finished:
		return
	await _hold(HOLD_SILENT)
	_finish()


## Escalating earthquake: a hand-rolled camera-offset jitter ramping 1 -> 4 px
## across the window. Wall-clock throughout — elapsed via ticks, steps via
## timers, never frame counts (the uncapped occluded-window gotcha).
func _quake() -> void:
	var start := Time.get_ticks_msec()
	while not _finished:
		var t := float(Time.get_ticks_msec() - start) / 1000.0
		if t >= QUAKE_TIME:
			break
		var amp := lerpf(QUAKE_AMP_LO, QUAKE_AMP_HI, t / QUAKE_TIME)
		camera.offset = Vector2(randf_range(-amp, amp), randf_range(-amp, amp))
		await get_tree().create_timer(QUAKE_STEP).timeout
	camera.offset = Vector2.ZERO


## THE SWAP — bright trio out, drained trio in, under the flash: the dead
## palette and the lit summit crystals (the drained glow) arrive together.
func _swap() -> void:
	for n: Node2D in [$TilesBright, $GlowBright, $TilesBrightUpper]:
		n.visible = false
	for n: Node2D in [$TilesDrained, $GlowDrained, $TilesDrainedUpper]:
		n.visible = true


## THE SPARKS: staggered motes of loose magic streaming home to the summit
## while the drained glow breathes underneath them.
func _spark_stream() -> void:
	var pulse := create_tween().set_loops()
	pulse.tween_property(glow_drained, "modulate:a", 0.65, 0.45)
	pulse.tween_property(glow_drained, "modulate:a", 1.0, 0.45)
	for i in SPARK_COUNT:
		if _finished:
			break
		_launch_spark(i)
		await get_tree().create_timer(SPARK_GAP).timeout
	if not _finished:
		await get_tree().create_timer(SPARK_SETTLE).timeout
	pulse.kill()
	glow_drained.modulate.a = 1.0


## One mote: born just off-screen, drifting home on a bowed firefly path the
## crystal's pull slowly wins (the EXPO ease: a lazy hang, then the whip),
## twinkling between the bright and dim cells, shedding a fading trail, and
## drunk by the crystal in a soft bloom at the chisel tip.
func _launch_spark(i: int) -> void:
	var s := WorldFx.sheet_sprite(FX_SHEET, FX_SPARK_A)
	s.material = _spark_mat
	s.modulate = SPARK_TINT
	var start := _cam_center + SPARK_OFFS[i % SPARK_OFFS.size()]
	s.position = start
	var hero := i % 5 == 2               # every fifth mote is a big slow drifter
	var scale0 := 1.5 if hero else 1.0 + 0.12 * float(i % 3)
	s.scale = Vector2(scale0, scale0)
	add_child(s)
	# aim jitter: strikes shimmer across the tip, never one stacked point
	var target := _tip + Vector2(float((i * 7) % 11) - 5.0, float((i * 5) % 7) - 3.0)
	var bow := (18.0 + 6.0 * float(i % 3)) * (1.0 if i % 2 == 0 else -1.0)
	var phase := 0.9 * float(i % 7)
	var dur := (1.45 if hero else 1.05) + 0.06 * float(i % 5)
	var tw := s.create_tween()
	tw.tween_method(_fly_spark.bind(s, start, target, bow, phase, scale0),
			0.0, 1.0, dur).set_trans(Tween.TRANS_EXPO).set_ease(Tween.EASE_IN)
	tw.tween_callback(_absorb.bind(target))
	tw.tween_callback(s.queue_free)


func _fly_spark(t: float, s: Sprite2D, start: Vector2, target: Vector2,
		bow: float, phase: float, scale0: float) -> void:
	if not is_instance_valid(s):
		return
	var perp := (target - start).normalized().orthogonal()
	s.position = start.lerp(target, t) + perp * bow * sin(t * PI)
	# the twinkle: per-mote phase; the eased t makes the blink quicken as
	# the pull wins
	s.frame = FX_SPARK_A if int(t * 26.0 + phase) % 2 == 0 else FX_SPARK_B
	var k := lerpf(scale0, 0.3, t) * (1.0 + 0.15 * sin(t * 34.0 + phase))
	s.scale = Vector2(k, k)
	s.rotation = (target - start).angle() + (1.0 - t) * (0.7 if bow > 0.0 else -0.7)
	var step := int(t * 14.0)
	if step > int(s.get_meta("trail_i", -1)):
		s.set_meta("trail_i", step)
		_shed_trail(s.position, k * 0.6)


## A dim mote left hanging where the spark just was, fading as the flight
## outruns it — the comet-tail read.
func _shed_trail(pos: Vector2, k: float) -> void:
	if _finished:
		return
	var m := WorldFx.sheet_sprite(FX_SHEET, FX_SPARK_B)
	m.material = _spark_mat
	m.modulate = SPARK_TINT
	m.position = pos
	m.scale = Vector2(k, k)
	add_child(m)
	var tw := m.create_tween().set_parallel()
	tw.tween_property(m, "modulate:a", 0.0, 0.4)
	tw.tween_property(m, "scale", Vector2(0.1, 0.1), 0.4)
	tw.chain().tween_callback(m.queue_free)


## The crystal drinks the mote: a brief bloom swelling off the strike point.
func _absorb(target: Vector2) -> void:
	if _finished:
		return
	var b := WorldFx.sheet_sprite(FX_SHEET, FX_SPARK_A)
	b.material = _spark_mat
	b.modulate = SPARK_TINT
	b.position = target
	b.scale = Vector2(0.6, 0.6)
	add_child(b)
	var tw := b.create_tween().set_parallel()
	tw.tween_property(b, "scale", Vector2(2.2, 2.2), 0.22)
	tw.tween_property(b, "modulate:a", 0.0, 0.22)
	tw.chain().tween_callback(b.queue_free)


## Idempotent ending — flag, fade, handoff (the skip lands here too, from
## anywhere in the sequence; every _run stage bails once this has fired).
func _finish() -> void:
	if _finished:
		return
	_finished = true
	camera.offset = Vector2.ZERO
	Game.set_flag("ebb_done")
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 1.0, FADE_OUT)
	await tw.finished
	get_tree().change_scene_to_file(NEXT_SCENE)


## Wall-clock beat (timers, never frame counts).
func _hold(t: float) -> void:
	await get_tree().create_timer(t).timeout
