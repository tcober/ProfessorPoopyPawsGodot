extends Node2D

## MOM'S BEDROOM — Prologue A0 "The Fever" (docs/DESIGN.md Story). Behind
## the plank door in the great room's west wall, on the sickroom recipe —
## but a home, not a ward: the family timber, the worn russet quilt, Sage's
## chair pulled up to the bedside, the nightstand candle. Mom lies propped
## on the pillow as the npc_mom_bed sprite (the sickroom idiom); the room
## plays two beats, gated on flags:
##
##   THE BEDSIDE (A0-3, not prologue_doctor_heard) — "some things are
##     longer than a mending" from her side of it: she is kind, he is
##     nine, and there is nothing to do. Ends on the plant cashing —
##     "'Not in my bag.' ...Somewhere else, then." — and the Academy hint.
##   SHE DRINKS (A0-7, prologue_remedy_made and not mom_better) — the
##     worst thing she has ever had in her mouth, and one night's sleep.
##     The door out plays "THAT NIGHT." and lands in the BUILT great room.
##
## Between the two, revisits find her resting (a bedside line, nothing
## else). Basil enters through the EAST door — the great room's west-wall
## plank door, from her side — and the bed is pulled up against that wall,
## so through the door IS the bedside. The arrival cell (player_spawn,
## col 15) and the exit zone (the - cells, col 16) can never overlap.

const MAP_PATH := "res://assets/maps/momroom.txt"
const LAYOUT_PATH := "res://assets/tilesets/momroom_layout.txt"
const PROPS_PATH := "res://assets/tilesets/momroom_props.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const SHEET_MOM_BED := preload("res://assets/npc_mom_bed_gen.png")

const DIM_DAY := Color(0.72, 0.72, 0.82)       # overcast, curtains half-drawn
const DIM_EVE := Color(0.6, 0.55, 0.74)        # the night she drinks it

var map: Dictionary
var player: Node2D
var _mom: NPC
var _busy := false
var _leaving := false
var _near := ""
var _zones: Dictionary = {}

@onready var theater: Theater = $Theater


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	PropSpawner.build(PROPS_PATH, map, $World)
	player = Party.spawn($World, MapData.anchor_px(map, "player_spawn"))
	Party.clamp_cameras(MapData.view_size())
	# Mom on the pillow: +8 centers her on the 2-cell bed row, -14 sets her
	# head on the pillow volume (the sickroom kitty_bed geometry, verbatim)
	_mom = NPCScene.instantiate()
	_mom.display_name = "Mom"
	_mom.sheet = SHEET_MOM_BED
	_mom.frame_cols = 6
	_mom.position = MapData.anchor_px(map, "mom_bed") + Vector2(8.0, -14.0)
	$World.add_child(_mom)
	_mom.sprite.play("idle_down")          # rest — asleep until a beat wakes her
	# the east-wall mouth: a vertical strip on the - cells (x from the
	# anchor's column, y centered on the two-cell gap)
	$ExitDoor.position = Vector2(MapData.anchor_px(map, "exit_door").x,
			MapData.bbox_rect(map, "-").get_center().y)
	$ExitDoor.body_entered.connect(_on_exit_door)
	_wire_zones()
	var drink := Game.flag("prologue_remedy_made") and not Game.flag("prologue_mom_better")
	$Dim.color = DIM_EVE if drink else DIM_DAY
	if not Game.flag("prologue_doctor_heard"):
		theater.lock_party()
		_bedside()
	elif drink:
		theater.lock_party()
		_drink()


func _process(_delta: float) -> void:
	if not _near.is_empty() and not _busy and not _cutscene() \
			and Input.is_action_just_pressed("interact"):
		_run_zone(_zones[_near])


func _cutscene() -> bool:
	return not is_instance_valid(player) or not player.is_physics_processing()


# ---- A0-3: the bedside -------------------------------------------------------------

## The verdict from her side of it. The doctor already mended her — twice —
## and she is still down, because mending an illness is not ending it.
## Nobody in the room says what that means.
func _bedside() -> void:
	await theater.wait(0.9)
	_mom.play_act()                        # awake, weak — but HER
	await theater.say("Mom", "Basil. Come here where I can see you without the turning.")
	theater.close_dialog()
	# the gate is the full-width open row below the bed (a point-rect at the
	# bedside is walkable around and reads as a hang — the sickroom law)
	await theater.walk_gate(Vector2(MapData.size_px(map).x * 0.5, 104.0),
			Vector2(MapData.size_px(map).x, 20.0))
	await theater.walk(player, MapData.anchor_px(map, "bedside"), 50.0)
	theater.face(player, Vector2.UP)
	await theater.say("Mom", "There. Hello, sunshine.")
	await theater.say("Mom", "Is your sister still doing her charm at me? Tell her it's lovely.")
	await theater.say("Basil", "It isn't working.")
	await theater.wait(0.6)
	await theater.say("Mom", "It's lovely.")
	theater.close_dialog()
	await theater.wait(0.9)
	player.sprite.play("sad")
	_mom.play_emote()
	await theater.say("Mom", "Go and be somewhere else, sweetheart. You've got a face on you like a wet Sunday.")
	theater.close_dialog()
	_mom.sprite.play("idle_down")          # she's under again before he answers
	await theater.wait(1.2)
	player.sprite.play("idle_down")
	Game.set_flag("prologue_doctor_heard")
	await theater.say("Basil", "...'Not in my bag.'")
	await theater.say("Basil", "Somewhere else, then.")
	theater.close_dialog()
	theater.unlock_party()
	theater.hint("THE ACADEMY - UP THE NORTH LANE", 2.6)


# ---- A0-7: she drinks --------------------------------------------------------------

func _drink() -> void:
	await theater.wait(0.9)
	_mom.play_act()
	await theater.say("Mom", "What's this face. And what, please, is THAT.")
	theater.close_dialog()
	await theater.walk_gate(Vector2(MapData.size_px(map).x * 0.5, 104.0),
			Vector2(MapData.size_px(map).x, 20.0))
	await theater.walk(player, MapData.anchor_px(map, "bedside"), 50.0)
	theater.face(player, Vector2.UP)
	await theater.say("Basil", "Drink it. All of it. While it's warm.")
	theater.close_dialog()
	await theater.wait(1.6)                # she drinks. All of it.
	await theater.say("Mom", "...That is the worst thing I have ever had in my mouth.")
	await theater.say("Basil", "It's supposed to be.")
	await theater.say("Mom", "Is it.")
	await theater.say("Basil", "It doesn't say. I think it just is.")
	theater.close_dialog()
	await theater.wait(1.0)
	_mom.play_emote()                      # the warm look — and nothing smaller
	await theater.wait(1.4)
	_mom.sprite.play("idle_down")          # asleep. Properly, this time.
	await theater.wait(1.8)
	Game.set_flag("prologue_mom_better")
	theater.unlock_party()
	theater.hint("QUIETLY", 2.2)


# ---- zones / doors -----------------------------------------------------------------

func _wire_zones() -> void:
	_zone("bedside", MapData.anchor_px(map, "bedside"), func() -> void:
		if Game.flag("prologue_mom_better"):
			await theater.say("Basil", "Asleep. Actually asleep.")
		elif Game.flag("prologue_remedy_made"):
			await theater.say("Mom", "Mm? ...I'm poor company, love. I keep nodding off mid-sentence.")
		else:
			await theater.say("Mom", "Mm. Still here? Go on - I'll keep. I always keep."))
	var win := MapData.bbox_rect(map, "W")
	_zone("window", Vector2(win.get_center().x, win.end.y + 24.0), func() -> void:
		await theater.say("Basil", "Grey again. It's been grey all week."))


func _zone(id: String, at: Vector2, action: Callable) -> void:
	_zones[id] = action
	var zone := Area2D.new()
	zone.collision_layer = 0
	zone.collision_mask = 2
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(32.0, 20.0)
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


func _run_zone(action: Callable) -> void:
	_busy = true
	theater.lock_party()
	await action.call()
	theater.close_dialog()
	theater.unlock_party()
	_busy = false


## Out through the plank door. The night she drinks it, the door carries the
## time card — hours pass between her falling asleep and A0-8's midnight,
## and a card may state exactly that much and nothing more.
func _on_exit_door(body: Node) -> void:
	# _busy too: it is how tools/zwalk.gd pins a scene still for the walk
	if not body.is_in_group("player") or _leaving or _busy:
		return
	_leaving = true
	Game.interior_spawn = "momdoor_out"
	if Game.flag("prologue_mom_better"):
		await theater.black(1.2)
		await theater.card("THAT NIGHT.", 2.0)
	get_tree().change_scene_to_file.call_deferred("res://scene/downstairs_fever.tscn")
