class_name Items
extends Object

## The item table, and the only place an [Item] is ever constructed.
##
## Same shape as `Alchemy`: an Object with nothing but statics, a registry built
## once, and pure lookups. Nothing anywhere else calls `Item.new()` — that is
## what keeps every balance number in this file instead of scattered across the
## scenes that happen to hand one out.
##
## Naming is in-world: this is a steampunk-medieval alchemist's world, so gear is
## wool and oilskin and brass, never "leather armour +1".

const TONIC := &"tonic"
const DRAUGHT := &"draught"

static var _table: Dictionary = {}


static func _def(id: StringName, name: String, kind: Item.Kind, desc: String,
		heal := 0, worn := {}, users: Array[StringName] = [],
		tint := Color(0.86, 0.86, 0.92)) -> Item:
	var it := Item.new()
	it.id = id
	it.display_name = name
	it.kind = kind
	it.description = desc
	it.heal = heal
	it.worn = worn
	it.users = users
	it.tint = tint
	return it


static func _build() -> void:
	var defs: Array[Item] = [
		# ---- consumables ----------------------------------------------------------
		_def(TONIC, "FIELD TONIC", Item.Kind.CONSUMABLE,
			"Restores two hearts. Bitter.", 4, {}, [],
			Color(0.42, 0.86, 0.52)),
		_def(DRAUGHT, "GREEN DRAUGHT", Item.Kind.CONSUMABLE,
			"Restores four hearts.", 8, {}, [],
			Color(0.34, 0.78, 0.46)),

		# ---- weapons. A weapon grants stats and a name; it NEVER changes a
		# character's kit (see the note in item.gd). Fuji fights with books
		# because she is a librarian, so hers are books.
		_def(&"primer", "FIELD PRIMER", Item.Kind.WEAPON,
			"Thin, but the spine holds.", 0, {"mig": 1}, [&"fuji"],
			Color(0.72, 0.56, 0.86)),
		# THE THREE SHELF BOOKS — what she can take off her own stacks on the
		# night she decides to go (Act 1 beat 3). One per shelf, so the choice is
		# made by WALKING somewhere rather than by scrolling a list, and the one
		# she picks is her weapon for the rest of the game. They are deliberately
		# close in power: this is a character question, not a build question.
		_def(&"husbandry", "THE COMPLEAT HUSBANDRY", Item.Kind.WEAPON,
			"Shelf three. It already saved her once.", 0, {"mig": 1, "foc": 1},
			[&"fuji"], Color(0.62, 0.78, 0.48)),
		_def(&"bound_ledger", "LANTERNWOOD GRAIN TITHES", Item.Kind.WEAPON,
			"Shelf six. Nine hundred pages of barley.", 0, {"mig": 2, "grd": 1},
			[&"fuji"], Color(0.86, 0.68, 0.34)),
		_def(&"principles", "PRINCIPLES OF ENCHANTMENT", Item.Kind.WEAPON,
			"Shelf nine. Every word of it useless now.", 0, {"mig": 1, "foc": 2},
			[&"fuji"], Color(0.68, 0.56, 0.88)),
		_def(&"focuser", "BRASS FOCUSER", Item.Kind.WEAPON,
			"A tighter beam. Same recoil.", 0, {"mig": 2}, [&"basil"],
			Color(0.86, 0.68, 0.34)),

		# ---- hats -----------------------------------------------------------------
		_def(&"earflaps", "WOOL EARFLAPS", Item.Kind.HEAD,
			"Lanternwood standard issue.", 0, {"vit": 1}, [],
			Color(0.78, 0.62, 0.48)),
		_def(&"readers", "READING GLASSES", Item.Kind.HEAD,
			"Small print, small mercies.", 0, {"foc": 2}, [],
			Color(0.66, 0.78, 0.86)),

		# ---- shirts ---------------------------------------------------------------
		_def(&"quilted_coat", "QUILTED COAT", Item.Kind.BODY,
			"Warm. Faintly smells of woodsmoke.", 0, {"vit": 1, "grd": 1}, [],
			Color(0.54, 0.46, 0.72)),
		_def(&"oilskin", "OILSKIN APRON", Item.Kind.BODY,
			"Sheds slime. Mostly.", 0, {"grd": 3}, [],
			Color(0.46, 0.56, 0.44)),

		# ---- charms ---------------------------------------------------------------
		_def(&"lucky_nib", "LUCKY NIB", Item.Kind.RELIC,
			"It has never once run dry.", 0, {"mig": 1, "foc": 1}, [],
			Color(0.86, 0.78, 0.42)),
		# The ONLY source of SPD in the game, and deliberately small. Level growth
		# grants none at all: the AI brains' hysteresis bands are tuned to the
		# shipped 150px/s, so anything that moves a member's speed has to be
		# re-checked against tools/party_probe.gd. See StatBlock.SPD_CLAMP.
		_def(&"snowshoes", "SNOWSHOES", Item.Kind.RELIC,
			"Stops the drifts arguing back.", 0, {"spd": 2}, [],
			Color(0.82, 0.88, 0.96)),
	]
	for it in defs:
		assert(not _table.has(it.id), "duplicate item id %s" % it.id)
		_validate(it)
		_table[it.id] = it


static func _validate(it: Item) -> void:
	for stat: String in it.worn:
		assert(CharacterSheet.STATS.has(stat),
			"item %s grants unknown stat %s" % [it.id, stat])
	assert(it.kind != Item.Kind.CONSUMABLE or it.worn.is_empty(),
		"item %s is a consumable but grants worn stats" % it.id)
	assert(it.kind == Item.Kind.CONSUMABLE or it.heal == 0,
		"item %s is gear but carries a heal payload" % it.id)


static func _ensure() -> void:
	if _table.is_empty():
		_build()


## Null for an unknown or empty id — callers treat null as "nothing equipped",
## which is what an empty slot already means, so a stale save id degrades to a
## bare slot instead of throwing.
static func get_item(id: StringName) -> Item:
	if id == &"":
		return null
	_ensure()
	return _table.get(id)


static func all() -> Array[Item]:
	_ensure()
	var out: Array[Item] = []
	for id: StringName in _table:
		out.append(_table[id])
	return out


## Every item that can go in `slot`, filtered to who may hold it.
static func for_slot(slot: Item.Kind, member_id: StringName) -> Array[Item]:
	var out: Array[Item] = []
	for it in all():
		if it.kind == slot and it.usable_by(member_id):
			out.append(it)
	return out
