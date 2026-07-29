class_name StatBlock
extends Object

## The growth tables and the EXP curve. All static, no instances — the
## `Alchemy` pattern: pure rules in one readable file.
##
## GROWTH IS A TABLE, NOT A CURVE. Every level of every character is hand
## authored and reviewable at a glance, so tuning is an edit rather than solving
## an equation, and nothing about growth can ever depend on what the character
## happened to be WEARING when they levelled. (FFVI's esper stat bonuses are the
## one part of FFVI this system deliberately does not copy — they punish playing
## naturally.)
##
## Rows are CUMULATIVE totals at that level, not per-level deltas. Deltas read
## smaller but every consumer then has to accumulate them correctly, and a sheet
## rebuilt from a dev-menu jump would have to replay nineteen additions to land
## in the same place. A total is just a lookup.

## Index 0 is LEVEL 1, and level 1 is all zeros: a member's baseline lives on its
## own scene (HealthComponent.max_health, PartyMember.speed), so the sheet only
## ever describes what LEVELLING added.
const MAX_LEVEL := 20

## vit, mig, foc, grd, spd
const GROWTH := {
	# FUJI — the front line. VIT and GRD lead, FOC solid, MIG middling. She
	# closes to tome range by design and has to survive being there.
	&"fuji": [
		[0, 0, 0, 0, 0], [1, 0, 1, 1, 0], [2, 1, 1, 1, 0], [3, 1, 2, 2, 0],
		[4, 2, 2, 3, 0], [5, 2, 3, 3, 0], [6, 3, 3, 4, 0], [7, 3, 4, 5, 0],
		[8, 4, 4, 5, 0], [9, 4, 5, 6, 0], [10, 5, 5, 7, 0], [11, 5, 6, 7, 0],
		[12, 6, 6, 8, 0], [13, 6, 7, 9, 0], [14, 7, 7, 9, 0], [15, 7, 8, 10, 0],
		[16, 8, 8, 11, 0], [17, 8, 9, 11, 0], [18, 9, 9, 12, 0], [19, 9, 10, 13, 0],
	],
	# BASIL — the glass gadgeteer. MIG and FOC lead, VIT and GRD lag. He is the
	# one who kites; if he can tank, the gun's recoil skid stops being a cost.
	&"basil": [
		[0, 0, 0, 0, 0], [0, 1, 1, 0, 0], [1, 2, 2, 0, 0], [1, 3, 2, 1, 0],
		[2, 4, 3, 1, 0], [2, 5, 4, 1, 0], [3, 6, 4, 2, 0], [3, 7, 5, 2, 0],
		[4, 8, 6, 2, 0], [4, 9, 6, 3, 0], [5, 10, 7, 3, 0], [5, 11, 8, 3, 0],
		[6, 12, 8, 4, 0], [6, 13, 9, 4, 0], [7, 14, 10, 4, 0], [7, 15, 10, 5, 0],
		[8, 16, 11, 5, 0], [8, 17, 12, 5, 0], [9, 18, 12, 6, 0], [9, 19, 13, 6, 0],
	],
}

## Bodies that must NEVER get a sheet: the prologue world is safe (no combat, no
## kit) and their SpriteFrames have no hurt or downed poses. They get a neutral
## sheet, which the apply path skips entirely — it does not write zeroes, because
## these scenes carry their own tuned max_health exports and a zero write would
## silently retune shipped prologue beats.
const SHEETLESS: Array[StringName] = [&"kid_basil", &"basil_student"]

## LEVEL GROWTH GRANTS NO SPD, on purpose, and gear should grant it sparingly.
## The AI brains' hysteresis bands (34/44/56/96/128px, ai_brain.gd) are all tuned
## to the shipped 150px/s; past roughly +20% the follower stops settling and
## reads as twitching. Any change that can raise a member's speed must re-run
## tools/party_probe.gd.
const SPD_CLAMP := 0.20


## EXP required to go from `level` to `level + 1`. The shape is 20 * level^1.5,
## rounded once here into a table so the numbers are inspectable and can be
## hand-tweaked per band without changing an exponent.
const TO_NEXT := [
	20, 57, 104, 160, 224, 294, 370, 453, 540, 632,
	730, 831, 937, 1047, 1162, 1280, 1402, 1528, 1657, 0,
]


static func exp_to_next(level: int) -> int:
	if level < 1 or level >= MAX_LEVEL:
		return 0                                  # 0 means "capped"
	return TO_NEXT[level - 1]


## Total EXP banked at the START of `level` — what a sheet's exp_total must reach
## for the level before it to be complete.
static func exp_at(level: int) -> int:
	var total := 0
	for l in range(1, mini(level, MAX_LEVEL)):
		total += TO_NEXT[l - 1]
	return total


static func has_growth(id: StringName) -> bool:
	return GROWTH.has(id)


## A fresh level-1 sheet, or a neutral one for a body that must not have stats.
static func fresh(id: StringName) -> CharacterSheet:
	if SHEETLESS.has(id) or not GROWTH.has(id):
		return CharacterSheet.neutral_sheet()
	var s := CharacterSheet.make(id, 1)
	apply_growth(s)
	return s


## Rewrite `sheet.base` from the growth table for its current level. Called on
## creation and after every level-up; never accumulates, so it is safe to call
## as often as you like.
static func apply_growth(sheet: CharacterSheet) -> void:
	if sheet.neutral or not GROWTH.has(sheet.member_id):
		return
	var rows: Array = GROWTH[sheet.member_id]
	var row: Array = rows[clampi(sheet.level, 1, rows.size()) - 1]
	for i in CharacterSheet.STATS.size():
		sheet.base[CharacterSheet.STATS[i]] = row[i]


## Bank EXP and level up as many times as it earns. Returns how many levels were
## gained so the caller can toast once per level (or once in total).
static func grant_exp(sheet: CharacterSheet, amount: int) -> int:
	if sheet.neutral or amount <= 0:
		return 0
	sheet.exp_total += amount
	var gained := 0
	while sheet.level < MAX_LEVEL:
		var need := exp_at(sheet.level + 1)
		if sheet.exp_total < need:
			break
		sheet.level += 1
		gained += 1
	if gained > 0:
		apply_growth(sheet)
	return gained


## EXP into the current level, and how much that level costs — the two numbers a
## progress bar needs. A capped sheet reports a full bar rather than dividing by
## zero, which is what every "1/0" bar bug in every RPG menu is.
static func level_progress(sheet: CharacterSheet) -> Vector2i:
	if sheet.neutral:
		return Vector2i(0, 1)
	var need := exp_to_next(sheet.level)
	if need <= 0:
		return Vector2i(1, 1)
	return Vector2i(sheet.exp_total - exp_at(sheet.level), need)
