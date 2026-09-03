extends TravelScene

## Alembic Town's FLOOR, FESTIVAL ERA — Prologue A "The Whirligig"
## (docs/DESIGN.md Story). The same village grid as the drained present,
## decades younger: the Founding Festival fills the square, magic is casually
## everywhere, and kid Basil is the one cat who can't do magic. Since the
## 2026-08-23 split the front door and the ring decks live in canopy_fest —
## first entry climbs DOWN a rope ladder from the boughs, and the town is
## FREE — the fountain-square teasing cutscene fires from a proximity zone
## when Basil first walks by the square. Then the chapter's wander rhythm
## (reworked 2026-07-15): three stinging villager talks → "I want to go
## home." → up tree 1 and through the FRONT DOOR to Mom downstairs, whose
## blessing by the hearth opens the south gate (the double-back — Mom stays
## home, no duplicate festival Mom). The goose steals Sage's ribbon
## mid-cutscene and goes UP — out the frame top on tree 3's own ladder line;
## the treed thief and the ribbon recovery live in canopy_fest.

const MAP_PATH := "res://assets/maps/town_fest.txt"
const LAYOUT_PATH := "res://assets/tilesets/town_fest_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const FX_SHEET := preload("res://assets/prologue_fx.png")

const SHEET_SAGE := preload("res://assets/npc_sage_gen.png")
const SHEET_SCHW := preload("res://assets/npc_schweinler_gen.png")
const SHEET_SHEEP := preload("res://assets/npc_sheep_gen.png")
const SHEET_OWL := preload("res://assets/npc_owl_gen.png")
const SHEET_GOOSE := preload("res://assets/npc_goose_gen.png")
const SHEET_MOUSE := preload("res://assets/npc_mouse_gen.png")

## stings before Basil wants to go home
const GATE_TALKS := 3

## ---- the goose theft's geometry (de-hardcoded 2026-07-29) -------------------
## The swoop used to be four absolute pixel literals hand-tuned against this
## grid — a start at (200,306), a snatch at (369,316), an exit at (700,292).
## Every one of them silently depends on something the MAP owns (the square's
## coordinates, sage_pos, the map's east/west extents), so a re-authored town
## would have left the goose diving at empty air a tile from the ribbons and
## teleporting in on camera. These are the same numbers expressed as offsets
## from things the map still knows after it moves.
##
## Where the goose BODY must be for the cell pinned at its beak to sit on the
## ribbon it is stealing (the carried sprite hangs at +12,+2 — see below).
const BEAK_OFF := Vector2(-9.0, -2.0)
## The glide line, measured UP from the snatch point: it levels off a touch above
## the ribbons and takes one on the way past rather than dropping onto it.
const FLY_LIFT := 10.0
## How far outside the locked view the flight ENDS. Since 2026-08-02 the exit is
## the only part of the flight measured off the camera — the take-off happens at
## the bird's own feet — and it needs the clearance because the hidden respawn
## happens behind it. A goose cell is 48px, so this covers the whole sprite.
const FLY_CLEAR := 68.0

var _talked := {}
var _gate_hinted := false
var _refusing := false
var _npcs := {}
## the bobbing square ribbons — the theft snatches one, so keep the refs
var _ribbons: Array[Sprite2D] = []

@onready var theater: Theater = $Theater


func _player_node() -> Node2D:
	return Party.spawn($World, Vector2.ZERO)


func _map_path() -> String:
	return MAP_PATH


func _layout_path() -> String:
	return LAYOUT_PATH


func _place_player() -> void:
	# Arrivals: down a rope ladder from the boughs ("top1".."top4" — the home
	# door lives in canopy_fest now), back from the meadow at the south gate,
	# or "festival" as the fallback for direct scene loads.
	var spawn := Game.town_spawn
	Game.town_spawn = ""
	if _place_on_rungs(spawn):
		return
	if Game.flag("prologue_festival_done"):
		Party.place(MapData.anchor_px(map, "player_start"))
	else:
		Party.place(MapData.anchor_px(map, "festival"))


func _extra_setup() -> void:
	PropSpawner.build("res://assets/tilesets/town_fest_props.txt", map, $World)
	_collect_animated()
	$ExitSouth.position = MapData.anchor_px(map, "exit_south")
	_wire_exit($ExitSouth, _on_exit_south)
	_wire_ladder_tops("res://scene/canopy_fest.tscn")
	_wall_gate_mouth()
	_fireflies()
	Party.clamp_cameras(MapData.size_px(map))
	_spawn_npcs()
	_spawn_goose()
	_spawn_ribbons()
	if not Game.flag("prologue_festival_done"):
		_spawn_fountain_zone()
	_open_academy()


## Fireflies under the festival too — the crown was closed in Basil's
## childhood as well, so even the bright era is filtered light. Fewer and
## fainter than the drained town's: this is golden hour, not night.
func _fireflies() -> void:
	var ff := Fireflies.new()
	add_child(ff)
	var size := MapData.size_px(map)
	ff.seed($World, Rect2(48.0, 304.0, size.x - 96.0, size.y - 384.0), 9, 0.8)


## THE ACADEMY DOOR GOES LIVE (2026-07-25). With the flask brewed, the recital
## Schweinler barred him from is the objective, and the Academy stops being
## scenery: the SAME OverworldLocation flips from announce to travel, because
## travel_scene._on_location_entered branches on target_scene alone and reads
## it at step-on time.
##
## The same node, never a second zone on the anchor — the home-door lesson
## (canopy_fest._free_home_location carries it now): two zones sharing an
## anchor can both fire in one physics flush, and an awaited _announce then
## holds _busy through the other's body_entered until the refused body is
## standing inside a zone that never re-fires. One node cannot overlap itself.
func _open_academy() -> void:
	if not Game.flag("prologue_potion_made") or Game.flag("prologue_recital"):
		return
	var loc := $Locations.get_node_or_null("School")
	if loc == null:
		return
	loc.target_scene = "res://scene/hall.tscn"
	# "UP THE STAIR" until 2026-08-01 — the Academy left the town grid in the
	# forest-floor rebuild, and the stair with it. The way there is the lane.
	_show_banner("THE RECITAL - THE ACADEMY, UP THE NORTH LANE", BANNER_HOLD)


## TravelScene's per-scene travel hook: set the read-and-cleared router and let
## the base class change the scene.
func _on_travel(loc: OverworldLocation) -> void:
	if loc.id == "school":
		Game.hall_phase = "recital"


## The mouth roads run to the map's edge and the collision layer only stamps
## grid cells — nothing stops a body walking off the map into the void. The
## 80x56 rebuild gave the shared grid THREE mouths (south gate, the north lane
## to the Academy's ground, the east lane for beat 5b), and this era wires an
## exit on none of them but the south — so all three need the wall, same as
## alembic_town._wall_mouths. The ExitSouth zone fires well before its wall
## when the gate is open.
func _wall_gate_mouth() -> void:
	var size := MapData.size_px(map)
	_wall(Vector2($ExitSouth.position.x, size.y + 4.0), Vector2(64.0, 8.0))
	_wall(Vector2(MapData.anchor_px(map, "exit_north").x, -4.0), Vector2(64.0, 8.0))
	_wall(Vector2(size.x + 4.0, MapData.anchor_px(map, "exit_se").y),
			Vector2(8.0, 64.0))


## The teasing beat fires from proximity, not scene entry (the home-start
## pacing pass): the town is free until Basil first walks by the square.
func _spawn_fountain_zone() -> void:
	var zone := Area2D.new()
	zone.collision_layer = 0
	zone.collision_mask = 2
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(96.0, 96.0)       # the road ring around the basin
	shape.shape = rect
	zone.add_child(shape)
	# The fountain's center, ASKED OF THE MAP (2026-07-29) instead of the old
	# Vector2(27.5 * 16.0, 21.5 * 16.0). The basin is the o/O cells at rows
	# 20-22, cols 26-28, so its bbox is (416,320,48,48) and the center is
	# (440,344) — bit-for-bit what those two literals spelled out. The same
	# rect _square_route already dog-legs around, so the trigger and the walk
	# that answers it can no longer disagree about where the square is.
	zone.position = MapData.bbox_rect(map, "oO").get_center()
	add_child(zone)
	zone.body_entered.connect(func(body: Node2D) -> void:
		if body.is_in_group("player") and not Game.flag("prologue_festival_done"):
			zone.queue_free()
			_festival_cutscene())


# ---- the cast ---------------------------------------------------------------

func _spawn_npcs() -> void:
	var sage_lines := _sage_lines()
	var cast: Array = [
		{"anchor": "sage_pos", "name": "Sage", "sheet": SHEET_SAGE, "cols": 6,
			"lines": sage_lines},
		{"anchor": "schw_pos", "name": "Schweinler", "sheet": SHEET_SCHW, "cols": 6,
			"lines": PackedStringArray([
				"What are YOU looking at? You can't even do magic.",
				"My father says magic is BREEDING. And pigs of quality have LOADS of it.",
			])},
		{"anchor": "npc_sheep", "name": "Mrs. Flockhart", "sheet": SHEET_SHEEP, "cols": 6,
			"lines": PackedStringArray([
				"Basil, dear! Lovely festival, isn't it?",
				"Don't fret about the magic. Everyone blooms eventually. My Wooliam didn't float his first ribbon till he was six.",
				"...You're ten? Oh. Oh dear. Well - wool over it, love!",
			])},
		{"anchor": "npc_owl", "name": "Professor Strix", "sheet": SHEET_OWL, "cols": 6,
			"lines": PackedStringArray([
				"Ah. The young Basil. I have read EVERY treatise on late-blooming magic. All nine of them.",
				"Chapter one is quite clear: some cats simply... don't. A fascinating case! May I take notes?",
			])},
		{"anchor": "npc_mouse", "name": "Pip", "sheet": SHEET_MOUSE, "cols": 6,
			"lines": PackedStringArray([
				"Basil! Wanna see MY magic? I learned it YESTERDAY and I'm only five!",
				"Oh... wait. Papa says I shouldn't show off in front of... um... I gotta go find Papa!",
			])},
	]
	for c: Dictionary in cast:
		var npc: NPC = NPCScene.instantiate()
		npc.display_name = c["name"]
		npc.sheet = c["sheet"]
		npc.frame_cols = c["cols"]
		npc.lines = c["lines"]
		npc.position = MapData.anchor_px(map, c["anchor"])
		npc.talked.connect(_on_npc_talked)
		$World.add_child(npc)
		_npcs[c["name"]] = npc


func _sage_lines() -> PackedStringArray:
	if Game.flag("prologue_ribbon_returned"):
		return PackedStringArray([
			"Best. Brother. Okay, SECOND best. I don't have another one, so you win by default.",
			"Honeycake's still coming. The BIG kind.",
		])
	if Game.flag("prologue_festival_done"):
		return PackedStringArray([
			"You're not REALLY mad, right? ...Basil?",
			"And the GOOSE! It went UP with it. Straight up the great tree, like the tree was ITS tree. Get it back and I'll forgive your sulking forever.",
		])
	return PackedStringArray(["Watch THIS!"])


## Three goose states (the theft rework, 2026-07-15; split 2026-08-23):
## ribbon recovered — a dignified goose back on the square; hidden — the thief
## is UP THE TREE, on tree 3's ring deck in canopy_fest, and does not spawn
## down here at all; else — the pre-theft goose loitering on the square's west
## road a few cells off Sage, eyeing the ribbons, and IN FRAME for the whole
## teasing cutscene, because the theft launches from exactly there.
func _spawn_goose() -> void:
	if Game.flag("prologue_goose_hidden") and not Game.flag("prologue_ribbon"):
		return                        # treed — canopy_fest owns the startle
	var npc: NPC = NPCScene.instantiate()
	npc.display_name = "Goose"
	npc.sheet = SHEET_GOOSE
	npc.frame_cols = 6
	if Game.flag("prologue_ribbon"):
		npc.lines = PackedStringArray([
			"HONK.",
			"(It seems to respect you now. Or it is planning something.)",
		])
		npc.position = MapData.anchor_px(map, "npc_goose")
		npc.talked.connect(_on_npc_talked)
	else:
		npc.lines = PackedStringArray([
			"HONK. (It is watching Sage's ribbons very, very closely.)",
		])
		npc.position = MapData.anchor_px(map, "npc_goose")
	$World.add_child(npc)
	_npcs["Goose"] = npc


## Sage's THREE levitated ribbons bobbing right over HER head — the casual
## living magic the whole prologue exists to take away later. Ownership must
## read on sight: her line counts three, the goose steals from this stack,
## and her "MY RIBBON!" needs no explaining. (They used to float over the
## square's center — nearer Schweinler than her — so the theft read
## backwards.) Airborne World FX: the origin sits on the ground under each
## ribbon (so depth sorts by the ground point) and the art floats via the
## sprite offset; the bob tweens the offset, never the origin.
func _spawn_ribbons() -> void:
	var over_sage := MapData.anchor_px(map, "sage_pos")
	var spots := [Vector2(-14, -58), Vector2(12, -72), Vector2(-2, -86)]
	for i in spots.size():
		var r := WorldFx.airborne($World, FX_SHEET, 1 if i % 2 else 0,
				over_sage + Vector2(spots[i].x, 0.0), -spots[i].y)
		var tw := r.create_tween().set_loops()
		tw.tween_property(r, "offset:y", r.offset.y - 5.0, 0.9 + 0.17 * i) \
				.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		tw.tween_property(r, "offset:y", r.offset.y, 0.9 + 0.17 * i) \
				.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		# Stash the REST pixel of the art — origin plus the lift offset — for
		# _goose_theft to aim at (2026-07-29). Stashed HERE, at spawn, and not
		# read live at snatch time: the bob is mid-flight by then, so a live
		# read would jitter the swoop by up to 5px on every playthrough. This
		# one Vector2 is what ties the theft to sage_pos, and it is why the
		# goose can no longer snatch thin air if the square is re-authored.
		r.set_meta("rest", r.position + r.offset)
		_ribbons.append(r)


## Road-ring route around the solid fountain: theater walks tween straight
## lines with physics off, so a scripted approach from the north or side
## roads must dog-leg via the ring corners or the body clips through the
## basin. Derived from the fountain's own footprint so map tweaks carry.
func _square_route(from: Vector2, to: Vector2) -> Array:
	var basin := MapData.bbox_rect(map, "oO")
	var west := from.x < basin.get_center().x
	var ring_x := basin.position.x - 8.0 if west else basin.end.x + 8.0
	var pts := []
	if from.y < basin.position.y + 16.0:
		pts.append(Vector2(ring_x, basin.position.y - 8.0))
		pts.append(Vector2(ring_x, basin.end.y + 8.0))
	elif from.y < basin.end.y + 8.0:
		pts.append(Vector2(ring_x, basin.end.y + 8.0))
	pts.append(to)
	return pts


## The camera's LOCKED VIEW while a cutscene holds a body still — the window
## anything staged off-camera has to clear. Every member's Camera2D is pinned to
## the map rect by Party.clamp_cameras, so the visible window is the base
## viewport (384x216, read from project settings — never a hardcoded 384) centred
## on the parked body and slid back inside the map at the edges.
##
## Standing at basil_mark this returns Rect2(248, 284, 384, 216) — which is
## exactly the "left edge ~x248, right ~x632" that _goose_theft's docstring used
## to state as a fact about THIS grid and now derives about any grid.
func _locked_view(at: Vector2) -> Rect2:
	var view := MapData.view_size()
	var span := MapData.size_px(map) - view
	var top_left := (at - view * 0.5).clamp(
			Vector2.ZERO, Vector2(maxf(span.x, 0.0), maxf(span.y, 0.0)))
	return Rect2(top_left, view)


# ---- the festival beat --------------------------------------------------------

func _festival_cutscene() -> void:
	theater.lock_party()
	var sage: NPC = _npcs["Sage"]
	var schw: NPC = _npcs["Schweinler"]
	await theater.wait(0.4)                      # (fires mid-play, no entry fade)
	# the hail: Sage spots him and calls him over BEFORE the scripted walk —
	# without it, control just vanishes and Basil wanders off on his own
	sage.play_emote()
	await theater.say("Sage", "BASIL! HEY! Over HERE! You have GOT to see this!")
	theater.close_dialog()
	sage.play_act()
	await theater.wait(0.4)
	await theater.walk_via(player, _square_route(player.global_position,
			MapData.anchor_px(map, "basil_mark")), 50.0)
	theater.face(player, Vector2.LEFT)
	await theater.say("Sage", "Look-look-LOOK! Three ribbons at once! Basil, count them. THREE.")
	await theater.say("Basil", "I'm counting. Three. Incredible. The whole town is very impressed.")
	await theater.say("Sage", "Maybe today is the day you figure it out! Ribbons basically float themselves.")
	await theater.wait(0.8)
	player.sprite.play("sad")
	await theater.wait(0.5)
	await theater.say("Basil", "...It doesn't work. You KNOW it doesn't work. It never works...")
	sage.play_emote()
	await theater.say("Sage", "Maybe you're holding your whiskers wrong?")
	theater.face(player, Vector2.RIGHT)
	schw.play_act()
	await theater.say("Schweinler", "HA! You still can't do magic Basil!?")
	schw.play_emote()
	await theater.hop(schw, 5.0)
	await theater.say("Schweinler", "No magic! BASIL'S GOT NO MAGIC! Oink-hahaha!")
	sage.play_idle()
	await theater.say("Sage", "HEY! Layoff mud-snout!")
	await theater.say("Schweinler", "See you at the recital, Basil. Oh wait - no magic so I guess you can't even participate!")
	schw.play_idle()
	await theater.wait(0.6)
	player.sprite.play("sad")
	await theater.say("Basil", "...I'm going for a walk.")
	theater.close_dialog()
	# ---- the goose theft (the fly-by restage 2026-07-18, still locked) -----
	await _goose_theft()
	Game.set_flag("prologue_festival_done")
	_npcs["Sage"].lines = _sage_lines()
	theater.unlock_party()
	# ONE objective at a time (2026-07-25): the goose is the whole job here.
	# "TALK TO THE TOWNSFOLK" used to fire on its heels and now waits for
	# _ribbon_return(), which is the beat that actually ends this thread.
	_show_banner("THE GOOSE WENT UP THE GREAT TREE - CLIMB", BANNER_HOLD)


## THE THEFT, RESTAGED FOR THE FOREST-FLOOR TOWN (2026-08-02). Three stagings
## now, and the sequence is the lesson:
##
##  1. the announced waddle to her elbow (retired 2026-07-18) read as anything
##     but a theft;
##  2. the sneak FLY-BY that replaced it swooped in from off-screen WEST, took
##     the ribbon mid-glide and climbed out east over the town's river bridge.
##     Then the 80x56 rebuild took the river, the bridge AND the orchard out of
##     this grid — and with them the loitering goose's cover. The bird stood on
##     the square in plain sight for the whole teasing scene and then BLINKED
##     OUT OF EXISTENCE one beat before it flew in, because the first thing the
##     flight did was teleport it off-camera to start from.
##
## So it does not fly IN any more. IT TAKES OFF FROM WHERE IT HAS BEEN STANDING,
## which is the fix and the better joke at once: it has been on the paving eyeing
## those ribbons since before Basil got here — the player can walk up and be told
## so, in as many words — and it goes while every character on screen is looking
## at Schweinler. Nothing teleports, so nothing can vanish.
##
## The only part still measured off the camera is the EXIT, and the exit is UP,
## aimed over the rooftops at the ring deck it will be found on. In a town whose
## north edge is four great trees, up is where a thief goes and the one direction
## you cannot follow at a walk — so "it went up the great tree" is something the
## player WATCHED rather than something Sage asserts. The snatch is still read off
## the ribbon's own stashed rest pixel, so Sage can stand anywhere.
func _goose_theft() -> void:
	var goose: NPC = _npcs["Goose"]
	await theater.wait(0.6)               # the sulk hangs one beat
	_goose_fly_clip(goose)
	var rib: Sprite2D = _ribbons[0]       # the LOWEST of Sage's three
	_ribbons.remove_at(0)                 # it's freed below — drop the dead ref
	var cell := rib.frame
	# THE SNATCH: the ribbon's rest pixel, backed off by where the beak carries
	# its load. Was Vector2(369.0, 316.0), hand-matched to a ribbon that happened
	# to hang at (378,318) because sage_pos happened to be cell (24,23) — the
	# theft would desync the moment she moved. Reading rib's own rest instead
	# means she can stand anywhere and the beak still crosses the ribbon.
	var snatch: Vector2 = (rib.get_meta("rest") as Vector2) + BEAK_OFF
	var view := _locked_view(player.global_position)
	var from := goose.global_position
	# Out the TOP of the frame on tree 3's own ladder column — the hide-out is
	# that tree's ring deck in canopy_fest now, so the line it leaves on is the
	# line the player is about to climb. Off-camera by construction: the
	# camera's window is thirteen tiles tall and the trunks run off the map's
	# north edge, so nothing aimed up one can end inside it.
	var to := Vector2(MapData.anchor_px(map, "top3").x,
			view.position.y - FLY_CLEAR)
	assert(not view.has_point(to), "the goose must leave the frame")
	assert(view.has_point(from), "the goose must take off ON camera — see above")
	goose.sprite.play("fly")
	goose.sprite.flip_h = true            # fly cells face LEFT; the run east = flipped
	var tw := create_tween()
	# Off the paving first: the heavy vertical scramble a goose actually leaves
	# on, straight up onto the glide line rather than any kind of approach.
	tw.tween_property(goose, "global_position",
			Vector2(from.x + 6.0, snatch.y - FLY_LIFT), 0.55) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	# ...then the run east across the square, on which the ribbon simply IS.
	tw.tween_property(goose, "global_position", snatch, 0.3)
	tw.tween_callback(func() -> void:
		rib.queue_free()                  # its bob tween dies with it
		var carried := WorldFx.sheet_sprite(FX_SHEET, cell)
		carried.position = Vector2(12.0, 2.0)   # the flying beak height
		goose.add_child(carried))
	# ...and away over the rooftops, climbing, gone before Sage turns round.
	tw.tween_property(goose, "global_position", to, 1.2) \
			.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	await tw.finished
	await theater.wait(0.8)               # a beat; it is very gone
	(_npcs["Sage"] as NPC).play_emote()
	await theater.say("Sage", "...did that goose just steal my RIBBON!?")
	await theater.say("Sage", "It went UP! Over the shop and up the GREAT TREE. Basil - you're the one who CLIMBS.")
	# DROP THE BOX before the caller's objective banner: the two share the
	# bottom of the frame, and a beat that opens the dialog owes it a close —
	# leaving Sage's last line up painted the banner out from under it
	theater.close_dialog()
	# the thief is TREED now — canopy_fest spawns it on tree 3's ring deck off
	# this flag, and the recovery (the startle, the ribbon) plays up there
	Game.set_flag("prologue_goose_hidden")
	goose.queue_free()
	_npcs.erase("Goose")


## The fly clip lives only in this scene: the sheet's cells 6-7, appended
## to the runtime SpriteFrames npc.gd built from the first 6 (frame_cols
## stays 6 so npc.gd never mints a bogus "back" clip from the fly art).
func _goose_fly_clip(goose: NPC) -> void:
	var frames := goose.sprite.sprite_frames
	if frames.has_animation("fly"):
		return
	frames.add_animation("fly")
	frames.set_animation_speed("fly", 7.0)  # wingbeats, not the lazy idle rate
	frames.set_animation_loop("fly", true)
	for i in [6, 7]:
		var at := AtlasTexture.new()
		at.atlas = SHEET_GOOSE
		at.region = Rect2(i * 48.0, 0.0, 48.0, 48.0)
		frames.add_frame("fly", at)


# ---- the wander rhythm: stings -> home to Mom -> the gate -------------------------

func _on_npc_talked(npc: NPC) -> void:
	if not Game.flag("prologue_festival_done"):
		return
	var returned_ribbon := false
	if npc.display_name == "Sage" and Game.flag("prologue_ribbon") \
			and not Game.flag("prologue_ribbon_returned"):
		# AWAIT it: if this Sage talk is also the third distinct talk, the
		# fall-through would start _want_home_line on the same DialogBox and
		# one advance press would resume BOTH pending say() awaits
		await _ribbon_return()
		returned_ribbon = true
	_talked[npc.display_name] = true
	if _talked.size() >= GATE_TALKS and not Game.flag("prologue_want_home"):
		Game.set_flag("prologue_want_home")
		_want_home_line()
	elif returned_ribbon:
		# The ribbon thread just closed with the box down, so the wander gate's
		# objective finally gets the frame to itself (2026-07-25 — it used to
		# fire on the heels of the THEFT, where Sage was still mid-sentence over
		# it and the goose was the actual job). Announced from HERE, not from
		# _ribbon_return, because only this scope knows the gate is still open:
		# when that Sage talk is ALSO the third one, _want_home_line owns the
		# next line and two objectives in one flush just paint over each other.
		# A player who never chases the goose never sees this and doesn't need
		# to — reaching the gate without the ribbon means they were already
		# talking to townsfolk.
		_show_banner("TALK TO THE TOWNSFOLK - E TO TALK", BANNER_HOLD)


func _want_home_line() -> void:
	theater.lock_party()
	player.sprite.play("sad")
	await theater.say("Basil", "Everyone's very... helpful. I want to go home.")
	theater.close_dialog()
	theater.unlock_party()
	# home is up tree 1 — canopy_fest owns the front door and frees its own
	# announce location off the prologue_want_home flag
	_show_banner("GO HOME - UP THE GREAT TREE", BANNER_HOLD)


func _ribbon_return() -> void:
	theater.lock_party()
	var sage: NPC = _npcs["Sage"]
	sage.play_emote()
	await theater.say("Sage", "MY RIBBON! You caught the goose?! Nobody catches the goose!")
	player.sprite.play("happy")
	await theater.say("Basil", "Nobody had my motivation.")
	await theater.say("Sage", "Okay. New rule. Anyone who picks on you about magic answers to ME.")
	theater.close_dialog()
	player.sprite.play("idle_down")
	Game.set_flag("prologue_ribbon_returned")
	sage.lines = _sage_lines()
	theater.unlock_party()


# ---- the south gate -------------------------------------------------------------

func _on_exit_south(body: Node) -> void:
	if not _exit_ok(body):
		return
	# The headland is SPENT once the whirligig has flown (2026-07-25). This
	# road re-enters bluff "meet", where every prologue_part_* flag is already
	# set and _on_kitty_zone would fire the flight finale a SECOND time. The
	# story points north now, at the Academy.
	if Game.flag("prologue_whirligig_done") and not Game.flag("prologue_recital"):
		_recital_refusal()
		return
	if not Game.flag("prologue_gate_open"):
		if not _gate_hinted:
			_gate_hinted = true
			_gate_hint()
		return
	_busy = true
	await fade_out()
	# the south road climbs the headland (2026-07-18: the meet moved onto
	# the bluff; the fest meadow scene was cut)
	Game.bluff_phase = "meet"
	get_tree().change_scene_to_file("res://scene/bluff.tscn")


## Not _gate_hinted's one-shot latch: this is a hard REFUSAL for the rest of
## the chapter, and a silent wall walked into three times reads as a bug. Its
## own re-entrancy latch instead — lock_party() freezes the body INSIDE the
## zone, so without one a second body_entered could stack a coroutine on the
## same DialogBox.
func _recital_refusal() -> void:
	if _refusing:
		return
	_refusing = true
	theater.lock_party()
	await theater.say("Basil", "Not the bluff. The ACADEMY. It's the other way, and they've already started.")
	theater.close_dialog()
	theater.unlock_party()
	_refusing = false


func _gate_hint() -> void:
	theater.lock_party()
	if Game.flag("prologue_want_home"):
		await theater.say("Basil", "Not without telling Mom. She has EARS.")
	else:
		await theater.say("Basil", "Mom said stay in town for the festival. The festival says otherwise.")
	theater.close_dialog()
	theater.unlock_party()
