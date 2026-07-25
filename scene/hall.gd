extends Node2D

## The Alembic Academy lecture hall — Prologue B "the naming" (docs/DESIGN.md
## Story). Basil delivers his re-enchantment thesis; Schweinler smells the
## bag on his paws and brands him "Professor Poopy Paws"; the gallery laughs;
## the cards fall. The emotional core of the prologue. Restaged 2026-07-18
## as a COLLEGE hall: a raised north STAGE closed by the apron riser, three
## tiered bench rows of audience seen from BEHIND (back cells, sheet cols
## 6-7), Basil entering from STAGE RIGHT — from behind the west CURTAIN LEG
## (the 2026-07-18 curtain pass: red valance + drapes dress the opening) —
## and fleeing back behind it the moment the laughing starts, one crushed
## "But... I..." and Schweinler's encore on the way down — the flee is
## automatic (his body giving up), the laugh rolls on around it. Interior scene
## pattern (Tiles -> Collision -> y-sorted World -> TilesUpper), the cast
## are one-row NPC sprites posed by the Theater, then it hands to bluff
## call1.
##
## TWO BEATS, ONE ROOM, twenty years apart (Game.hall_phase, 2026-07-25):
##   ""        Prologue B's naming, above — the default this room was built for.
##   "recital" Prologue A's kid magic recital: the night a ten-year-old with no
##             aptitude flew a loaded whirligig over the house and got told to
##             apply. Deliberately the OPPOSITE staging, not a copy — the stage
##             is sealed by the apron riser (rows 3-4 have no walkable link to
##             the house at all; adult Basil only ever spawns and fades there),
##             so the kid isn't ALLOWED up on it. He sets up on the floor with
##             the faculty looking down over the rail, and years later he
##             finally stands behind that podium and is destroyed at it.

const MAP_PATH := "res://assets/maps/hall.txt"
const LAYOUT_PATH := "res://assets/tilesets/hall_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const SHEET_SCHW := preload("res://assets/npc_schweinler_adult_gen.png")
const SHEET_SCHW_KID := preload("res://assets/npc_schweinler_gen.png")
const SHEET_KITTY_KID := preload("res://assets/npc_kitty_gen.png")
const SHEET_OWL := preload("res://assets/npc_owl_gen.png")
const SHEET_SHEEP := preload("res://assets/npc_sheep_gen.png")
const SHEET_MOUSE := preload("res://assets/npc_mouse_gen.png")
const SHEET_BADGER := preload("res://assets/npc_badger_gen.png")
const SHEET_STORK := preload("res://assets/npc_stork_gen.png")
const FX_SHEET := preload("res://assets/prologue_fx.png")

const FX_WHIRL_DROOP := 7
const FX_WHIRL_SPIN0 := 8
const FX_BURST_S := 22
const FX_BURST_B := 23
const FX_BEAKER := 24

const TINT_NAMING := Color(0.82, 0.78, 0.92)    # the authored plum (hall.tscn)
const TINT_RECITAL := Color(1.0, 0.96, 0.90)    # festival evening — same room,
                                                # opposite weather

## The four reagent colours, straight off the compound registry (see the same
## const in downstairs_fest.gd): what goes up over the house tonight is the
## same green/blue/red/purple the adult will be loading into a gun.
const FW_TINTS := [Alchemy.GREEN, Alchemy.BLUE, Alchemy.RED, Alchemy.PURPLE]

var map: Dictionary
var player: Node2D
var _dean: NPC
var _schw: NPC
var _kitty: NPC
var _panel: Array[NPC] = []
var _audience: Array[NPC] = []
var _aud_rest_y := 0.0
var _whirligig: Sprite2D
var _flask: Sprite2D
var _flying := false

@onready var theater: Theater = $Theater


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	PropSpawner.build("res://assets/tilesets/hall_props.txt", map, $World)
	# read-and-clear BEFORE any await, so a stale value can never re-route a
	# later entry into the wrong chapter
	var phase := Game.hall_phase
	Game.hall_phase = ""
	var recital := phase == "recital"
	$Dim.color = TINT_RECITAL if recital else TINT_NAMING
	# the recital comes in the back doors like everybody else — `door` (11,15)
	# was declared and unused until now, and x11 is the centre-aisle column, so
	# the walk up is straight and crosses no benchtop
	player = Party.spawn($World, MapData.anchor_px(map,
			"door" if recital else "player_spawn"))
	Party.clamp_cameras(MapData.size_px(map))
	if recital:
		_spawn_recital_cast()
		_recital()
	else:
		_spawn_cast()
		_naming_cutscene()


func _spawn_cast() -> void:
	# the judging panel behind the stage-LEFT desk — the Dean presides,
	# three faculty beside him; they stand on the tuck row behind the desk
	# so the desktop plane hides their legs (the desk() entity idiom)
	_dean = _npc("Dean Strix", SHEET_OWL, 6, "judge_1")
	_dean.play_act()                                   # a lecturing wing
	var jsheets := [SHEET_STORK, SHEET_BADGER, SHEET_SHEEP]
	for i in jsheets.size():
		_panel.append(_npc("", jsheets[i], 6, "judge_%d" % (i + 2)))
	# Schweinler heckles from the east aisle beside the front tier, turned
	# round to work the room (his sheet has no back cells; he never sits)
	_schw = _npc("Schweinler", SHEET_SCHW, 6, "schweinler_spot")
	_spawn_audience()


## A PACKED tiered gallery: three to a bench, six benches, EIGHTEEN in all —
## seated facing the stage, backs to the camera (sheet cols 6-7; frame_cols 8
## so npc.gd builds the back clip). Shared by both beats; the house is the
## house in either century. NEVER play_emote one of these — the emote cells are
## front-facing and the head would flip round.
func _spawn_audience() -> void:
	var sheets := [SHEET_SHEEP, SHEET_MOUSE, SHEET_BADGER]
	for i in 18:
		var a := _npc("", sheets[i % 3], 8, "aud_%d" % (i + 1))
		a.play_back()
		_audience.append(a)
	# read the authored rest pose rather than assuming 0 — _kill_bobs has to
	# put the heads back and npc.tscn owns where "back" is
	_aud_rest_y = _audience[0].sprite.position.y


func _npc(nm: String, sheet: Texture2D, cols: int, anchor: String) -> NPC:
	var npc: NPC = NPCScene.instantiate()
	npc.display_name = nm
	npc.sheet = sheet
	npc.frame_cols = cols
	npc.position = MapData.anchor_px(map, anchor)
	$World.add_child(npc)
	return npc


func _naming_cutscene() -> void:
	theater.lock_party()
	await theater.wait(0.6)
	theater.face(player, Vector2.RIGHT)
	# he waits in the stage-right wing; the Dean's welcome is the summons,
	# and the walk onto the stage is the player's own (the pacing pass —
	# control between every beat)
	await theater.say("Dean Strix", "...and so. Never before has a cat with no magic at all stood at this podium. The work stood for itself instead - every measured drop of it. The floor is yours, Basil.")
	theater.close_dialog()
	# the stage rows are the only path out of the wing (the apron riser
	# seals the platform's south edge), so a band across them just west of
	# the podium is unavoidable — the GATE GEOMETRY rule
	var podium := MapData.bbox_rect(map, "L")
	var stage_y := MapData.anchor_px(map, "lectern_spot").y
	await theater.walk_gate(Vector2(podium.position.x - 24.0, stage_y + 8.0),
			Vector2(16.0, 48.0))
	await theater.walk_via(player, [
			Vector2(podium.get_center().x - 32.0, stage_y),
			Vector2(podium.get_center().x, stage_y)], 55.0)
	theater.face(player, Vector2.DOWN)
	await theater.say("Basil", "Th-thank you, Dean. Esteemed faculty.")
	await theater.say("Basil", "My thesis is simple. Magic is not GONE where it seems absent. It is asleep. And what sleeps can be woken - measured, bottled, RE-KINDLED.")
	await theater.say("Basil", "You call my flasks 'potions.' They are chemistry. And chemistry does not need magic to be TRUE.")
	await theater.wait(0.4)
	# Schweinler, from the house
	_schw.play_idle()
	await theater.say("Schweinler", "Hold on. HOLD ON. Does anyone else... smell that?")
	theater.face(player, Vector2.DOWN)
	await theater.say("Basil", "S-Schweinler? Smell wh-")
	_schw.play_act()
	await theater.say("Schweinler", "LOOK at his paws! He TRACKED it! All the way up onto the STAGE!")
	await theater.hop(_schw, 5.0)
	_schw.play_emote()
	await theater.say("Schweinler", "A brilliant lecture, everyone. From PROFESSOR... POOPY... PAWS!")
	# the gallery ROARS. The house is rows of BACKS, so its laugh is all
	# body — every head gets its own looped bob, periods staggered so the
	# tiers RIPPLE instead of metronoming; the panel + Dean crack up
	# face-first (that's the sting)
	for j in _panel:
		j.play_emote()
	_dean.play_emote()
	var bobs: Array[Tween] = []
	for i in _audience.size():
		bobs.append(_laugh_bob(_audience[i], 0.13 + 0.03 * (i % 4),
				5.0 + float(i % 3)))
	theater.hop(_schw, 6.0)
	# he tries. It makes it worse — the stammer hands Schweinler the encore
	player.sprite.play("sad")
	await theater.say("Basil", "But... I...")
	_schw.play_act()
	await theater.say("Schweinler", "'BUT'?! HA! HE SAID BUTT! Even his EXCUSES are potty talk! Oink-hahaha!")
	_schw.play_emote()
	await theater.hop(_schw, 6.0)
	# nothing left to say — the head goes down and STAYS down a beat, the
	# laughter rolling on
	player.sprite.play("bow_head")
	await theater.wait(1.2)
	# and he's already retreating AS they laugh (the 2026-07-18 restage:
	# exit ON the laugh, not after the chant): the flee is automatic — his
	# body giving up — back behind the west curtain leg he entered from,
	# the chant rolling over the walk. The trudge is SLOW and BOWED (the
	# row-9 `defeat_walk` pair — head on his chest; theater.walk would
	# override it with walk_side, so the tween is hand-rolled), and the
	# curtain SWALLOWS him: his ~33px figure is wider than the 24px leg, so
	# the last steps fade his modulate out behind the drape — no tail left
	# hanging past the fabric while the chant rolls
	Game.set_flag("prologue_named")
	var wing := MapData.anchor_px(map, "wing_exit")
	player.sprite.play("defeat_walk")
	player.sprite.flip_h = true
	var trip := player.global_position.distance_to(wing) / 20.0
	# the fade rides the LAST 0.6s of the trudge — clamped, because a negative
	# delay is a tween error (and a short trip just fades the whole way)
	var fade_dur := minf(0.6, trip)
	var flee := create_tween().set_parallel()
	flee.tween_property(player, "global_position", wing, trip)
	flee.tween_property(player, "modulate:a", 0.0, fade_dur).set_delay(trip - fade_dur)
	await theater.say("Gallery", "Poopy Paws! POOPY PAWS! POOPY PAWS!")
	theater.close_dialog()
	# the chant can outrun the trudge (or the reverse) — wait the walk out
	if flee.is_running():
		await flee.finished
	for tw in bobs:
		tw.kill()
	await theater.wait(0.4)
	await theater.black(1.2)
	# "THE NAME STUCK." was cut (the 2026-07-18 card purge) — cards may
	# only say how much time passed; the dusk jump is the passage here
	await theater.card("THAT EVENING.", 1.8)
	# dusk falls on the bluff — she calls to ask how it went
	Game.bluff_phase = "call1"
	get_tree().change_scene_to_file("res://scene/bluff.tscn")


## One audience head's laugh: a looped sprite bob (the hop axis) at its own
## period + height, so eighteen of them read as a shaking crowd, not a drill
## team. Kill the returned tween when the beat ends.
func _laugh_bob(a: NPC, period: float, height: float) -> Tween:
	var base := a.sprite.position.y
	var tw := a.sprite.create_tween().set_loops()
	tw.tween_property(a.sprite, "position:y", base - height, period) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	tw.tween_property(a.sprite, "position:y", base, period) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	return tw


## Kill a bob set and PUT THE HEADS BACK. _laugh_bob captures its rest y at
## call time, and killing a looped tween mid-bob leaves the sprite wherever it
## stopped — start a second set on top and it treats a sunk head as the rest
## pose, so the tier sinks a little further every time. The naming never hit
## this because it kills once and fades immediately; the recital bobs twice.
func _kill_bobs(bobs: Array[Tween]) -> void:
	for tw in bobs:
		tw.kill()
	for a in _audience:
		a.sprite.position.y = _aud_rest_y


# ---- the recital (Prologue A) ------------------------------------------------------

func _spawn_recital_cast() -> void:
	# he presides from the podium the boy will one day stand behind. Still
	# "Professor" here — the Dean's chair comes later (town_fest names him).
	_dean = _npc("Professor Strix", SHEET_OWL, 6, "lectern_spot")
	_dean.play_act()
	var jsheets := [SHEET_STORK, SHEET_BADGER, SHEET_SHEEP]
	for i in jsheets.size():
		_panel.append(_npc("", jsheets[i], 6, "judge_%d" % (i + 2)))
	# the same east-aisle cell the grown one heckles from, twenty years early
	_schw = _npc("Schweinler", SHEET_SCHW_KID, 6, "schweinler_spot")
	_spawn_audience()


func _recital() -> void:
	theater.lock_party()                    # before any await
	var apron := MapData.bbox_rect(map, "D")
	var floor_y := apron.end.y + 8.0        # row 6 — the open strip below the
	                                        # riser, the only row adjacent to it
	var mid_x := apron.get_center().x
	# she comes in beside him but takes the WEST aisle column (x9) the whole
	# way up, leaving x10-11 clear — the aisle is only three cells wide and an
	# NPC is a solid StaticBody2D, so a shared column would block his own walk
	_kitty = _npc("Kitty", SHEET_KITTY_KID, 6, "door")
	_kitty.position += Vector2(-32.0, 0.0)
	await theater.wait(0.6)
	_kitty.play_act()
	await theater.say("Kitty", "Sign-up sheet said MAGIC RECITAL. I scratched out 'magic.' They'll cope.")
	await theater.say("Basil", "Kitty, there are a LOT of people in here.")
	await theater.say("Kitty", "Up the middle. I've got the crank, you've got the flask.")
	theater.close_dialog()
	# she goes on ahead, straight up her own column, while the walk is his own
	theater.walk(_kitty, Vector2(_kitty.position.x, floor_y), 50.0)
	# row 6 is the ONLY row touching the apron, so a full-width band across it
	# cannot be walked around — the gate geometry rule, the same shape as the
	# naming's stage band and the sickroom's row 6
	await theater.walk_gate(Vector2(mid_x, floor_y), Vector2(apron.size.x - 16.0, 20.0))
	await theater.walk(player, Vector2(mid_x, floor_y), 55.0)
	theater.face(player, Vector2.UP)
	await theater.say("Professor Strix", "Next. ...Basil. There is a note against this name. It says 'no aptitude.'")
	await theater.say("Professor Strix", "The evening is short, child. The floor is... yours, I suppose.")
	_schw.play_act()
	await theater.hop(_schw, 5.0)
	await theater.say("Schweinler", "He can't do MAGIC! What's he going to do, WIND something at us?")
	await theater.say("Basil", "...Yes.")
	theater.close_dialog()
	await _load_and_fly(mid_x, floor_y)
	await _fireworks(mid_x, floor_y)
	await _invitation()


## The load: the flask leaves his paws, and from here it rides UNDER the pod as
## a pinned child — through the rotor frames, through the lift, through the
## whole orbit — until the fireworks drain it.
func _load_and_fly(mid_x: float, floor_y: float) -> void:
	_kitty.play_act()
	_whirligig = WorldFx.airborne($World, FX_SHEET, FX_WHIRL_DROOP,
			Vector2(mid_x, floor_y + 2.0), 6.0)
	_flask = WorldFx.sheet_sprite(FX_SHEET, FX_BEAKER)
	_flask.position = Vector2(0.0, 9.0)     # under the pod (centre 8,10 in all
	                                        # three rotor modes)
	_flask.modulate = FW_TINTS[3]
	_whirligig.add_child(_flask)
	await theater.hop(_kitty, 4.0)
	await theater.hop(_kitty, 4.0)
	_whirligig.frame = FX_WHIRL_SPIN0
	_flying = true
	_spin_rotor()
	var tw := create_tween()
	tw.tween_method(_set_rig_offset, Vector2(0.0, -6.0), Vector2(0.0, -46.0), 1.1) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	await tw.finished
	var sway := create_tween().set_loops()
	sway.tween_method(_set_rig_offset, Vector2(0.0, -46.0), Vector2(10.0, -52.0), 1.2) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	sway.tween_method(_set_rig_offset, Vector2(10.0, -52.0), Vector2(-10.0, -44.0), 2.4) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	sway.tween_method(_set_rig_offset, Vector2(-10.0, -44.0), Vector2(0.0, -46.0), 1.2) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)


## Fly the whirligig by its sprite OFFSET, never its origin: lifting position:y
## would raise its y-sort key past the row-5 stage_front() entity, which is
## opaque across its footprint — it would fly BEHIND the apron and vanish
## (world_fx.gd states the rule; this scene is where it bites).
##
## The flask must be given the SAME offset rather than ride along as a child:
## `offset` shifts a Sprite2D's own texture only, so a pinned child stays
## planted while its parent's art climbs. Equal offsets on both keep the flask
## 9px under the pod all the way up.
func _set_rig_offset(v: Vector2) -> void:
	if not is_instance_valid(_whirligig):
		return
	_whirligig.offset = v
	_flask.offset = v


## Rotor flicker while it's up (scene-lifetime loop; the is_inside_tree guard
## stops it when the montage swaps the scene out — the bluff's lesson).
func _spin_rotor() -> void:
	while _flying and is_inside_tree() and is_instance_valid(_whirligig):
		_whirligig.frame = FX_WHIRL_SPIN0 if _whirligig.frame != FX_WHIRL_SPIN0 \
				else FX_WHIRL_SPIN0 + 1
		await get_tree().create_timer(0.09).timeout


## One colour: a mote climbs, opens, and throws tinted sparks. The cells are
## drawn white-hot and colourless so ONE pair makes all four.
##
## Deliberately NOT additive (the library.gd magic-mote idiom): cream at ~250
## added onto the hall's plum saturates every channel and every colour arrives
## the same pale white — and WHICH colour it is is the entire point of the
## beat. Straight MIX keeps the tint exact and the pixels hard, which is the
## house style anyway.
func _firework(tint: Color, ground: Vector2, dx: float, apex: float) -> void:
	var mote := WorldFx.airborne($World, FX_SHEET, FX_BURST_S,
			ground + Vector2(dx, 0.0), 46.0)
	mote.modulate = tint
	var rise := mote.create_tween()
	rise.tween_property(mote, "offset:y", -apex, 0.32) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	await rise.finished
	mote.frame = FX_BURST_B
	var burst := mote.create_tween().set_parallel()
	burst.tween_property(mote, "scale", Vector2(1.35, 1.35), 0.45)
	burst.tween_property(mote, "modulate:a", 0.0, 0.45)
	for i in 5:
		var ang := TAU * float(i) / 5.0
		var spark := WorldFx.airborne($World, FX_SHEET, FX_BURST_S,
				mote.position, apex)
		spark.modulate = tint
		var fling := spark.create_tween().set_parallel()
		fling.tween_property(spark, "offset",
				spark.offset + Vector2(cos(ang) * 14.0, sin(ang) * 14.0), 0.4)
		fling.tween_property(spark, "modulate:a", 0.0, 0.4)
		fling.chain().tween_callback(spark.queue_free)
	await burst.finished
	mote.queue_free()


func _fireworks(mid_x: float, floor_y: float) -> void:
	var ground := Vector2(mid_x, floor_y + 2.0)
	# the flask empties as it spends itself
	var drain := _flask.create_tween()
	drain.tween_property(_flask, "modulate:a", 0.0, 4.2)
	# the house leans back as one — _laugh_bob slowed and flattened until it
	# reads as awe instead of a laugh. The same helper, the opposite feeling.
	var sway: Array[Tween] = []
	for i in _audience.size():
		sway.append(_laugh_bob(_audience[i], 0.9 + 0.09 * (i % 4),
				1.5 + 0.5 * float(i % 3)))
	for j in _panel:
		j.play_emote()
	_dean.play_emote()
	# apexes keep the bursts clear of the whirligig (art at y=60) and inside the
	# clamped view — this room has no sky, so "up" is the wall above the stage
	_firework(FW_TINTS[0], ground, 0.0, 68.0)
	await theater.wait(0.55)
	_firework(FW_TINTS[1], ground, -16.0, 62.0)
	await theater.wait(0.2)
	_schw.play_idle()                       # the gloat pose just... stops
	await theater.say("Schweinler", "That's not - that's not magic, that's just -")
	theater.close_dialog()
	_firework(FW_TINTS[2], ground, 16.0, 66.0)
	await theater.wait(0.55)
	_firework(FW_TINTS[3], ground, 0.0, 74.0)
	await theater.wait(0.25)
	_kitty.play_emote()
	await theater.say("Kitty", "THAT'S MY WHIRLIGIG! THAT'S BASIL! WHOOOOO!")
	theater.close_dialog()
	# the finale: all four at once, and the sway becomes an eruption
	_kill_bobs(sway)
	var erupt: Array[Tween] = []
	for i in _audience.size():
		erupt.append(_laugh_bob(_audience[i], 0.16 + 0.03 * (i % 4),
				6.0 + float(i % 3)))
	for i in 4:
		_firework(FW_TINTS[i], ground, -18.0 + 12.0 * float(i), 58.0 + 6.0 * float(i % 3))
		await theater.wait(0.25)
	await theater.wait(1.0)
	_kill_bobs(erupt)


func _invitation() -> void:
	player.sprite.play("happy")
	_dean.play_emote()
	await theater.say("Professor Strix", "Stop. STOP. Young man - what IS that.")
	await theater.say("Basil", "Reagents, sir. Four of them. They burn different colours.")
	await theater.say("Professor Strix", "It is POTIONS is what it is.")
	# the line the grown one says at that same podium (see _naming_cutscene),
	# planted here in a ten-year-old's mouth
	await theater.say("Basil", "...It's chemistry, sir.")
	await theater.say("Professor Strix", "Apply to this Academy the year you are old enough. I will know the name.")
	_kitty.play_act()
	await theater.say("Kitty", "It's Basil. Write it down.")
	await theater.say("Basil", "I'll be here.")
	theater.close_dialog()
	Game.set_flag("prologue_recital")
	await theater.wait(1.4)
	# Prologue A closes into the romance: the cards skip to the college years,
	# the roster swaps to basil_student, and the bluff reloads in the sunset —
	# the acceptance-letter evening this recital just earned him.
	await theater.black(1.0)
	# one TIME card only (the 2026-07-18 card purge: cards may only say how
	# much time passed)
	await theater.card("THREE SUMMERS LATER.", 2.0)
	_flying = false
	Party.set_roster([&"basil_student"])
	Game.bluff_phase = "romance"
	get_tree().change_scene_to_file("res://scene/bluff.tscn")
