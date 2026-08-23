extends Node2D

## The great room, THE FEVER — Prologue A0 (docs/DESIGN.md Story). The same
## room as downstairs_fest, years earlier, and NOT a lab yet: this scene
## picks its own dressing from story state — assets/maps/downstairs_bare.txt
## (crates and preserve jars where the boiler and bench will stand) until
## prologue_remedy_made, and the built downstairs.txt after it. The corner
## getting built IS the beat; the swap happens across a scene change, never
## mid-scene. The two grids are byte-locked twins (same anchors, same
## kitchen), so every position below survives the swap.
##
## Beats this one room plays, gated on flags (the downstairs_fest idiom):
##   the DOCTOR LEAVING (A0-2, not prologue_doctor_gone) — Ciconia's "not
##     in my bag" at the front door, Sage against her mother's door;
##   the SIMMER (A0-6, prologue_herbal_found and not remedy_made) — the
##     copied recipe at the hearth, one colour warming from cold to amber
##     (ONE colour on purpose: the four reagents are A12's, two years out);
##   the NIGHT CLOSE (A0-8, prologue_mom_better) — the built room at night,
##     Sage on the stairs, "What are you making." / "I don't know yet.",
##     then "TWO SUMMERS LATER." and the festival morning.
##
## MOM'S DOOR (the ' cells, a gap in the WEST wall) walks through to
## scene/momroom.tscn.

const NPCScene := preload("res://entities/npcs/npc.tscn")
const SHEET_SAGE := preload("res://assets/npc_sage_gen.png")
const SHEET_STORK := preload("res://assets/npc_stork_gen.png")
const FX_SHEET := preload("res://assets/prologue_fx.png")

const FX_BEAKER := 24

const DIM_GREY := Color(0.76, 0.76, 0.85)      # overcast fever morning
const DIM_DUSK := Color(0.74, 0.6, 0.68)       # back from the Academy
const DIM_NIGHT := Color(0.52, 0.5, 0.72)      # the night the corner is built
const FIRE_OFFSET := Vector2(10.0, 20.0)       # see scene/downstairs.gd

## The simmer's pot colour, cold to amber — ONE colour warming, deliberately
## not the four Alchemy reagents (those are the brew's, two years from now).
const POT_COLD := Color(0.62, 0.68, 0.78)
const POT_WARM := Color(1.0, 0.78, 0.42)

var map: Dictionary
var player: Node2D
var _built := false
var _anim_t := 0.0
var _busy := false
var _leaving := false
var _sage: NPC
var _pot: Sprite2D

@onready var theater: Theater = $Theater


func _simmering() -> bool:
	return Game.flag("prologue_herbal_found") and not Game.flag("prologue_remedy_made")


func _ready() -> void:
	# THE ART IS CHOSEN BY STORY STATE (the phase-router rule applied to
	# dressing): the bare twin until the remedy is made, the built lab after
	_built = Game.flag("prologue_remedy_made")
	var stem := "downstairs" if _built else "downstairs_bare"
	map = MapData.load_map("res://assets/maps/%s.txt" % stem)
	var tiles: TileSet = load("res://assets/tilesets/%s_tiles.tres" % stem)
	$Tiles.tile_set = tiles
	$TilesUpper.tile_set = tiles
	$Glow.texture = load("res://assets/tilesets/%s_glow.png" % stem)
	TiledMap.build("res://assets/tilesets/%s_layout.txt" % stem,
			{"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	PropSpawner.build("res://assets/tilesets/%s_props.txt" % stem, map, $World)
	var spawn := Game.interior_spawn
	Game.interior_spawn = ""
	if spawn.is_empty() or not map.anchors.has(spawn):
		spawn = "stair_arrival"
	var spawn_px := MapData.anchor_px(map, spawn)
	var door_x := MapData.bbox_rect(map, "-").get_center().x
	if spawn == "front_door":
		spawn_px.x = door_x
	elif spawn == "momdoor_out":
		# the door is a vertical gap in the west wall — center on it in y
		spawn_px.y = MapData.bbox_rect(map, "'").get_center().y
	player = Party.spawn($World, spawn_px)
	Party.clamp_cameras(MapData.view_size())
	$Fire.position = MapData.bbox_rect(map, "H").position + FIRE_OFFSET
	$ExitDoor.position = Vector2(door_x, MapData.anchor_px(map, "exit_door").y)
	$ExitDoor.body_entered.connect(_on_exit_door)
	_wire_momdoor()
	if not Game.flag("prologue_doctor_gone"):
		$Dim.color = DIM_GREY
		_doctor_leaving()
	elif _simmering():
		$Dim.color = DIM_DUSK
		_simmer()
	elif Game.flag("prologue_mom_better"):
		$Dim.color = DIM_NIGHT
		_night_close()
	elif Game.flag("prologue_remedy_made"):
		$Dim.color = DIM_DUSK
		_spawn_sage_hearth()
		theater.hint("HER ROOM", 2.2)
	else:
		# between the bedside and the recipe: the house holds its breath
		$Dim.color = DIM_GREY
		_spawn_sage_hearth()
		theater.hint("THE ACADEMY - UP THE NORTH LANE", 2.4)


# ---- A0-2: the doctor leaving ------------------------------------------------------

## Ciconia with his hat in his hands at the front door; Sage on the floor
## against her mother's door. "Not in my bag" is the whole plant — a
## nine-year-old hears "somewhere else, then", and the chapter is him going
## to look for the somewhere else.
func _doctor_leaving() -> void:
	theater.lock_party()                   # before any await (the probe rule)
	var doctor := _npc("Dr. Ciconia", SHEET_STORK, 6,
			Vector2(MapData.bbox_rect(map, "-").get_center().x, 136.0))
	# Sage against her mother's door — the floor cell beside the west-wall
	# plank door. The mouth is two cells tall and she moves off before
	# control returns, so she never walls the doorway (the room-to-move rule).
	_sage = _npc("Sage", SHEET_SAGE, 10,
			MapData.anchor_px(map, "momdoor_out") + Vector2(0.0, 16.0))
	await theater.wait(1.0)
	doctor.play_act()
	await theater.say("Dr. Ciconia", "That's the second time this week. It just won't stick.")
	await theater.say("Dr. Ciconia", "Some things are longer than a mending. Keep her warm, keep her drinking. I'll check in Thursday.")
	await theater.say("Basil", "It's Monday.")
	doctor.play_idle()
	await theater.say("Dr. Ciconia", "It is.")
	await theater.wait(0.5)
	await theater.say("Basil", "Is there anything else?")
	await theater.wait(0.7)
	await theater.say("Dr. Ciconia", "Not in my bag.")
	theater.close_dialog()
	await theater.wait(0.6)
	# he lets himself out — the door swallows him mid-step (the stoop fiction)
	await theater.walk(doctor, doctor.position + Vector2(0.0, 40.0), 40.0)
	doctor.queue_free()
	await theater.wait(0.8)
	_sage.play_act()                       # the little warm charm, again
	await theater.say("Sage", "I did the warm spell on her. The one Mrs. Pell does on the bread.")
	await theater.say("Sage", "...")
	await theater.say("Sage", "...")
	await theater.wait(0.6)
	await theater.say("Basil", "...Do it again.")
	theater.close_dialog()
	# she takes the kettle instead — an eight-year-old keeping the house
	# running is the picture; nobody remarks on it
	await theater.walk(_sage, Vector2(72.0, 104.0), 50.0)
	_bind_sage_wander()
	Game.set_flag("prologue_doctor_gone")
	theater.unlock_party()
	theater.hint("HER ROOM", 2.4)


# ---- A0-6: the simmer --------------------------------------------------------------

## Home with half a copied page. The pot goes on the family hearth — mom's
## kettle, the good pot, no bench (there is no bench yet; that is the point
## of the room he is standing in).
func _simmer() -> void:
	theater.lock_party()
	_spawn_sage_hearth()
	_sage.hold()
	await theater.wait(0.8)
	await theater.say("Sage", "Where have you been?")
	await theater.say("Basil", "Researching.")
	await theater.wait(0.5)
	await theater.say("Basil", "I might have found a way to help her.")
	theater.close_dialog()
	theater.hint("THE HEARTH", 2.0)
	# the gate is the hearth's whole foot row — unavoidable for its objective
	var hearth := MapData.bbox_rect(map, "H")
	await theater.walk_gate(Vector2(hearth.get_center().x, hearth.end.y + 8.0),
			Vector2(hearth.size.x + 16.0, 20.0))
	await theater.walk(player, Vector2(hearth.get_center().x, hearth.end.y + 8.0), 45.0)
	theater.face(player, Vector2.UP)
	await theater.say("Basil", "2 parts water. 1 part willow Bark. Dash of creek moss. Boil for 10 minutes. Keep it at a simmer.")
	theater.close_dialog()
	_pot = WorldFx.airborne($World, FX_SHEET, FX_BEAKER,
			Vector2(hearth.get_center().x + 10.0, hearth.end.y - 2.0), 22.0)
	_pot.modulate = POT_COLD
	await theater.mash_meter("KEEP IT AT A SIMMER - MASH E", _pot_tick)
	Game.set_flag("prologue_remedy_made")
	_pot.modulate = POT_WARM
	player.sprite.play("happy")
	await theater.say("Sage", "It smells like a HEDGE.")
	await theater.say("Basil", "It's supposed to.")
	theater.close_dialog()
	player.sprite.play("idle_down")
	theater.unlock_party()
	theater.hint("HER ROOM", 2.4)


## The pot warms with the fill — one colour, cold slate to hearth amber.
func _pot_tick(fill: float) -> void:
	if is_instance_valid(_pot):
		_pot.modulate = POT_COLD.lerp(POT_WARM, fill)


# ---- A0-8: the night close ---------------------------------------------------------

## The built room, the middle of the night. The corner happened while she
## slept, and he is still at it. Four lines, a card, and the festival.
func _night_close() -> void:
	theater.lock_party()
	await theater.wait(0.8)
	# he crosses to the bench that exists now — tucked in behind it, working.
	# Dog-leg south then west along the benchtop row (theater walks are
	# straight no-collision tweens, and the boiler stands on the diagonal)
	var bench := MapData.bbox_rect(map, "E")
	await theater.walk_via(player, [
			Vector2(328.0, bench.get_center().y),
			Vector2(bench.position.x + 24.0, bench.get_center().y)], 40.0)
	theater.face(player, Vector2.DOWN)
	await theater.wait(1.4)
	_sage = _npc("Sage", SHEET_SAGE, 10,
			MapData.anchor_px(map, "stair_arrival") + Vector2(8.0, 0.0))
	await theater.wait(0.6)
	await theater.say("Sage", "It's the middle of the night.")
	await theater.say("Basil", "I know.")
	await theater.wait(0.6)
	await theater.say("Sage", "What are you making.")
	await theater.wait(0.8)
	await theater.say("Basil", "I don't know yet.")
	theater.close_dialog()
	await theater.wait(1.2)
	await theater.black(1.4)
	await theater.card("TWO SUMMERS LATER.", 2.2)
	get_tree().change_scene_to_file("res://scene/house_fest.tscn")


# ---- cast / doors ------------------------------------------------------------------

func _npc(nm: String, sheet: Texture2D, cols: int, pos: Vector2) -> NPC:
	var npc: NPC = NPCScene.instantiate()
	npc.display_name = nm
	npc.sheet = sheet
	npc.frame_cols = cols
	npc.position = pos
	$World.add_child(npc)
	return npc


## Sage at the hearth end, keeping the kettle on — and casting the little
## warm charm at it every time she settles (wander_rest = "act": her act
## cells ARE the cast). An eight-year-old running the kitchen; no line
## points at it.
func _spawn_sage_hearth() -> void:
	_sage = _npc("Sage", SHEET_SAGE, 10, Vector2(72.0, 104.0))
	_sage.lines = PackedStringArray([
		"She's resting. The doctor said drinking and warm.",
	])
	_bind_sage_wander()


func _bind_sage_wander() -> void:
	_sage.wander_cells = Rect2i(3, 6, 3, 3)
	_sage.wander = true
	_sage.wander_rest = "act"
	_sage.bind_map(map)


## Mom's door: the plank door set into the west wall. Walkable in the bare
## grid — stepping west into the wall gap walks through into her room. In
## the built grid the cells are solid and this zone can never fire (a body
## pressed against the closed door halts flush with the wall face, outside
## the strip); it is wired unconditionally because the anchors exist in
## both twins.
func _wire_momdoor() -> void:
	var door := Area2D.new()
	door.collision_layer = 0
	door.collision_mask = 2
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(14.0, 28.0)
	shape.shape = rect
	door.add_child(shape)
	door.position = MapData.bbox_rect(map, "'").get_center()
	add_child(door)
	door.body_entered.connect(_on_momdoor)


func _on_momdoor(body: Node) -> void:
	if not body.is_in_group("player") or _leaving or _busy:
		return
	_leaving = true
	get_tree().change_scene_to_file.call_deferred("res://scene/momroom.tscn")


func _process(delta: float) -> void:
	_anim_t += delta
	$Fire.frame = int(_anim_t / 0.16) % 3
	if _built and has_node("World/Boiler"):
		$World/Boiler.frame = int(_anim_t / 0.28) % 4


func _on_exit_door(body: Node) -> void:
	if not body.is_in_group("player") or _busy or _leaving:
		return
	if not Game.flag("prologue_doctor_heard"):
		_door_hint("Not before I've seen her.")
		return
	if _simmering():
		_door_hint("No. The pot first.")
		return
	if Game.flag("prologue_remedy_made") and not Game.flag("prologue_mom_better"):
		_door_hint("Her room. Now.")
		return
	if Game.flag("prologue_mom_better"):
		_door_hint("It's the middle of the night.")
		return
	_leaving = true
	Game.town_spawn = "home"
	get_tree().change_scene_to_file.call_deferred("res://scene/town_fever.tscn")


func _door_hint(line: String) -> void:
	_busy = true
	theater.lock_party()
	await theater.say("Basil", line)
	theater.close_dialog()
	theater.unlock_party()
	_busy = false
