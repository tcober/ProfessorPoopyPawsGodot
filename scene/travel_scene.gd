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
	_wire_locations()
	_place_player()
	_extra_setup()
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 0.0, ENTRY_FADE)
	await get_tree().create_timer(ENTRY_LOCK).timeout
	_entry_locked = false
	# A body that pushed into a marker during the entry fade already fired its
	# body_entered (swallowed by the lock) and won't re-fire — deliver it now.
	_deliver_standing()


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
