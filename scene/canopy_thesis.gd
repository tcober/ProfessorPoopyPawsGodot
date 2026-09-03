extends CanopyScene

## THE BOUGHS on THESIS DAY — Prologue B's canopy half, two phases on the
## shared Game.town_thesis_phase router (the ground half is town_thesis.gd;
## each scene re-arms the router before handing the body down or up, so the
## day survives the door):
##   plant  (night)   the player's own climb home ends here: the doorstep
##                    watch call at his own front door, then — with Basil
##                    inside — Schweinler rises out of the dark on the SAME
##                    ladder, leaves the bag on the deck lip, and sinks back
##                    down it. Pre-split, the creep walked the whole ground
##                    lane web first; the camera was parked up here at the
##                    deck the entire time, so the visible beat is unchanged
##                    and the fifteen off-screen seconds are now a held quiet.
##   dash   (morning) the step onto the bag is SHOWN, the SQUELCH, then the
##                    run — down the ladder, where town_thesis's dash phase
##                    picks up the paw-print trail to the Academy.

const MAP_PATH := "res://assets/maps/canopy_fest.txt"
const LAYOUT_PATH := "res://assets/tilesets/canopy_fest_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const FX_SHEET := preload("res://assets/prologue_fx.png")
const SHEET_SCHW := preload("res://assets/npc_schweinler_adult_gen.png")

const FX_BAG := 10
const FX_PRINT := 11
## The deck lip — the ladder head, the one cell Basil cannot leave home
## without crossing. Same offset as town_thesis.BAG_OFF: the two scenes must
## agree on where the bag sits, and both hang it off "home".
const BAG_OFF := Vector2(8.0, 16.0)

const TINT_NIGHT := Color(0.42, 0.40, 0.66)
const TINT_MORNING := Color(0.98, 0.93, 0.86)

var phase := "plant"
var _door_armed := true
var _door_fired := false
var _dashing := false
var _from_ladder := false
var _last_print := Vector2.ZERO

@onready var theater: Theater = $Theater
@onready var tint: CanvasModulate = $Tint


func _map_path() -> String:
	return MAP_PATH


func _layout_path() -> String:
	return LAYOUT_PATH


func _props_path() -> String:
	return "res://assets/tilesets/canopy_fest_props.txt"


func _ground_scene() -> String:
	return "res://scene/town_thesis.tscn"


func _wants_fireflies() -> bool:
	return phase != "dash"


## Both routers are read here: the phase names the beat, the spawn names the
## ladder. Reading the phase in _place_player (before _extra_setup) is what
## lets the tint and the staging key off it.
func _place_player() -> void:
	phase = Game.town_thesis_phase
	Game.town_thesis_phase = ""
	if phase == "":
		phase = "plant"
	var spawn := Game.town_spawn
	Game.town_spawn = ""
	_from_ladder = spawn.begins_with("head") and map.anchors.has(spawn)
	if _from_ladder:
		Party.place(MapData.anchor_px(map, spawn) + Vector2(8.0, -24.0))
	elif phase == "dash":
		# morning opens ON the door marker — the walk onto the bag below needs
		# the step south to be visible
		Party.place(MapData.anchor_px(map, "home"))
	else:
		# a direct plant load (dev menu): seat the body on tree 1's rungs
		Party.place(MapData.anchor_px(map, "head1") + Vector2(8.0, -24.0))


## Re-arm the shared router before the ground scene loads — Game fields are
## the only state that survives the door (standing rule 3).
func _on_descend(_ladder: int) -> void:
	Game.town_thesis_phase = "dash" if _dashing else phase
	_dashing = false


func _extra_setup() -> void:
	super()
	tint.color = TINT_MORNING if phase == "dash" else TINT_NIGHT
	match phase:
		"dash":
			if _from_ladder:
				# back UP mid-run — the squelch is spent; the run just resumes
				_dashing = true
				_last_print = player.global_position
				_show_banner("GET TO THE ACADEMY - DOWN THE LADDER", BANNER_HOLD)
			else:
				_phase_dash()
		_:
			_spawn_plant_door()
			_show_banner("HOME - GET SOME SLEEP", BANNER_HOLD)


# ---- plant (night): the doorstep call, then the creep -------------------------------

## The front door is the walk-gate: only a press UP into it fires the beat,
## which is the same geometry every era's home door uses.
func _spawn_plant_door() -> void:
	var door := Area2D.new()
	door.collision_layer = 0
	door.collision_mask = 2
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(24.0, 8.0)
	shape.shape = rect
	shape.position = Vector2(8.0, -8.0)
	door.add_child(shape)
	door.position = MapData.anchor_px(map, "home")
	add_child(door)
	door.body_exited.connect(func(body: Node2D) -> void:
		if body.is_in_group("player"):
			_door_armed = true)
	door.body_entered.connect(func(body: Node2D) -> void:
		if not body.is_in_group("player") or not _door_armed or _busy \
				or _door_fired:
			return
		_door_fired = true
		_doorstep())


func _doorstep() -> void:
	theater.lock_party()
	# the bookend call (the Kitty thread): on his own doorstep, the watch SHE
	# MADE raised to his muzzle — the same look_watch gesture as the bluff's
	# first blink and the dusk calls, opposite emotional poles
	theater.face(player, Vector2.DOWN)
	player.sprite.play("look_watch")
	await theater.wait(0.5)
	await theater.say("Kitty", "Hi")
	await theater.say("Basil", "Tomorrow is the day...")
	await theater.say("Kitty", "You've got this. I know it!")
	await theater.say("Kitty", "It sucks only students and professors get to attend. I'll be there in spirit. Whooping you psychically.")
	await theater.say("Basil", "Please don't whoop. ...The watch you made me says it's past midnight, you know.")
	await theater.say("Kitty", "That watch keeps PERFECT time. It's the cat wearing it who runs late. Bed! You'll be brilliant tomorrow.")
	await theater.say("Basil", "...Goodnight, Kitty.")
	theater.close_dialog()
	player.sprite.play("idle_down")
	theater.face(player, Vector2.UP)
	await theater.walk(player, MapData.anchor_px(map, "home"), 40.0)
	player.visible = false            # inside; the deck goes quiet
	# the sleeping boughs hold a beat — pre-split this was the creep's whole
	# off-camera lane walk; the quiet is the same length a held breath is
	await theater.wait(2.4)
	await _creep()
	theater.close_dialog()
	await theater.black(1.0)
	await theater.card("THE NEXT MORNING.", 1.8)
	get_tree().change_scene_to_file("res://scene/house_thesis.tscn")


## THE CREEP'S LAST LEG — the only part anyone ever saw. Schweinler rises out
## of the gloom on Basil's own ladder (the sneer had to climb), leaves the bag
## at the deck lip, and goes back down the way no honest visitor arrives.
func _creep() -> void:
	var mouth := MapData.anchor_px(map, "head1") + Vector2(8.0, 24.0)
	var schw: NPC = NPCScene.instantiate()
	schw.display_name = "Schweinler"
	schw.sheet = SHEET_SCHW
	schw.frame_cols = 6
	schw.position = mouth
	schw.modulate.a = 0.0
	$World.add_child(schw)
	var fade_in := schw.create_tween()
	fade_in.tween_property(schw, "modulate:a", 1.0, 0.5)
	# UP THE LADDER — dead vertical and slower than a walk; theater.walk faces
	# the climb up its own travel direction (the back view)
	await theater.walk(schw, _ladder_top(), 30.0)
	# one step onto the deck, clear of the lip the bag is about to own
	await theater.walk(schw, MapData.anchor_px(map, "home") + Vector2(-16.0, 4.0), 36.0)
	schw.face_dir(Vector2.RIGHT)
	var bag := WorldFx.decal($World, FX_SHEET, FX_BAG,
			MapData.anchor_px(map, "home") + BAG_OFF)
	await theater.say("Schweinler", "Heh heh heh. A little congratulations for the graduate.")
	schw.play_emote()
	await theater.say("Schweinler", "Enjoy your big lecture tomorrow, Basil. Oink - hahaha!")
	# back down — the descent keeps the back-facing walk (turn=false): a
	# front-facing glide down the rungs is the strata float all over again
	await theater.walk(schw, _ladder_top(), 36.0)
	schw.face_dir(Vector2.UP, true)
	await theater.walk(schw, mouth, 34.0, false)
	var fade_off := schw.create_tween()
	fade_off.tween_property(schw, "modulate:a", 0.0, 0.6)
	fade_off.tween_callback(schw.queue_free)
	bag.queue_free()


# ---- dash (morning): the squelch, then down --------------------------------------

func _phase_dash() -> void:
	theater.lock_party()
	theater.face(player, Vector2.DOWN)
	# the bag is already THERE — planted last night, waiting through the line
	var bag := WorldFx.decal($World, FX_SHEET, FX_BAG,
			MapData.anchor_px(map, "home") + BAG_OFF)
	await theater.wait(ENTRY_FADE + 0.3)
	await theater.say("Basil", "The lecture! I OVERSLEPT!!")
	# the step is SHOWN: he bolts for the ladder, straight onto it
	await theater.walk(player, MapData.anchor_px(map, "home") + BAG_OFF, 72.0)
	# the squelch is PLAYED, not narrated: the landing hop is the flinch off
	# the bag, and his own line names what his paw just learned
	await theater.hop(player, 6.0)
	await theater.say("Basil", "Ew. EW. Squishy. Why was that SQUISHY?!")
	await theater.say("Basil", "...I don't have time.")
	await theater.say("Basil", "Gotta go gotta go GOTTA GO!")
	theater.close_dialog()
	var btw := bag.create_tween()
	btw.tween_interval(0.4)
	btw.tween_property(bag, "modulate:a", 0.0, 0.9)
	btw.tween_callback(bag.queue_free)
	_dashing = true
	theater.unlock_party()
	_show_banner("GET TO THE ACADEMY - DOWN THE LADDER", BANNER_HOLD)


func _physics_process(_delta: float) -> void:
	# the paw-print trail starts on the deck — the ground scene continues it
	if not _dashing or not is_instance_valid(player):
		return
	if player.global_position.distance_to(_last_print) >= 14.0:
		_last_print = player.global_position
		var p := WorldFx.decal($World, FX_SHEET, FX_PRINT,
				player.global_position + Vector2(0.0, 8.0))
		var tw := p.create_tween()
		tw.tween_interval(1.2)
		tw.tween_property(p, "modulate:a", 0.0, 1.4)
		tw.tween_callback(p.queue_free)


## The deck lip / ladder head — also where the bag sits (BAG_OFF): the prank
## and the ladder share that cell on purpose.
func _ladder_top() -> Vector2:
	return MapData.anchor_px(map, "home") + BAG_OFF
