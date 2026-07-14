extends Node

## The party roster and its leader — SoM-style: one member under the keyboard,
## the rest driven by their Brain nodes. Scenes call spawn() instead of
## instancing a player; the autoload survives scene changes, so who leads
## persists (HP deliberately does not — same as the old single-player flow).
## Leadership is expressed three ways, all applied here: is_leader on the
## body (keyboard vs brain), sole membership of the "player" group (doors,
## exits, pickups keep working untouched), and the active Camera2D.

signal leader_changed(leader: PartyMember)

const SCENES := {
	&"basil": preload("res://entities/player/player.tscn"),
	&"fuji": preload("res://entities/fuji/fuji.tscn"),
	&"kid_basil": preload("res://entities/kid/kid_basil.tscn"),
	&"basil_student": preload("res://entities/student/basil_student.tscn"),
}

## Follower spawn nudge — party bodies don't collide with each other, this
## just keeps the pile readable (kept modest so it stays on the spawn cell's
## open floor; the brains' follow spacing separates them properly on the
## first steps). Stacks per extra member.
const FOLLOW_OFFSET := Vector2(0.0, 14.0)
const SWAP_BLINK := 0.15

## Party composition in HUD-row order. A third member is one more entry here
## (plus its scene in SCENES).
var roster: Array[StringName] = [&"basil", &"fuji"]
var leader_id: StringName = &"basil"     # survives scene changes
var members: Array[PartyMember] = []
var leader: PartyMember


## Story-driven recomposition (the prologue plays kid Basil solo; Act 1 will
## open as Fuji alone). Call BETWEEN scenes — the next spawn() instances the
## new roster; live bodies in the current scene are left to die with it.
func set_roster(ids: Array[StringName], lead: StringName = &"") -> void:
	for id in ids:
		assert(SCENES.has(id), "unknown party member: " + String(id))
	roster = ids.duplicate()
	leader_id = lead if ids.has(lead) else ids[0]
	members.clear()
	leader = null


## Instance the whole roster under `world` with the leader at `pos`.
## Returns the leader — scenes keep it as their `player`.
func spawn(world: Node2D, pos: Vector2) -> PartyMember:
	members.clear()
	for id in roster:
		var m: PartyMember = SCENES[id].instantiate()
		m.member_id = id
		world.add_child(m)
		members.append(m)
	var lead := _member_by_id(leader_id)
	if lead == null:
		lead = members[0]
	_apply_leader(lead)
	place(pos)
	return leader


## Leader at pos, followers fanned below — used at spawn and by scenes that
## reposition the party after the fact (TravelScene's _place_player).
func place(pos: Vector2) -> void:
	var offset := Vector2.ZERO
	for m in members:
		if m == leader:
			m.global_position = pos
		else:
			offset += FOLLOW_OFFSET
			m.global_position = pos + offset


## Pin every member's camera to the scene rect (the leader's is the live one,
## but the others must be ready for a swap).
func clamp_cameras(size: Vector2) -> void:
	for m in members:
		MapData.clamp_camera(m.get_node("Camera2D") as Camera2D, size)


func _process(_delta: float) -> void:
	# Polled like every other action in the project (and synthesized presses
	# from tools/shot.gd only exist in the polled state, not as InputEvents).
	if Input.is_action_just_pressed("swap_member"):
		swap()


func swap() -> void:
	# Scene changes free the old bodies out from under us — prune first.
	var alive: Array[PartyMember] = []
	for m in members:
		if is_instance_valid(m):
			alive.append(m)
	members = alive
	if members.size() < 2 or not is_instance_valid(leader):
		return
	_apply_leader(members[(members.find(leader) + 1) % members.size()])
	leader_changed.emit(leader)
	_blink(leader)


func _apply_leader(next: PartyMember) -> void:
	leader = next
	leader_id = next.member_id
	for m in members:
		var leads := m == next
		m.is_leader = leads
		if leads:
			m.add_to_group("player")
		elif m.is_in_group("player"):
			m.remove_from_group("player")
		if m.brain is AIBrain:
			# Moods are about the OLD leader — a demoted member must not
			# resume a stale RETURN/ENGAGE from before its stint in the lead.
			(m.brain as AIBrain).reset()
		var cam := m.get_node("Camera2D") as Camera2D
		cam.enabled = leads
		if leads:
			cam.make_current()
			# Snap, don't lerp — members stand ~a tile apart, and a smoothing
			# glide from the old leader reads as a camera mistake.
			cam.reset_smoothing()


func _member_by_id(id: StringName) -> PartyMember:
	for m in members:
		if m.member_id == id:
			return m
	return null


## Quick "you are here now" flash on the new leader.
func _blink(m: PartyMember) -> void:
	m.modulate = Color(1.6, 1.6, 1.6)
	m.create_tween().tween_property(m, "modulate", Color.WHITE, SWAP_BLINK)
