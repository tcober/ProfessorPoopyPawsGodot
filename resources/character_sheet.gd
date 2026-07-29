class_name CharacterSheet
extends Resource

## One party member's persistent RPG state: level, EXP, the five stats, and the
## four equipped items.
##
## WHY THIS IS A RESOURCE ON `Game` AND NOT STATE ON THE BODY: `Party.spawn()`
## rebuilds every member from its PackedScene at every single door, so anything
## living on the CharacterBody2D is gone by the next scene. This is the same
## reason `Game` already holds the gun loadout (`loaded`/`spares`/`ammo_left`).
##
## `Game.reset_story()` MUST clear the sheet table, for the same reason it blanks
## the loadout: the dev chapter menu can jump BACKWARDS, and a level-18 Fuji
## with a socketed relic must not turn up in the prologue.

## The five stats, in menu order. These strings are the canonical keys used by
## Item.worn, StatBlock's growth rows, and the menu — one vocabulary, no
## per-site enums to drift.
const STATS: Array[String] = ["vit", "mig", "foc", "grd", "spd"]

const STAT_BLURB := {
	"vit": "VITALITY",
	"mig": "MIGHT",
	"foc": "FOCUS",
	"grd": "GUARD",
	"spd": "SPEED",
}

@export var member_id: StringName = &""
@export var level: int = 1
@export var exp_total: int = 0

## BASE stats — what levelling grants. Equipment is never folded in here.
## Keeping the two apart is what makes un-equipping safe and is the one part of
## FFVI's esper bonuses worth NOT copying: growth must never depend on what you
## happened to be wearing when you levelled.
@export var base: Dictionary = {"vit": 0, "mig": 0, "foc": 0, "grd": 0, "spd": 0}

## Item.Kind -> item id. Empty StringName means the slot is bare.
@export var gear: Dictionary = {}

## A neutral sheet answers "no" to everything and is what prologue bodies get.
## kid_basil and basil_student have no combat, no levels, and no downed pose;
## a sheet that WROTE their max_health would silently retune scenes that have
## shipped since 2026-07-12. Neutral sheets are skipped by the apply path
## entirely rather than applying zeroes — see PartyMember._apply_sheet.
@export var neutral: bool = false


static func make(id: StringName, lvl: int = 1) -> CharacterSheet:
	var s := CharacterSheet.new()
	s.member_id = id
	s.level = maxi(1, lvl)
	s.base = {"vit": 0, "mig": 0, "foc": 0, "grd": 0, "spd": 0}
	s.gear = {}
	return s


static func neutral_sheet() -> CharacterSheet:
	var s := CharacterSheet.new()
	s.neutral = true
	return s


## Base + every equipped item's contribution.
func stat(key: String) -> int:
	var total: int = base.get(key, 0)
	for slot: int in gear:
		var it := Items.get_item(gear[slot])
		if it:
			total += int(it.worn.get(key, 0))
	return total


func equipped(slot: int) -> Item:
	return Items.get_item(gear.get(slot, &""))


## Returns the item that came OFF, so the caller can put it back in the satchel.
## Callers must not assume the slot was empty: swapping is the common case.
func equip(slot: int, item_id: StringName) -> Item:
	var prev := equipped(slot)
	if item_id == &"":
		gear.erase(slot)
	else:
		gear[slot] = item_id
	return prev


func unequip(slot: int) -> Item:
	return equip(slot, &"")


## A compact "LV 4  FUJI" style line for the menu's roster pane.
func label() -> String:
	return "LV%2d" % level
