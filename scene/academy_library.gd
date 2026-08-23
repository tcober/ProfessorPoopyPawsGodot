extends Node2D

## THE ACADEMY READING ROOM — Prologue A0 "The Fever" (docs/DESIGN.md
## Story). The one room in the game a nine-year-old is not allowed into,
## entered anyway, quietly, because the doctor said "not in my bag" and a
## boy heard "somewhere else, then". Deliberately the Lanternwood library's
## shape — the three stacks, the aisles, the desk — twenty years and an
## ocean before Fuji searches its mirror, and neither scene says so.
##
## THE SEARCH GATE (the research-night shape: control from the first
## frame, a hint, no cutscene): the fancy shelf first. ENCHANTMENT - THEORY
## is nine hundred pages of wards for THINGS, and only after it has failed
## him twice (prologue_wrong_shelf) does he look at the unfancy still-room
## shelf by the desk — where a household physick book has half a page on
## fevers. He cannot borrow it (he is not a member; nobody is here to ask),
## so he COPIES it at the desk, and leaves with a piece of paper instead of
## a book (prologue_herbal_found). Write it down.

const MAP_PATH := "res://assets/maps/academy_library.txt"
const LAYOUT_PATH := "res://assets/tilesets/academy_library_layout.txt"
const PROPS_PATH := "res://assets/tilesets/academy_library_props.txt"
const NEXT_SCENE := "res://scene/town_fever.tscn"

const LOOK_ZONE := Vector2(32.0, 20.0)

## The three stacks, west to east: the aisle anchor a body searches each
## from, and its brass plate. The still-room is the ANSWER, and it is the
## plain one by the desk — the shelf nobody at this school respects.
const STACKS := [
	{anchor = "stack_a", line = "ENCHANTMENT - THEORY. Wards. Nine hundred pages on keeping rain off a roof."},
	{anchor = "stack_b", line = "HISTORIES. Five lands of kings. None of them was ever ill, apparently."},
	{anchor = "stack_c", line = "THE STILL-ROOM. Beasts and bees and brewing."},
]
const ANSWER := 2

var map: Dictionary
var player: Node2D
var _near := ""
var _zones: Dictionary = {}
var _busy := false
var _leaving := false
## The enchantment stack has been read once this visit. An instance var,
## not a flag (the _wand_half precedent): "it failed him twice" is a fact
## about this afternoon in this room.
var _ench_read := false

@onready var theater: Theater = $Theater


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	PropSpawner.build(PROPS_PATH, map, $World)
	player = Party.spawn($World, MapData.anchor_px(map, "player_spawn"))
	Party.clamp_cameras(MapData.view_size())
	$ExitDoor.position = Vector2(MapData.bbox_rect(map, "-").get_center().x,
			MapData.anchor_px(map, "exit_door").y)
	$ExitDoor.body_entered.connect(_on_exit_door)
	_wire_zones()
	if not Game.flag("prologue_herbal_found"):
		theater.lock_party()
		_first_visit()


## Control straight back — this is a GATE, not a cutscene (the
## research-night shape, twenty years early).
func _first_visit() -> void:
	await theater.wait(0.8)
	await theater.say("Basil", "...Nobody. Everyone's up at the wards hall.")
	await theater.say("Basil", "Magic fixes everything. So the books about magic will say how.")
	theater.close_dialog()
	theater.unlock_party()
	theater.hint("SEARCH THE STACKS", 2.4)


func _process(_delta: float) -> void:
	if not _near.is_empty() and not _busy and not _cutscene() \
			and Input.is_action_just_pressed("interact"):
		_run_zone(_zones[_near])


func _cutscene() -> bool:
	return not is_instance_valid(player) or not player.is_physics_processing()


# ---- the search gate ---------------------------------------------------------------

func _search_stack(i: int) -> void:
	if Game.flag("prologue_herbal_found"):
		await theater.say("Basil", STACKS[i].line)
		await theater.say("Basil", "I have what I came for. ...I was never here.")
		return
	if i == ANSWER:
		if Game.flag("prologue_wrong_shelf"):
			await _find_recipe()
		else:
			# he walks straight past the plain shelf — the lock is the beat
			await theater.say("Basil", STACKS[i].line)
			await theater.say("Basil", "That's not - no. It's ENCHANTMENT I want.")
		return
	await theater.say("Basil", STACKS[i].line)
	if i == 0:
		# TWO VISITS on purpose (the two-visit precedent): the first read is
		# hope, the second is the shelf failing him — and only a shelf that
		# has failed him twice sends him to the plain one by the desk
		if Game.flag("prologue_wrong_shelf"):
			await theater.say("Basil", "Wards, wards, wards. Things, things, things.")
		elif not _ench_read:
			_ench_read = true
			await theater.say("Basil", "Nine hundred pages. One of them will say fevers.")
			theater.close_dialog()
			await theater.wait(0.8)
			await theater.say("Basil", "...Start at the top.")
		else:
			Game.set_flag("prologue_wrong_shelf")
			theater.close_dialog()
			await theater.wait(0.7)
			await theater.say("Basil", "Warm a roof. Ward a well. Charm a cart-axle.")
			await theater.say("Basil", "None of it is for a PERSON. It's all for THINGS.")
			theater.close_dialog()
			theater.hint("THE PLAIN SHELF - BY THE DESK", 2.6)


## The find, and the copy. He cannot borrow it — so half a page goes out
## the door in his own handwriting, which is the first time in his life
## that writing something down fixes anything.
func _find_recipe() -> void:
	await theater.say("Basil", "Beasts and bees and... 'A HOUSEHOLD PHYSICK.'")
	theater.close_dialog()
	await theater.wait(0.8)
	theater.hop(player, 4.0)
	await theater.say("Basil", "'Of Fevers, and the Ordering of a Still-Room.'")
	await theater.say("Basil", "It's a recipe. It's just a RECIPE.")
	theater.close_dialog()
	await theater.wait(0.6)
	await theater.say("Basil", "'...may not leave the room.' Fine. FINE.")
	theater.close_dialog()
	# to the desk: dog-leg the aisle (theater walks are straight no-collision
	# tweens and the east stack stands between him and the lamp)
	await theater.walk_via(player, [
		MapData.anchor_px(map, "stack_c") + Vector2(32.0, 0.0),
		MapData.anchor_px(map, "stack_c") + Vector2(32.0, -32.0),
		MapData.anchor_px(map, "desk_spot")])
	theater.face(player, Vector2.UP)
	await theater.wait(0.9)
	await theater.say("Basil", "Write it down. Write it down, write it down -")
	theater.close_dialog()
	await theater.wait(1.8)                # the copying. All of it.
	await theater.say("Basil", "Water. Bark. Time. ...Half a page. That's all it was.")
	Game.set_flag("prologue_herbal_found")
	theater.close_dialog()
	theater.hint("HOME", 2.4)


# ---- zones -------------------------------------------------------------------------

func _wire_zones() -> void:
	_zone("plaque", MapData.anchor_px(map, "plaque"), func() -> void:
		await theater.say("Basil", "'MEMBERS OF THE FACULTY AND ENROLLED STUDENTS.'")
		theater.close_dialog()
		await theater.wait(0.5)
		await theater.say("Basil", "...The door was open."))
	_zone("desk", MapData.anchor_px(map, "desk_spot"), func() -> void:
		if Game.flag("prologue_herbal_found"):
			await theater.say("Basil", "Half a page. In my OWN handwriting. Which is terrible.")
		else:
			await theater.say("Basil", "Somebody important's desk. Somebody important's inkwell."))
	_look("K", "You could read for a YEAR in here. Nobody's reading.", -32.0)
	_look("W", "Grey out. It's been grey all week.")
	for i in STACKS.size():
		var idx := i             # bind the index, not the loop variable
		_zone("stack%d" % i, MapData.anchor_px(map, STACKS[i].anchor),
				func() -> void: await _search_stack(idx))


func _look(chars: String, line: String, nudge := 0.0) -> void:
	var box := MapData.bbox_rect(map, chars)
	_zone(chars, _look_cell(box.get_center().x + nudge, box.end.y),
			func() -> void: await theater.say("Basil", line))


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


func _look_cell(x: float, bottom: float) -> Vector2:
	var cx := int(x / 16.0)
	var ty := int(bottom / 16.0)
	while ty < map.rows and MapData.is_solid(map, Vector2i(cx, ty)):
		ty += 1
	return Vector2(cx * 16 + 8, ty * 16 + 8)


func _run_zone(action: Callable) -> void:
	_busy = true
	theater.lock_party()
	await action.call()
	theater.close_dialog()
	theater.unlock_party()
	_busy = false


func _on_exit_door(body: Node) -> void:
	# _busy too: it is how tools/zwalk.gd pins a scene still for the walk
	if not body.is_in_group("player") or _leaving or _busy:
		return
	_leaving = true
	Game.town_spawn = "school"
	get_tree().change_scene_to_file.call_deferred(NEXT_SCENE)
