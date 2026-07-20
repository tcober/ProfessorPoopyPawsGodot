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

const MAP_PATH := "res://assets/maps/hall.txt"
const LAYOUT_PATH := "res://assets/tilesets/hall_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const SHEET_SCHW := preload("res://assets/npc_schweinler_adult_gen.png")
const SHEET_OWL := preload("res://assets/npc_owl_gen.png")
const SHEET_SHEEP := preload("res://assets/npc_sheep_gen.png")
const SHEET_MOUSE := preload("res://assets/npc_mouse_gen.png")
const SHEET_BADGER := preload("res://assets/npc_badger_gen.png")
const SHEET_STORK := preload("res://assets/npc_stork_gen.png")

var map: Dictionary
var player: Node2D
var _dean: NPC
var _schw: NPC
var _panel: Array[NPC] = []
var _audience: Array[NPC] = []

@onready var theater: Theater = $Theater


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	PropSpawner.build("res://assets/tilesets/hall_props.txt", map, $World)
	player = Party.spawn($World, MapData.anchor_px(map, "player_spawn"))
	Party.clamp_cameras(MapData.size_px(map))
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
	# a PACKED tiered gallery: three to a bench, six benches, EIGHTEEN in
	# all — seated facing the stage, backs to the camera (sheet cols 6-7;
	# frame_cols 8 so npc.gd builds the back clip)
	var sheets := [SHEET_SHEEP, SHEET_MOUSE, SHEET_BADGER]
	for i in 18:
		var a := _npc("", sheets[i % 3], 8, "aud_%d" % (i + 1))
		a.play_back()
		_audience.append(a)


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
	var flee := create_tween().set_parallel()
	flee.tween_property(player, "global_position", wing, trip)
	flee.tween_property(player, "modulate:a", 0.0, 0.6).set_delay(trip - 0.6)
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
