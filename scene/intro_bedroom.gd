extends Cutscene

## Opening scene, part 2 — morning in Basil's bedroom. A songbird lands on the
## windowsill and chirps him awake... at 8:57. The alarm never went off. Panic.

const SILL := Vector2(418, 94)              # bird's perch on the windowsill

@onready var bed: Sprite2D = $Bed           # frames: asleep A / asleep B / upright / empty
@onready var bird: Sprite2D = $Bird         # frames: perched / chirp / flap
@onready var basil: AnimatedSprite2D = $Basil
@onready var clock_dim: ColorRect = $ClockLayer/Dim
@onready var clock_face: Sprite2D = $ClockLayer/ClockFace

var _breathing: bool = true


func _play() -> void:
	_breathe()
	await card("THE NEXT MORNING.", 1.6)
	await fade_in(0.9)
	await wait(0.8)
	await say("BASIL: ZZZ... ZZZ... MMM... TENURE...")

	# the bird flaps in from off-screen and lands on the sill
	bird.visible = true
	bird.frame = 2
	var tw := create_tween()
	tw.tween_property(bird, "position", SILL, 0.9).from(Vector2(700, 30)) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	await tw.finished
	bird.frame = 0
	await wait(0.5)

	await _chirp(3)
	await say("BIRD: TWEET! TWEET! TWEET!")
	await say("BASIL: MNNH... FIVE MORE MINUTES, DR. FEATHERS...")
	await _chirp(5)
	await say("BIRD: TWEET!! TWEET!! TWEET!!")
	await wait(0.3)
	await say("BASIL: ...WAIT. BIRDS. MORNING BIRDS. WHY IS IT SO BRIGHT IN HERE?")

	# bolt upright
	_breathing = false
	bed.frame = 2
	await hop(bed, 3.0, 0.16)
	await say("BASIL: THE CLOCK. WHERE'S THE CLOCK. CLOCK CLOCK CLOCK--")

	# close-up: 8:57, the alarm hand still parked at 8
	await _show_clock()
	await say("BASIL: EIGHT FIFTY-SEVEN?!")
	await say("BASIL: THE ALARM NEVER WENT OFF. THE LECTURE IS AT NINE!!")
	await _hide_clock()

	# bird bails, Basil bails harder
	_fly_off()
	bed.frame = 3
	basil.visible = true
	await hop(basil, 4.0, 0.16)
	await say("BASIL: NO NO NO NO NO NO NO!!")
	await walk(basil, Vector2(320, 292), 150)   # to the doormat
	walk(basil, Vector2(320, 400), 180)         # out the door (fire-and-forget)
	await fade_out(0.7)
	finish()


## Fire-and-forget: slow breathing loop while Basil sleeps (frames 0/1).
func _breathe() -> void:
	while _breathing:
		bed.frame = 0
		await wait(0.7)
		if not _breathing:
			return
		bed.frame = 1
		await wait(0.7)


## Open beak + eighth note, a few times.
func _chirp(times: int) -> void:
	for i in times:
		bird.frame = 1
		await wait(0.16)
		bird.frame = 0
		await wait(0.12)


## Fire-and-forget: the bird flaps away off the top of the screen.
func _fly_off() -> void:
	bird.frame = 2
	var tw := create_tween()
	tw.tween_property(bird, "position", Vector2(700, -30), 0.8) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)


func _show_clock() -> void:
	clock_dim.visible = true
	clock_face.visible = true
	clock_dim.modulate.a = 0.0
	clock_face.scale = Vector2(0.3, 0.3)
	var tw := create_tween().set_parallel()
	tw.tween_property(clock_dim, "modulate:a", 1.0, 0.25)
	tw.tween_property(clock_face, "scale", Vector2(2.5, 2.5), 0.3) \
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	await tw.finished


func _hide_clock() -> void:
	var tw := create_tween().set_parallel()
	tw.tween_property(clock_dim, "modulate:a", 0.0, 0.2)
	tw.tween_property(clock_face, "scale", Vector2(0.3, 0.3), 0.2)
	await tw.finished
	clock_dim.visible = false
	clock_face.visible = false
