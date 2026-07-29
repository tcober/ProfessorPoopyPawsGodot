class_name Item
extends Resource

## One entry in the satchel — a consumable or a piece of gear.
##
## Plain @export data with no behaviour, exactly like [Compound]: every instance
## in the game is built by the static factory in `resources/items.gd`, never by
## `Item.new()` at a call site. That keeps the whole item table readable in one
## file and means a balance change is a one-line edit rather than a hunt.
##
## FOUR EQUIP SLOTS (canon 2026-07-28, and a deliberate revision of the
## "one socket is the entire equipment layer" rule in DESIGN.md): WEAPON, HEAD
## (the hat), BODY (the shirt) and RELIC (the special item) — the FFVI shape.
## The VESTIGE socket that DESIGN.md's magic ladder describes is a FIFTH,
## separate slot and is not built yet; gear and magicite were always meant to be
## different systems, and collapsing them was the part of the old rule that
## did not survive contact with wanting a hat.
##
## A WEAPON never changes a character's KIT. Basil fires a laser and Fuji swings
## a book because of who they are, not what they hold — a weapon grants stats
## and a name. This is load-bearing: the kit lives in `_process_kit` overrides on
## the member subclasses, and letting an item swap it would put branching combat
## code behind an inventory screen.

enum Kind {
	CONSUMABLE,
	WEAPON,
	HEAD,
	BODY,
	RELIC,
}

## Slots in menu order. CONSUMABLE is deliberately absent — it is not a slot.
const SLOTS: Array[Kind] = [Kind.WEAPON, Kind.HEAD, Kind.BODY, Kind.RELIC]

const SLOT_NAMES := {
	Kind.WEAPON: "WEAPON",
	Kind.HEAD: "HAT",
	Kind.BODY: "SHIRT",
	Kind.RELIC: "CHARM",
}

@export var id: StringName = &""
@export var display_name: String = "ITEM"
@export var kind: Kind = Kind.CONSUMABLE
## One short line, shown under the cursor. Keep it to ~34 chars — the menu pane
## is 384px wide at base resolution and the pixel font is not narrow.
@export var description: String = ""

# ---- consumable payload ----------------------------------------------------------
## Half-hearts restored. HP is in half-hearts everywhere in this project and
## always will be, because it is drawn as hearts.
@export var heal: int = 0
## Revives a downed member instead of healing a standing one. Reserved: the
## downed state ships with the RESTORE magic slice, not with this one.
@export var revive: bool = false

# ---- equipment payload -----------------------------------------------------------
## stat name -> flat bonus, e.g. {"grd": 2}. Keys must be lowercase stat ids
## (see CharacterSheet.STATS); anything else is rejected at build time by
## Items._validate so a typo can't silently do nothing forever.
@export var worn: Dictionary = {}
## Member ids that may equip this. EMPTY MEANS ANYONE — the common case, and
## the default that keeps the item table short.
@export var users: Array[StringName] = []
## Menu accent, the way Compound.tint colours the ammo pips.
@export var tint: Color = Color(0.86, 0.86, 0.92)


func is_gear() -> bool:
	return kind != Kind.CONSUMABLE


func slot_name() -> String:
	return SLOT_NAMES.get(kind, "")


func usable_by(member_id: StringName) -> bool:
	return users.is_empty() or users.has(member_id)


## The "+2 GRD" line the menu prints. Empty for a plain consumable.
func worn_summary() -> String:
	if worn.is_empty():
		return ""
	var parts: PackedStringArray = []
	for stat: String in worn:
		var v: int = worn[stat]
		parts.append("%s%d %s" % ["+" if v >= 0 else "", v, stat.to_upper()])
	return " ".join(parts)
