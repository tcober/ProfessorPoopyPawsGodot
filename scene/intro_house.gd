extends Cutscene

## Front-yard scene, used twice. Night (default): Schweinler the pig leaves a
## "gift" on Basil's doorstep. Morning (`morning = true`, set by
## intro_house_morning.tscn): Basil bursts out the door late for his lecture
## and steps right in it.

const PRINT_TEX := preload("res://assets/props/paw_print.png")

## Paper Girls night: violet-magenta dusk instead of plain blue — still bright
## enough that the bully reads.
const NIGHT := Color(0.55, 0.46, 0.98)

## false = night (Schweinler plants the bag), true = morning (Basil steps in it).
@export var morning: bool = false

@onready var ground: TileMapLayer = $Ground
@onready var basil: AnimatedSprite2D = $Basil
@onready var schweinler: AnimatedSprite2D = $Schweinler
@onready var bag: Sprite2D = $PoopBag
@onready var tint: CanvasModulate = $Tint
@onready var prints: Node2D = $Prints

var _printing: bool = false


func _ready() -> void:
	_paint_yard()
	if morning:
		schweinler.visible = false
		bag.visible = true
	else:
		tint.color = NIGHT
	super._ready()


func _paint_yard() -> void:
	var flowers: Array[Vector2i] = [
		Vector2i(8, 14), Vector2i(30, 12), Vector2i(33, 20), Vector2i(6, 20),
		Vector2i(14, 17), Vector2i(26, 18), Vector2i(11, 11), Vector2i(35, 15),
	]
	for y in 23:
		for x in 40:
			var coords := Vector2i(0, 0)                     # grass
			if (x == 19 or x == 20) and y >= 8:
				coords = Vector2i(3, 0)                      # path from the door
			elif flowers.has(Vector2i(x, y)):
				coords = Vector2i(2, 0)                      # flowers
			elif absi((x * 73856093) ^ (y * 19349663)) % 11 == 0:
				coords = Vector2i(1, 0)                      # tufts
			ground.set_cell(Vector2i(x, y), 0, coords)


func _play() -> void:
	if morning:
		await _play_morning()
	else:
		await _play_night()
	finish()


func _play_night() -> void:
	await fade_in(0.9)
	await wait(0.4)
	await walk(schweinler, Vector2(352, 300), 110)
	await walk(schweinler, Vector2(340, 168), 85)
	schweinler.play("idle_up")
	await wait(0.4)
	bag.visible = true
	await hop(schweinler)
	await say("???: HEHEHE. A LITTLE 'CONGRATULATIONS' FOR MR. YOUNGEST-PROFESSOR-EVER.")
	schweinler.play("laugh_down")
	await say("???: ENJOY YOUR BIG LECTURE TOMORROW, BASIL! OINK-HAHAHA!!")
	await walk(schweinler, Vector2(352, 300), 120)
	await walk(schweinler, Vector2(704, 330), 140)
	await fade_out(0.9)


func _play_morning() -> void:
	await fade_in(0.5)
	basil.visible = true                        # bursts into the doorway
	await hop(basil, 3.0, 0.16)
	await say("BASIL: THE LECTURE!!! I OVERSLEPT!!")
	await say("BASIL: FIRST LECTURE AS A PROFESSOR AND I OVERSLEPT!!")
	await walk(basil, Vector2(320, 162), 100)   # one step out -- right onto the bag
	bag.frame = 2
	await hop(basil, 4.0, 0.16)
	await say("SQUELCH.")
	await say("BASIL: ...I DON'T HAVE TIME TO THINK ABOUT WHAT THAT WAS.")
	await say("BASIL: GOTTA GO GOTTA GO GOTTA GO!!")
	_printing = true
	_drop_prints()
	await walk(basil, Vector2(320, 420), 170)
	_printing = false
	await fade_out(0.8)


## Fire-and-forget: leaves alternating brown paw prints under Basil while he runs.
func _drop_prints() -> void:
	var side := 1
	while _printing and is_instance_valid(basil):
		var p := Sprite2D.new()
		p.texture = PRINT_TEX
		p.position = basil.position + Vector2(4 * side, 18)
		side = -side
		prints.add_child(p)
		await wait(0.09)
