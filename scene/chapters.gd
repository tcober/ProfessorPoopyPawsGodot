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

## Prologue A's town flag ladder, named once — town_fest.gd's dressing is the
## densest flag matrix in the game and these sets are easy to get subtly wrong.
const FEST_ARRIVED := ["prologue_saw_mom", "prologue_left_home"]
const FEST_WANDER := ["prologue_saw_mom", "prologue_left_home",
		"prologue_festival_done"]
const FEST_HOMESICK := ["prologue_saw_mom", "prologue_left_home",
		"prologue_festival_done", "prologue_ribbon",
		"prologue_ribbon_returned", "prologue_want_home"]

## static var, not const: the flag ladders above are concatenated per beat and
## GDScript can't constant-fold array `+`. Static initializers run at class load,
## so `Chapters.BEATS` reads the same either way.
static var BEATS: Array[Dictionary] = [
	{group = "PROLOGUE A - THE WHIRLIGIG"},
	{
		name = "TITLE CARDS", scene = "res://scene/prologue_open.tscn",
		roster = KID, lead = &"kid_basil", state = {}, flags = [],
	},
	{
		name = "A1 - FESTIVAL MORNING", scene = "res://scene/house_fest.tscn",
		roster = KID, lead = &"kid_basil", state = {}, flags = [],
	},
	{
		name = "A2 - MOM AT THE HEARTH",
		scene = "res://scene/downstairs_fest.tscn",
		roster = KID, lead = &"kid_basil",
		state = {interior_spawn = "stair_arrival"}, flags = [],
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
		# the goose on the LANE with its pre-theft lines, which is incoherent
		# next to Sage complaining her ribbon is gone.
		name = "A4 - THE GOOSE IN THE ORCHARD",
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
		name = "A9 - THE BLUFF - THE MEET", scene = "res://scene/bluff.tscn",
		roster = KID, lead = &"kid_basil",
		state = {bluff_phase = "meet"}, flags = [],
	},
	{
		name = "A10 - GEAR SPRING CRANK", scene = "res://scene/bluff.tscn",
		roster = KID, lead = &"kid_basil",
		state = {bluff_phase = "meet"}, flags = ["prologue_met_kitty"],
	},
	{
		name = "A11 - THE WHIRLIGIG FLIES", scene = "res://scene/bluff.tscn",
		roster = KID, lead = &"kid_basil", state = {bluff_phase = "meet"},
		flags = ["prologue_met_kitty", "prologue_part_gear",
				"prologue_part_spring", "prologue_part_crank"],
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
		# any library_phase other than "" or "ebb" renders an EMPTY room
		name = "FUJI'S LIBRARY", scene = "res://scene/library.tscn",
		roster = FUJI, lead = &"fuji",
		state = {library_phase = "ebb"}, flags = [],
	},
	{
		name = "LANTERNWOOD - EBB NIGHT",
		scene = "res://scene/lanternwood.tscn",
		roster = FUJI, lead = &"fuji",
		state = {town_spawn = "library"}, flags = ["ebb_done"],
	},

	{group = "SANDBOX"},
	{
		name = "THE LOFT", scene = "res://scene/house.tscn",
		roster = ADULTS, lead = &"basil", state = {},
		flags = ["prologue_done", "ebb_done"],
	},
	{
		name = "THE LAB", scene = "res://scene/downstairs.tscn",
		roster = ADULTS, lead = &"basil", state = {},
		flags = ["prologue_done", "ebb_done"],
	},
	{
		name = "ALEMBIC TOWN", scene = "res://scene/alembic_town.tscn",
		roster = ADULTS, lead = &"basil", state = {},
		flags = ["prologue_done", "ebb_done"],
	},
	{
		name = "THE OVERWORLD", scene = "res://scene/overworld.tscn",
		roster = ADULTS, lead = &"basil", state = {overworld_spawn = "town"},
		flags = ["prologue_done", "ebb_done"],
	},
	{
		name = "WHISKER MEADOW", scene = "res://scene/meadow.tscn",
		roster = ADULTS, lead = &"basil", state = {},
		flags = ["prologue_done", "ebb_done"],
	},
	{
		# ebb_done deliberately UNSET — that flag is the whole of Lanternwood's
		# night dressing, so this is the same town by day
		name = "LANTERNWOOD (DAY)", scene = "res://scene/lanternwood.tscn",
		roster = ADULTS, lead = &"basil", state = {}, flags = ["prologue_done"],
	},
]


## True for the non-selectable chapter headings.
static func is_group(beat: Dictionary) -> bool:
	return not beat.has("scene")
