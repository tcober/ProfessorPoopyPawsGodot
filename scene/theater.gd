class_name Theater
extends CanvasLayer

## The cutscene kit, built fresh 2026-07-12 (the deleted Cutscene class is NOT
## recovered): awaitable staging helpers a story scene scripts its beats with.
## Instance scene/theater.tscn once per story scene; NPCs find it through the
## "theater" group. Fade is the full-screen black, Card the centered
## time-skip/title text over it, DialogBox the typewriter box. The actor
## helpers (walk/face/hop) drive any Node2D exposing an AnimatedSprite2D
## `sprite` with walk_/idle_ clips — PartyMember and NPC both qualify.

@onready var fade: ColorRect = $Fade
@onready var card_label: Label = $Card
@onready var dialog: DialogBox = $DialogBox


func _ready() -> void:
	add_to_group("theater")
	card_label.modulate.a = 0.0
	fade.modulate.a = 0.0


# ---- screen ---------------------------------------------------------------

func black(dur := 0.5) -> void:
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 1.0, dur)
	await tw.finished


func clear(dur := 0.7) -> void:
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 0.0, dur)
	await tw.finished


## Full-screen text over the black: fades in, rests, fades out. Callers put
## the screen to black() first (card sequences chain on one black).
func card(line: String, hold := 1.6) -> void:
	card_label.text = line
	var tw := create_tween()
	tw.tween_property(card_label, "modulate:a", 1.0, 0.4)
	tw.tween_interval(hold)
	tw.tween_property(card_label, "modulate:a", 0.0, 0.4)
	await tw.finished


func wait(sec: float) -> void:
	await get_tree().create_timer(sec).timeout


# ---- words ----------------------------------------------------------------

func say(speaker: String, line: String) -> void:
	await dialog.say(speaker, line)


func converse(speaker: String, conversation: PackedStringArray) -> void:
	await dialog.converse(speaker, conversation)


func close_dialog() -> void:
	dialog.close()


# ---- actors ---------------------------------------------------------------

## Tween an actor to a point at walking pace, playing its directional walk,
## then settle into the matching idle.
func walk(actor: Node2D, to: Vector2, speed := 55.0) -> void:
	var d := to - actor.global_position
	if d.length() < 1.0:
		return
	_face_anim(actor, d, "walk")
	var tw := create_tween()
	tw.tween_property(actor, "global_position", to, d.length() / speed)
	await tw.finished
	_face_anim(actor, d, "idle")


## Walk an actor through waypoints in order. walk() tweens straight lines
## with physics off (no collision), so any scripted approach that could
## cross a solid prop must dog-leg around it — callers pick the clear path.
func walk_via(actor: Node2D, points: Array, speed := 55.0) -> void:
	for p in points:
		await walk(actor, p, speed)


func face(actor: Node2D, dir: Vector2) -> void:
	_face_anim(actor, dir, "idle")


## A little vertical bounce on the actor's sprite (surprise, laughter) — the
## body and its collision stay planted.
func hop(actor: Node2D, height := 6.0, dur := 0.26) -> void:
	var sprite: Node2D = actor.sprite
	var base := sprite.position.y
	var tw := create_tween()
	tw.tween_property(sprite, "position:y", base - height, dur * 0.5) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw.tween_property(sprite, "position:y", base, dur * 0.5) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	await tw.finished


func _face_anim(actor: Node2D, dir: Vector2, prefix: String) -> void:
	var suffix := "down"
	if absf(dir.x) > absf(dir.y):
		suffix = "side"
	elif dir.y < 0.0:
		suffix = "up"
	var sprite: AnimatedSprite2D = actor.sprite
	var anim := prefix + "_" + suffix
	if not sprite.sprite_frames.has_animation(anim):
		# single-facing NPC sheets fall back to their front view
		anim = prefix + "_down"
		if not sprite.sprite_frames.has_animation(anim):
			return
	sprite.play(anim)
	sprite.flip_h = absf(dir.x) > absf(dir.y) and dir.x < 0.0


# ---- control --------------------------------------------------------------

## Freeze the party for staged beats (their _physics_process both moves them
## AND polls input, so one switch parks body and controls together). Uses the
## "party" GROUP, not the Party autoload — the kit stays decoupled, and
## --script tool runs (probes) can compile it before autoloads register.
func lock_party() -> void:
	for m in get_tree().get_nodes_in_group("party"):
		m.set_physics_process(false)
		m.velocity = Vector2.ZERO
		m._play_directional("idle")


func unlock_party() -> void:
	for m in get_tree().get_nodes_in_group("party"):
		m.set_physics_process(true)


## Hand control back mid-scene until the player reaches `goal` (the pacing
## pass, 2026-07-12 — "never >90s without control"): unlock the party, drop a
## one-shot goal Area2D (the dash-goal idiom), await a "player"-group body,
## then optionally re-lock for the next beat. The goal is a POSITION passed
## in — the kit stays free of autoload identifiers (callers resolve their own
## anchors). Callers close_dialog() first; a body already standing in the
## rect fires on the next physics step.
func walk_gate(goal: Vector2, size := Vector2(32.0, 24.0), relock := true) -> void:
	unlock_party()
	var gate := Area2D.new()
	gate.collision_layer = 0
	gate.collision_mask = 2
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = size
	shape.shape = rect
	gate.add_child(shape)
	gate.position = goal
	get_parent().add_child(gate)      # the scene root — never this CanvasLayer
	while true:
		var body: Node2D = await gate.body_entered
		if body.is_in_group("player"):
			break
	gate.queue_free()
	if relock:
		lock_party()


## The mash meter (extracted from the bluff crank-up, 2026-07-25 — the brew's
## stir wants it verbatim): a draining fill bar under a prompt, resolved when
## the fill tops out. `tick` is called every frame with the current fill so the
## caller drives its own art off it (the whirligig's rotor waking, the flask
## coming to the boil).
##
## Children of THIS CanvasLayer, so a caller needs no $UI of its own (hall.tscn
## has none). The party must ALREADY be locked — npc.gd only refuses
## conversations while a body is physics-frozen, so an unlocked mash leaks E
## presses into whatever villager is standing nearby.
func mash_meter(prompt: String, tick := Callable(), gain := 0.09,
		decay := 0.05) -> void:
	var back := ColorRect.new()
	back.offset_left = 128.0
	back.offset_top = 120.0
	back.offset_right = 256.0
	back.offset_bottom = 134.0
	back.color = Color(0.055, 0.04, 0.115, 0.9)
	var fill_rect := ColorRect.new()
	fill_rect.offset_left = 130.0
	fill_rect.offset_top = 122.0
	fill_rect.offset_right = 130.0
	fill_rect.offset_bottom = 132.0
	fill_rect.color = Color(0.91, 0.74, 0.38)
	var label := Label.new()
	label.text = prompt
	label.offset_left = 128.0
	label.offset_top = 106.0
	label.offset_right = 256.0
	label.offset_bottom = 118.0
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.add_theme_font_override("font", preload("res://assets/font/pixel_font.fnt"))
	label.add_theme_font_size_override("font_size", 8)
	label.add_theme_color_override("font_shadow_color", Color.BLACK)
	for node in [back, fill_rect, label]:
		add_child(node)
	var fill := 0.0
	var was_down := false
	while fill < 1.0:
		var delta := get_process_delta_time()
		# level-edge detection, NOT is_action_just_pressed: this coroutine
		# resumes on the tree's process_frame signal, which can run before
		# the same-frame press lands — a just_pressed edge would be missed
		# every time (found by the prologue probe, 2026-07-12)
		var down := Input.is_action_pressed("interact") \
				or Input.is_action_pressed("attack")
		if down and not was_down:
			fill = minf(1.0, fill + gain)
			if fill >= 1.0:
				break     # full NOW — the decay below must never gnaw it back
		was_down = down
		fill = maxf(0.0, fill - delta * decay)
		fill_rect.offset_right = 130.0 + 124.0 * fill
		if tick.is_valid():
			tick.call(fill)
		await get_tree().process_frame
	fill_rect.offset_right = 254.0
	for node in [back, fill_rect, label]:
		node.queue_free()
