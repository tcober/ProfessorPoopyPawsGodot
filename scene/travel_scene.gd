class_name TravelScene
extends Node2D

## Shared driver for the CT-style walk-on-a-tiled-map scenes: the overworld
## travel layer and the walkable Alembic Town. Both stamp visible tiles from a
## generated layout onto Tiles (under the body) + TilesUpper (over it), take
## collision from the same map txt, and carry OverworldLocation markers that the
## body steps onto to travel or to read a locked-spot banner. Subclasses supply
## the player node, the map/layout paths, and where the body spawns; everything
## else — camera clamp, marker wiring, the entry fade, the announce/banner
## timing — lives here so the two scenes can't drift.

const ENTRY_FADE := 0.7      ## fade-from-black on arrival
const ENTRY_LOCK := 0.8      ## markers ignore the body until the fade settles
const TRAVEL_FADE := 0.5     ## fade-to-black when leaving through a marker
const BANNER_IN := 0.25
const BANNER_OUT := 0.35
const BANNER_HOLD := 1.6     ## how long a banner line rests before fading
const ANIM_STEP := 0.18      ## frame time for the animated Tier-3 props

var map: Dictionary
var player: Node2D

var _entry_locked := true
var _busy := false
var _banner_tw: Tween
## [zone, handler] pairs registered by _wire_exit, so _deliver_standing can
## re-deliver a gate the body is still standing in after a swallowed event.
var _exits: Array = []
## Marker ids the body is currently standing on; cleared on body_exited so a
## marker can't re-fire until the body steps off and back onto it.
var _standing: Dictionary = {}
## Animated Tier-3 props (multi-frame prop sheets — the fountain's pour,
## chimney smoke, flickering cabin windows). Subclasses call
## _collect_animated() once their PropSpawner pass has run.
var _anim_t := 0.0
var _animated: Array[Sprite2D] = []

@onready var locations: Node2D = $Locations
@onready var banner: Label = $UI/Banner
@onready var fade: ColorRect = $UI/Fade


func _ready() -> void:
	player = _player_node()
	map = MapData.load_map(_map_path())
	TiledMap.build(_layout_path(), {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	MapData.clamp_camera(player.get_node("Camera2D"), MapData.size_px(map))
	_pin_locations()
	_wire_locations()
	_place_player()
	_extra_setup()
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 0.0, ENTRY_FADE)
	await get_tree().create_timer(ENTRY_LOCK).timeout
	_entry_locked = false
	# A pre-latched marker guards the arrival spot (the door-mouth contract) —
	# but a latch whose zone the body is NOT actually inside will never see a
	# body_exited, and would hold its marker shut forever. Resync from the real
	# overlaps (the _on_leader_changed rule) BEFORE re-delivering: a body still
	# pressed into its arrival door keeps the latch (no bounce-back), a body
	# clear of it hands the door back.
	for loc: OverworldLocation in locations.get_children():
		if _standing.get(loc.id, false) and not loc.overlaps_body(player):
			_standing[loc.id] = false
	# A body that pushed into a marker during the entry fade already fired its
	# body_entered (swallowed by the lock) and won't re-fire — deliver it now.
	_deliver_standing()


## A DOOR MARKER IS ITS MAP ANCHOR, DERIVED — never a number typed into a .tscn
## (2026-08-04). Every other piece of geometry in this project already works this
## way (the exits, the dock, the mayor, every spawn) for the reason the map format
## exists at all: paint, collision and logic all come from the one file, so nothing
## can drift. Location markers were the last hand-placed thing, and they had.
##
## Found by measuring all 13 travel scenes' markers against the anchors whose names
## they already share. **Fourteen of them were wrong, in three scenes**, and the two
## worst classes both look like "the door is broken" rather than "the door is 8px
## off":
##
##  - ON A SOLID CELL — Alembic's `weapons` (a ring deck's edge) and `items` (inside
##    the forest wall), and Lanternwood's `library` and `cabin_c`. A trigger no body
##    can stand on can never fire, so those four doors did not exist. The library is
##    the one that matters: Fuji SPAWNS from its anchor correctly on the way out and
##    then cannot walk back in.
##  - IN ANOTHER PART OF TOWN — Lanternwood's `fuji_home` was 24 rows from its
##    anchor and `cabin_a` a third of the map away; Alembic's whole set was left on
##    canopy-era coordinates by the forest-floor rebuild, announcing shop names in
##    empty grass. Basil's own front door was 128px off, which silently broke the
##    door-mouth arrival contract: `_place_player` lands him ON the `home` anchor and
##    latches `_standing`, so the latch was guarding a zone he was not in.
##
## Nothing caught any of it. `_check_art`'s placement lint reads only nodes parented
## to `World`, and these live under `Locations`. It has a companion rule now.
##
## An id with no matching anchor keeps its authored position, so a marker that is
## deliberately not a map feature stays hand-placeable.
func _pin_locations() -> void:
	for loc: OverworldLocation in locations.get_children():
		if map.anchors.has(loc.id):
			loc.position = MapData.anchor_px(map, loc.id)


## Re-deliver the marker the body is ALREADY standing in. Godot fires
## body_entered once per entry, so any marker whose event we swallowed — the
## entry lock above, or a banner still playing (_busy) — stays dead until the
## player steps off and back on. That is only a missed line for an announce
## marker, but a TRAVEL marker silently refusing to open is a door that looks
## broken: step off a cabin banner onto the library arch inside its ~2s and
## nothing happens. The _standing latch makes this safe to call at will — a
## marker that fired properly is already latched and won't fire twice.
##
## RAW EXIT ZONES GET THE SAME TREATMENT (2026-08-01). The gate-mouth Area2Ds
## the subclasses wire are not Locations, so they used to be exempt — and an
## exit whose one body_entered landed during a banner was a gate that silently
## stopped working until you stepped off it and back on (a shop banner holds
## _busy for 2.2-4.4s, which is plenty to walk onto the south gate). Exits
## registered through _wire_exit are re-delivered here; their handlers gate on
## _exit_ok and their own latches, so a double delivery is harmless.
func _deliver_standing() -> void:
	for loc: OverworldLocation in locations.get_children():
		if not _standing.get(loc.id, false) and loc.overlaps_body(player):
			_on_location_entered(player, loc)
	for e in _exits:
		if is_instance_valid(e[0]) and (e[0] as Area2D).overlaps_body(player):
			(e[1] as Callable).call(player)


func _wire_locations() -> void:
	for loc: OverworldLocation in locations.get_children():
		loc.position = MapData.anchor_px(map, loc.id)
		loc.body_entered.connect(_on_location_entered.bind(loc))
		loc.body_exited.connect(_on_location_exited.bind(loc))


## Every zone that spawns the whole party wires this to Party.leader_changed:
## the marker gates all key off `player`, so Q/Tab has to re-aim them. The
## _standing latches must be resynced from the real overlaps too — the old
## leader's body_exited arrives as a non-player body and would leave its
## marker latched shut, swallowing the new leader's next step onto it.
func _on_leader_changed(leader: PartyMember) -> void:
	player = leader
	for loc: OverworldLocation in locations.get_children():
		_standing[loc.id] = loc.overlaps_body(leader)


## Sprite2Ds under $World with a multi-frame sheet cycle as one animated set.
func _collect_animated() -> void:
	for c in $World.get_children():
		if c is Sprite2D and (c as Sprite2D).hframes > 1:
			_animated.append(c as Sprite2D)


func _process(delta: float) -> void:
	if _animated.is_empty():
		return
	_anim_t += delta
	var f := int(_anim_t / ANIM_STEP)
	for i in _animated.size():   # per-prop phase offset = looser, less mechanical
		var s := _animated[i]
		s.frame = (f + i) % s.hframes


func _on_location_entered(body: Node2D, loc: OverworldLocation) -> void:
	if body != player or _entry_locked or _busy:
		return
	if _standing.get(loc.id, false):
		return
	_standing[loc.id] = true
	if loc.target_scene != "":
		_travel(loc)
	else:
		_announce(loc)


func _on_location_exited(body: Node2D, loc: OverworldLocation) -> void:
	if body == player:
		_standing[loc.id] = false


func _travel(loc: OverworldLocation) -> void:
	_busy = true
	Sfx.door()
	_on_travel(loc)
	_show_banner(loc.display_name, BANNER_HOLD)
	await fade_out()
	get_tree().change_scene_to_file(loc.target_scene)


func _announce(loc: OverworldLocation) -> void:
	_busy = true
	await _show_banner(loc.display_name, BANNER_HOLD)
	if loc.locked_text != "":
		await _show_banner(loc.locked_text, BANNER_HOLD)
	_busy = false
	# whatever the player walked onto while this banner held the scene busy
	_deliver_standing()


func _show_banner(text: String, hold: float) -> void:
	banner.text = text
	# kill the previous banner's tween or its fade-out yanks THIS text
	# mid-hold (two fire-and-forget callers can overlap — create_tween()
	# never auto-kills).
	if _banner_tw:
		_banner_tw.kill()
	_banner_tw = create_tween()
	_banner_tw.tween_property(banner, "modulate:a", 1.0, BANNER_IN)
	_banner_tw.tween_interval(hold)
	_banner_tw.tween_property(banner, "modulate:a", 0.0, BANNER_OUT)
	# Await a matched timer, NOT _banner_tw.finished: a later _show_banner
	# kill()s this tween, and a killed Godot tween never emits finished — an
	# awaiting _announce would hang there with _busy stuck true, which
	# dead-locks every marker, the home door and the south gate (a fire-and-
	# forget banner from _want_home_line / _goose_startle / the festival close
	# CAN supersede an announce banner, since _announce doesn't lock the party).
	# The timer fires regardless, so _busy is always released; a superseded
	# banner just loses its visual to the newer one.
	await get_tree().create_timer(BANNER_IN + hold + BANNER_OUT).timeout


## Wire a raw exit Area2D (a gate mouth) and register it for re-delivery. Use
## this instead of connecting body_entered directly, or the exit goes silently
## dead for any body whose one entered-event lands during a banner or the
## entry fade.
func _wire_exit(zone: Area2D, handler: Callable) -> void:
	zone.body_entered.connect(handler)
	_exits.append([zone, handler])


## The gate every raw exit handler must pass: the right body, the entry fade
## settled, and no banner/travel owning the scene. The ENTRY_LOCK term is what
## stops "walked onto the town icon holding down" from bouncing straight back
## to the overworld before the town's own fade has even finished — markers
## always had that guard; the raw exits never did.
func _exit_ok(body: Node) -> bool:
	return body.is_in_group("player") and not _entry_locked and not _busy


## The shared south-gate exit: leave for the overworld, arriving back at this
## zone's own icon marker (explicit, never the value the overworld wrote on
## the way in).
func _exit_to_overworld(marker: String) -> void:
	if _busy:
		return
	_busy = true
	Game.overworld_spawn = marker
	await fade_out()
	get_tree().change_scene_to_file("res://scene/overworld.tscn")


## THE LADDER MOUTHS UP (2026-08-23, the two-scene town split): one travel zone
## over each rope ladder's TOP two rungs (anchors top1..top4 in the floor maps),
## handing the climb to the era's canopy scene mid-ladder. The body arrives up
## there seated ON the canopy's rungs still facing up, so the climb is
## continuous across the door — see scene/canopy_scene.gd for the other half.
## Wired through _wire_exit so the raw-exit contract (re-delivery, entry lock)
## holds. `_on_ascend` is the era hook for re-arming a phase router first.
func _wire_ladder_tops(canopy_scene: String) -> void:
	for i in range(1, 5):
		var a := "top%d" % i
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
		_wire_exit(zone, _on_ladder_top.bind(i, canopy_scene))


func _on_ladder_top(body: Node, ladder: int, canopy_scene: String) -> void:
	if not _exit_ok(body):
		return
	_busy = true
	Game.town_spawn = "head%d" % ladder
	_on_ascend(ladder)
	await fade_out()
	get_tree().change_scene_to_file(canopy_scene)


## Era hook: fired just before a ladder ascent changes scene (re-arm a phase
## router here — Game fields are the only state that survives the door).
func _on_ascend(_ladder: int) -> void:
	pass


## The matching arrival: a body descending FROM the canopy is seated on the
## rungs two rows below its ladder's travel mouth, still facing down.
## Returns true if `spawn` named a ladder ("top1".."top4") and was handled.
func _place_on_rungs(spawn: String) -> bool:
	if not spawn.begins_with("top") or not map.anchors.has(spawn):
		return false
	Party.place(MapData.anchor_px(map, spawn) + Vector2(8.0, 40.0))
	return true


## A backstop wall just off the map edge, at `at`, `size` px.
##
## THE SAME WALL EVERY GATE MOUTH IN THIS PROJECT GETS. A mouth road runs to the grid's
## last row and the collision layer only stamps grid CELLS, so past the mouth there is
## nothing at all — and the exit zone is not a substitute, because a zone that has
## already fired holds `_busy` for a fade's worth of frames and a body keeps walking
## during it. Alembic's north and east mouths have no trigger at all yet.
##
## It lived here as five verbatim copies of the same nine lines — alembic_town,
## town_fest and town_thesis each carried an identical private `_wall()`, and
## lanternwood and academy each open-coded it a sixth and seventh time inside their own
## mouth function. Every one of those scenes already extends this class. The GEOMETRY
## stays with each scene, because which mouths a map has is a fact about that map; only
## the body-building moves.
func _wall(at: Vector2, size: Vector2) -> void:
	var wall := StaticBody2D.new()
	wall.collision_layer = 1
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = size
	shape.shape = rect
	wall.add_child(shape)
	wall.position = at
	add_child(wall)


## Fade to black; callers change scene once it resolves.
func fade_out() -> void:
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 1.0, TRAVEL_FADE)
	await tw.finished


# ---- subclass hooks --------------------------------------------------------

## The travel body this scene wires markers against (path differs per scene).
func _player_node() -> Node2D:
	assert(false, "TravelScene subclass must override _player_node()")
	return null

func _map_path() -> String:
	return ""

func _layout_path() -> String:
	return ""

## Put the body at its spawn (default anchor, or a routed return spawn).
func _place_player() -> void:
	pass

## Extra per-scene wiring (e.g. an exit zone) before the entry fade. Optional.
func _extra_setup() -> void:
	pass

## Per-scene spawn bookkeeping when leaving through a marker (records where to
## return). Optional.
func _on_travel(_loc: OverworldLocation) -> void:
	pass
