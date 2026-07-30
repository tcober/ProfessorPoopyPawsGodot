class_name NPC
extends StaticBody2D

## Interact-to-talk villager (the first NPC entity, 2026-07-12). Stand in the
## TalkZone and press interact (E / Circle) to run the NPC's conversation
## through the scene's Theater. Interact is POLLED like every action in the
## project (the shot.gd gotcha).
##
## ROW 0 of a sheet is the POSE row — [idle0, idle1, act0, act1, emote0, emote1]
## (frame_cols may stop at 2 or 4) — and the SpriteFrames build at runtime, so
## a new villager is a PNG plus exports: no .tres authoring. Anim names:
## idle_down (the Theater helpers' single-facing fallback), act (the NPC's
## business pose: casting, pointing, tinkering), emote (its big feeling).
## Cols 6-9 are OPTIONAL facings (2026-07-17, the bluff's from-behind
## staging): back x2 (frame_cols >= 8) and side x2 drawn facing LEFT
## (frame_cols >= 10; play_side(true) flips it right) — sheets without
## them are untouched, the play_* helpers no-op. face_dir() picks the right
## one off a movement/look vector, and Theater.walk drives it automatically
## so a staged villager turns instead of gliding front-first (2026-07-29).
## The body is solid on the world layer and y-sorts in World at the party's
## feet convention (48-cell art, feet y=44 = node.y + 20).
##
## ROWS 1-3 ARE THE WALK CYCLE (2026-07-29) and they are OPTIONAL — a 48px-tall
## sheet is still legal and still works exactly as it always did. A tall sheet
## carries `walk_down` / `walk_up` / `walk_side` as SIX cells each, one direction
## per row, side drawn facing LEFT:
##
##   row 0  idle_down x2 | act x2 | emote x2 | back x2 | side x2   (cols 0-9)
##   row 1  walk_down x6                                     (cols 0-5, 6-9 pad)
##   row 2  walk_up   x6
##   row 3  walk_side x6  (faces LEFT)
##
## That is the SAME contract the party sheets use — direction is the row, the
## cycle is the columns — which is why the proven 6-frame stride tables in the
## generators are reused verbatim. The walk clips are gated on the sheet's real
## HEIGHT, deliberately NOT on frame_cols: a sheet that grows rows starts walking
## with no scene edit at all, so every staged theater.walk in the game animates
## the moment its art lands. They also run at their own walk_fps — sharing
## idle_fps (1.6) is what made a moving villager read as a sliding statue.
##
## WANDER (2026-07-29) is opt-in per villager and OFF by default. It is bounded
## by an AUTHORED cell rect, never a radius: this map has one-cell lanes where a
## StaticBody2D is a wall rather than a squeeze, and walk-behind crowns that are
## walkable but would swallow a villager whole. See `wander_cells`.

signal talked(npc: NPC)

## Cells that are WALKABLE but hide a body behind their art — conifer crowns
## (`Y`/`P`), lamp mantles (`L`) and gatepost caps (`N`/`M`) in Lanternwood,
## counter and bench tops (`T`/`E`) indoors. MapData.is_solid says yes to every
## one of them, so a wander bounded only by solidity parks villagers inside
## spruces. Keyed by map char, which is the only place the distinction exists.
##
## The set is shared across maps and the chars are not globally unique — `T` is
## also Lanternwood's stair cap. Refusing it there is harmless and arguably
## right: a neighbour who wanders down a terrace has left the beat.
const WALK_BEHIND := "YPLNMTE"

## Cell size, and the offset from the node origin to the CENTRE OF THE COLLISION
## BOX ($CollisionShape2D sits at (0,6), 12x8 — the same feet box the party
## bodies use). Deliberately NOT the art's feet line at +20: that number is the
## y-sort convention, and testing solidity with it would check the cell a row
## BELOW the one the body is actually standing in. Cross-check: a villager
## dropped on MapData.anchor_px(cell) has origin y = cell*16 + 8, so its box
## centre lands at cell*16 + 14 — inside the anchor's own cell, as it must.
const TILE := 16.0
const BODY_DY := 6.0

@export var display_name := ""
@export var sheet: Texture2D
@export var frame_cols := 6
@export var idle_fps := 1.6
@export var walk_fps := 10.0
@export_multiline var lines: PackedStringArray = []

@export_group("Wander")
## Idle-life wander. Off by default — a villager only moves if its scene says so.
@export var wander := false
## The cell rect the villager may occupy. Standard Rect2i semantics — `position`
## is the top-left cell and `size` is a COUNT, so the last legal cell is
## `position + size - 1`. Authored at the call site against the map grid; leave
## it empty and wander is a no-op.
@export var wander_cells := Rect2i()
@export var wander_speed := 22.0
## Seconds of standing still between hops, randomised +/- 50%.
@export var wander_pause := 2.4
## The clip to settle into between hops. Empty means the DIRECTIONAL idle — the
## villager keeps facing the way it just walked, which is what a neighbour out in
## the snow should do. Naming a clip instead (`act`) means the villager goes back
## to its business every time it stops, which is what Basil's mother wants: she
## is not pacing the kitchen, she is working it, and the pauses are the work.
@export var wander_rest := ""

var _player_in := false
var _busy := false

## The map dictionary the wander tests solidity against. Handed over by the scene
## (it already owns the parsed map); wander stays off until it arrives.
var _map: Dictionary = {}
var _home := Vector2.ZERO
var _wait := 0.0
var _step_to := Vector2.ZERO
var _stepping := false
## Set while a theater.walk tween owns global_position. The tween and a per-frame
## mover would otherwise fight over the same property.
var _staged := false

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D


func _ready() -> void:
	_build_frames()
	sprite.play("idle_down")
	$TalkZone.body_entered.connect(_on_zone.bind(true))
	$TalkZone.body_exited.connect(_on_zone.bind(false))
	_home = position
	_wait = randf_range(0.0, wander_pause)


func _build_frames() -> void:
	assert(sheet != null, display_name + " NPC has no sheet")
	# frame_cols is a REQUEST, clamped by the art actually on disk. A scene may
	# name 10 columns before the generator has drawn cells 6-9 (staging and art
	# land in different commits), and an AtlasTexture region past the sheet's
	# right edge draws NOTHING — the villager would go INVISIBLE the moment it
	# turned round, which is far worse than the play_* helpers' silent no-op.
	# Clamping means the missing clip simply never exists, so play_back() /
	# play_side() / face_dir() all fall back to the front view instead.
	var cols := mini(frame_cols, floori(sheet.get_width() / 48.0))
	var rows := floori(sheet.get_height() / 48.0)
	var f := SpriteFrames.new()
	var defs := {"idle_down": [0, 1], "act": [2, 3], "emote": [4, 5],
			"back": [6, 7], "side": [8, 9]}
	for anim: String in defs:
		var cells: Array = defs[anim]
		if cells[0] >= cols:
			continue
		f.add_animation(anim)
		f.set_animation_speed(anim, idle_fps)
		f.set_animation_loop(anim, true)
		for i: int in cells:
			if i < cols:
				var at := AtlasTexture.new()
				at.atlas = sheet
				at.region = Rect2(i * 48, 0, 48, 48)
				f.add_frame(anim, at)
	# The walk rows, when the art exists. Gated on the sheet's real HEIGHT and
	# never on frame_cols: frame_cols describes the POSE row, and making it
	# double as a walk switch would mean editing all ~79 spawn sites before a
	# single villager animated. Six cells per row, so a sheet padded to 10
	# columns still slices its cycle from cols 0-5.
	var walk := {"walk_down": 1, "walk_up": 2, "walk_side": 3}
	# Same width clamp as the pose row, and for the same reason: a region past
	# the sheet's right edge draws NOTHING, so a short cycle beats a villager
	# that blinks out of existence on every other frame.
	var wcols := mini(6, floori(sheet.get_width() / 48.0))
	for anim: String in walk:
		var row: int = walk[anim]
		if row >= rows or wcols < 1:
			continue
		f.add_animation(anim)
		f.set_animation_speed(anim, walk_fps)
		f.set_animation_loop(anim, true)
		for i in wcols:
			var at := AtlasTexture.new()
			at.atlas = sheet
			at.region = Rect2(i * 48, row * 48, 48, 48)
			f.add_frame(anim, at)
	f.remove_animation("default")
	sprite.sprite_frames = f


func _on_zone(body: Node2D, entering: bool) -> void:
	# leader only — a follower drifting through must not arm the prompt
	if body.is_in_group("player"):
		_player_in = entering


func _process(delta: float) -> void:
	if _player_in and not _busy and lines.size() > 0 \
			and Input.is_action_just_pressed("interact") and not _cutscene():
		_talk()
	_process_wander(delta)


# ---- wander -----------------------------------------------------------------
#
# Idle life, and it is deliberately timid. A villager is a StaticBody2D on the
# WORLD layer: it is a wall to the party and it has no collision response of its
# own, so every step has to be proven walkable BEFORE it is taken rather than
# resolved after. Hence an authored cell rect plus a four-way test, and hence
# `hold()` — the one call a scene makes before it stages anything.


## Hand the villager the scene's parsed map. Wander stays inert until this
## arrives, so a scene that forgets it gets a statue, never a villager walking
## through a wall.
func bind_map(map: Dictionary) -> void:
	_map = map


## Claim/release the body for a staged tween. Theater.walk brackets itself with
## this so a wandering villager stops writing global_position underneath it.
func set_staged(on: bool) -> void:
	_staged = on
	if on:
		_stepping = false


## Park the villager back on its spawn mark and stop the wander — the call a
## scene makes before a beat that faces it, or that assumes where it stands.
func hold() -> void:
	wander = false
	_stepping = false
	position = _home
	play_idle()


func _process_wander(delta: float) -> void:
	if not wander or _map.is_empty() or wander_cells.size == Vector2i.ZERO:
		return
	# Every reason to stand still, in one place. _busy is mid-conversation (a
	# villager that walks out from under its own dialogue is the bug the mayor's
	# handler documents), _staged is a theater tween owning global_position,
	# _cutscene() is the party physics-frozen for a staged beat, and _player_in
	# means somebody is standing right here trying to talk.
	if _busy or _staged or _cutscene():
		return
	if _player_in:
		# Somebody is standing here trying to talk. Stop mid-step and turn to
		# them rather than walking out from under the prompt.
		if _stepping:
			_stepping = false
			_rest(_step_to - position)
		return
	if _stepping:
		var d := _step_to - position
		var travel := wander_speed * delta
		if d.length() <= travel:
			position = _step_to
			_stepping = false
			_wait = wander_pause * randf_range(0.5, 1.5)
			_rest(d)
		else:
			position += d.normalized() * travel
			face_dir(d, true)
		return
	_wait -= delta
	if _wait <= 0.0:
		_pick_step()


## Settle out of a hop. `wander_rest` wins when the sheet actually has that clip;
## otherwise the villager keeps facing the way it was walking.
func _rest(dir: Vector2) -> void:
	if wander_rest != "" and sprite.sprite_frames.has_animation(wander_rest):
		sprite.flip_h = false
		sprite.play(wander_rest)
		return
	face_dir(dir)


## One cardinal hop of one cell. Cardinal because the art has three facings and a
## diagonal reads as a slide in whichever one wins the dominant axis; one cell
## because a longer leg cannot be proven clear without walking the cells between.
func _pick_step() -> void:
	var dirs := [Vector2i.RIGHT, Vector2i.LEFT, Vector2i.DOWN, Vector2i.UP]
	dirs.shuffle()
	var here := _cell_of(position)
	for d: Vector2i in dirs:
		if _can_stand(here + d):
			_step_to = _px_of(here + d)
			_stepping = true
			return
	# Boxed in — try again after a beat rather than every frame.
	_wait = wander_pause


## The cell a body OCCUPIES — the one its collision box is in, not the one its
## head is drawn in. Testing the raw origin would clear a step by the villager's
## chest while the box it actually collides with walked into a wall.
func _cell_of(pos: Vector2) -> Vector2i:
	return Vector2i(floori(pos.x / TILE), floori((pos.y + BODY_DY) / TILE))


## The inverse — the node position that puts the box in the middle of `cell`.
## Matches MapData.anchor_px, so a villager stepping home lands exactly on its
## spawn mark rather than 6px off it.
func _px_of(cell: Vector2i) -> Vector2:
	return Vector2(cell.x * TILE + TILE * 0.5, cell.y * TILE + TILE * 0.5)


## All four reasons a cell is off-limits. `is_solid` alone is not enough twice
## over: walk-behind crowns are walkable art a villager would vanish inside, and
## the party is not in the map at all.
func _can_stand(cell: Vector2i) -> bool:
	if not wander_cells.has_point(cell):
		return false
	if MapData.is_solid(_map, cell):
		return false
	# The empty-string guard is load-bearing: String.contains("") is TRUE, so an
	# off-grid lookup would read as "walk-behind" by accident. Refusing it is the
	# right answer anyway — this only fails safe.
	var ch := _char_at(cell)
	if ch == "" or WALK_BEHIND.contains(ch):
		return false
	return _clear_of_party(_px_of(cell))


func _char_at(cell: Vector2i) -> String:
	var lines_: PackedStringArray = _map.get("lines", PackedStringArray())
	if cell.y < 0 or cell.y >= lines_.size():
		return ""
	var row: String = lines_[cell.y]
	if cell.x < 0 or cell.x >= row.length():
		return ""
	return row[cell.x]


## Never step onto a party body. An NPC is solid and does not push, so landing on
## the leader would embed them in each other.
func _clear_of_party(pos: Vector2) -> bool:
	for body: Node2D in get_tree().get_nodes_in_group("party"):
		if pos.distance_to(body.global_position) < TILE:
			return false
	return true


## A locked party means a staged beat (or a minigame mashing E) is running —
## no NPC may open a nested conversation through it.
func _cutscene() -> bool:
	var players := get_tree().get_nodes_in_group("player")
	return players.is_empty() or not players[0].is_physics_processing()


func _talk() -> void:
	var theater: Theater = get_tree().get_first_node_in_group("theater")
	if theater == null:
		return
	_busy = true
	theater.lock_party()
	await theater.converse(display_name, lines)
	theater.unlock_party()
	talked.emit(self)
	_busy = false


# ---- cutscene poses ---------------------------------------------------------
#
# EVERY helper below owns flip_h — a pose never inherits the mirror the previous
# one left (2026-07-29). act and emote are drawn FRONT-facing, so a `side` clip
# flipped right followed by play_act() used to hand back a mirrored act: exactly
# what the brew's Kitty did the moment walk_via started turning her (her last
# leg to the bench runs east). A scene that genuinely wants a mirrored pose sets
# flip_h AFTER the play call — sickroom's mother rounding on Basil is the one
# place in the game that does, and it reads as a deliberate act there.
#
# Scenes whose act/emote art is NOT front-facing bypass these helpers and drive
# sprite.play() directly (library.gd's wand casts, town_fest's flying goose) —
# that is the escape hatch, and it is why this reset is safe.

func play_act() -> void:
	if sprite.sprite_frames.has_animation("act"):
		sprite.flip_h = false
		sprite.play("act")


func play_emote() -> void:
	if sprite.sprite_frames.has_animation("emote"):
		sprite.flip_h = false
		sprite.play("emote")


func play_idle() -> void:
	sprite.flip_h = false
	sprite.play("idle_down")


## Back to the camera (the bluff's facing-the-water staging).
func play_back() -> void:
	if sprite.sprite_frames.has_animation("back"):
		sprite.flip_h = false
		sprite.play("back")


## Profile. The cells face LEFT; right = false keeps that, true flips.
func play_side(right := false) -> void:
	if sprite.sprite_frames.has_animation("side"):
		sprite.flip_h = right
		sprite.play("side")


## Turn to face a movement or LOOK vector — the single entry point staged
## facing goes through (Theater routes walk/walk_via/face here for any NPC
## body, 2026-07-29, so a scene stops hand-choreographing the obvious case).
##
## The DOMINANT AXIS wins and a tie goes to the vertical, matching
## Theater._face_anim's rule for party bodies — a diagonal approach reads as
## the axis it travelled furthest along.
##
## A ZERO vector is a no-op: a walk that ends where it started, or a
## face(Vector2.ZERO), must never silently blank an authored pose.
##
## It DEGRADES, never errors. A 6-column sheet has no `back` and no `side` clip,
## so north and both profiles fall back to `idle_down` — exactly the front view
## those sheets show today, which is why raising a sheet's frame_cols to 10
## before the art lands is safe (the cells that aren't drawn yet simply aren't
## built; see _build_frames' width clamp).
##
## The horizontal fallback MIRRORS that front view, and does so on purpose:
## it is precisely what Theater._face_anim's `_down` fallback did before this
## existed, so every sheet still stuck at 6 columns keeps the staging it shipped
## with — town_thesis's Ridley crossing west to the clinic stoop is the one
## visible case. Bug-compatible beats tidier here: turning a villager round is
## the change being made, re-mirroring somebody else's scene is not.
##
## `moving` asks for the WALK clip of that facing (2026-07-29). It defaults to
## false so all ~79 shipped call sites keep their exact behaviour, and it too
## degrades: a sheet with no walk rows falls straight through to the pose ladder
## below, which is what every villager did before the rows existed.
func face_dir(v: Vector2, moving := false) -> void:
	if v.is_zero_approx():
		return
	if moving and _play_walk(v):
		return
	if absf(v.x) > absf(v.y):
		if sprite.sprite_frames.has_animation("side"):
			play_side(v.x > 0.0)
		else:
			play_idle()
			sprite.flip_h = v.x < 0.0
		return
	if v.y < 0.0 and sprite.sprite_frames.has_animation("back"):
		play_back()
		return
	play_idle()


## The walk half of face_dir's ladder. Same dominant-axis rule, same LEFT-drawn
## side cells. Returns false when this sheet has no walk art, which is the signal
## to fall back to the pose row.
func _play_walk(v: Vector2) -> bool:
	var anim := "walk_down"
	var flip := false
	if absf(v.x) > absf(v.y):
		anim = "walk_side"
		flip = v.x > 0.0
	elif v.y < 0.0:
		anim = "walk_up"
	if not sprite.sprite_frames.has_animation(anim):
		return false
	sprite.flip_h = flip
	sprite.play(anim)
	return true
