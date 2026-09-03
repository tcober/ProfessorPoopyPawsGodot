class_name CanopyScene
extends TravelScene

## Shared driver for THE BOUGHS — the canopy half of Alembic Town since the
## 2026-08-23 two-scene split (assets/maps/canopy.txt; the doctrine note is in
## that map's header and DESIGN.md -> "STACKED WALKABLE STOREYS").
##
## Four ring decks joined by rope bridges over THE DROP; below every ring the
## trunk descends into the dark with the rope ladder on it, and the ladder's
## bottom two rungs are a TRAVEL MOUTH back down to the floor scene. The climb
## is continuous by construction: the floor scene hands the body over
## mid-ladder (Game.town_spawn = "headN"), this scene seats it ON the rungs a
## row above the mouth still facing up, and the same in reverse going down —
## you leave climbing and arrive climbing, which is the split's answer to the
## old REJECTED-bullet's sense-of-place objection. The other answer is the
## view: the drop renders the town itself, lit windows and all.
##
## Era subclasses (alembic_canopy / canopy_fest / canopy_fever / canopy_thesis)
## supply the map/layout/props paths, the floor scene to descend into, and
## their story beats — this base owns the ladder mouths, the spawn routing and
## the fireflies, so the eras can't drift (the _alembic.py lesson, in GDScript).

const LADDERS := 4


func _player_node() -> Node2D:
	return Party.spawn($World, Vector2.ZERO)


## The era's floor scene — where the ladders descend to.
func _ground_scene() -> String:
	assert(false, "CanopyScene subclass must override _ground_scene()")
	return ""


func _props_path() -> String:
	return ""


## Era hook: fired just before a ladder descent changes scene (re-arm a phase
## router here — Game fields are the only state that survives the door).
func _on_descend(_ladder: int) -> void:
	pass


func _place_player() -> void:
	var spawn := Game.town_spawn
	Game.town_spawn = ""
	if spawn.begins_with("head") and map.anchors.has(spawn):
		# arriving UP the ladder: seat the body ON the rungs a row above the
		# travel mouth, on the lane's own centre line, still climbing
		Party.place(MapData.anchor_px(map, spawn) + Vector2(8.0, -24.0))
	else:
		# out of Basil's own front door (or a direct scene load): land ON the
		# home anchor — the door-mouth arrival contract; the door zone hangs
		# over the trunk face so the arrival spot is outside it
		Party.place(MapData.anchor_px(map, "home"))
		_standing["home"] = true


## Era hook: whether this visit gets the firefly field (thesis MORNING says no
## — fireflies at breakfast are the wrong kind of magic).
func _wants_fireflies() -> bool:
	return true


func _extra_setup() -> void:
	if _props_path() != "":
		PropSpawner.build(_props_path(), map, $World)
	_collect_animated()
	_wire_ladder_mouths()
	if _wants_fireflies():
		_fireflies()
	Party.clamp_cameras(MapData.size_px(map))
	Party.leader_changed.connect(_on_leader_changed)


## The four ladder mouths — one zone over each run's bottom two rungs
## (anchors head1..head4), wired through _wire_exit so a swallowed event
## re-delivers and the entry lock holds (the raw-exit contract).
func _wire_ladder_mouths() -> void:
	for i in range(1, LADDERS + 1):
		var a := "head%d" % i
		if not map.anchors.has(a):
			continue
		var zone := Area2D.new()
		zone.collision_layer = 0
		zone.collision_mask = 2
		var shape := CollisionShape2D.new()
		var rect := RectangleShape2D.new()
		rect.size = Vector2(28.0, 30.0)
		shape.shape = rect
		zone.add_child(shape)
		zone.position = MapData.anchor_px(map, a) + Vector2(8.0, 8.0)
		add_child(zone)
		_wire_exit(zone, _on_ladder_mouth.bind(i))


func _on_ladder_mouth(body: Node, ladder: int) -> void:
	if not _exit_ok(body):
		return
	_busy = true
	Game.town_spawn = "top%d" % ladder
	_on_descend(ladder)
	await fade_out()
	get_tree().change_scene_to_file(_ground_scene())


## The fireflies, in two fields: a sparse one drifting at deck level and a
## denser, dimmer one down in the drop — motes UNDER your feet are what sell
## thirty feet of air better than any fascia can.
func _fireflies() -> void:
	var ff := Fireflies.new()
	add_child(ff)
	var size := MapData.size_px(map)
	ff.seed($World, Rect2(48.0, 150.0, size.x - 96.0, 130.0), 8)
	ff.seed($World, Rect2(32.0, 330.0, size.x - 64.0, 150.0), 14, 0.5)
