extends Node2D

## The great room, FESTIVAL MORNING — the second beat of the home-start
## opening (2026-07-12 pacing pass): Mom is at the hearth, and her good-morning
## is the front-door key (`prologue_saw_mom`). She STAYS home all festival
## (2026-07-15 — no duplicate festival Mom): after the three stings Basil
## doubles back through his own front door, and her blessing by the hearth
## is what opens the south gate (`prologue_gate_open`). Same map/tiles/props
## as the drained-era downstairs (the workshop corner has always been
## half-built — this family tinkers), brighter tint, fire and boiler alive.
## Out the front door lies the festival town at Basil's home door.
##
## THE BREW (2026-07-25) is this room's third beat, gated on flags rather than
## a router: back off the bluff with Kitty and an idea, Basil mixes the four
## reagents that go up over the recital. The workshop corner has always been
## half-built — this is the day it gets used.

const MAP_PATH := "res://assets/maps/downstairs.txt"
const LAYOUT_PATH := "res://assets/tilesets/downstairs_layout.txt"
const PROPS_PATH := "res://assets/tilesets/downstairs_props.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const SHEET_MOM := preload("res://assets/npc_mom_gen.png")
const SHEET_KITTY_KID := preload("res://assets/npc_kitty_gen.png")
const FX_SHEET := preload("res://assets/prologue_fx.png")

const FX_POOF := 17
const FX_BEAKER := 24

const DIM_MORNING := Color(0.9, 0.85, 0.9)     # festival daylight indoors
const FIRE_OFFSET := Vector2(10.0, 20.0)       # see scene/downstairs.gd

## The four reagent colours the stir cycles through, straight off the compound
## registry — this flask is the literal ancestor of the beakers the adult pours
## into his gun, so the four colours must never be re-typed as Color() literals
## here and drift apart from Alchemy's.
const REAGENTS := [Alchemy.GREEN, Alchemy.BLUE, Alchemy.RED, Alchemy.PURPLE]

var map: Dictionary
var player: Node2D
var _anim_t := 0.0
var _busy := false
var _mom: NPC
var _kitty: NPC
var _flask: Sprite2D

@onready var theater: Theater = $Theater


## Mom is home before the first leaving, and from the blessing double-back
## on she STAYS home — pies don't bake themselves, and vanishing right after
## her big scene read as a continuity hole.
func _mom_home() -> bool:
	return not Game.flag("prologue_left_home") or Game.flag("prologue_want_home")


## THE BREW (2026-07-25) — the third beat this one room plays, gated on flags
## rather than a router (the town_thesis / bluff / library idiom: one scene,
## N phases). Back off the bluff with Kitty and an idea, Basil mixes the four
## reagents that will go up over the recital.
func _brewing() -> bool:
	return Game.flag("prologue_whirligig_done") and not Game.flag("prologue_potion_made")


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	PropSpawner.build(PROPS_PATH, map, $World)
	$Dim.color = DIM_MORNING
	var spawn := Game.interior_spawn
	Game.interior_spawn = ""
	if spawn.is_empty() or not map.anchors.has(spawn):
		spawn = "stair_arrival"
	var spawn_px := MapData.anchor_px(map, spawn)
	# the doorway is 2 cells wide — center on the arch, not the anchor's
	# whole-cell column (8px west of it)
	var door_x := MapData.bbox_rect(map, "-").get_center().x
	if spawn == "front_door":
		spawn_px.x = door_x
	player = Party.spawn($World, spawn_px)
	Party.clamp_cameras(MapData.view_size())
	$Fire.position = MapData.bbox_rect(map, "H").position + FIRE_OFFSET
	if _mom_home():
		_spawn_mom()
	$ExitDoor.position = Vector2(door_x, MapData.anchor_px(map, "exit_door").y)
	$ExitDoor.body_entered.connect(_on_exit_door)
	if _brewing():
		_brew()
	elif not Game.flag("prologue_saw_mom"):
		theater.hint("SAY GOOD MORNING TO MOM - E TO TALK")
	elif Game.flag("prologue_want_home") and not Game.flag("prologue_gate_open"):
		theater.hint("MOM'S BY THE HEARTH")


func _spawn_mom() -> void:
	_mom = NPCScene.instantiate()
	_mom.display_name = "Mom"
	_mom.sheet = SHEET_MOM
	_mom.frame_cols = 10               # cols 6-9: back x2 + side x2, drawn with
	                                   # the walk rows (2026-07-29) — without
	                                   # this she owns the art and never turns
	if _brewing():
		# elbow-deep in pie and now sharing her kitchen with a chemistry set.
		# Checked BEFORE the gate_open branch, which would otherwise hand her
		# the go-to-the-meadow lines while there's a flask on her workbench.
		_mom.lines = PackedStringArray([
			"That is my GOOD copper pot. ...Fine. FINE. Just not on the ceiling.",
			"Hello, dear. Are you the one who's been keeping him out on that headland?",
			"He's been quiet all week. Quiet means he's THINKING. Take cover.",
		])
	elif Game.flag("prologue_potion_made") and not Game.flag("prologue_recital"):
		_mom.lines = PackedStringArray([
			"GO. You will be late for your own recital.",
		])
	elif Game.flag("prologue_gate_open"):
		# post-blessing: she's still here, elbow-deep in pie
		_mom.lines = PackedStringArray([
			"Still here? The meadow won't sulk FOR you, sweetheart.",
			"Home before the lamps. And if that goose follows you, it is NOT staying for dinner.",
		])
	elif Game.flag("prologue_want_home"):
		# the double-back: he came home stung; her lines open the blessing
		_mom.lines = PackedStringArray([
			"Basil? Back already - and with a face like wet flour. Come here.",
		])
	else:
		_mom.lines = PackedStringArray([
			"Morning Sunshine!",
			"It's the Founding Festival, sweetheart. Everyone's out.",
			"I think I saw Sage out there. Go play with your friends!",
		])
	# by the hearth, flour on her paws
	_mom.position = Vector2(4.0 * 16.0 + 8.0, 5.0 * 16.0 + 8.0)
	# ...and she WORKS the kitchen rather than standing in it (2026-07-29). The
	# box is the hearth end only — cols 3-5, rows 5-9 — which is fifteen cells of
	# clear floor. It stops at col 5 on purpose: east of that is the table base
	# at (7,7)/(8,7), then the stair alcove, then the row-5 lane Kitty's brew
	# route tweens along, and the front door sits at (184,184) a good 88px clear
	# of anywhere she can reach. She is elbow-deep in pie; she is not leaving.
	_mom.wander_cells = Rect2i(3, 5, 3, 5)
	_mom.wander = true
	_mom.wander_rest = "act"        # she goes back to the dough every time she stops
	_mom.bind_map(map)
	_mom.talked.connect(_on_mom_talked)
	$World.add_child(_mom)
	_mom.play_act()


func _on_mom_talked(_npc: NPC) -> void:
	if not Game.flag("prologue_saw_mom"):
		Game.set_flag("prologue_saw_mom")
		theater.hint("THE FESTIVAL AWAITS - OUT THE FRONT DOOR")
		return
	if Game.flag("prologue_want_home") and not Game.flag("prologue_gate_open"):
		_mom_blessing()


## Her blessing is the gate key: warmth first, permission second (ported
## from the festival-Mom beat when the blessing moved home, 2026-07-15).
func _mom_blessing() -> void:
	theater.lock_party()
	_mom.play_idle()
	await theater.say("Mom", "Basil, what's the matter?")
	player.sprite.play("sad")
	await theater.say("Basil", "Maybe I'm just not magic like everyone else...")
	await theater.say("Mom", "Listen to me. Magic is common as dandelions. You've got science!")
	_mom.play_emote()
	await theater.say("Mom", "You made me that amazing remedy last time I was sick didn't you?")
	await theater.say("Mom", "You'll always be magic to me sweetheart.")
	await theater.say("Basil", "...You have to say that. You're my mom.")
	await theater.say("Mom", "And moms are always right.")
	await theater.say("Mom", "Now scoot. Sulk somewhere sunny. Ride your bike out to the coast or something.")
	theater.close_dialog()
	player.sprite.play("idle_down")
	Game.set_flag("prologue_gate_open")
	theater.unlock_party()
	theater.hint("THE SOUTH GATE IS OPEN")


# ---- the brew ---------------------------------------------------------------------

## The workbench pocket has exactly ONE entrance — the bench base (row 8) is
## solid below it, the armchair and boiler wall off row 6, and the plant seals
## row 5's east end — so the only route in is x17 down the row-5 lane. A band
## over the whole bench top therefore cannot be walked around: the gate is
## unavoidable for its objective, which is the law.
func _brew() -> void:
	theater.lock_party()                   # before any await — a probe polling
	                                       # the unlock must not see frame 1 free
	_spawn_kitty()
	var bench := MapData.bbox_rect(map, "E")
	await theater.wait(0.6)
	# she is always here in the real chain (_mom_home is true — the brew's flag
	# ladder carries both left_home and want_home), but posing a null Mom would
	# be a hard crash rather than a missing line, so the greeting is guarded
	if _mom != null:
		_mom.play_emote()
		await theater.say("Mom", "BASIL. And a friend. Wipe your paws, both of you? What is that?")
		await theater.say("Kitty", "It's a whirligig. I made it. It flies. I'm Kitty.")
		await theater.say("Mom", "Nice to meet you Kitty.")
		await theater.say("Basil", "Let's use my lab.")
		_mom.play_act()
	theater.close_dialog()
	_kitty_to_bench()                      # un-awaited: it plays out under the gate
	theater.hint("THE WORKBENCH - THE EAST CORNER")
	await theater.walk_gate(bench.get_center(), bench.size + Vector2(0.0, 8.0))
	# he takes the middle of the bench: she is parked at its EAST end (the
	# pocket's only entrance is its west cell, so she can never be the one
	# standing in it) and the flask goes between them
	await theater.walk(player, Vector2(bench.position.x + 24.0, bench.get_center().y), 45.0)
	theater.face(player, Vector2.DOWN)     # tucked in BEHIND the counter, the
	                                       # workbench art drawing over his legs
	_kitty.play_act()
	await theater.say("Basil", "Everyone at that recital has magic.")
	await theater.say("Basil", "I don't. But I know how to do cool things.")
	await theater.say("Kitty", "You are going to shoot those out of my whirlygig!?")
	await theater.say("Basil", "That's the idea, but first we need to put it together.")
	theater.close_dialog()
	# the stir: the four reagents go in one at a time, and the flask takes the
	# colour of whichever is on top
	_flask = WorldFx.airborne($World, FX_SHEET, FX_BEAKER,
			bench.get_center() + Vector2(12.0, 16.0), 26.0)
	_flask.modulate = REAGENTS[0]
	await theater.mash_meter("STIR IT! MASH E", _flask_tick)
	Game.set_flag("prologue_potion_made")
	var poof := WorldFx.airborne($World, FX_SHEET, FX_POOF,
			_flask.position, 26.0)
	await theater.wait(0.5)
	poof.queue_free()
	_flask.modulate = REAGENTS[3]
	player.sprite.play("happy")
	_kitty.play_emote()
	await theater.say("Kitty", "...Basil. That's four.")
	await theater.say("Basil", "That's four.")
	if _mom != null:
		_mom.play_emote()
		await theater.say("Mom", "Whatever that is, it is not staying in my kitchen.")
	await theater.say("Kitty", "It isn't. It's going to the Academy.")
	theater.close_dialog()
	player.sprite.play("idle_down")
	theater.unlock_party()
	theater.hint("THE ACADEMY - ACROSS TOWN, UP THE STAIR")


## She heads for the bench while the walk over is his own — fired un-awaited so
## it plays out under the walk-gate. theater.walk_via turns her along each leg
## (2026-07-29), so the lane north reads as a back and the run east as a profile
## instead of the old front-facing glide.
##
## She ARRIVES in the act pose, deliberately: the last leg is necessarily
## EASTWARD (the pocket's only entrance is its west cell), so auto-facing would
## leave her staring into the corner until the dialogue starts, and the whole
## bench beat is staged front-first behind the counter anyway — Basil faces DOWN
## there too. It also means the beat's own _kitty.play_act() can never be
## clobbered by this coroutine landing late (the player's walk-gate can resolve
## in a fraction of the 3s crossing, and a probe teleports).
func _kitty_to_bench() -> void:
	await theater.walk_via(_kitty, [
			Vector2(208.0, 88.0),          # x13, the clear vertical lane
			Vector2(280.0, 88.0),          # east along row 5 to the pocket mouth
			Vector2(280.0, 120.0),         # down onto the bench top
			MapData.anchor_px(map, "kitty_pos")], 70.0)
	_kitty.play_act()


## The flask takes each reagent's colour as it goes in — green, blue, red, and
## the purple that only exists because the first two went in together.
func _flask_tick(fill: float) -> void:
	if is_instance_valid(_flask):
		_flask.modulate = REAGENTS[mini(int(fill * REAGENTS.size()), REAGENTS.size() - 1)]


func _spawn_kitty() -> void:
	_kitty = NPCScene.instantiate()
	_kitty.display_name = "Kitty"
	_kitty.sheet = SHEET_KITTY_KID
	_kitty.frame_cols = 10                 # cols 6-9: back x2 + side x2 — she
	                                       # crosses the whole room to the bench,
	                                       # and that walk is the one place in the
	                                       # brew she isn't stood still
	_kitty.position = Vector2(208.0, 152.0)
	_kitty.lines = PackedStringArray([
		"Your mother is so sweet. I love her.",
	])
	$World.add_child(_kitty)


func _process(delta: float) -> void:
	# the room's little life (see scene/downstairs.gd)
	_anim_t += delta
	$Fire.frame = int(_anim_t / 0.16) % 3
	$World/Boiler.frame = int(_anim_t / 0.28) % 4


func _on_exit_door(body: Node) -> void:
	if not body.is_in_group("player") or _busy:
		return
	if not Game.flag("prologue_saw_mom"):
		_door_hint("Can't just leave. Need to say goodbye to mom.")
		return
	# softlock guard: he came home FOR Mom — the door refuses until the
	# blessing opens the gate
	if Game.flag("prologue_want_home") and not Game.flag("prologue_gate_open"):
		_door_hint("No. I came home to talk to Mom. She's by the hearth.")
		return
	# same softlock guard, one beat later: out there the south gate now refuses
	# and the Academy door is still dead, so leaving mid-brew is a dead wander
	if _brewing():
		_door_hint("Not yet. The flask first - Kitty's holding the crank.")
		return
	_busy = true
	Game.set_flag("prologue_left_home")
	Game.town_spawn = "home"
	get_tree().change_scene_to_file.call_deferred("res://scene/town_fest.tscn")


func _door_hint(line: String) -> void:
	_busy = true
	theater.lock_party()
	await theater.say("Basil", line)
	theater.close_dialog()
	theater.unlock_party()
	_busy = false


