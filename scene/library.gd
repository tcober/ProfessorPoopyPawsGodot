extends Node2D

## THE LANTERNWOOD LIBRARY — Fuji's little reading room in her snow town,
## and her first appearance. Phase "ebb" (the default) is the Ebb night from
## HER side of the world: closing time, one more chapter, wand-made coffee —
## the sparks fly but keep missing the kettle... and then a flick lands
## exactly on the earthquake.
##
## THE SYNC (2026-07-24, the Venice-library gag from Last Crusade — the
## librarian's stamp keeps landing on Indy's crash and he never questions
## it): the third cast fires NO SPARK. The quake starts on the flick, she
## freezes mid-follow-through, and for a moment she is certain she did it.
## The magic was already gone on that flick — the quake covered for it, and
## the next cast, with nothing to hide behind, makes nothing at all.
##
## The room is a CUTSCENE that becomes PLAYABLE. Fuji acts the beat as an
## NPC puppet (her party sheet has no wand-cast pose — it's walk/tome/darts)
## over her own hidden body; at the hand-over the puppet goes, the body
## takes its place on the matching front-facing pose, and the player walks
## her out her own door into the Ebb-night street. Nothing drags her out.
##
## Phase "research" (2026-07-25) is Act 1 beat 2, in the SAME room weeks
## later: the ledger on the desk, three stacks to search by candlelight, and
## behind the twelfth spine on shelf nine an unbound bundle nobody ever
## catalogued — Basil's thesis. It is a real gate, not a cutscene: the ledger
## is what tells her the shelf holds one more thing than the catalogue
## admits, and until she has read it, shelf nine is just books.
##
## Any other library_phase (and the town door's plain visit) just opens the
## room (Game.library_phase).

const MAP_PATH := "res://assets/maps/library.txt"
const LAYOUT_PATH := "res://assets/tilesets/library_layout.txt"
const NEXT_SCENE := "res://scene/lanternwood.tscn"

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
## How long she holds the cast pose once the ground goes — the whole joke is
## that she is still in the follow-through when the world starts moving.
const QUAKE_HOLD_ACT := 0.6
## The wind-up: the beat between the flick and where the spark would leave
## the bead. The quake lands on it instead.
const SYNC_WINDUP := 0.3

## Look-at zones: one cell wide, on the first walkable cell south of the
## feature (the north-wall pieces sit above a solid wall row).
const LOOK_ZONE := Vector2(32.0, 20.0)

## The three stacks, west to east: the anchor a body searches each from, and
## the shelf number painted on its brass plate. The ledger names NINE — and
## the marks are the whole puzzle, so they live here, not in the prose.
const STACKS := [
	{anchor = "stack_a", mark = "THREE",
	 line = "SHELF THREE. Husbandry, weather, the keeping of bees."},
	{anchor = "stack_b", mark = "SIX",
	 line = "SHELF SIX. Histories. Five lands' worth of kings, and not one of them useful."},
	{anchor = "stack_c", mark = "NINE",
	 line = "SHELF NINE. Enchantment - theory."},
]
const ANSWER := 2                    # index into STACKS: the shelf the ledger names

var map: Dictionary
var player: DirectionalBody2D
var _fuji: NPC
var _cam: Camera2D
var _anim_t := 0.0
var _spark_mat := CanvasItemMaterial.new()
## Id of the interact zone the body is standing in ("" = none), and what each
## id does. A zone's action is a Callable so a stack can run the research
## gate where the kettle only says a line.
var _near := ""
var _zones: Dictionary = {}
## The research beat is live: the desk is an accession ledger, not furniture.
var _research := false
## The KIT beat is live (Act 1 beat 3): the room is a supply list, not a room.
var _kit := false
## The wand is half bored out. Two VISITS, not two presses: _run_zone holds the
## party locked for a whole action, so "stop her halfway" is a state check at
## the top of the second visit rather than surgery on the zone runner.
var _wand_half := false
## A dialog coroutine owns the room — swallow interacts until it lets go.
var _busy := false
## The door fired once; a second body_entered can't queue a second load.
var _leaving := false

@onready var theater: Theater = $Theater


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	PropSpawner.build("res://assets/tilesets/library_props.txt", map, $World)
	# the hearth fire overlay, positioned from the map like downstairs
	$Fire.position = MapData.bbox_rect(map, "H").position + Vector2(10.0, 20.0)
	_spark_mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	var phase := Game.library_phase
	Game.library_phase = ""
	# "" is the boot default a bare scene load lands on, so it keeps meaning
	# the shipped Ebb beat; the town door always names a phase explicitly, so
	# walking in the front door can never replay it.
	var ebb := phase == "" or phase == "ebb"
	var research := phase == "research"
	var kit := phase == "kit"
	if ebb or research or kit:
		# the live flow arrives from ebb.tscn still carrying the ADULTS
		# roster — the story stays with HER from here, so the room sets its
		# own cast (TYPED array: the Party.set_roster contract)
		Party.set_roster([&"fuji"], &"fuji")
	# the Ebb beat starts her AT the counter (the kettle one tuck-cell west)
	# and the research night at her desk; every other way in is her own door
	var spawn := MapData.anchor_px(map, "player_spawn")
	if ebb:
		spawn = MapData.anchor_px(map, "kettle") + Vector2(16.0, 0.0)
	elif research:
		spawn = MapData.anchor_px(map, "desk_spot")
	player = Party.spawn($World, spawn)
	# a 384x224 map under a 384x216 view: clamp to the VIEW and the camera is
	# pinned dead still (the loft idiom — size_px would give it a follow drift)
	Party.clamp_cameras(MapData.view_size())
	_cam = player.get_node("Camera2D") as Camera2D
	# the door mouth below the south wall. The anchor column sits 8px west of
	# the 2-cell arch, so x comes off the '-' bbox (the downstairs rule).
	$ExitDoor.position = Vector2(MapData.bbox_rect(map, "-").get_center().x,
			MapData.anchor_px(map, "exit_door").y)
	$ExitDoor.body_entered.connect(_on_exit_door)
	_wire_look_zones()
	if ebb:
		_spawn_fuji()
		player.visible = false           # the puppet acts over her
		theater.lock_party()
		_ebb_night()
	elif research:
		theater.lock_party()
		_research_night()
	elif kit:
		_kit = true
		theater.lock_party()
		_kit_night()


func _process(delta: float) -> void:
	_anim_t += delta
	$Fire.frame = int(_anim_t / 0.16) % 3
	if not _near.is_empty() and not _busy and not _cutscene() \
			and Input.is_action_just_pressed("interact"):
		_run_zone(_zones[_near])


## npc.gd's guard, and for the same reason: `interact` is also a dialog-advance
## key, so without this the press that advances _ebb_night/_research_night would
## ALSO open a zone and park a second say() on the one DialogBox — one advance
## then resumes both. The research phase spawns her ON desk_spot, i.e. inside
## the ledger zone, so _near is set from the first physics frame and even the
## opening card is exposed. _busy alone can't cover it: only _run_zone sets it.
func _cutscene() -> bool:
	return not is_instance_valid(player) or not player.is_physics_processing()


func _spawn_fuji() -> void:
	_fuji = NPCScene.instantiate()
	_fuji.display_name = "Fuji"
	_fuji.sheet = SHEET_FUJI
	_fuji.frame_cols = 10
	_fuji.position = player.global_position
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
	# ---- cast three: THE SYNC. She flicks; the mountain answers. No spark
	# leaves the bead — the magic is already gone, and the quake covers it.
	await theater.wait(0.5)
	_fuji.sprite.flip_h = true
	_fuji.sprite.play("act")
	await theater.wait(SYNC_WINDUP)
	await _quake(QUAKE_HOLD_ACT)
	await theater.wait(1.2)          # the stillness after
	_fuji.play_idle()
	await theater.wait(0.7)
	await theater.say("Fuji", "...Did I do that?")
	await theater.say("Fuji", "...That was the ground. That was DEFINITELY the ground. Ground does that.")
	await theater.say("Fuji", "...Everything seems okay, though? Nothing even fell.")
	await theater.say("Fuji", "Where was I. Coffee.")
	theater.close_dialog()
	# ---- cast four: NOTHING. No spark, and nothing to blame it on.
	await theater.wait(0.5)
	_fuji.sprite.flip_h = true
	_fuji.sprite.play("act")
	await theater.wait(1.5)
	_fuji.sprite.stop()              # she flicks it again -
	_fuji.sprite.play("act")
	await theater.wait(1.5)
	_fuji.play_idle()                # - and lowers it, looking at it
	await theater.wait(2.0)          # the held silent beat
	await theater.say("Fuji", "...It's not the wand.")
	await theater.say("Fuji", "...Is it just my wand?")
	await theater.say("Fuji", "...I need to go and see.")
	theater.close_dialog()
	_hand_control()


## The cutscene ends IN the room — no fade, no card, nobody drags her out.
## The puppet goes and her real body takes its place on the SAME front-facing
## pose (npc_fuji_gen is drawn to her canonical player sheet's geometry off
## the same palette, so the change reads as nothing); from here the player
## walks her out her own door.
func _hand_control() -> void:
	Game.set_flag("ebb_done")
	var spot := _fuji.global_position
	_fuji.queue_free()
	_fuji = null
	player.global_position = spot
	player.visible = true
	player.sprite.play("idle_down")
	theater.unlock_party()
	theater.hint("GO OUTSIDE - THE SOUTH DOOR", 2.2)


# ---- Act 1 beat 2: the research gate ---------------------------------------

## Weeks after the Ebb, in the same room. She has read everything in it and
## found nothing, and the beat hands control straight back — this is a GATE,
## not a cutscene. The ledger on her desk is the only clue: the catalogue
## says shelf nine holds eleven titles, and shelf nine holds twelve spines.
## The twelfth was never catalogued because nobody ever accessioned it, which
## is also the honest answer to how it crossed an ocean — nobody wrote that
## down either.
func _research_night() -> void:
	_research = true
	theater.fade.modulate.a = 1.0
	await theater.wait(0.5)
	await theater.card("SOME WEEKS LATER.")
	await theater.clear(1.2)
	await theater.wait(0.7)
	await theater.say("Fuji", "Six weeks. Every shelf in this room, twice.")
	await theater.say("Fuji", "Every book about magic in Lanternwood says the same thing. What magic IS. What it DOES.")
	await theater.say("Fuji", "Not one of them says what to do when it stops.")
	theater.close_dialog()
	await theater.wait(0.6)
	await theater.say("Fuji", "...Fine. Properly, then. From the ledger.")
	theater.close_dialog()
	theater.unlock_party()
	theater.hint("READ THE LEDGER - THE DESK", 2.2)


# ---- ACT 1 BEAT 3: THE KIT (2026-07-28) ----------------------------------------------
# She has the thesis and a destination and owns nothing that can hurt anything.
# So the room she has been reading in for six weeks becomes a supply list.
#
# THE WHOLE POINT: her kit is a LIBRARIAN'S. The shelf gives her the dose, the
# dead wand becomes the pipe, and the weapon is a book. Nothing is invented,
# nothing is found in a chest — it is one room she already had, used correctly.
# And it happens BEFORE she ever meets Basil, which is what makes her the right
# person to go and get him: she is the only other creature alive who answered a
# drained world the way he did, and she has no idea yet.
#
# Deliberately built on the SHELVES that already exist rather than new anchors:
# the three stacks are already a wander gate with three distinct brass plates,
# so "which book do you take" is answered by WALKING somewhere.

## Which shelf yields which book. The husbandry manual is the one that already
## saved her life; the grain tithes are the heaviest object in the building and
## she knows it; the enchantment theory is nine hundred pages of subject matter
## that stopped being true six weeks ago.
const SHELF_BOOKS := [&"husbandry", &"bound_ledger", &"principles"]


func _kit_night() -> void:
	theater.fade.modulate.a = 1.0
	await theater.wait(0.5)
	await theater.clear(1.0)
	# Re-entry mid-kit (the lane is still out there and she can duck back in)
	# skips the resolve speech — it only makes sense said once.
	if Game.flag("fuji_dose_found") or Game.flag("fuji_darts_made") \
			or Game.flag("fuji_tome_taken"):
		theater.unlock_party()
		theater.hint("SHELF THREE   THE COUNTER   PICK A BOOK", 3.0)
		return
	await theater.say("Fuji", "Right. He's across an ocean and the road there has things on it.")
	await theater.say("Fuji", "And I have... a dead stick and a library card.")
	theater.close_dialog()
	await theater.wait(0.6)
	await theater.say("Fuji", "...No. I have a LIBRARY.")
	theater.close_dialog()
	theater.unlock_party()
	theater.hint("SHELF THREE   THE COUNTER   PICK A BOOK", 3.0)


## Progress check, run after every kit step. Sets the flag the street reads.
func _kit_check() -> void:
	if Game.flag("fuji_kit_made"):
		return
	if Game.flag("fuji_dose_found") and Game.flag("fuji_darts_made") \
			and Game.flag("fuji_tome_taken"):
		Game.set_flag("fuji_kit_made")
		await theater.say("Fuji", "A dose, a pipe, and something heavy. That's a kit.")
		theater.close_dialog()
		theater.hint("GO OUT THE DOOR", 2.4)


## Shelf three, husbandry — where you look up how to put a large animal down to
## have its hooves trimmed. That is the sleep dart, and it is pharmacology, and
## she reads it off a shelf. Shelf NINE, enchantment theory, is worthless now.
## The room says that on its own; nobody says it out loud.
func _kit_dose() -> void:
	await theater.say("Fuji", "Husbandry. Bees, weather, and... hooves.")
	await theater.say("Fuji", "'To trim the hooves of a full-grown ox, the beast must first be put down soft.'")
	theater.close_dialog()
	await theater.wait(0.7)
	await theater.say("Fuji", "'Two grains to the hundredweight. It comes on slow. Do not stand where it will fall.'")
	theater.close_dialog()
	await theater.wait(0.5)
	await theater.say("Fuji", "...Two grains to the hundredweight.")
	Game.set_flag("fuji_dose_found")
	await _kit_check()


## The delivery problem, solved with the thing already in her hand. A wand is a
## stick. Hers has been dead for six weeks. TWO VISITS on purpose — she stops
## halfway, and the player has to come back and finish it.
func _kit_wand() -> void:
	if Game.flag("fuji_darts_made"):
		await theater.say("Fuji", "A tube, a dose, and a good hard breath. It'll do.")
		return
	if not Game.flag("fuji_dose_found"):
		await theater.say("Fuji", "Something to put it IN. That's the other half.")
		return
	if not _wand_half:
		_wand_half = true
		await theater.say("Fuji", "It's a stick. It has always just been a stick.")
		theater.close_dialog()
		await theater.wait(0.8)
		await theater.say("Fuji", "Hollow it out and it's a tube. Hollow it out and it's -")
		theater.close_dialog()
		await theater.wait(1.0)
		await theater.say("Fuji", "...")
		theater.close_dialog()
		theater.hint("SHE PUT IT DOWN HALFWAY", 2.4)
		return
	await theater.say("Fuji", "...It was never the wand. It was never going to be the wand again.")
	theater.close_dialog()
	await theater.wait(0.6)
	await theater.say("Fuji", "So it may as well be useful.")
	Game.set_flag("fuji_darts_made")
	theater.close_dialog()
	await _kit_check()


## The book. Whichever shelf she takes it from is her weapon for the whole game.
## The tender half costs one line: she reaches for the one she loves FIRST, and
## puts it back, because you do not hit things with a book you love.
func _kit_book(i: int) -> void:
	if Game.flag("fuji_tome_taken"):
		await theater.say("Fuji", STACKS[i].line)
		await theater.say("Fuji", "I've got mine. The rest of you stay where you are.")
		return
	if not _wand_half and not Game.flag("fuji_dose_found"):
		await theater.say("Fuji", STACKS[i].line)
		await theater.say("Fuji", "Something to swing. But not yet - the dose first.")
		return
	if not Game.flag("fuji_reached_first"):
		Game.set_flag("fuji_reached_first")
		await theater.say("Fuji", "...")
		theater.close_dialog()
		await theater.wait(0.6)
		await theater.say("Fuji", "Not this one. Never this one.")
		await theater.say("Fuji", "You don't hit things with a book you love.")
		theater.close_dialog()
		await theater.wait(0.5)
		theater.hint("PICK ONE YOU CAN LIVE WITH BREAKING", 2.8)
		return

	var book_id: StringName = SHELF_BOOKS[i]
	var book := Items.get_item(book_id)
	await theater.say("Fuji", STACKS[i].line)
	await theater.say("Fuji", "...This one. %s." % book.display_name)
	theater.close_dialog()
	await theater.wait(0.5)
	await theater.say("Fuji", "Heavy. That's the whole review.")
	# The chosen book goes straight into the WEAPON slot, not the satchel: it is
	# already in her hands. Game.fuji_tome remembers which one for later scenes.
	Game.fuji_tome = book_id
	Game.sheet(&"fuji").equip(Item.Kind.WEAPON, book_id)
	Game.set_flag("fuji_tome_taken")
	theater.close_dialog()
	await _kit_check()


## The desk. Outside the research beat it is just her desk; inside it, the
## accession ledger is the clue, and reading it is what makes shelf nine
## searchable at all.
func _read_ledger() -> void:
	if Game.flag("thesis_found"):
		await theater.say("Fuji", "Not in the ledger. Not in ANY ledger. Somebody just... left it here.")
		return
	if not _research:
		await theater.say("Fuji", "One more chapter. ...It'll keep.")
		return
	if Game.flag("ledger_read"):
		await theater.say("Fuji", "Shelf nine. Eleven titles listed. Twelve spines on the shelf.")
		return
	await theater.say("Fuji", "Accessions. Every book this library ever took in, in somebody's handwriting.")
	await theater.say("Fuji", "Shelf three, husbandry, forty-one titles. Shelf six, histories, ninety-two.")
	await theater.say("Fuji", "Shelf nine. Enchantment, theory. ...Eleven titles.")
	theater.close_dialog()
	await theater.wait(0.8)
	await theater.say("Fuji", "...Eleven.")
	await theater.say("Fuji", "I have counted TWELVE spines on that shelf every week for six weeks.")
	await theater.say("Fuji", "I have never once counted the ledger.")
	Game.set_flag("ledger_read")
	theater.close_dialog()
	theater.hint("FIND SHELF NINE", 2.2)


## A stack. Every one reads its brass plate; only shelf nine, and only once
## the ledger has told her what to look for, gives up the twelfth thing.
func _search_stack(i: int) -> void:
	# On the kit night the stacks are a weapons rack. Shelf three is also where
	# the dose comes from, so it answers whichever question is still open.
	if _kit:
		if i == 0 and not Game.flag("fuji_dose_found"):
			await _kit_dose()
		else:
			await _kit_book(i)
		return
	if i == ANSWER and Game.flag("ledger_read") and not Game.flag("thesis_found"):
		await _find_thesis()
		return
	await theater.say("Fuji", STACKS[i].line)
	if not _research:
		return
	if i == ANSWER:
		await theater.say("Fuji", "Read them. Read them all. ...Twice.")
	elif Game.flag("ledger_read"):
		await theater.say("Fuji", "Not this one. Nine. It has to be nine.")


## The find, and the end of the beat: she pulls the row, the twelfth spine
## isn't a book, and she carries it to the lamp to read it. No narrator box —
## she has the whole thing in her own mouth (the narration purge).
func _find_thesis() -> void:
	await theater.say("Fuji", "Eleven titles. All right. One... four... nine, ten, eleven -")
	theater.close_dialog()
	await theater.wait(0.9)
	theater.hop(player, 4.0)
	await theater.say("Fuji", "- twelve.")
	theater.close_dialog()
	await theater.wait(0.7)
	await theater.say("Fuji", "It isn't a book. It's PAPER. Somebody's paper, string-tied, shoved in behind the rest.")
	await theater.say("Fuji", "No spine. No binding. No accession stamp.")
	await theater.say("Fuji", "Nobody ever wrote this down. It just... got here.")
	theater.close_dialog()
	# to the lamp: dog-leg the aisle, since theater walks are straight
	# no-collision tweens and the desk sits between her and the light
	await theater.walk_via(player, [
		MapData.anchor_px(map, "stack_c") + Vector2(32.0, 0.0),
		MapData.anchor_px(map, "stack_c") + Vector2(32.0, -32.0),
		MapData.anchor_px(map, "desk_spot")])
	theater.face(player, Vector2.UP)
	await theater.wait(0.9)
	await theater.say("Fuji", "\"ON RE-ENCHANTMENT: WHY SCIENCE IS MAGIC'S EQUAL.\"")
	await theater.say("Fuji", "B. Basil.")
	theater.close_dialog()
	await theater.wait(0.8)
	await theater.say("Fuji", "There's a note in the margin. Not his hand - somebody else's, pressed hard enough to dent the page.")
	await theater.say("Fuji", "\"Laughed out of the Academy.\"")
	theater.close_dialog()
	await theater.wait(1.4)
	await theater.say("Fuji", "...Magic isn't gone. It's asleep. And it can be woken, and here is HOW.")
	await theater.say("Fuji", "Somebody worked this out. Years ago. And they laughed at him and shelved him and forgot which shelf.")
	theater.close_dialog()
	await theater.wait(0.9)
	await theater.say("Fuji", "...Where are you, B. Basil?")
	Game.set_flag("thesis_found")
	theater.close_dialog()
	theater.hint("GO AND FIND HIM", 2.2)


## Out into her own street — the SAME night (no card: no time passes between
## her floor and the town), where the whole neighborhood is out comparing
## dead charms. lanternwood.gd lands her a step south of this door.
func _on_exit_door(body: Node) -> void:
	if not body.is_in_group("player") or _leaving:
		return
	_leaving = true
	Game.town_spawn = "library"
	# Deferred: freeing the scene inside the Area2D callback is a physics error.
	get_tree().change_scene_to_file.call_deferred(NEXT_SCENE)


## One wand attempt: `n` sparks off the bead, `hits` of them reaching the
## kettle (a bright blink on the spout), the rest going wide and popping
## into little poofs on the floorboards — the mess. Hits INTERLEAVE with the
## misses (nearly, no, nearly, no) rather than front-loading.
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
		var to_kettle := i % 2 == 0 and i < hits * 2
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
## the mountain scene rolls, wall-clock throughout (elapsed via ticks, steps
## via timers, never frame counts: the uncapped occluded-window gotcha).
## `startle_at` is when she breaks the cast pose — she holds the
## follow-through first, because as far as she knows the follow-through is
## what did this.
func _quake(startle_at := -1.0) -> void:
	var start := Time.get_ticks_msec()
	var startled := false
	while true:
		var t := float(Time.get_ticks_msec() - start) / 1000.0
		if t >= QUAKE_TIME:
			break
		if not startled and startle_at >= 0.0 and t >= startle_at:
			startled = true
			_fuji.sprite.flip_h = false
			_fuji.play_emote()       # ears flat, shoulders up
		var amp := lerpf(QUAKE_AMP_LO, QUAKE_AMP_HI, t / QUAKE_TIME)
		_cam.offset = Vector2(randf_range(-amp, amp), randf_range(-amp, amp))
		await get_tree().create_timer(QUAKE_STEP).timeout
	_cam.offset = Vector2.ZERO


## The room's interact zones: stand at a thing, press interact. Most just say
## a line; the desk and the three stacks are the research gate. Every zone is
## skippable — the walk-out gates on nothing but the door.
func _wire_look_zones() -> void:
	_look("H", "The fire's fine. The fire never needed me.")
	_look("W", "...Lamps lit in every window. Nobody's gone back to bed.")
	# The counter is a look-at line in every phase but ONE: on the kit night it
	# is the workbench she bores the wand out on. Same cell, same zone — a beat
	# earns a piece of furniture rather than adding one.
	_look_or("cC", "Stone cold. It never even got warm.", _kit_wand)
	_look("K", "Nine hundred books in this room. Not one of them is about THIS.", -32.0)
	_zone("nook", MapData.anchor_px(map, "nook"),
			func() -> void: await theater.say("Fuji",
					"Somebody's chair. Nobody's sat in it since the lamps went strange."))
	_zone("ledger", MapData.anchor_px(map, "desk_spot"), _read_ledger)
	for i in STACKS.size():
		var idx := i             # bind the index, not the loop variable
		_zone("stack%d" % i, MapData.anchor_px(map, STACKS[i].anchor),
				func() -> void: await _search_stack(idx))


## A plain look-at line, keyed off a feature's bbox. `nudge` shifts the zone
## off the bbox's center column when a char has several runs sharing one bbox.
func _look(chars: String, line: String, nudge := 0.0) -> void:
	var box := MapData.bbox_rect(map, chars)
	_zone(chars, _look_cell(box.get_center().x + nudge, box.end.y),
			func() -> void: await theater.say("Fuji", line))


## A look-at line that becomes a WORKBENCH on the kit night. Same cell, same
## zone, two jobs — a beat should earn a piece of furniture rather than adding
## one, and a second zone on the same cell would silently replace this one in
## `_zones` (it is keyed by id) and leave an orphan Area2D behind.
func _look_or(chars: String, line: String, action: Callable, nudge := 0.0) -> void:
	var box := MapData.bbox_rect(map, chars)
	_zone(chars, _look_cell(box.get_center().x + nudge, box.end.y),
			func() -> void:
				if _kit:
					await action.call()
				else:
					await theater.say("Fuji", line))


## One interact zone at a world position, running `action` on the button.
func _zone(id: String, at: Vector2, action: Callable) -> void:
	_zones[id] = action
	var zone := Area2D.new()
	zone.collision_layer = 0
	zone.collision_mask = 2
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = LOOK_ZONE
	shape.shape = rect
	zone.add_child(shape)
	zone.position = at
	add_child(zone)
	zone.body_entered.connect(func(body: Node2D) -> void:
		if body.is_in_group("player"):
			_near = id)
	zone.body_exited.connect(func(body: Node2D) -> void:
		if body.is_in_group("player") and _near == id:
			_near = "")


## The floor cell a body stands on to look at a feature: scan south from the
## bbox for the first walkable cell in its column (the north-wall pieces sit
## above a solid wall row, the floor pieces sit straight on the floor).
func _look_cell(x: float, bottom: float) -> Vector2:
	var cx := int(x / 16.0)
	var ty := int(bottom / 16.0)
	while ty < map.rows and MapData.is_solid(map, Vector2i(cx, ty)):
		ty += 1
	return Vector2(cx * 16 + 8, ty * 16 + 8)


## Run a zone's action, on the downstairs_fest door-hint idiom: hold the room
## while the box is up so she can't walk out from under her own sentence.
func _run_zone(action: Callable) -> void:
	_busy = true
	theater.lock_party()
	await action.call()
	theater.close_dialog()
	theater.unlock_party()
	_busy = false


