extends Node2D

## THE GREAT HALL of the Alembic Academy — Prologue B "the naming"
## (docs/DESIGN.md Story). Basil delivers his re-enchantment thesis;
## Schweinler smells the bag on his paws and brands him "Professor Poopy
## Paws"; the gallery laughs; the cards fall. The emotional core of the
## prologue. Rebuilt 2026-08-04 as the FF6 OPERA SHOT in the wizard-school
## register: a stone vault whose arch runs off the top of the frame, a mint
## rose window over the podium, FLOATING CANDLES over everything (Tier-3,
## flickered by _process, doused for the recital's act), and a house that
## is pure ambiance — the only walkable ground is the raised timber STAGE
## and the pit strip at its foot; everything south is packed pew backs and
## rows of heads falling into gloom. Basil enters from STAGE RIGHT — from
## behind the west CURTAIN LEG — and flees back behind it the moment the
## laughing starts, one crushed "But... I..." and Schweinler's encore on
## the way down — the flee is automatic (his body giving up), the laugh
## rolls on around it. Interior scene pattern (Tiles -> Collision ->
## y-sorted World -> TilesUpper), the cast are one-row NPC sprites posed by
## the Theater, then it hands to bluff call1.
##
## TWO BEATS, ONE ROOM, twenty years apart (Game.hall_phase, 2026-07-25):
##   ""        Prologue B's naming, above — the default this room was built for.
##   "recital" Prologue A's kid magic recital: the night a ten-year-old with no
##             aptitude flew a loaded whirligig over the house and got told to
##             apply. Deliberately the OPPOSITE staging, not a copy — the stage
##             is sealed by the apron riser (rows 8-9 have no walkable link to
##             the pit at all; adult Basil only ever spawns and fades there),
##             so the kid isn't ALLOWED up on it. He sets up on the pit floor
##             with the faculty looking down over the rail, and years later he
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

## THE HOUSELIGHTS (2026-07-28). The recital is a PERFORMANCE, so the room is
## lit like one: a warm evening while the hall fills and talks, all the way
## down for the act itself, and back up the moment the Professor stops it.
##
## Deliberately NOT the $Dim CanvasModulate the rest of the scene's light rides
## on (the bluff/town_thesis nightfall idiom). A CanvasModulate multiplies the
## WHOLE canvas — fireworks included — so dimming with it would take the bursts
## down by exactly the same factor and buy nothing. The ROOM'S OWN LAYERS are
## modulated instead (_house_take snapshots tiles, glow, props and cast), which
## means every FX sprite spawned AFTERWARDS sits outside the dim and burns at
## full strength against it. That is the entire trick: the bursts are not
## brighter than they were, the room stopped competing with them.
const HOUSE_EVENING := Color(0.80, 0.74, 0.70)  # lamps up, hall talking
const HOUSE_DOWN := Color(0.30, 0.27, 0.44)     # the act — his flask is the light
const HOUSE_UP := Color(1.0, 1.0, 1.0)          # "Stop. STOP."
## How hard one burst throws its own colour back across the darkened room.
const BURST_WASH := 0.55
## The rig is spawned after _house_take, so nothing dims it — but a wooden
## whirligig at full daylight in a blacked-out hall reads as unlit rather than
## lit. This is the light its own payload throws on it: bright enough to keep
## the silhouette legible, cool enough to owe the purple in the pod.
const RIG_LIT := Color(0.80, 0.72, 0.90)

## The four reagent colours, straight off the compound registry (see the same
## const in downstairs_fest.gd): what goes up over the house tonight is the
## same green/blue/red/purple the adult will be loading into a gun.
const FW_TINTS := [Alchemy.GREEN, Alchemy.BLUE, Alchemy.RED, Alchemy.PURPLE]

## One burst: an inner ring flung far and a tighter offset ring behind it, so
## the star reads as a shell opening rather than a snowflake.
const FW_RINGS := [{"n": 6, "reach": 21.0, "dur": 0.62},
		{"n": 5, "reach": 13.0, "dur": 0.46}]
## Embers shed by the rising ember on the way up.
const FW_TRAIL := 4

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
var _flask_pulse: Tween
var _flying := false
var _house: Array[CanvasItem] = []
var _house_now := Color.WHITE       # what is actually on the room right now
var _house_level := Color.WHITE     # the level a burst wash returns to
var _house_tw: Tween
var _wash_tw: Tween

## THE FLOATING CANDLES (2026-08-04, the opera restage). The hall is lit by
## its own magic — bare tapers hanging on nothing, flickering on a 4-frame
## sheet cycled by _process (interior scenes have no TravelScene _animated
## scanner). They are deliberately OUTSIDE the houselights snapshot: they are
## lights, not lit things, and the recital douses them on their own tweens —
## _house_apply writing modulate across the snapshot would fight the wave.
const ANIM_STEP := 0.18             # frame time for the flicker cycle
const CANDLE_OUT := Color(0.30, 0.27, 0.44)   # = HOUSE_DOWN: a dead flame
                                    # dims exactly as far as the dark room
var _candles: Array[Sprite2D] = []
var _anim_t := 0.0

@onready var theater: Theater = $Theater


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	PropSpawner.build("res://assets/tilesets/hall_props.txt", map, $World)
	_collect_candles()
	# read-and-clear BEFORE any await, so a stale value can never re-route a
	# later entry into the wrong chapter
	var phase := Game.hall_phase
	Game.hall_phase = ""
	var recital := phase == "recital"
	$Dim.color = TINT_RECITAL if recital else TINT_NAMING
	# the recital opens at the FOOT of the stage (the opera restage: the
	# house is ambiance, nobody walks it — the great doors are a glint in the
	# gloom band). `door` (4,12) is the pit's WEST END, by the little service
	# door baked into the wall there — the unbilled entrance.
	player = Party.spawn($World, MapData.anchor_px(map,
			"door" if recital else "player_spawn"))
	Party.clamp_cameras(MapData.size_px(map))
	if recital:
		_spawn_recital_cast()
		_recital()
	else:
		_spawn_cast()
		_naming_cutscene()


## The spawned candle props, by name prefix — PropSpawner names each component
## sprite off its manifest row (CandleHigh, CandleHigh2, ... CandleVault...).
func _collect_candles() -> void:
	for c in $World.get_children():
		if c is Sprite2D and (c as Sprite2D).hframes > 1 \
				and String(c.name).begins_with("Candle"):
			_candles.append(c as Sprite2D)


## The flicker: every candle rides the same 4-frame mean-zero cycle at its
## own phase (i offset), so the drift never metronomes — the travel scenes'
## _collect_animated idiom, kept local because this room is not a TravelScene.
func _process(delta: float) -> void:
	if _candles.is_empty():
		return
	_anim_t += delta
	var f := int(_anim_t / ANIM_STEP)
	for i in _candles.size():
		_candles[i].frame = (f + i) % _candles[i].hframes


## THE DOUSE — the room's own answer to a boy with no magic in him: the
## hall's candles go out in a wave, north to south, ahead of the act. Each
## candle dims to exactly the houselights' own dark, so a dead taper and a
## dark room read as one event. Fired un-awaited beside _house_set — the two
## run in parallel and nobody announces either (the narration purge).
func _candle_douse(dur: float) -> void:
	var by_y: Array[Sprite2D] = _candles.duplicate()
	by_y.sort_custom(func(a: Sprite2D, b: Sprite2D) -> bool:
		return a.global_position.y < b.global_position.y)
	for i in by_y.size():
		var tw := by_y[i].create_tween()
		tw.tween_interval(dur * float(i) / maxf(1.0, float(by_y.size())))
		tw.tween_property(by_y[i], "modulate", CANDLE_OUT, 0.30)


## And the room comes back — every candle relights under the Professor's
## "Stop. STOP.", on its own tween, same as it went out.
func _candle_relight(dur: float) -> void:
	for c in _candles:
		c.create_tween().tween_property(c, "modulate", Color.WHITE, dur)


## A BODY POSED BEHIND A COUNTER STANDS ON THE CELL'S SOUTH EDGE, NOT IN THE
## MIDDLE OF IT. `anchor_px` returns a cell's CENTRE and a 48px body draws
## its feet 20px below its origin, so a fixture anchored to the tuck row has
## its feet 12px PAST that row's south edge — for a body that WALKS that
## overhang is correct and load-bearing, but a professor posed against the
## panel desk sinks to a head bobbing in the desk clutter. Lifted onto the
## row's south edge, head and shoulders ride clear above the desktop plane
## and the legs tuck behind it — the composition the desk was drawn for.
const DESK_TUCK := 12.0


func _spawn_cast() -> void:
	# the judging panel behind the stage-LEFT desk — the Dean presides,
	# three faculty beside him; they stand on the tuck row behind the desk
	# so the desktop plane hides their legs (the desk() entity idiom)
	_dean = _npc("Dean Strix", SHEET_OWL, 6, "judge_1", DESK_TUCK)
	_dean.play_act()                                   # a lecturing wing
	var jsheets := [SHEET_STORK, SHEET_BADGER, SHEET_SHEEP]
	for i in jsheets.size():
		_panel.append(_npc("", jsheets[i], 6, "judge_%d" % (i + 2), DESK_TUCK))
	# Schweinler heckles from the east end of the FRONT PEW, turned round to
	# work the room — the one face in a house of backs (his sheet has no back
	# cells; he never sits)
	_schw = _npc("Schweinler", SHEET_SCHW, 6, "schweinler_spot")
	_arc_seat(_schw)
	_spawn_audience()


## THE PACKED HOUSE: THIRTY, shoulder to shoulder — five per pew block, two
## blocks across three amphitheatre tiers, every head 16px from the next
## (the FF6 crowd), seated facing the stage, backs to the camera (sheet cols
## 6-7; frame_cols 8 so npc.gd builds the back clip). They stand on the E
## perch cells no body can ever reach (the opera restage: the house is
## ambiance) and every one is a LIVE NPC so the whole crowd can bob with
## laughter or an eruption. Each is nudged onto its tier's own ARC — the
## generator draws the pew backs curved (HOUSE_ARC) and the heads must sit
## on the same curve. Shared by both beats; the house is the house in either
## century. NEVER play_emote one of these — the emote cells are front-facing
## and the head would flip round.
const AUD_ARC := 12.0     # px the tiers dip at the walls — married to the
                          # generator's HOUSE_ARC; drift shows as heads
                          # floating off their own pew line
const ARC_CX := 192.0     # the podium midline the arcs are centred on
const ARC_HALF := 144.0   # the house band's half-width


## Seat a body on its tier's arc — the audience, and Schweinler in the crowd.
func _arc_seat(n: NPC) -> void:
	var u := (n.position.x - ARC_CX) / ARC_HALF
	n.position.y += AUD_ARC * u * u


func _spawn_audience() -> void:
	var sheets := [SHEET_SHEEP, SHEET_MOUSE, SHEET_BADGER]
	for i in 30:
		var a := _npc("", sheets[i % 3], 8, "aud_%d" % (i + 1))
		_arc_seat(a)
		a.play_back()
		_audience.append(a)
	# read the authored rest pose rather than assuming 0 — _kill_bobs has to
	# put the heads back and npc.tscn owns where "back" is
	_aud_rest_y = _audience[0].sprite.position.y


func _npc(nm: String, sheet: Texture2D, cols: int, anchor: String,
		lift: float = 0.0) -> NPC:
	var npc: NPC = NPCScene.instantiate()
	npc.display_name = nm
	npc.sheet = sheet
	npc.frame_cols = cols
	npc.position = MapData.anchor_px(map, anchor) - Vector2(0.0, lift)
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
	# THE ROAR IS SEEN (2026-08-07): the amphitheatre lives below the podium
	# camera's frame line, so without this the whole eruption — thirty
	# bobbing backs, Schweinler working the room — would play behind the
	# dialog box. Close the box and ride the camera down into the laughing
	# house for a breath, then come back up to him standing alone with it.
	theater.close_dialog()
	await _pan_house(72.0, 1.0, 1.1)
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
	# the fade rides the last 2s of the trudge — long enough that it STARTS
	# while the masking leg still covers him (he enters the velvet at x~69
	# and wing_exit sits past it at the frame edge; a 0.6s fade let him pop
	# out the far side at full alpha for a beat). Clamped, because a
	# negative delay is a tween error (a short trip just fades the whole way)
	var fade_dur := minf(2.0, trip)
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


## Ride the leader's camera down into the house and back — the one moment
## where what the ROOM is doing is the beat, and the room lives below the
## frame line. Offset-only, so the camera stays owned by the body and the
## clamp limits still hold; symmetric and awaitable.
func _pan_house(dy: float, dur: float, hold: float) -> void:
	var cam := player.get_node_or_null("Camera2D") as Camera2D
	if cam == null:
		await theater.wait(dur * 2.0 + hold)
		return
	var tw := create_tween()
	tw.tween_property(cam, "offset:y", dy, dur) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tw.tween_interval(hold)
	tw.tween_property(cam, "offset:y", 0.0, dur) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	await tw.finished


## One audience head's laugh: a looped sprite bob (the hop axis) at its own
## period + height, so thirty of them read as a shaking crowd, not a drill
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


# ---- the houselights ---------------------------------------------------------------

## Snapshot the ROOM: the two tile layers, the baked lamp glow, and everything
## standing in the world right now (props, cast, the player). Call it once the
## scene is fully dressed — anything added later is, by construction, a LIGHT
## rather than a thing being lit, and stays out of the dim.
func _house_take() -> void:
	_house.clear()
	var room: Array = [$Tiles, $TilesUpper, $Glow]
	room.append_array($World.get_children())
	for n in room:
		# the floating candles stay OUT: they are lights, not lit things, and
		# their douse/relight runs on their own tweens — one modulate cannot
		# serve two owners (the _flask_pulse lesson, from the other side).
		# The `n is Sprite2D` guard first: has() on a typed array validates
		# its argument and spews errors for every TileMapLayer it's handed.
		if n is CanvasItem and \
				not (n is Sprite2D and _candles.has(n as Sprite2D)):
			_house.append(n as CanvasItem)


## Paint one level onto every room item. Everything moves together, so the
## tweens below interpolate ONE colour through this rather than stacking a
## tweener per node (dozens of them for a thirty-seat gallery).
func _house_apply(c: Color) -> void:
	_house_now = c
	for ci in _house:
		if is_instance_valid(ci):
			ci.modulate = c


func _house_snap(level: Color) -> void:
	_house_level = level
	_house_apply(level)


## Move the houselights and hold there. Awaitable; also fine fired un-awaited
## under a line of dialogue.
func _house_set(level: Color, dur: float) -> void:
	if _wash_tw and _wash_tw.is_valid():
		_wash_tw.kill()
	if _house_tw and _house_tw.is_valid():
		_house_tw.kill()
	_house_level = level
	if _house.is_empty():
		return
	_house_tw = create_tween()
	_house_tw.tween_method(_house_apply, _house_now, level, dur)
	await _house_tw.finished


## One burst throwing its colour back across the room — the walls, the benches
## and thirty backs all catch it for a beat. This is what makes a firework
## read as a LIGHT SOURCE instead of a sprite, and it only works because the
## room is dark enough to have somewhere to go. Kept on its own tween so it can
## never kill (and hang) an awaited _house_set.
func _house_wash(tint: Color) -> void:
	if _house.is_empty():
		return
	if _wash_tw and _wash_tw.is_valid():
		_wash_tw.kill()
	var hit := Color(
			minf(1.0, _house_level.r + tint.r * BURST_WASH),
			minf(1.0, _house_level.g + tint.g * BURST_WASH),
			minf(1.0, _house_level.b + tint.b * BURST_WASH))
	_wash_tw = create_tween()
	_wash_tw.tween_method(_house_apply, _house_now, hit, 0.07) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	_wash_tw.tween_method(_house_apply, hit, _house_level, 0.55) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)


# ---- the recital (Prologue A) ------------------------------------------------------

func _spawn_recital_cast() -> void:
	# he presides from the podium the boy will one day stand behind. Still
	# "Professor" here — the Dean's chair comes later (town_fest names him).
	_dean = _npc("Professor Strix", SHEET_OWL, 6, "lectern_spot", DESK_TUCK)
	_dean.play_act()
	var jsheets := [SHEET_STORK, SHEET_BADGER, SHEET_SHEEP]
	for i in jsheets.size():
		_panel.append(_npc("", jsheets[i], 6, "judge_%d" % (i + 2), DESK_TUCK))
	# the same front-pew corner the grown one heckles from, twenty years early.
	# 10 cols: the kid sheet grew back + side cells (2026-07-29), which is what
	# lets him TURN AND WATCH when the first colour goes up (see _fireworks) —
	# the adult sheet still has none, and the naming never needs them.
	_schw = _npc("Schweinler", SHEET_SCHW_KID, 10, "schweinler_spot")
	_arc_seat(_schw)
	_spawn_audience()


func _recital() -> void:
	theater.lock_party()                    # before any await
	var apron := MapData.bbox_rect(map, "D")
	var floor_y := apron.end.y + 8.0        # row 11 — the pit strip below the
	                                        # riser, the only row adjacent to it
	var mid_x := apron.get_center().x
	# they slip in through the SIDE DOOR at the pit's west end (everybody
	# enters this room from the wings — the great doors at the back are
	# scenery now); she comes in a step AHEAD of him, east toward the room —
	# spawned west of the player, her entrance tween would sweep straight
	# through his body (theater walks are no-collision), and she leads
	# anyway: "Up the middle" is her plan
	_kitty = _npc("Kitty", SHEET_KITTY_KID, 10, "door")
	_kitty.position += Vector2(16.0, 0.0)
	# the room is dressed and peopled — take it, and open on lamplight rather
	# than noon: a full hall on a festival evening, waiting on the next name
	_house_take()
	_house_snap(HOUSE_EVENING)
	await theater.wait(0.6)
	_kitty.play_act()
	await theater.say("Kitty", "Sign-up sheet said MAGIC RECITAL. I scratched out 'magic.' They'll cope.")
	await theater.say("Basil", "Kitty, there are a LOT of people in here.")
	await theater.say("Kitty", "Up the middle. I've got the crank, you've got the flask.")
	theater.close_dialog()
	# she cuts ahead across the pit to her crank position just west of where
	# the rig will stand, while the walk to centre is his own. theater.walk
	# turns her along the legs (2026-07-29) — no play_back() needed, and the
	# sign-up-sheet pose is meant to drop
	theater.walk(_kitty, Vector2(mid_x - 40.0, floor_y), 50.0)
	# row 11 is the ONLY row touching the apron, so a full-width band across
	# it cannot be walked around — the gate geometry rule, the same shape as
	# the naming's stage band
	await theater.walk_gate(Vector2(mid_x, floor_y), Vector2(apron.size.x - 16.0, 20.0))
	await theater.walk(player, Vector2(mid_x, floor_y), 55.0)
	theater.face(player, Vector2.UP)
	await theater.say("Professor Strix", "Next. ...Basil. There is a note against this name. It says 'no aptitude.'")
	await theater.say("Professor Strix", "The evening is short, child. The floor is... yours, I suppose.")
	# box CLOSED for the hop — he sits at the frame's bottom edge and the
	# dialog box owns that third of the screen; hopping under it is a
	# heckle nobody sees (2026-08-07)
	theater.close_dialog()
	_schw.play_act()
	await theater.hop(_schw, 5.0)
	await theater.say("Schweinler", "He can't do MAGIC! What's he going to do, WIND something at us?")
	await theater.say("Basil", "...Yes.")
	theater.close_dialog()
	# HOUSELIGHTS DOWN — and the ROOM ITSELF does it: the floating candles go
	# out in a wave, north to south, the hall's own magic leaving the air over
	# a ten-year-old with no spark in him. Nobody says so (the narration
	# purge), and from here the only real light in the hall is the one he
	# brewed this morning.
	_candle_douse(1.2)
	await _house_set(HOUSE_DOWN, 1.2)
	await theater.wait(0.5)
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
	# the rig is spawned AFTER _house_take, so the dark room never touches it —
	# it is the one lit thing on the floor, and RIG_LIT is the light its own
	# payload throws back up the frame. The pulse sells the rest: the reagent
	# glowing in the pod, which keeps the silhouette legible through the whole
	# orbit. _fireworks KILLS this before draining the flask's alpha — a looped
	# `modulate` tween writes a=1 every cycle and would fight the drain forever.
	_whirligig.modulate = RIG_LIT
	_flask_pulse = _flask.create_tween().set_loops()
	_flask_pulse.tween_property(_flask, "modulate",
			FW_TINTS[3].lerp(Color.WHITE, 0.45), 0.9) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	_flask_pulse.tween_property(_flask, "modulate", FW_TINTS[3], 0.9) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
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


## One colour, in four movements: an ember CLIMBS shedding a trail, FLASHES
## white-hot at the top, COOLS into its compound colour as the ring opens, and
## throws two rings of sparks that arc out and FALL. The cells are drawn
## white-hot and colourless so ONE pair makes all four colours.
##
## Deliberately NOT additive (the library.gd magic-mote idiom): cream at ~250
## added onto the hall's plum saturates every channel and every colour arrives
## the same pale white — and WHICH colour it is is the entire point of the
## beat. Straight MIX keeps the tint exact and the pixels hard, which is the
## house style anyway. The brightness comes from the ROOM going dark around it
## (the houselights above), never from turning the blend up.
func _firework(tint: Color, ground: Vector2, dx: float, apex: float) -> void:
	var mote := WorldFx.airborne($World, FX_SHEET, FX_BURST_S,
			ground + Vector2(dx, 0.0), 46.0)
	mote.modulate = tint.lerp(Color.WHITE, 0.35)   # hotter than it will land
	var rise := mote.create_tween()
	rise.tween_property(mote, "offset:y", -apex, 0.36) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	_trail(mote, tint)
	await rise.finished
	# the room catches it — one wash across walls, benches and backs
	_house_wash(tint)
	mote.frame = FX_BURST_B
	# white-hot for a frame or two, then it settles onto the reagent's own
	# colour: the flash sells the bang, the settle keeps the hue exact
	var flash := mote.create_tween()
	flash.tween_property(mote, "modulate", tint, 0.14)
	var burst := mote.create_tween().set_parallel()
	burst.tween_method(_burst_scale.bind(mote, apex), 1.0, 2.2, 0.6) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	burst.tween_property(mote, "modulate:a", 0.0, 0.44).set_delay(0.16)
	for r in FW_RINGS.size():
		var ring: Dictionary = FW_RINGS[r]
		var n: int = ring["n"]
		var reach: float = ring["reach"]
		var dur: float = ring["dur"]
		# rings after the first are rotated half a step, so no two ever line up
		# into one thicker star
		var skew := 0.0 if r == 0 else PI / float(n)
		for i in n:
			var ang := TAU * float(i) / float(n) + skew
			_spark(mote.position, apex, tint, ang, reach, dur)
	await burst.finished
	mote.queue_free()


## Grow the burst ring IN PLACE. A Sprite2D's `offset` lives in the node's own
## space, so scaling multiplies it too — tweening scale alone would fling the
## ring another 80px up the wall (the same offset-vs-transform trap
## _set_rig_offset documents from the other side). Dividing the lift by the
## scale pins the visual centre exactly on the apex it burst at.
func _burst_scale(s: float, mote: Sprite2D, apex: float) -> void:
	if not is_instance_valid(mote):
		return
	mote.scale = Vector2(s, s)
	mote.offset.y = -apex / s


## One spark: flung out on a quad ease-out, then it DROOPS and goes out.
## Fireworks fall; a star that only ever expands reads as a decal.
func _spark(ground: Vector2, apex: float, tint: Color, ang: float,
		reach: float, dur: float) -> void:
	var spark := WorldFx.airborne($World, FX_SHEET, FX_BURST_S, ground, apex)
	spark.modulate = tint
	var out := spark.offset + Vector2(cos(ang) * reach, sin(ang) * reach)
	var fall := out + Vector2(cos(ang) * reach * 0.3, 11.0)
	var fling := spark.create_tween().set_parallel()
	fling.tween_property(spark, "offset", out, dur * 0.55) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	fling.chain().tween_property(spark, "offset", fall, dur * 0.45) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	fling.tween_property(spark, "modulate:a", 0.0, dur * 0.45)
	fling.chain().tween_callback(spark.queue_free)


## Embers shed by the rising ember, each dropping away behind it — the climb
## reads as a comet instead of a sliding sprite. Deliberately NOT scaled down:
## `scale` would drag the lift offset with it and drop every ember to the floor.
func _trail(mote: Sprite2D, tint: Color) -> void:
	for i in FW_TRAIL:
		await get_tree().create_timer(0.07).timeout
		if not is_instance_valid(mote) or not is_inside_tree():
			return
		var e := WorldFx.airborne($World, FX_SHEET, FX_BURST_S, mote.position,
				-mote.offset.y)
		e.modulate = Color(tint.r, tint.g, tint.b, 0.75)
		var tw := e.create_tween().set_parallel()
		tw.tween_property(e, "offset:y", e.offset.y + 8.0, 0.42) \
				.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
		tw.tween_property(e, "modulate:a", 0.0, 0.42)
		tw.chain().tween_callback(e.queue_free)


func _fireworks(mid_x: float, floor_y: float) -> void:
	var ground := Vector2(mid_x, floor_y + 2.0)
	# the flask empties as it spends itself. The pulse has to go FIRST — it is a
	# looped tween on the whole `modulate`, so it would rewrite a=1 twice a
	# second and the drain would never land.
	if _flask_pulse and _flask_pulse.is_valid():
		_flask_pulse.kill()
	_flask.modulate = FW_TINTS[3]
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
	# the gloat pose just... stops, and he TURNS ROUND to the stage — the only
	# body in the room that was facing the house, joining the thirty backs.
	# The line comes off a back view on purpose: the nameplate says who it is,
	# and we don't get to see his face for it
	_schw.play_back()
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
	# houselights back up, over his line — the Professor is on his feet calling
	# for them and the room comes back around the boy who did that: every
	# candle relights. The rig is outside the house set, so it rejoins the lit
	# room by hand.
	_house_set(HOUSE_UP, 1.0)
	_candle_relight(1.0)
	if is_instance_valid(_whirligig):
		_whirligig.create_tween().tween_property(_whirligig, "modulate",
				HOUSE_UP, 1.0)
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
