extends TravelScene

## Lanternwood, walkable at zone scale — Fuji's winter pine-forest hometown
## on the ice land (see TravelScene for the shared machinery). THE LIBRARY
## DOOR TRAVELS (2026-07-25): the hall on the north side of the square is
## where Fuji works, and its arch opens into scene/library.tscn. Every other
## door — Fuji's family home, the three snow-banked cabins, THE MOOT HALL —
## is announce-only; the south gate lane exits to the overworld at
## Lanternwood's icon marker, and THE PIER on the east cove is the crossing.
##
## THE TOWN HAS TWO WAYS OUT (2026-07-29), and they are not interchangeable.
## The south gate walks onto the island Lanternwood sits on, which is the same
## place it has always gone. THE LAUNCH crosses the ocean, and it only exists
## once Mayor Hollis has given it to her — see "MAYOR HOLLIS AND THE MOTION"
## below, which is the beat that turns a librarian with a stolen thesis into
## somebody her town has formally asked to go.
##
## Once the Ebb has happened (`ebb_done` — the story's current resting
## state: solo Fuji, stepped out of her library into the SAME night), the
## town dresses for it: a deep night tint the fire-lit windows and oil
## lanterns burn through — Lanternwood earns its name, honest flame owes
## magic nothing — and the neighbors are out in the snow comparing charms
## that all died at once.

const MAP_PATH := "res://assets/maps/lanternwood.txt"
const LAYOUT_PATH := "res://assets/tilesets/lanternwood_layout.txt"

const NPCScene := preload("res://entities/npcs/npc.tscn")
const SHEET_HARE := preload("res://assets/npc_hare_gen.png")
const SHEET_BEAVER := preload("res://assets/npc_beaver_gen.png")
const SHEET_FOXKID := preload("res://assets/npc_foxkid_gen.png")
const SHEET_MAYOR := preload("res://assets/npc_mayor_gen.png")

const HUDScene := preload("res://scene/hud.tscn")
const SlimeScene := preload("res://entities/enemies/slime.tscn")
const BigSlimeScene := preload("res://entities/enemies/big_slime.tscn")
const PickupScene := preload("res://entities/pickups/item_pickup.tscn")

## The map anchors the defence spawns at. Explicit, never random: the town is
## FIVE TERRACES now, and a random spawn lands as often as not on the wrong
## ledge, where a slime's 90px detect_range is aimed uselessly at a cliff face.
const DEFENCE_SPAWNS := ["slime_a", "slime_b", "slime_c"]

## The Ebb night's street register: a shade lighter than ebb.gd's cutscene
## indigo (snow bounces moonlight; the player still has to read the lanes)
## but deep enough that the additive window/lantern glow carries the town.
# Retuned UP 2026-07-28 with the Narshe palette. This is a CanvasModulate, i.e.
# a multiply over art that is now dark to begin with — at the old 0.38 the
# terraced street went unreadably black. The tint's job is still to say "night";
# the fire-lit windows and oil lanterns burn through it either way.
const NIGHT := Color(0.58, 0.6, 0.8)

## How many of the Ebb-night neighbours she has to ask before the library
## door opens onto the research beat (all three — the point of the gate is
## that the whole street tells her the same nothing).
const ASK_GATE := 3

## Ebb-night villagers already talked to, by name.
var _asked: Dictionary = {}

## Mayor Hollis, once he is out on his own step. Null while the defence is
## running (see _spawn_mayor).
var _mayor: NPC = null

## Re-entrancy latch for the pier. `$DockZone.body_entered` fires once per entry
## and _on_dock AWAITS (it waits out a banner holding `_busy`), so without this a
## second overlap during the await would run the departure twice.
var _casting := false

## The scene's own Theater (an instanced theater.tscn in lanternwood.tscn).
## TravelScene doesn't expose one — it has no cutscenes of its own — so this is
## declared here, the way every other scene with a Theater does it.
@onready var theater: Theater = $Theater

## Slimes still standing in the street. Counted DOWN rather than respawned:
## the meadow is an endless field and its refill loop is right for that, but a
## defence has to be winnable or the beat never ends.
var _alive := 0
var _hud: CanvasLayer = null


func _player_node() -> Node2D:
	return Party.spawn($World, Vector2.ZERO)   # placed for real in _place_player


func _map_path() -> String:
	return MAP_PATH


func _layout_path() -> String:
	return LAYOUT_PATH


func _place_player() -> void:
	var spawn := Game.town_spawn
	Game.town_spawn = ""
	if spawn == "library":
		# Land ON the door marker — feet on the lane right under the arch
		# (the door-mouth arrival doctrine). Now that the marker TRAVELS,
		# _standing is not cosmetic: without it, the body standing in the
		# zone at the end of the entry lock fires it and walks straight back
		# into the room it just left, forever.
		Party.place(MapData.anchor_px(map, "library"))
		_standing["library"] = true
	else:
		Party.place(MapData.anchor_px(map, "player_start"))


func _extra_setup() -> void:
	# cabins, conifers and lamps as y-sorted World entities; the spawner
	# front-loads them in child order so the party (spawned first by
	# TravelScene) still wins y-sort ties
	PropSpawner.build("res://assets/tilesets/lanternwood_props.txt", map, $World)
	_collect_animated()
	$ExitSouth.position = MapData.anchor_px(map, "exit_south")
	$ExitSouth.body_entered.connect(_on_exit_south)
	# THE PIER. A plain Area2D rather than an OverworldLocation, because boarding
	# is a staged beat and not a banner-and-fade: TravelScene's _announce would
	# hold _busy across the whole cutscene, and the doctrine forbids putting a
	# second zone on an anchor that already has one. One zone, one owner.
	$DockZone.position = MapData.anchor_px(map, "dock")
	$DockZone.body_entered.connect(_on_dock)
	_wall_gate_mouth()
	Party.clamp_cameras(MapData.size_px(map))
	# TravelScene gates its markers on `body != player` — re-aim it when the
	# lead changes hands mid-town.
	Party.leader_changed.connect(_on_leader_changed)
	if Game.flag("ebb_done"):
		_ebb_night_town()
	if _defence_due():
		_start_defence()
	_spawn_mayor()


## The gate-mouth road runs to the map's last row and the collision layer only
## stamps grid cells, so nothing stops a body walking off the south edge into
## the void on the one frame the exit refuses. Wall it just past the edge — the
## same guard both Alembic maps carry, and new here because the lane used to
## dead-end in open snow instead of running out through the pines.
func _wall_gate_mouth() -> void:
	_wall(Vector2($ExitSouth.position.x, MapData.size_px(map).y + 4.0),
			Vector2(64.0, 8.0))


## Out the south gate lane, back to the overworld at the Lanternwood icon.
##
## REFUSED while the defence is running (2026-07-29). The fight is staged in
## the lower street, a step or two from the gate, and slime knockback plus a
## backpedal is all it takes to leave town mid-beat — which drops the whole
## set-piece and re-arms it from scratch on the way back in. Nobody can lose
## this fight (a party member cannot die), so holding the gate costs the player
## nothing but the option to walk out on it. Said out loud, because a travel
## door that silently refuses reads as broken.
func _on_exit_south(body: Node) -> void:
	if not body.is_in_group("player"):
		return
	if _alive > 0:
		theater.hint("NOT WITH SOMETHING STILL IN THE LANES.", 2.2)
		return
	_exit_to_overworld("lanternwood")


## Through the library arch. The phase is ALWAYS named explicitly — "" is the
## boot default library.gd reads as the Ebb-night cutscene, and walking in
## the front door must never replay it. The research beat opens once the
## street has told her everything it can (every neighbour asked) and closes
## once she has the thesis.
func _on_travel(loc: OverworldLocation) -> void:
	if loc.id != "library":
		return
	Game.library_phase = "research" if Game.flag("asked_around") \
			and not Game.flag("thesis_found") else "open"


## The night the magic left, from the street: night falls over the snow
## (the fire-lit windows and oil lanterns burn straight through it) and the
## neighbors are out comparing notes. Interact-to-talk villagers — every
## line is about the sudden dead charms; nobody blames anybody (the Ebb has
## no author).
##
## THEY DRIFT (2026-07-29). A street full of people standing at perfect
## attention reads as a menu, not a bad night, and this is the beat where the
## whole town is out because nobody can sit down. Each roam box is authored
## against the grid and kept SMALL for three reasons: talking to all three is
## the `asked_around` gate and the player must never have to hunt somebody; a
## villager is a solid StaticBody2D, so a wide box eventually plugs a lane; and
## every box below is verified ≥2 cells wide in open snow. `npc.gd` filters the
## conifer crowns inside Bramble's box on its own — they are walkable cells that
## would swallow him whole.
func _ebb_night_town() -> void:
	$Dim.color = NIGHT
	if Game.flag("thesis_found"):
		return                           # weeks on; the street went back in
	# cols 16-23, rows 43-45 — the west lane, clear but for the two Y crowns at
	# (20,45) and (21,45), which the walk-behind filter drops.
	_villager("Bramble", SHEET_HARE, MapData.anchor_px(map, "villager_a"), [
		"My warming-wand died mid-stir! I held it to my ear like a fool. Nothing. Not even a hum.",
		"Every charm on my washing line, cold as river stones. All at ONCE. What takes everything at once?",
	], Rect2i(16, 43, 8, 3))
	# cols 28-32, rows 43-48 — open snow east of the gate road. Stops short of
	# col 27: the lamp post at (27,44) is solid and its head at (27,43) is
	# walk-behind.
	_villager("Alder", SHEET_BEAVER, MapData.anchor_px(map, "villager_b"), [
		"Sixty years my ember-charm kept the workshop warm. Tonight - pfft. A dead pebble.",
		"But look around you. The lanterns still burn. Honest oil, honest fire. Whatever left us didn't take THAT.",
	], Rect2i(28, 43, 5, 6))
	# cols 10-22, rows 39-40 — LEVEL 2, the lane outside Fuji's own front door.
	# Stops at col 22: (23,39) is a trunk, and (9,39) is the door itself.
	_villager("Pip", SHEET_FOXKID, MapData.anchor_px(map, "villager_c"), [
		"Did you FEEL it?! The ground went rrrRUMBLE and my glow-marble just... stopped.",
		"Papa says the magic's only hiding. It is NOT hiding. I checked under the ice. TWICE.",
	], Rect2i(10, 39, 13, 2))


# ---- THE DEFENCE OF LANTERNWOOD (Act 1, 2026-07-28) ---------------------------------
# The first real fight in the game, and it is Fuji's alone. She comes back out of
# her own library with a kit she built that afternoon and the street is not empty
# any more — curdled magic has pooled in the lanes the way it has everywhere
# else since the Ebb, except this is HER lane. Three slimes, no respawns, a level
# on the second kill, and a tonic left in the snow when it is over.
#
# Staged in the STREET rather than out on a road somewhere on purpose: a town
# turning dangerous is a stronger beat than a road being dangerous, it costs no
# new zone, and it puts the terraces to work — she fights UP them.

## Armed, the Ebb has happened, and nobody has cleared the lanes yet.
func _defence_due() -> bool:
	return Game.flag("fuji_kit_made") and not Game.flag("town_defended")


func _start_defence() -> void:
	# The HUD lives in meadow.tscn, not here, because this scene is a town nine
	# times out of ten. Instance it for the fight and let it go with the scene.
	# Its CanvasLayer defaults to layer 1, correctly under UI (10), Theater (15)
	# and the dialog box (20).
	_hud = HUDScene.instantiate()
	add_child(_hud)
	_hud.bind_party(Party.members)

	for i in DEFENCE_SPAWNS.size():
		var anchor: String = DEFENCE_SPAWNS[i]
		# One bruiser in the set so the drowse threshold has something to say:
		# a BigSlime needs five darts where a small one needs two.
		var scene: PackedScene = BigSlimeScene if i == 1 else SlimeScene
		var slime := scene.instantiate()
		slime.position = MapData.anchor_px(map, anchor)
		$World.add_child(slime)
		slime.died.connect(_on_defender_kill)
		_alive += 1

	Game.levelled.connect(_on_levelled)
	theater.hint("SOMETHING IS IN THE LANES.", 3.0)


## `died` fires mid-physics, from inside the slime's own signal handler — do the
## bookkeeping deferred so the beat's closing walk-through never runs while the
## physics server is still mid-step.
func _on_defender_kill() -> void:
	_alive -= 1
	if _alive <= 0:
		_finish_defence.call_deferred()


# ---- MAYOR HOLLIS AND THE MOTION (Act 1, 2026-07-29) --------------------------------
# The beat that answers "why does she leave?" with somebody ASKING her to, and the
# beat that hands her the boat. An old elk who is the town's mayor and its clerk in
# the same body, and whose instrument against the end of magic is a set of minutes.
#
# The joke and the wound are the same thing: the machinery of a parish council
# applied, completely straight, to an apocalypse. He seconds his own motion because
# there is nobody else in the room. He is not being brave and he never says the word
# — he is filing. And the reason it lands is that filing is all he has, he knows it,
# and he asks her for a record instead of a rescue.
#
# He is a fixture, not a quest-giver who appears when needed: he is out on his step
# on the Ebb night too, already writing it up, so that by the time he sends her the
# player has met him. Only the LINES change with the story.


## Mayor Hollis on his own step. Skipped for the length of the defence — a mayor
## standing calmly in a lane with a slime in it is a worse joke than any of his —
## and spawned by _finish_defence the moment the lanes are clear, so his stepping
## out is a beat rather than furniture. Idempotent: both callers may fire.
func _spawn_mayor() -> void:
	if _mayor != null or _defence_due():
		return
	var lines: PackedStringArray
	if Game.flag("mayor_briefed"):
		lines = PackedStringArray([
			"The launch is at the pier and the pier is east of here. Coal's in the bunker. Take all of it.",
			"I have written 'DEPARTED' and left the date blank. Don't make me guess, Librarian.",
		])
	elif Game.flag("town_defended"):
		lines = PackedStringArray([
			"Stand there. Don't move. I am writing this down.",
		])
	else:
		# the Ebb night: he is already doing the only thing he knows how to do
		lines = PackedStringArray([
			"Every charm in this town died between one bell and the next. I have it minuted. Minuted, and no use to anybody.",
			"Sixty-one years I have kept these books, and tonight is the first entry I could not put a CAUSE to.",
		])
	_mayor = NPCScene.instantiate()
	_mayor.display_name = "Mayor Hollis"
	_mayor.sheet = SHEET_MAYOR
	_mayor.frame_cols = 10                 # cols 6-9: back x2 + side x2
	_mayor.position = MapData.anchor_px(map, "mayor_pos")
	_mayor.lines = lines
	_mayor.talked.connect(_on_mayor_talked)
	$World.add_child(_mayor)


## Out of the hall and into the lane, the moment the street is safe. Fire-and-forget:
## the walk is scenery, and the party is not locked for it.
func _mayor_steps_out() -> void:
	_spawn_mayor()
	if _mayor == null:
		return
	_mayor.position = MapData.anchor_px(map, "moot_hall")
	theater.walk(_mayor, MapData.anchor_px(map, "mayor_pos"), 34.0)


## His opener has already played through NPC.converse by the time `talked` fires,
## and the party is unlocked again — so LOCK FIRST, before any await, or the
## body can walk out from under the beat (and NPC._process would arm a second
## conversation through it: it gates on the party being locked).
func _on_mayor_talked(_npc: NPC) -> void:
	if Game.flag("mayor_briefed") or not Game.flag("town_defended"):
		return
	theater.lock_party()
	await _the_motion()
	theater.unlock_party()


func _the_motion() -> void:
	theater.face(player, Vector2.RIGHT)
	_mayor.play_act()                      # the slate and the pencil
	await theater.say("Mayor Hollis", "'Item four. Curdled magic in the lower lanes. Cleared by' - by WHOM, exactly. What do I put.")
	await theater.say("Fuji", "Fuji. I work at the library.")
	await theater.say("Mayor Hollis", "I KNOW where you work. I signed your ledger. I am asking what you are NOW, because that was not a librarian.")
	theater.close_dialog()
	await theater.wait(0.5)
	# she tells him. He does not understand a word of it and does not need to:
	# he understands a DOCUMENT, and that turns out to be enough.
	_mayor.play_idle()
	await theater.say("Fuji", "There's a paper on my own shelves. Someone worked out why the magic could go. And how to bring it back.")
	await theater.say("Mayor Hollis", "A paper.")
	await theater.say("Fuji", "A thesis. Twenty years old. It came here and nobody stamped it.")
	await theater.say("Mayor Hollis", "...Nobody stamped it.")
	await theater.say("Fuji", "No.")
	await theater.say("Mayor Hollis", "Then it is not in the record. Then as far as this town is concerned, it does not exist.")
	await theater.say("Mayor Hollis", "Which is the most frightening sentence I have said out loud in my life.")
	theater.close_dialog()
	await theater.wait(0.7)
	# THE MOTION. The pause after it is the whole gag — leave it in.
	_mayor.play_emote()
	await theater.say("Mayor Hollis", "I move that Lanternwood send somebody to find the author of it.")
	theater.close_dialog()
	await theater.wait(1.1)
	await theater.say("Mayor Hollis", "Seconded.")
	await theater.say("Fuji", "You can't second your own-")
	await theater.say("Mayor Hollis", "Seconded. Carried. Minuted.")
	theater.close_dialog()
	await theater.wait(0.6)
	# ...and then he stops performing, which is where it stops being funny.
	_mayor.play_idle()
	await theater.say("Mayor Hollis", "Now the part I would rather not minute. Nobody is coming.")
	await theater.say("Mayor Hollis", "Sixty-one years I have written to the Capital. The road. The ice. The mail. Sixty-one years of 'received'.")
	await theater.say("Mayor Hollis", "We are the last place anybody thinks of. So it is one of ours or it is nobody.")
	await theater.say("Mayor Hollis", "And you are the one holding the paper.")
	theater.close_dialog()
	# THE BOAT. He looks east, down at the water, and the reason it can still cross
	# is a line Alder already said in this street on the night the magic died.
	_mayor.play_side(true)
	await theater.wait(0.8)
	await theater.say("Mayor Hollis", "The town launch is at the pier. It is yours until you bring it back to me.")
	await theater.say("Fuji", "It's an OCEAN. And every charm in this town is dead. Everything is out.")
	await theater.say("Mayor Hollis", "The launch does not care. It never did. It burns coal, it makes fire, and it goes.")
	await theater.say("Mayor Hollis", "Whatever left us did not take THAT.")
	await theater.say("Fuji", "...Alder said that. Word for word.")
	await theater.say("Mayor Hollis", "Alder is right twice a decade. Let him have this one.")
	theater.close_dialog()
	await theater.wait(0.5)
	# the condition. A clerk's idea of immortality, asked of somebody about to
	# cross an ocean, and he means it more than he can say.
	_mayor.play_act()
	await theater.say("Mayor Hollis", "One condition, and it is the only thing I have the authority to ask. You write down what you find.")
	await theater.say("Mayor Hollis", "All of it. For the minutes.")
	await theater.say("Fuji", "...The minutes.")
	await theater.say("Mayor Hollis", "It is what I have, Librarian. A town that wrote nothing down was never here at all.")
	theater.close_dialog()
	await theater.wait(1.2)
	# the one time all scene he uses her name.
	_mayor.play_idle()
	await theater.say("Mayor Hollis", "...Fuji.")
	await theater.say("Mayor Hollis", "Come back and read it to me.")
	theater.close_dialog()
	await theater.wait(0.6)
	Game.set_flag("mayor_briefed")
	Game.set_flag("boat_ready")
	_mayor.lines = PackedStringArray([
		"The launch is at the pier and the pier is east of here. Coal's in the bunker. Take all of it.",
		"I have written 'DEPARTED' and left the date blank. Don't make me guess, Librarian.",
	])
	theater.hint("THE LAUNCH IS YOURS.   THE PIER IS EAST, PAST THE HALL.", 3.6)


# ---- THE CROSSING -------------------------------------------------------------------
# Boarding is a beat, not a door. She walks the pier under her own steam, says the
# one line that means she has decided, and the card carries the sea — a card may
# only state how much time passed, and three days is how much time passed.


## `$DockZone` is a plain Area2D, so `body_entered` fires exactly ONCE per entry —
## which makes an early `return` here the same bug as a travel marker swallowed by
## `_busy`: the pier goes dead and stays dead until the body steps off and back on.
## And the case is not hypothetical. The moot hall door is eight cells west of the
## pier and its announce banner holds TravelScene's `_busy` for over two seconds,
## which is comfortably less than the walk — so "read the hall banner, keep walking
## onto the pier" was a silently dead pier every time.
##
## TravelScene answers this for Locations with `_deliver_standing()`; a lone zone has
## to answer it itself. So: WAIT the banner out rather than refusing, then re-check
## she is still standing on the deck (she may have turned back), and only then decide.
## `_casting` is the re-entrancy latch that makes the await safe.
func _on_dock(body: Node) -> void:
	if not body.is_in_group("player") or _casting:
		return
	_casting = true
	while _busy:
		await get_tree().process_frame
	if not $DockZone.overlaps_body(body):
		_casting = false          # she read the banner and went back up the lane
		return
	if _alive > 0:
		theater.hint("NOT WITH SOMETHING STILL IN THE LANES.", 2.2)
		_casting = false
		return
	if not Game.flag("boat_ready"):
		# Said out loud, and said as HIS: a moored boat you cannot take reads as a
		# bug unless somebody has told you whose it is.
		theater.hint("THE TOWN LAUNCH. BANKED, MOORED, AND NOT HERS TO TAKE.", 2.6)
		_casting = false
		return
	await _cast_off()             # never releases the latch: the scene is leaving


func _cast_off() -> void:
	_busy = true
	theater.lock_party()
	# out to the pier head, past the gangway — the walk is the departure, so it is
	# staged rather than faded through. walk() tweens with collision OFF, and the
	# deck is a straight run, so no dog-leg is needed.
	await theater.walk(player, MapData.anchor_px(map, "dock") + Vector2(40.0, 0.0), 44.0)
	await theater.wait(0.6)
	theater.face(player, Vector2.RIGHT)
	await theater.say("Fuji", "It burns coal. It makes fire. It goes.")
	await theater.say("Fuji", "...I can do the third one.")
	theater.close_dialog()
	await theater.wait(0.8)
	await theater.black(1.8)
	await theater.card("THREE DAYS LATER.")
	Game.set_flag("left_lanternwood")
	Game.overworld_spawn = "landing"
	get_tree().change_scene_to_file("res://scene/overworld.tscn")


func _finish_defence() -> void:
	Game.set_flag("town_defended")
	# The reward is left in the snow rather than granted invisibly: a line
	# saying "you got a tonic" is a notification, an object on the ground is a
	# thing you walk over and pick up, and the second one is a game.
	var drop := PickupScene.instantiate()
	drop.item_id = Items.TONIC
	drop.count = 2
	drop.position = MapData.anchor_px(map, DEFENCE_SPAWNS[0])
	$World.add_child(drop)
	theater.hint("THE LANES ARE CLEAR.   SOMETHING GLINTS IN THE SNOW.", 3.4)
	# ...and the hall door opens. He was inside the whole time, and he has been
	# writing it up since the second slime.
	_mayor_steps_out()


## Levelling is toasted through the Theater, not the HUD: every scene in the
## game has a Theater and only combat zones have a HUD, so a HUD toast would
## simply not exist in most of the places a level can now be earned.
func _on_levelled(member_id: StringName, level: int) -> void:
	theater.hint("%s REACHED LEVEL %d." % [String(member_id).to_upper(), level], 2.6)


## `roam` is the cell rect the neighbour may drift around in, authored against
## the map grid and deliberately SMALL — see _ebb_night_town for why each one is
## the shape it is. Pass an empty Rect2i for a villager that must hold its mark.
func _villager(nm: String, sheet: Texture2D, pos: Vector2, npc_lines: PackedStringArray,
		roam := Rect2i()) -> NPC:
	var npc: NPC = NPCScene.instantiate()
	npc.display_name = nm
	npc.sheet = sheet
	# All three sheets carry the 10-column facing set now. Raising this before
	# the art lands is safe either way — npc.gd clamps by the PNG's real width.
	npc.frame_cols = 10
	npc.position = pos
	npc.lines = npc_lines
	npc.wander_cells = roam
	npc.wander = roam.size != Vector2i.ZERO
	npc.bind_map(map)
	npc.talked.connect(_on_villager_talked)
	$World.add_child(npc)
	return npc


## The street's own wander gate: once she has asked every neighbour and been
## told the same nothing three times over, the only place left to look is her
## own shelves — and the library door starts opening onto the research beat.
func _on_villager_talked(npc: NPC) -> void:
	_asked[npc.display_name] = true
	if _asked.size() >= ASK_GATE:
		Game.set_flag("asked_around")
