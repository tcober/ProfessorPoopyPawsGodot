extends Node2D

## THE DOCTOR'S OFFICE — Prologue B "the verdict" (docs/DESIGN.md Story).
## The front room of the east neighbor cottage in town (the door banners
## name it — one village, one doctor), rebuilt 2026-07-16 as a small dense
## diorama on the loft-bedroom recipe. Kitty survives the crash but her
## memory is gone; the stork doctor delivers the verdict; Basil sits at the
## bedside and she looks at him like a kind stranger. Then he leaves, and
## the town's clinic-steps phase closes the chapter. Interior pattern; Kitty is
## the npc_kitty_bed sprite propped at the pillow, the doctor an npc_stork
## sprite, both posed by the Theater.

const MAP_PATH := "res://assets/maps/sickroom.txt"
const LAYOUT_PATH := "res://assets/tilesets/sickroom_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const SHEET_KITTY := preload("res://assets/npc_kitty_bed_gen.png")
const SHEET_STORK := preload("res://assets/npc_stork_gen.png")
const SHEET_KITTYMOM := preload("res://assets/npc_kittymom_gen.png")

var map: Dictionary
var player: Node2D
var _kitty: NPC
var _doctor: NPC

@onready var theater: Theater = $Theater


func _ready() -> void:
	map = MapData.load_map(MAP_PATH)
	TiledMap.build(LAYOUT_PATH, {"lower": $Tiles, "upper": $TilesUpper})
	PaintedMap.build_collision(map, $Collision)
	PropSpawner.build("res://assets/tilesets/sickroom_props.txt", map, $World)
	player = Party.spawn($World, MapData.anchor_px(map, "player_spawn"))
	Party.clamp_cameras(MapData.size_px(map))
	_spawn_cast()
	_verdict_cutscene()


func _spawn_cast() -> void:
	# Kitty in the bed: her sprite sits at the pillow; the frame cols are the
	# rest/vacant/polite trio (frame_cols=6 = [rest x2, vacant x2, polite x2])
	_kitty = NPCScene.instantiate()
	_kitty.display_name = "Kitty"
	_kitty.sheet = SHEET_KITTY
	_kitty.frame_cols = 6
	# +8 centers her on the 4-cell bed's pillow (the anchor is the west
	# walk cell); -14 sets her head ON the pillow volume with the gown
	# meeting the folded sheet — the 2026-07-16 small-room geometry
	_kitty.position = MapData.anchor_px(map, "kitty_bed") + Vector2(8.0, -14.0)
	$World.add_child(_kitty)
	_kitty.sprite.play("act")             # 'vacant' pair = act (cols 2-3)
	_doctor = NPCScene.instantiate()
	_doctor.display_name = "Dr. Ciconia"
	_doctor.sheet = SHEET_STORK
	_doctor.frame_cols = 6
	_doctor.position = MapData.anchor_px(map, "doctor_spot")
	$World.add_child(_doctor)


func _make_npc(nm: String, sheet: Texture2D, pos: Vector2) -> NPC:
	var npc: NPC = NPCScene.instantiate()
	npc.display_name = nm
	npc.sheet = sheet
	npc.frame_cols = 6
	npc.position = pos
	$World.add_child(npc)
	return npc


func _verdict_cutscene() -> void:
	theater.lock_party()
	theater.face(player, Vector2.UP)
	await theater.wait(0.8)
	_doctor.play_act()
	await theater.say("Dr. Ciconia", "You're Basil. The name engraved on her little glass. Sit, if you like. She's stable.")
	theater.close_dialog()
	# the player crosses the room themselves (the pacing pass); the gate is
	# the full-width open row below the bed — the east floor reaches the bed
	# row too, so a point-gate at the bedside is walkable around — then the
	# last steps slide along the row to her side (y = the bedside row of the
	# 2026-07-16 small-room map)
	await theater.walk_gate(Vector2(MapData.size_px(map).x * 0.5, 104.0),
			Vector2(MapData.size_px(map).x, 20.0))
	await theater.walk(player, MapData.anchor_px(map, "bedside"), 50.0)
	theater.face(player, Vector2.UP)
	await theater.say("Basil", "Kitty. Kitty, I'm here. It's me. I'm so sorry - you told ME to stay put, and then YOU were the one on the road, I -")
	_kitty.sprite.play("act")             # vacant stare
	await theater.say("Dr. Ciconia", "Gently. She's been asking who she is. The body will mend - the leg, the ribs. All of it heals.")
	await theater.say("Dr. Ciconia", "But the blow to her head... the memories are gone. We have magic to mend near anything - bone, blood, fever. Memory is the one thing it will not touch.")
	await theater.say("Dr. Ciconia", "And a memory doesn't simply vanish. When it leaves her, it returns to the spirit of the world - it lives on out there, somewhere. Just... not in her.")
	await theater.say("Dr. Ciconia", "Perhaps some part of what you two were will surface again one day, in some far-off place. But she will not be the one to carry it. I am sorry. It is permanent.")
	await theater.say("Basil", "Permanent. No. No, she - we've known each other since we were TEN. She taught me everything. She has to -")
	_kitty.sprite.play("emote")           # polite, kind to a stranger
	await theater.say("Kitty", "...Oh. Hello. You seem very upset. Are you one of my friends? I'm sorry - the nice stork says I've forgotten quite a lot.")
	await theater.say("Kitty", "You have a kind face. Did we... make something together? I keep thinking about my hands. Isn't that funny.")
	# the hands remember (2026-07-16 Kitty thread): the present-day "hands
	# still remembering what her mind lost" is planted HERE — told in
	# DIALOGUE since the 2026-07-18 narration purge: Basil watches her paws
	# folding pleats into the blanket, starts to say so, and can't finish
	player.sprite.play("sad")
	await theater.wait(0.6)
	await theater.say("Basil", "Your paws. They're folding pleats into the blanket. You always do that when you're think-")
	await theater.wait(0.5)
	await theater.say("Basil", "...No. No, we didn't. I'm sorry. I have the wrong room.")
	await theater.say("Kitty", "Oh. Well - I hope you find who you're looking for. You look like you need to.")
	# Kitty's mother bursts in (2026-07-18): the human rejection that pushes
	# Basil into exile and sets up the "wished he could have been welcome"
	# goodbye at the south gate. No narrator on the door — the BANG is
	# staged: everyone snaps round to it, and she's already charging.
	theater.close_dialog()
	var kmom: NPC = _make_npc("Kitty's Mother", SHEET_KITTYMOM,
			MapData.anchor_px(map, "door"))
	theater.face(player, Vector2.DOWN)
	theater.hop(_doctor, 3.0)
	await theater.wait(0.25)
	# she rushes up the room to the bed's west foot — flanking the bedside
	# opposite Basil (the east side is the ward screen's corner)
	await theater.walk(kmom, MapData.anchor_px(map, "bedside") + Vector2(-16.0, 0.0), 86.0)
	kmom.play_act()                       # hands to her cheeks
	await theater.say("Kitty's Mother", "Oh no - Kitty! My baby, what HAPPENED to you?!")
	await theater.say("Basil", "It was an accident. She was on the road - she was riding out to see me. It's my fault, I -")
	kmom.sprite.flip_h = true             # rounds on him — the point aims east,
	kmom.play_emote()                     # right at Basil beside her
	await theater.say("Kitty's Mother", "You. YOU did this. She was coming to YOU, and now she doesn't even know her own name.")
	await theater.say("Kitty's Mother", "Get away from her. I never want you near my daughter again - not now, not ever. Do you understand me?")
	player.sprite.play("sad")
	await theater.say("Basil", "But - I -")
	await theater.say("Kitty's Mother", "LEAVE.")
	theater.close_dialog()
	# he takes it — a beat, then he turns and walks himself out the door
	await theater.wait(0.9)
	await theater.walk(player, MapData.anchor_px(map, "door"), 40.0)
	await theater.wait(0.4)
	await theater.black(1.4)
	# no card (the 2026-07-18 card purge): the steps phase is the SAME
	# dusk, straight out the door — nothing to bridge
	# out onto the clinic steps — Ridley, the bowed head, the leaving
	Game.town_thesis_phase = "steps"
	get_tree().change_scene_to_file("res://scene/town_thesis.tscn")
