extends RefCounted

## The dev chapter selector's beat table (scene/dev_menu.gd) — every point in the
## story you can drop into, and the exact autoload state that makes it play.
##
## Every beat in this game is already a pure function of scene + Party.roster +
## Game's routers and flags; tools/prologue_probe.gd proves it by staging the
## same state per beat. This file is that knowledge written down once.
##
## DELIBERATELY DUMB: no class_name (a new one needs --headless --import before
## headless runs see it) and NO reference to Game/Party, so tools/shot.gd can
## load() it under --script, where autoloads are not compile-time identifiers.
## Consumers do `const Chapters = preload("res://scene/chapters.gd")`.
##
## Row shape:
##   {group = "HEADER"}                     a non-selectable chapter heading
##   {name, scene, roster, lead, state, flags}
##     state = Game property name -> value (phase AND spawn routers alike —
##             they are all plain properties, so one dict covers both)
##     flags = story flags to pre-set, applied after Game.reset_story()
##
## ROSTER IS NOT COSMETIC — it is a SpriteFrames contract. kid_basil_frames and
## player_frames are disjoint in the clips the cutscenes drive: sleep/wake/sigh
## are kid-only, sit/look_watch/bow_head/knapsack*/defeat_walk are adult-only.
## The wrong body plays a beat as error spam and a frozen pose. Never pass an
## empty roster either (party.gd indexes ids[0]), and never route kid_basil or
## basil_student into the meadow — neither has a Brain node or an attack kit.

const KID: Array[StringName] = [&"kid_basil"]
const STUDENT: Array[StringName] = [&"basil_student"]
const FUJI: Array[StringName] = [&"fuji"]
const ADULTS: Array[StringName] = [&"basil", &"fuji"]

## FUJI'S KIT, named once. Her tome and blow-pipe are flag-gated (she MAKES them
## in Act 1 beat 3, "THE KIT" — see entities/fuji/fuji.gd), and Game.reset_story()
## wipes flags, so EVERY beat that expects to be able to fight has to carry these
## two or she turns up empty-pawed and the meadow silently stops working.
## Anything routed into a combat scene from here on needs KIT_ARMED.
const KIT_ARMED := ["fuji_darts_made", "fuji_tome_taken", "fuji_kit_made"]

## Everything Prologue A0 "The Fever" leaves behind — the cold open that now
## precedes the festival. Every A-beat below carries it, so a dev jump into
## the festival stages a world where the fever chapter already happened
## (inert to those scenes today, and the same shape as KIT_ARMED: name the
## ladder once or someone forgets a rung).
const FEVER_DONE := ["prologue_fever", "prologue_doctor_gone",
		"prologue_doctor_heard", "prologue_wrong_shelf",
		"prologue_herbal_found", "prologue_remedy_made",
		"prologue_mom_better"]

## Prologue A's town flag ladder, named once — town_fest.gd's dressing is the
## densest flag matrix in the game and these sets are easy to get subtly wrong.
## static var, not const: built on FEVER_DONE with array `+`, which GDScript
## cannot constant-fold (the BEATS rule).
static var FEST_ARRIVED: Array = FEVER_DONE + ["prologue_saw_mom",
		"prologue_left_home"]
static var FEST_WANDER: Array = FEST_ARRIVED + ["prologue_festival_done"]
static var FEST_HOMESICK: Array = FEST_WANDER + ["prologue_ribbon",
		"prologue_ribbon_returned", "prologue_want_home"]

## What the real chain carries when the south gate opens the bluff. The bluff's
## "meet" phase ends by handing off to the brew (bluff._the_idea loads
## downstairs_fest), so a meet beat needs the SAME door keys the brew does or it
## dead-ends in the lab — see FEST_WHIRLIGIG's note below.
static var BLUFF_MEET: Array = FEST_HOMESICK + ["prologue_gate_open"]

## Everything the whirligig beat leaves behind, for the three legs that follow
## it (the brew / the walk across town / the recital). NOTE prologue_gate_open:
## without it downstairs_fest._on_exit_door refuses forever ("I came home to
## talk to Mom") and a jump straight into the brew is trapped in the lab.
## static var for the same reason BEATS is — array `+` can't be const-folded.
static var FEST_WHIRLIGIG: Array = BLUFF_MEET + ["prologue_met_kitty",
		"prologue_part_gear", "prologue_part_spring",
		"prologue_part_crank", "prologue_whirligig_done"]

## static var, not const: the flag ladders above are concatenated per beat and
## GDScript can't constant-fold array `+`. Static initializers run at class load,
## so `Chapters.BEATS` reads the same either way.
static var BEATS: Array[Dictionary] = [
	{group = "PROLOGUE A0 - THE FEVER"},
	{
		name = "TITLE CARDS", scene = "res://scene/prologue_open.tscn",
		roster = KID, lead = &"kid_basil", state = {}, flags = [],
	},
	{
		name = "A0-1 - THE QUIET HOUSE", scene = "res://scene/house_fever.tscn",
		roster = KID, lead = &"kid_basil", state = {}, flags = [],
	},
	{
		name = "A0-2 - THE DOCTOR LEAVING",
		scene = "res://scene/downstairs_fever.tscn",
		roster = KID, lead = &"kid_basil",
		state = {interior_spawn = "stair_arrival"}, flags = ["prologue_fever"],
	},
	{
		# doctor_gone but not doctor_heard: momroom plays the bedside
		name = "A0-3 - HER ROOM", scene = "res://scene/momroom.tscn",
		roster = KID, lead = &"kid_basil", state = {},
		flags = ["prologue_fever", "prologue_doctor_gone"],
	},
	{
		name = "A0-4 - THE GREY MORNING", scene = "res://scene/town_fever.tscn",
		roster = KID, lead = &"kid_basil", state = {town_spawn = "home"},
		flags = ["prologue_fever", "prologue_doctor_gone",
				"prologue_doctor_heard"],
	},
	{
		name = "A0-5 - THE READING ROOM",
		scene = "res://scene/academy_library.tscn",
		roster = KID, lead = &"kid_basil", state = {},
		flags = ["prologue_fever", "prologue_doctor_gone",
				"prologue_doctor_heard"],
	},
	{
		# herbal_found and not remedy_made arms the simmer on entry
		name = "A0-6 - THE SIMMER", scene = "res://scene/downstairs_fever.tscn",
		roster = KID, lead = &"kid_basil",
		state = {interior_spawn = "front_door"},
		flags = ["prologue_fever", "prologue_doctor_gone",
				"prologue_doctor_heard", "prologue_wrong_shelf",
				"prologue_herbal_found"],
	},
	{
		# remedy_made and not mom_better: momroom plays the drink; the room
		# outside is BUILT from here on (downstairs_fever swaps its own map)
		name = "A0-7 - SHE DRINKS", scene = "res://scene/momroom.tscn",
		roster = KID, lead = &"kid_basil", state = {},
		flags = ["prologue_fever", "prologue_doctor_gone",
				"prologue_doctor_heard", "prologue_wrong_shelf",
				"prologue_herbal_found", "prologue_remedy_made"],
	},
	{
		name = "A0-8 - THE MIDDLE OF THE NIGHT",
		scene = "res://scene/downstairs_fever.tscn",
		roster = KID, lead = &"kid_basil",
		state = {interior_spawn = "momdoor_out"}, flags = FEVER_DONE,
	},

	{group = "PROLOGUE A - THE WHIRLIGIG"},
	{
		name = "A1 - FESTIVAL MORNING", scene = "res://scene/house_fest.tscn",
		roster = KID, lead = &"kid_basil", state = {}, flags = FEVER_DONE,
	},
	{
		name = "A2 - MOM AT THE HEARTH",
		scene = "res://scene/downstairs_fest.tscn",
		roster = KID, lead = &"kid_basil",
		state = {interior_spawn = "stair_arrival"}, flags = FEVER_DONE,
	},
	{
		# town_spawn "home" also clears _home_armed, so the arrival doesn't
		# bounce straight back through the door it landed on.
		name = "A3 - INTO THE FESTIVAL", scene = "res://scene/town_fest.tscn",
		roster = KID, lead = &"kid_basil",
		state = {town_spawn = "home"}, flags = FEST_ARRIVED,
	},
	{
		# goose_hidden as well as festival_done: festival_done alone re-spawns
		# the goose in the SQUARE with its pre-theft lines, which is incoherent
		# next to Sage complaining her ribbon is gone. Lands you on the forest
		# floor — the goose is up a great tree and the rope ladder is the beat.
		name = "A4 - THE GOOSE UP THE TREE",
		scene = "res://scene/town_fest.tscn",
		roster = KID, lead = &"kid_basil", state = {},
		flags = FEST_WANDER + ["prologue_goose_hidden"],
	},
	{
		name = "A5 - RETURN THE RIBBON", scene = "res://scene/town_fest.tscn",
		roster = KID, lead = &"kid_basil", state = {},
		flags = FEST_WANDER + ["prologue_ribbon"],
	},
	{
		name = "A6 - I WANT TO GO HOME", scene = "res://scene/town_fest.tscn",
		roster = KID, lead = &"kid_basil", state = {}, flags = FEST_HOMESICK,
	},
	{
		name = "A7 - MOM'S BLESSING",
		scene = "res://scene/downstairs_fest.tscn",
		roster = KID, lead = &"kid_basil",
		state = {interior_spawn = "front_door"}, flags = FEST_HOMESICK,
	},
	{
		name = "A8 - THE SOUTH GATE", scene = "res://scene/town_fest.tscn",
		roster = KID, lead = &"kid_basil", state = {},
		flags = FEST_HOMESICK + ["prologue_gate_open"],
	},
	{
		# BLUFF_MEET, not []: the meet plays through to _the_idea, which loads
		# the fest downstairs for the brew — and that room's only exit is the
		# front door, which refuses without prologue_saw_mom.
		name = "A9 - THE BLUFF - THE MEET", scene = "res://scene/bluff.tscn",
		roster = KID, lead = &"kid_basil",
		state = {bluff_phase = "meet"}, flags = BLUFF_MEET,
	},
	{
		name = "A10 - GEAR SPRING CRANK", scene = "res://scene/bluff.tscn",
		roster = KID, lead = &"kid_basil",
		state = {bluff_phase = "meet"}, flags = BLUFF_MEET + ["prologue_met_kitty"],
	},
	{
		name = "A11 - THE WHIRLIGIG FLIES", scene = "res://scene/bluff.tscn",
		roster = KID, lead = &"kid_basil", state = {bluff_phase = "meet"},
		flags = BLUFF_MEET + ["prologue_met_kitty", "prologue_part_gear",
				"prologue_part_spring", "prologue_part_crank"],
	},
	{
		# Mom is home for this one (_mom_home: left_home AND want_home are both
		# in the ladder) and has her own brew lines
		name = "A12 - THE BREW", scene = "res://scene/downstairs_fest.tscn",
		roster = KID, lead = &"kid_basil",
		state = {interior_spawn = "front_door"}, flags = FEST_WHIRLIGIG,
	},
	{
		# the leg where the Academy door is LIVE and the south gate refuses
		name = "A13 - ACROSS TOWN", scene = "res://scene/town_fest.tscn",
		roster = KID, lead = &"kid_basil", state = {town_spawn = "home"},
		flags = FEST_WHIRLIGIG + ["prologue_potion_made"],
	},
	{
		name = "A14 - THE RECITAL", scene = "res://scene/hall.tscn",
		roster = KID, lead = &"kid_basil", state = {hall_phase = "recital"},
		flags = FEST_WHIRLIGIG + ["prologue_potion_made"],
	},

	# group headings are clipped to one column (~30 chars) — keep them short
	{group = "PROLOGUE B - POOPY PAWS"},
	{
		name = "B1 - THE WATCH", scene = "res://scene/bluff.tscn",
		roster = STUDENT, lead = &"basil_student",
		state = {bluff_phase = "romance"}, flags = [],
	},
	{
		# ALL THREE wpart flags or none. A partial set is an unrecoverable
		# softlock: _all_parts_found can never go true, the Kitty talk never
		# fires, and the bluff has no exits. prologue_watch_given must stay
		# UNSET here too, or the refit is skipped the same way.
		name = "B2 - THE KISS", scene = "res://scene/bluff.tscn",
		roster = STUDENT, lead = &"basil_student",
		state = {bluff_phase = "romance"},
		flags = ["prologue_wpart_gear", "prologue_wpart_spring",
				"prologue_wpart_crank"],
	},
	{
		name = "B3 - THE WALK HOME", scene = "res://scene/town_thesis.tscn",
		roster = STUDENT, lead = &"basil_student",
		state = {town_thesis_phase = "plant"}, flags = [],
	},
	{
		name = "B4 - EIGHT FIFTY-SEVEN",
		scene = "res://scene/house_thesis.tscn",
		roster = STUDENT, lead = &"basil_student", state = {}, flags = [],
	},
	{
		name = "B5 - THE SQUELCH", scene = "res://scene/town_thesis.tscn",
		roster = STUDENT, lead = &"basil_student",
		state = {town_thesis_phase = "dash"}, flags = [],
	},
	{
		# state = {} is LOAD-BEARING: the hall routes on Game.hall_phase now,
		# and this beat relies on reset_story() blanking it back to "". Without
		# that, a jump down from A14 would play the kid recital with the
		# student roster — the wrong SpriteFrames contract.
		name = "B6 - THE NAMING", scene = "res://scene/hall.tscn",
		roster = STUDENT, lead = &"basil_student", state = {}, flags = [],
	},
	{
		name = "B7 - SHE CALLS", scene = "res://scene/bluff.tscn",
		roster = STUDENT, lead = &"basil_student",
		state = {bluff_phase = "call1"}, flags = [],
	},
	{
		# partyless set-piece; the roster still has to be valid to spawn into
		# whatever it hands to next
		name = "B8 - THE ACCIDENT", scene = "res://scene/accident.tscn",
		roster = STUDENT, lead = &"basil_student", state = {}, flags = [],
	},
	{
		name = "B9 - THE WRONG VOICE", scene = "res://scene/bluff.tscn",
		roster = STUDENT, lead = &"basil_student",
		state = {bluff_phase = "call2"}, flags = [],
	},
	{
		name = "B10 - THE VERDICT", scene = "res://scene/sickroom.tscn",
		roster = STUDENT, lead = &"basil_student", state = {}, flags = [],
	},
	{
		name = "B11 - THE CLINIC STEPS", scene = "res://scene/town_thesis.tscn",
		roster = STUDENT, lead = &"basil_student",
		state = {town_thesis_phase = "steps"}, flags = [],
	},

	{group = "THE EBB"},
	{
		name = "THE EBB NIGHT", scene = "res://scene/ebb.tscn",
		roster = ADULTS, lead = &"basil", state = {}, flags = [],
	},
	{
		# the sync gag + the dead-wand beat, ending on control in the room
		name = "FUJI'S LIBRARY", scene = "res://scene/library.tscn",
		roster = FUJI, lead = &"fuji",
		state = {library_phase = "ebb"}, flags = [],
	},
	{
		# any library_phase other than "" or "ebb" SKIPS the cutscene and
		# just opens the room — the walk-out, without sitting through it
		name = "FUJI'S LIBRARY (WALK OUT)", scene = "res://scene/library.tscn",
		roster = FUJI, lead = &"fuji",
		state = {library_phase = "night"}, flags = ["ebb_done"],
	},
	{
		name = "LANTERNWOOD - EBB NIGHT",
		scene = "res://scene/lanternwood.tscn",
		roster = FUJI, lead = &"fuji",
		state = {town_spawn = "library"}, flags = ["ebb_done"],
	},
	{
		# Act 1 beat 2: the ledger, the three stacks, the uncatalogued thesis.
		# asked_around is what the Ebb-night street sets once every neighbour
		# has been asked — the flag the library door reads to open this.
		name = "THE RESEARCH NIGHT", scene = "res://scene/library.tscn",
		roster = FUJI, lead = &"fuji",
		state = {library_phase = "research"},
		flags = ["ebb_done", "asked_around"],
	},
	{
		# Act 1 beat 3 leg (a): the night she reads the paper, the lanes reach
		# her own square — she can hurt nothing and runs for her own door. The
		# beat that turns the library into the workbench (the arch routes "kit"
		# while thesis_found holds and the kit is unmade).
		name = "THE AMBUSH", scene = "res://scene/lanternwood.tscn",
		roster = FUJI, lead = &"fuji",
		state = {town_spawn = "library"},
		flags = ["ebb_done", "asked_around", "ledger_read", "thesis_found"],
	},
	{
		# Act 1 beat 3a: the room she has read in for six weeks becomes a supply
		# list. Shelf three gives her the dose, her dead wand becomes the pipe,
		# and whichever stack she takes a book off is her weapon for the game.
		name = "THE KIT", scene = "res://scene/library.tscn",
		roster = FUJI, lead = &"fuji",
		state = {library_phase = "kit"},
		flags = ["ebb_done", "asked_around", "ledger_read", "thesis_found"],
	},
	{
		# Act 1 beat 3: the first real fight in the game, and Fuji's alone. She
		# comes back out of her own library with a kit she built that afternoon
		# and the lanes are not empty any more. Three slimes, no respawns, a
		# level on the second kill, a tonic in the snow when it is done.
		name = "THE DEFENCE OF LANTERNWOOD",
		scene = "res://scene/lanternwood.tscn",
		roster = FUJI, lead = &"fuji",
		state = {}, flags = ["ebb_done", "asked_around", "thesis_found"] + KIT_ARMED,
	},
	{
		# Act 1 beat 3b: THE MOTION. The lanes are clear, so Mayor Hollis is out
		# on his step with a slate. She tells him about the thesis; he minutes it,
		# moves that the town send somebody, seconds himself, and hands her the
		# launch. town_defended is what puts him in the street — without it
		# _spawn_mayor gives him his Ebb-night lines and the beat never arms.
		name = "THE MOTION (MAYOR HOLLIS)",
		scene = "res://scene/lanternwood.tscn",
		roster = FUJI, lead = &"fuji",
		state = {}, flags = ["ebb_done", "asked_around", "thesis_found",
				"town_defended"] + KIT_ARMED,
	},
	{
		# Act 1 beat 4 opens: the pier is armed, so stepping onto it casts off and
		# lands her on Forest Land's west shingle, five cells from Alembic Town.
		name = "THE CROSSING (THE PIER)",
		scene = "res://scene/lanternwood.tscn",
		roster = FUJI, lead = &"fuji",
		state = {}, flags = ["ebb_done", "asked_around", "thesis_found",
				"town_defended", "mayor_briefed", "boat_ready"] + KIT_ARMED,
	},
	{
		# ...and where it puts her. Solo Fuji on the travel map for the first
		# time (overworld.gd repoints the chibi's SpriteFrames off Party.leader_id).
		name = "THE WEST SHINGLE (LANDED)",
		scene = "res://scene/overworld.tscn",
		roster = FUJI, lead = &"fuji",
		state = {overworld_spawn = "landing"},
		flags = ["ebb_done", "asked_around", "thesis_found", "town_defended",
				"mayor_briefed", "boat_ready", "left_lanternwood"] + KIT_ARMED,
	},

	{group = "SANDBOX"},
	{
		name = "THE LOFT", scene = "res://scene/house.tscn",
		roster = ADULTS, lead = &"basil", state = {},
		flags = ["prologue_done", "ebb_done"] + KIT_ARMED,
	},
	{
		name = "THE LAB", scene = "res://scene/downstairs.tscn",
		roster = ADULTS, lead = &"basil", state = {},
		flags = ["prologue_done", "ebb_done"] + KIT_ARMED,
	},
	{
		name = "ALEMBIC TOWN", scene = "res://scene/alembic_town.tscn",
		roster = ADULTS, lead = &"basil", state = {},
		flags = ["prologue_done", "ebb_done"] + KIT_ARMED,
	},
	{
		name = "THE ACADEMY", scene = "res://scene/academy.tscn",
		roster = ADULTS, lead = &"basil", state = {},
		flags = ["prologue_done", "ebb_done"] + KIT_ARMED,
	},
	{
		name = "THE OVERWORLD", scene = "res://scene/overworld.tscn",
		roster = ADULTS, lead = &"basil", state = {overworld_spawn = "town"},
		flags = ["prologue_done", "ebb_done"] + KIT_ARMED,
	},
	{
		name = "WHISKER MEADOW", scene = "res://scene/meadow.tscn",
		roster = ADULTS, lead = &"basil", state = {},
		flags = ["prologue_done", "ebb_done"] + KIT_ARMED,
	},
	{
		# ebb_done deliberately UNSET — that flag is the whole of Lanternwood's
		# night dressing, so this is the same town by day.
		#
		# town_defended IS set, and it has to be: _defence_due() is
		# `fuji_kit_made and not town_defended`, and KIT_ARMED carries
		# fuji_kit_made. Without it this row — the one that exists to be a quiet
		# town to walk around in — armed THE DEFENCE OF LANTERNWOOD instead:
		# three slimes, a combat HUD, and the south gate refusing to open until
		# they were dead. It also suppressed Mayor Hollis, since _spawn_mayor
		# returns early while a defence is due.
		name = "LANTERNWOOD (DAY)", scene = "res://scene/lanternwood.tscn",
		roster = ADULTS, lead = &"basil", state = {},
		flags = ["prologue_done", "town_defended"] + KIT_ARMED,
	},
]


## True for the non-selectable chapter headings.
static func is_group(beat: Dictionary) -> bool:
	return not beat.has("scene")
