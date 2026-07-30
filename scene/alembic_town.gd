extends TravelScene

## Alembic Town, walkable at zone scale — the Kakariko-style village the
## overworld's town icon opens into (see TravelScene for the shared machinery),
## and since 2026-07-29 a TWO-STRATA CANOPY TOWN: the forest floor, the plank
## boardwalk in the boughs above it, and the DINGHY LIFT joining them.
## Basil's open door travels down to the lab (downstairs); the shops, inn,
## neighbor cottages and the terrace's barred Academy announce in the banner;
## the south lane exits to the overworld. The spawn is routed through
## Game.town_spawn (read-and-clear; "home" = below Basil's door for the
## downstairs front door, "" = the south gate, where the overworld drops you).

const MAP_PATH := "res://assets/maps/town.txt"
const LAYOUT_PATH := "res://assets/tilesets/town_layout.txt"

## THE DINGHY LIFT. The two storeys are DISJOINT in the grid — that is the whole
## reason two storeys are expressible at all here — and the lift's shaft is SOLID,
## so this is the one place they are joined by CODE rather than by authoring. That
## is exactly what a door is: a scripted crossing of a wall. See
## TileScene.assert_lift for why a walkable shaft is not an option (there are no
## treads and there is no ground; the honest art for it is nothing, and the player
## walks up a wall with a boat overhead — the shipped chasm failure verbatim).
const RIDE_TIME := 1.1

## Re-entrancy latch. lock_party() freezes the body INSIDE the zone it fired
## from, so without this a second body_entered would stack a coroutine on the
## same ride.
var _riding := false
## The zones' own _standing latches, cleared on body_exited — the same shape
## TravelScene uses for its markers, kept local because these two zones are not
## OverworldLocations.
var _on_lift := {}

@onready var theater: Theater = $Theater


func _player_node() -> Node2D:
	return Party.spawn($World, Vector2.ZERO)   # placed for real in _place_player


func _map_path() -> String:
	return MAP_PATH


func _layout_path() -> String:
	return LAYOUT_PATH


func _place_player() -> void:
	var spawn := Game.town_spawn
	Game.town_spawn = ""
	if spawn == "home":
		# Land ON the door marker — feet on the deck right under the arch
		# (the old tile-and-a-half drop read as appearing nowhere near the
		# door). _standing suppresses the marker until he steps off it once.
		Party.place(MapData.anchor_px(map, "home"))
		_standing["home"] = true
	else:
		Party.place(MapData.anchor_px(map, "player_start"))


func _extra_setup() -> void:
	# street furniture (well, lamps, stall, fountain) as y-sorted World
	# entities; the spawner front-loads them in child order so the party
	# (spawned first by TravelScene) still wins y-sort ties
	PropSpawner.build("res://assets/tilesets/town_props.txt", map, $World)
	_collect_animated()
	$ExitSouth.position = MapData.anchor_px(map, "exit_south")
	$ExitSouth.body_entered.connect(_on_exit_south)
	_wall_gate_mouth()
	_spawn_lift()
	Party.clamp_cameras(MapData.size_px(map))
	# TravelScene gates its markers on `body != player` — re-aim it when the
	# lead changes hands mid-town.
	Party.leader_changed.connect(_on_leader_changed)


## Through Basil's open door, down to the lab.
func _on_travel(loc: OverworldLocation) -> void:
	if loc.id == "home":
		Game.interior_spawn = "front_door"


## Out the south lane, back to the overworld at the town icon.
func _on_exit_south(body: Node) -> void:
	if body.is_in_group("player"):
		_exit_to_overworld("town")


## The same wall town_fest, town_thesis and lanternwood all put here, and the one
## this scene was missing (2026-07-29): the gate-mouth road runs to the map's last
## row and the collision layer only stamps grid cells, so past the mouth there is
## nothing. It never bit because the exit trigger happened to cover the whole
## 2-cell mouth — but the adult sandbox has no backstop and no refusal state, so
## the day the mouth widens the player walks off the collision grid into the void.
func _wall_gate_mouth() -> void:
	var wall := StaticBody2D.new()
	wall.collision_layer = 1
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(64.0, 8.0)
	shape.shape = rect
	wall.add_child(shape)
	wall.position = Vector2($ExitSouth.position.x, MapData.size_px(map).y + 4.0)
	add_child(wall)


# ---- THE DINGHY LIFT ---------------------------------------------------------

## Two Area2Ds on their OWN anchors, shared with nothing. That is not tidiness:
## two zones on one anchor is a documented softlock in this codebase — a body
## teleported onto both enters both in one physics flush, and whichever awaited
## coroutine wins holds _busy through the other's body_entered, leaving the
## refused body standing inside a zone that never re-fires (2026-07-18).
## assert_lift keeps the two anchors two cells clear of every other anchor for
## the same reason.
##
## WIRED HERE AND NOWHERE ELSE. The grids are byte-locked so the chars, the art
## and the landings exist in all three town scenes, but the ZONES are per scene:
## in the bright era the lift is a landmark you look at and kid Basil is not
## allowed on it, which is a better announce line than a working lift and buys
## zero new Prologue A/B risk — including no interaction with town_thesis's dash,
## where the party is free with a scripted goal.
func _spawn_lift() -> void:
	for id in ["lift_down", "lift_up"]:
		var zone := Area2D.new()
		zone.name = id
		zone.collision_layer = 0
		zone.collision_mask = 2
		var shape := CollisionShape2D.new()
		var rect := RectangleShape2D.new()
		rect.size = Vector2(24.0, 16.0)
		shape.shape = rect
		zone.add_child(shape)
		zone.position = MapData.anchor_px(map, id)
		add_child(zone)
		zone.body_entered.connect(_on_lift_zone.bind(id))
		zone.body_exited.connect(func(body: Node2D) -> void:
			if body.is_in_group("player"):
				_on_lift[id] = false)


func _on_lift_zone(body: Node2D, id: String) -> void:
	if body != player or _entry_locked or _riding or _on_lift.get(id, false):
		return
	_on_lift[id] = true
	if _busy:
		# A machine that silently does nothing reads as broken, so say so out
		# loud rather than swallowing the step.
		theater.hint("THE HOIST IS BUSY.")
		return
	_ride(id)


## The ride: ~1.1s, no fade. A fade to black to climb inside one town is exactly
## what made a two-scene canopy/ground split unacceptable — it destroys the sense
## of place, which is the entire reason to build a treehouse town.
##
## The three hard questions, answered:
##  * THE FOLLOWER — the ride is a cutscene, so lock_party() freezes EVERY member
##    and all of them tween by the same delta alongside the car. Two frozen
##    bodies, one delta, no AI interaction.
##  * THE LEASH — the AIBrain mood machine and its teleport run in the follower's
##    _physics_process, which is precisely what lock_party() stops. So the lock is
##    NOT optional, and the ride must not await anything skippable.
##  * THE ZONES — own anchors, a re-entrancy latch, and body_exited latches.
##
## THE ARRIVAL LANDS ON THE DESTINATION ANCHOR, inside the destination zone, and
## that is the DOOR convention rather than a hazard: _place_player lands the party
## on Basil's door marker and latches it shut the same way. An arrival dropped one
## cell CLEAR of the rect was tried first and is the wrong shape here — the drum's
## works are solid to the south and its shaft is solid to the north, so "one cell
## further from the shaft" has nowhere to go on the ground side, and picking a
## direction per landing is three lines of geometry to avoid a latch that already
## exists. Step off, body_exited clears it, step back on and you ride.
func _ride(from_id: String) -> void:
	_riding = true
	_busy = true
	theater.lock_party()
	var up := from_id == "lift_up"
	var to := MapData.anchor_px(map, "lift_down" if up else "lift_up")
	var delta := to - player.global_position
	var tw := create_tween().set_parallel(true)
	for m in Party.members:
		tw.tween_property(m, "global_position", m.global_position + delta,
				RIDE_TIME).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	await tw.finished
	# RESYNC BOTH LATCHES FROM THE REAL OVERLAPS, and do not just latch the
	# destination shut. Godot fires body_entered once per entry, and the tween
	# carried the body THROUGH the destination zone with _riding swallowing the
	# event — so a hand-set latch that body_exited later clears leaves the body
	# standing in a zone with no pending entry, and the ride back never arms.
	# Asking the zones what is actually inside them is the only answer that
	# survives both the arrival landing clear of the rect and a follower fanned
	# out into it. One physics frame first, or the teleport hasn't been seen yet.
	await get_tree().physics_frame
	for id in ["lift_down", "lift_up"]:
		var z := get_node_or_null(NodePath(id)) as Area2D
		if z != null:
			_on_lift[id] = z.overlaps_body(player)
	theater.unlock_party()
	_busy = false
	_riding = false
	_show_banner("THE DINGHY LIFT", BANNER_HOLD)
