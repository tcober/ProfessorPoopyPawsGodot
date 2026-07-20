extends TravelScene

## Lanternwood, walkable at zone scale — Fuji's winter pine-forest hometown
## on the ice land (see TravelScene for the shared machinery). Every door is
## announce-only for now: the library, Fuji's family home and the three
## snow-banked cabins read their banner lines; the south gate lane exits to
## the overworld at Lanternwood's icon marker.

const MAP_PATH := "res://assets/maps/lanternwood.txt"
const LAYOUT_PATH := "res://assets/tilesets/lanternwood_layout.txt"


## Animated Tier-3 props (multi-frame sheets — the five cabins' window
## flicker + woodsmoke); cycled in _process the way alembic town cycles its
## fountain and chimneys.
var _anim_t := 0.0
var _animated: Array[Sprite2D] = []


func _player_node() -> Node2D:
	return Party.spawn($World, Vector2.ZERO)   # placed for real in _place_player


func _map_path() -> String:
	return MAP_PATH


func _layout_path() -> String:
	return LAYOUT_PATH


func _place_player() -> void:
	Party.place(MapData.anchor_px(map, "player_start"))


func _extra_setup() -> void:
	# cabins, conifers and lamps as y-sorted World entities; the spawner
	# front-loads them in child order so the party (spawned first by
	# TravelScene) still wins y-sort ties
	PropSpawner.build("res://assets/tilesets/lanternwood_props.txt", map, $World)
	for c in $World.get_children():
		if c is Sprite2D and (c as Sprite2D).hframes > 1:
			_animated.append(c)
	$ExitSouth.position = MapData.anchor_px(map, "exit_south")
	$ExitSouth.body_entered.connect(_on_exit_south)
	Party.clamp_cameras(MapData.size_px(map))
	# TravelScene gates its markers on `body != player` — re-aim it when the
	# lead changes hands mid-town.
	Party.leader_changed.connect(_on_leader_changed)


func _process(delta: float) -> void:
	if _animated.is_empty():
		return
	_anim_t += delta
	var f := int(_anim_t / 0.18)
	for i in _animated.size():          # per-cabin phase offset = looser, less mechanical
		var s := _animated[i]
		s.frame = (f + i) % s.hframes


func _on_leader_changed(leader: PartyMember) -> void:
	player = leader


## Out the south gate lane, back to the overworld at the Lanternwood icon.
func _on_exit_south(body: Node) -> void:
	if body.is_in_group("player") and not _busy:
		_busy = true
		Game.overworld_spawn = "lanternwood"
		await fade_out()
		get_tree().change_scene_to_file("res://scene/overworld.tscn")
