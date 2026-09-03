extends TravelScene

## Alembic Town's FLOOR on THESIS DAY — Prologue B (docs/DESIGN.md Story).
## Since the 2026-08-23 split this scene owns the GROUND half of the day and
## scene/canopy_thesis.gd owns the deck half; the two share the
## Game.town_thesis_phase router and each re-arms it before handing the body
## up or down a ladder:
##   plant    (night)   the Academy stair -> the player's own walk home
##                      through the sleeping town -> UP the ladder (the
##                      doorstep call and Schweinler's creep play on the
##                      boughs — the camera never saw the ground half of the
##                      creep anyway, it was parked at the deck)
##   dash     (morning) the ground run: the squelch already happened on the
##                      deck; down here it is the paw-print dash across town
##                      to the Academy -> hall
##   steps    (dusk)    out of the doctor's door onto the clinic steps —
##                      Ridley's blunt "perspective," the bowed head, then
##                      the night leaving (the bindle tableau, the look-back,
##                      the south trudge out the gate) -> the
##                      closing cards and the hand-off to the adult build
## Rides the festival town's map + tiles (same era-frozen village); this is the
## same day the festival palette shows, just tinted by hour.

const MAP_PATH := "res://assets/maps/town_fest.txt"
const LAYOUT_PATH := "res://assets/tilesets/town_fest_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const FX_SHEET := preload("res://assets/prologue_fx.png")
const SHEET_BADGER := preload("res://assets/npc_badger_gen.png")

const FX_PRINT := 11
## The pace of the leaving trudge, px/s. It used to be implied — a fixed 4.6s
## tween onto a hardcoded Vector2(440, 545) — which meant the SPEED was a
## function of where the map's south edge happened to be. Now the endpoint is
## derived (one tile past the last row, off-map on purpose) and the duration is
## derived from it, so a taller or shorter town changes how long he walks and
## never how fast: 85px over 4.6s, the shipped trudge, held exactly.
const TRUDGE_SPEED := 18.5
## Where the morning dash ENDS, hung off the "school" anchor — the finish line
## in the north lane's mouth. It is a const rather than a literal because
## tools/prologue_probe.gd has to land a body on it, and the two copies of the
## number DID drift: the goal moved from +40 to +24 in the Alembic rebuild, the
## probe kept teleporting to +40, and a body whose collision box sits 10px below
## the rect's bottom edge never fires body_entered — a beat that hangs forever
## with no error. The probe reads this off the live scene now.
const DASH_GOAL_OFF := Vector2(0.0, 24.0)
## ...and how big that finish line is: a band across the two-cell lane.
const DASH_GOAL_SIZE := Vector2(48.0, 16.0)

const TINT_NIGHT := Color(0.42, 0.40, 0.66)
const TINT_MORNING := Color(0.98, 0.93, 0.86)
const TINT_DUSK := Color(0.74, 0.56, 0.66)

var phase := "plant"
var _last_print := Vector2.ZERO
var _dashing := false
var _from_ladder := false

@onready var theater: Theater = $Theater
@onready var tint: CanvasModulate = $Tint


func _player_node() -> Node2D:
	return Party.spawn($World, Vector2.ZERO)


func _map_path() -> String:
	return MAP_PATH


func _layout_path() -> String:
	return LAYOUT_PATH


func _place_player() -> void:
	phase = Game.town_thesis_phase
	Game.town_thesis_phase = ""
	if phase == "":
		phase = "plant"
	var spawn := Game.town_spawn
	Game.town_spawn = ""
	# down a ladder from the boughs, whatever the phase — the climb continues
	_from_ladder = _place_on_rungs(spawn)
	if _from_ladder:
		return
	match phase:
		"dash":
			# a direct dash-ground load (dev menu / probe): the run starts at
			# the foot of Basil's tree, where the descent lands it in play
			Party.place(MapData.anchor_px(map, "top1") + Vector2(8.0, 40.0))
		"steps":
			Party.place(MapData.anchor_px(map, "cottage_e"))
		_:
			# plant opens at the Academy stair — Basil's been prepping the
			# hall; the walk home is the player's own (2026-07-16, the
			# night-before made playable)
			Party.place(MapData.anchor_px(map, "school") + Vector2(0.0, 24.0))


func _extra_setup() -> void:
	PropSpawner.build("res://assets/tilesets/town_fest_props.txt", map, $World)
	# The fountain's pour + the buildings' window flicker/smoke: the same
	# era-frozen village as town_fest, so the same props must live and breathe
	# on thesis day. Collected BEFORE the phase cutscenes add their
	# (single-frame) FX, so only the standing props get cycled.
	_collect_animated()
	$ExitSouth.position = MapData.anchor_px(map, "exit_south")
	_wall_gate_mouth()
	_wire_ladder_tops("res://scene/canopy_thesis.tscn")
	if phase != "dash":
		# the night and the dusk get their fireflies; fireflies at breakfast
		# are the wrong kind of magic
		var ff := Fireflies.new()
		add_child(ff)
		var size := MapData.size_px(map)
		ff.seed($World, Rect2(48.0, 304.0, size.x - 96.0, size.y - 384.0), 11, 0.85)
	Party.clamp_cameras(MapData.size_px(map))
	match phase:
		"plant": _phase_plant()
		"dash": _phase_dash()
		"steps": _phase_steps()


## Re-arm the shared router before the canopy scene loads — Game fields are
## the only state that survives the door (standing rule 3).
func _on_ascend(_ladder: int) -> void:
	Game.town_thesis_phase = phase
	_dashing = false


# ---- plant (night) ----------------------------------------------------------------

## The ground half of the night: the walk home is the player's own, and it
## ends at a ladder foot — the doorstep call and the creep play on the boughs
## (canopy_thesis._doorstep / _creep). Coming back DOWN mid-night just holds
## the sleeping town; the intro lines never replay.
func _phase_plant() -> void:
	tint.color = TINT_NIGHT
	if _from_ladder:
		return
	theater.lock_party()
	# the night before, PLAYABLE (2026-07-16): Basil has been prepping the
	# hall all evening; the walk home through the sleeping town is the
	# player's own, up to the top of his own rope ladder
	theater.face(player, Vector2.DOWN)
	await theater.wait(ENTRY_FADE + 0.4)
	await theater.say("Basil", "I can't believe I'm going to actually graduate from wizard school having never performed a single spell.")
	await theater.say("Basil", "Home. Sleep.")
	theater.close_dialog()
	theater.unlock_party()
	_show_banner("HOME - GET SOME SLEEP", BANNER_HOLD)


# ---- dash (morning): the ground run — paw-prints, reach the school -----------------

## The squelch already happened on the deck (canopy_thesis); the moment the
## descent seats the body on the rungs, the run is live.
func _phase_dash() -> void:
	tint.color = TINT_MORNING
	_dashing = true
	_last_print = player.global_position
	_show_banner("GET TO THE ACADEMY", BANNER_HOLD)
	# the Academy stair is the finish
	var goal := Area2D.new()
	goal.collision_layer = 0
	goal.collision_mask = 2
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = DASH_GOAL_SIZE
	shape.shape = rect
	goal.add_child(shape)
	# DASH_GOAL_OFF is +24, not the +40 this used to be: since the Alembic rebuild
	# the Academy is its own scene and `school` names the NORTH LANE'S MOUTH, the
	# way there rather than a building. Two rows down the lane is still lane — the
	# old +40 was the forecourt cliff band, a goal rect of solid cells the player
	# could never enter, which hangs the beat forever with no error. The plant
	# spawn happens to use the same offset and that is fine: the two are in
	# different phases and never coexist.
	goal.position = MapData.anchor_px(map, "school") + DASH_GOAL_OFF
	add_child(goal)
	goal.body_entered.connect(_on_reach_school)


func _on_reach_school(body: Node2D) -> void:
	if not body.is_in_group("player") or not _dashing:
		return
	_dashing = false
	theater.lock_party()
	await theater.say("Basil", "Made it. Okay. Deep breath. You belong here.")
	theater.close_dialog()
	await fade_out()
	get_tree().change_scene_to_file("res://scene/hall.tscn")


func _process(delta: float) -> void:
	# the village breathes on thesis day too — cycle the fountain + buildings
	# (per-prop phase offset = looser, less mechanical), same as town_fest
	if _animated.is_empty():
		return
	_anim_t += delta
	var f := int(_anim_t / 0.18)
	for i in _animated.size():
		var s := _animated[i]
		s.frame = (f + i) % s.hframes


func _physics_process(_delta: float) -> void:
	# drop a fading paw-print trail behind Basil during the dash
	if not _dashing or not is_instance_valid(player):
		return
	if player.global_position.distance_to(_last_print) >= 14.0:
		_last_print = player.global_position
		_drop_print(player.global_position + Vector2(0.0, 8.0))


func _drop_print(pos: Vector2) -> void:
	var p := WorldFx.decal($World, FX_SHEET, FX_PRINT, pos)
	var tw := p.create_tween()
	tw.tween_interval(1.2)
	tw.tween_property(p, "modulate:a", 0.0, 1.4)
	tw.tween_callback(p.queue_free)


# ---- steps (dusk) + the leaving (night) --------------------------------------------
## The clinic-steps ending (2026-07-17): Basil gets six steps out of the
## doctor's door and folds onto the stoop. Ridley finds him there, says the
## blunt thing, and leaves — Basil barely speaks; the bowed head says it.
## Then the cut: the south gate at night — the knapsack, one look back at the
## town, the goodbye he owes nobody, and he walks out of the story. Fully
## scripted on purpose — the user's agency spent itself at the sickroom door;
## this part just happens TO him.

func _phase_steps() -> void:
	tint.color = TINT_DUSK
	theater.lock_party()
	# out the doctor's door — the east neighbor cottage; he lands on the
	# door mouth, feet on the lane below the arch
	Party.place(MapData.anchor_px(map, "cottage_e"))
	player.sprite.play("sad")
	await theater.wait(ENTRY_FADE + 0.4)
	# no "six steps" narrator (2026-07-18) — the six steps are just WALKED,
	# slow, and then his legs quit
	await theater.walk(player, MapData.anchor_px(map, "cottage_e") + Vector2(4.0, 14.0), 26.0)
	player.sprite.play("sit")             # down onto the clinic steps
	player.sprite.flip_h = false          # profile east, where the lane runs
	await theater.wait(1.6)
	# Ridley comes up the lane — the witness, still carrying it. He arrives from
	# and leaves to ONE spot, the lane east of the stoop, and it is now the
	# "lane_e" anchor rather than a bare Vector2(430, 456) written twice: two
	# copies of a pixel are two chances for a re-author to move the lane out
	# from under him and leave the witness walking in from inside a wall.
	var badger: NPC = _npc("Ridley", SHEET_BADGER, 6, MapData.anchor_px(map, "lane_e"))
	await theater.walk(badger, MapData.anchor_px(map, "cottage_e") + Vector2(38.0, 14.0), 44.0)
	await theater.say("Ridley", "Hey. Basil, right? I was there. On the road. I saw the whole thing.")
	await theater.say("Ridley", "The doctor won't say it plain, so: how is she?")
	await theater.say("Basil", "...")
	await theater.wait(0.6)
	await theater.say("Ridley", "That bad. ...You know what? Sitting out here like the sky fell on YOU...that's pretty selfish.")
	player.sprite.play("hurt")
	await theater.wait(0.4)
	player.sprite.play("sit")
	await theater.say("Ridley", "You weren't the one who got run over. She's the one in the bed. And you're over here feeling sorry for yourself?")
	await theater.say("Ridley", "...I'm just saying. Perspective. Anyway. Feel better!")
	theater.close_dialog()
	# he says his piece and walks off — nobody stops him, back down the same
	# lane he came up (the one anchor, both directions)
	await theater.walk(badger, MapData.anchor_px(map, "lane_e"), 52.0)
	badger.queue_free()
	await theater.wait(0.8)
	await theater.say("Basil", "...")
	theater.close_dialog()
	player.sprite.play("bow_head")        # the slump past sad — no more words
	# night falls on him sitting there
	var tw := create_tween()
	tw.tween_property(tint, "color", TINT_NIGHT, 2.4)
	await tw.finished
	await theater.wait(1.2)
	# the pollable end-state for the probe (kept from the fountain phase)
	Game.set_flag("prologue_scolded")
	await theater.black(1.4)
	_leaving()


## The cut: the south gate at night. A knapsack over his shoulder, one look
## back at the town (2026-07-18 — restaged from the east lane), and out.
func _leaving() -> void:
	# the central road, just inside the gate — the "gate_inside" anchor, not the
	# old Vector2(440, 460). The tableau has to read as HIM STANDING IN THE
	# GATEWAY; a stale pixel would park him in whatever the re-author puts there
	Party.place(MapData.anchor_px(map, "gate_inside"))
	player.sprite.play("knapsack")
	player.sprite.flip_h = false          # profile: the held tableau
	await theater.clear(1.2)
	await theater.wait(1.8)               # the tableau holds: knapsack Basil
	# the look back: he turns to face the town he's leaving
	player.sprite.play("knapsack_back")
	player.sprite.flip_h = false
	await theater.wait(1.2)
	await theater.say("Basil", "...Goodbye.")
	await theater.say("Basil", "I wish I could have belonged here...")
	theater.close_dialog()
	await theater.wait(1.0)
	# then he turns away and trudges out the lamp-flanked gate — the turn is a
	# beat of profile, then the SOUTH-facing trudge (2026-07-19: the walk used
	# to play the side clip while tweening south and read as a sideways glide)
	player.sprite.play("knapsack")
	player.sprite.flip_h = false
	await theater.wait(0.5)               # the turn: a profile flash...
	player.sprite.play("knapsack_walk_down")   # ...then face down the road
	# South, through the gate mouth, gone. The destination is DELIBERATELY
	# off-map — one tile past the last row — so he is still walking when the
	# black lands and is never seen to stop; that is why it gets no anchor
	# (every anchor must sit on a walkable cell) and is derived from the map's
	# own height instead of the old Vector2(440, 545). The x is the gate's own
	# axis, exit_south — the same x _wall_gate_mouth() puts its wall on, so the
	# trudge and the wall that stops a wander can never end up on different
	# roads. The duration comes from the distance at TRUDGE_SPEED, because the
	# tween is killed by the fade at 4.4s and its endpoint only ever set the
	# PACE.
	var out := Vector2(MapData.anchor_px(map, "exit_south").x,
			MapData.size_px(map).y + 16.0)
	var walk := create_tween()
	walk.tween_property(player, "global_position", out,
			player.global_position.distance_to(out) / TRUDGE_SPEED)
	await theater.wait(2.8)
	await theater.black(1.6)
	if walk.is_running():
		walk.kill()
	# one TIME card only (the 2026-07-18 card purge — the hermit years and
	# the kept watch are shown by the adult build itself: the shut-in house,
	# the mantel whirligig, look_watch)
	await theater.card("YEARS LATER.", 2.0)
	Game.set_flag("prologue_done")
	Party.set_roster([&"basil", &"fuji"], &"basil")
	# ... and the years end on the night the magic does: the Ebb sequence
	# (scene/ebb.gd -> scene/library.gd) plays before the adult build wakes
	get_tree().change_scene_to_file("res://scene/ebb.tscn")


# ---- helpers ----------------------------------------------------------------------

## Same walls as town_fest's: the 80x56 grid has THREE mouth roads running to
## the map edge (south gate, north lane, east lane) and the thesis phases wire
## an exit on none of them — without these a body can walk off the collision
## grid into the void.
func _wall_gate_mouth() -> void:
	var size := MapData.size_px(map)
	_wall(Vector2($ExitSouth.position.x, size.y + 4.0), Vector2(64.0, 8.0))
	_wall(Vector2(MapData.anchor_px(map, "exit_north").x, -4.0), Vector2(64.0, 8.0))
	_wall(Vector2(size.x + 4.0, MapData.anchor_px(map, "exit_se").y),
			Vector2(8.0, 64.0))


func _npc(nm: String, sheet: Texture2D, cols: int, pos: Vector2) -> NPC:
	var npc: NPC = NPCScene.instantiate()
	npc.display_name = nm
	npc.sheet = sheet
	npc.frame_cols = cols
	npc.position = pos
	$World.add_child(npc)
	return npc
