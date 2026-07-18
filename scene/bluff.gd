extends Node2D

## THE SUNSET BLUFF — one headland, three beats (2026-07-17; docs/DESIGN.md
## Story). Routed by Game.bluff_phase over one warm painting (the tint law:
## the call phases lay a cooler CanvasModulate over the same sunset tiles):
##   romance (sunset)  from meadow_fest's cards: college Kitty summons Basil
##                     up here with the acceptance letter news — the watch
##                     gift. It EXPLODES on the handoff, the three pieces
##                     scatter across the headland (the whirligig fetch
##                     recipe, on purpose), she re-tinkers it working, he
##                     plays look_watch for the FIRST time, and the kiss
##                     seals it. -> town_thesis "plant"
##   call1   (dusk)    from the hall's laugh-out: Basil sits on the lip;
##                     KITTY calls to ask how it went; he can barely answer;
##                     "I'm coming. Stay right there." -> the accident
##   call2   (night)   from the accident's cut: her watch calls his — but
##                     the voice on it is Ridley's, from the roadside.
##                     -> sickroom
## The SAME place on purpose: where their love began is where the bad news
## finds him. Semi-playable like the old workshop interlude (walk/interact;
## no exits — the story leaves for you).

const MAP_PATH := "res://assets/maps/bluff.txt"
const LAYOUT_PATH := "res://assets/tilesets/bluff_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const FX_SHEET := preload("res://assets/prologue_fx.png")
const SHEET_KITTY := preload("res://assets/npc_kitty_adult_gen.png")

## fx strip cells (two-row sheet; WorldFx.sheet_sprite infers the rows)
const FX_SPARK0 := 2
const FX_SPARK1 := 3
const FX_POOF := 17
const FX_HEART := 19

const TINT_SUNSET := Color(1.0, 0.94, 0.88)    # the painting's own hour
const TINT_DUSK := Color(0.80, 0.64, 0.74)     # call1: the light going
const TINT_NIGHT := Color(0.54, 0.50, 0.74)    # call2: gone

## The exploded watch scatters into the whirligig recipe — Kitty keeps the
## recipes that work. Anchors live in maps/bluff.txt.
const PARTS := {
	"gear": {"anchor": "part_gear", "cell": 4,
		"line": "THE GEAR - IT ROLLED FOR THE TREELINE"},
	"spring": {"anchor": "part_spring", "cell": 5,
		"line": "THE SPRING - SPROINGED HALFWAY TO THE POINT"},
	"crank": {"anchor": "part_crank", "cell": 6,
		"line": "THE CRANK - IN THE FLOWERS. CLASSIC CRANK"},
}

var map: Dictionary
var player: Node2D
var phase := "romance"
var _busy_scene := false
var _kitty: NPC
var _hint_tw: Tween

@onready var theater: Theater = $Theater


func _ready() -> void:
	phase = Game.bluff_phase
	Game.bluff_phase = ""
	if phase == "":
		phase = "romance"
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	player = Party.spawn($World, MapData.anchor_px(map, "player_spawn"))
	Party.clamp_cameras(MapData.size_px(map))
	match phase:
		"call1": _phase_call1()
		"call2": _phase_call2()
		_: _phase_romance()


# ---- romance (sunset): the watch — explode, gather, fix, the kiss ------------------

func _phase_romance() -> void:
	$Dim.color = TINT_SUNSET
	_spawn_kitty()
	theater.lock_party()
	await theater.wait(0.7)
	await theater.say("Basil", "Okay, I climbed your bluff. The letter's going to crease in this wind, you know.")
	theater.close_dialog()
	# she waves him to the lip — the scripted walk is announced, never mute
	_kitty.play_emote()
	await theater.say("Kitty", "It CAME? IT CAME. Get over here, Academy cat!")
	theater.close_dialog()
	await theater.walk_via(player, [
			MapData.anchor_px(map, "basil_mark") + Vector2(0.0, -20.0),
			MapData.anchor_px(map, "basil_mark")], 55.0)
	theater.face(player, Vector2.RIGHT)
	_kitty.play_act()
	await theater.say("Kitty", "In on CRAFT alone. Wiggle-fingers: zero. Paws: ONE. I could BURST.")
	await theater.say("Kitty", "Which is why you're up here. I finished something. Three summers of something.")
	await theater.say("Kitty", "It's a watch. I made it. Academy cats cannot be late. It keeps PERFECT time.")
	await theater.say("Kitty", "Paw.")
	await theater.say("Basil", "What? Why?")
	await theater.say("Kitty", "PAW.")
	theater.close_dialog()
	await theater.wait(0.5)
	# ---- the handoff... and the mainspring's opinion of it
	var poof := WorldFx.airborne($World, FX_SHEET, FX_POOF,
			player.global_position + Vector2(6.0, 0.0), 30.0)
	await _scatter_parts()
	poof.queue_free()
	_kitty.play_idle()
	await theater.say("Kitty", "...")
	await theater.say("Basil", "It keeps perfect time.")
	await theater.say("Kitty", "The MAINSPRING was overwound, that's ALL. Nothing is lost that isn't lying in this grass.")
	await theater.say("Kitty", "Gear. Spring. Crank. Fetch, and I will PROVE it to you.")
	theater.close_dialog()
	_kitty.lines = PackedStringArray([
		"Gear, spring, crank. A headland this size can only hide them so well.",
		"Overwound. OVER-wound. The case is FINE.",
	])
	theater.unlock_party()
	_show_hint("GEAR - SPRING - CRANK. SOME RECIPES DON'T CHANGE.")


## The poof kicks the three pieces out across the headland: each icon flies
## from Basil's paws to its anchor, then becomes the meadow pickup idiom.
func _scatter_parts() -> void:
	var flights: Array = []
	for part: String in PARTS:
		var cfg: Dictionary = PARTS[part]
		var icon := WorldFx.sheet_sprite(FX_SHEET, cfg["cell"])
		$World.add_child(icon)
		icon.global_position = player.global_position + Vector2(6.0, -14.0)
		var tw := create_tween()
		tw.tween_property(icon, "global_position",
				MapData.anchor_px(map, cfg["anchor"]), 0.55) \
				.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		flights.append([tw, icon, part])
	await theater.wait(0.65)
	for f: Array in flights:
		(f[1] as Node).queue_free()
		_spawn_part(f[2])


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


func _spawn_kitty() -> void:
	_kitty = NPCScene.instantiate()
	_kitty.display_name = "Kitty"
	_kitty.sheet = SHEET_KITTY
	_kitty.frame_cols = 6
	_kitty.position = MapData.anchor_px(map, "kitty_pos")
	_kitty.lines = PackedStringArray(["Sunset waits for nobody. Up here, QUICK."])
	_kitty.talked.connect(_on_kitty_talked)
	$World.add_child(_kitty)


## The talked handler AWAITS the beat it starts (the Sage ribbon lesson —
## one advance press must never resume two pending say() awaits).
func _on_kitty_talked(_npc: NPC) -> void:
	if _all_parts_found() and not _busy_scene \
			and not Game.flag("prologue_watch_given"):
		await _refit_and_kiss()


func _refit_and_kiss() -> void:
	_busy_scene = true
	theater.lock_party()
	_kitty.play_act()
	await theater.say("Kitty", "Gear... spring... crank. And THIS time the mainspring gets some respect.")
	theater.close_dialog()
	# re-tinker sparkle over her paws while she sets it right
	var spark := WorldFx.airborne($World, FX_SHEET, FX_SPARK0,
			_kitty.position + Vector2(2.0, -2.0), 22.0)
	for i in 6:
		await theater.wait(0.22)
		spark.frame = FX_SPARK1 if spark.frame == FX_SPARK0 else FX_SPARK0
	spark.queue_free()
	_kitty.play_idle()
	await theater.say("Kitty", "Paw. ...It's safe. Probably. Paw anyway.")
	theater.close_dialog()
	# the watch on his wrist for the FIRST time — the raised-paw gesture
	# every later call beat repeats (player_frames `look_watch`)
	player.sprite.play("look_watch")
	await theater.wait(1.0)
	await theater.say("Basil", "It ticks. Kitty, the escapement alone - three summers? For me?")
	await theater.say("Kitty", "Every time you ran late I added a jewel to spite you. Does it still keep perfect time? PERFECT-er.")
	await theater.say("Basil", "...I'm never taking it off.")
	await theater.say("Kitty", "I know. And when you're the one up FRONT in one of those big halls - because you WILL be -")
	await theater.say("Kitty", "- I'll be in the front row. Whooping.")
	await theater.say("Basil", "Please don't whoop.")
	await theater.say("Kitty", "Whooping is a promise, professor.")
	theater.close_dialog()
	# ---- the kiss: she closes the gap; the heart blooms over the sunset
	player.sprite.play("idle_down")
	theater.face(player, Vector2.RIGHT)
	await theater.walk(_kitty, player.global_position + Vector2(14.0, 0.0), 30.0)
	await theater.wait(0.4)
	var heart := WorldFx.airborne($World, FX_SHEET, FX_HEART,
			player.global_position + Vector2(7.0, 0.0), 40.0)
	var htw := heart.create_tween()
	htw.tween_property(heart, "offset:y", heart.offset.y - 8.0, 1.6) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	await theater.wait(2.0)
	heart.queue_free()
	Game.set_flag("prologue_watch_given")
	Game.set_flag("prologue_romance")
	await theater.black(1.6)
	await theater.card("He was still late, most days.  He never took the watch off.", 2.6)
	await theater.card("And she never once missed a sunset up there with him.", 2.4)
	await theater.card("YEARS LATER.", 2.0)
	Game.town_thesis_phase = "plant"
	get_tree().change_scene_to_file("res://scene/town_thesis.tscn")


# ---- call1 (dusk): she calls to ask how it went ------------------------------------

func _phase_call1() -> void:
	$Dim.color = TINT_DUSK
	theater.lock_party()
	player.sprite.play("sad")
	await theater.wait(0.8)
	await theater.say("Basil", "Poopy Paws. They're all still laughing. I can hear it from here.")
	theater.close_dialog()
	# the walk to the lip is the player's own (the pacing law: agency, not cuts)
	_show_hint("THE EDGE OF THE BLUFF - SOMEWHERE NOBODY IS")
	await theater.walk_gate(MapData.anchor_px(map, "sit_spot"), Vector2(48.0, 32.0))
	await theater.walk(player, MapData.anchor_px(map, "sit_spot"), 40.0)
	player.sprite.play("sit")
	player.sprite.flip_h = false          # profile RIGHT, against the water
	await theater.wait(1.6)
	await theater.say("", "The town's lamps come on below, one by one. The water doesn't care about any of it.")
	# the watch blinks — SHE calls HIM (she never saw the hall; her axle did
	# that). He stands to answer: the same gesture she taught him.
	await theater.wait(0.8)
	player.sprite.play("look_watch")
	await theater.wait(0.9)
	await theater.say("Kitty", "SO? Professor Basil. How'd it go? Did they whoop? Tell me somebody whooped.")
	await theater.say("Basil", "...")
	await theater.say("Kitty", "Basil?")
	await theater.say("Basil", "...The hall. Schweinler. I can't - Kitty, I can't even say it.")
	await theater.wait(0.6)
	await theater.say("Kitty", "...That bad, huh. Okay. Listen to me. I'm coming. Stay right there.")
	await theater.say("Basil", "Wait - it's nearly dark, the road - Kitty? ...She's already pedaling.")
	theater.close_dialog()
	player.sprite.play("sit")
	await theater.wait(1.4)
	await theater.black(1.0)
	# the accident is SHOWN — the side-view set-piece owns the flag
	get_tree().change_scene_to_file("res://scene/accident.tscn")


# ---- call2 (night): her watch calls his — with the wrong voice on it ---------------

func _phase_call2() -> void:
	$Dim.color = TINT_NIGHT
	theater.lock_party()
	# still where she told him to stay
	Party.place(MapData.anchor_px(map, "sit_spot"))
	player.sprite.play("sit")
	await theater.wait(1.2)
	await theater.say("", "He stays right there. The stars come out. She is taking too long.")
	await theater.wait(0.6)
	player.sprite.play("look_watch")
	await theater.wait(0.9)
	await theater.say("Basil", "Kitty! Finally - where ARE you, I was about to -")
	await theater.say("Ridley", "...Is this Basil? Your name's engraved on the little glass. I'm - there's been an accident. On the dusk road.")
	await theater.say("Ridley", "The doctor has her. The east cottage, by the fountain. You should... you should run.")
	theater.close_dialog()
	await theater.wait(0.5)
	player.sprite.play("walk_side")
	await theater.wait(0.3)
	await theater.black(0.8)
	get_tree().change_scene_to_file("res://scene/sickroom.tscn")


# ---- helpers ----------------------------------------------------------------------

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
