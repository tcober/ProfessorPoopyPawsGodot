extends Node

## Autoloaded as `Game`: state that survives scene changes. `overworld_spawn` names
## the OverworldLocation id the travel player appears at when the overworld loads.
## `town_spawn` and `interior_spawn` are the zone analogs: the map anchor the next
## town/interior scene should spawn at. Both are READ AND CLEARED ("" = use the
## scene's default), so a stale value can never teleport a later entry.
## (`town_spawn`: "home" = below Basil's door in Alembic Town, "library" =
## Fuji's library door in Lanternwood (the Ebb-night arrival), "" = the
## town's south gate.)

var overworld_spawn: String = "town"
var town_spawn: String = ""
var interior_spawn: String = ""

## Story flags — set-once booleans that survive scene changes (no save system
## yet, so a run's story state lives and dies with the process). Prologue
## flags in use: prologue_festival_done, prologue_gate_open, prologue_done.
var flags: Dictionary = {}

## Which phase the thesis-day town scene (scene/town_thesis.gd) plays on entry
## ("plant" | "dash" | "steps"), read-and-cleared like the spawn routers.
## "" = the scene's default (plant).
var town_thesis_phase: String = ""

## Which beat the sunset bluff (scene/bluff.gd) plays on entry — the SAME
## headland hosts Prologue A's whirligig meet, the romance and both thesis-day
## calls, on purpose (the place their love began is where the bad news finds
## him). Read-and-cleared; "" = "romance". ("meet" | "romance" | "call1" | "call2")
var bluff_phase: String = ""

## Basil's gun loadout: what is poured into the gun right now, and the spare
## beakers in his coat. Lives HERE rather than on the body because Party.spawn()
## rebuilds every member from scratch on each scene load — anything held on the
## Player instance (ammo, HP) resets at every door. The compound you mixed has
## to outlive the walk to the meadow, so it lives with the rest of the
## run-scoped state. Cleared by reset_story() like everything else.
var loaded: Compound = null
var spares: Array[Compound] = []
var ammo_left: int = 0

## Which beat the Lanternwood library (scene/library.gd) plays on entry —
## Fuji's little reading room in her snow-town. "ebb" (the default for now)
## = the Ebb-night wand-coffee beat, her first appearance; Act 1's playable
## research phase will reuse the same room. Read-and-cleared.
var library_phase: String = ""

## Which beat the Academy hall (scene/hall.gd) plays on entry. "" = Prologue B's
## naming, the default this room was built for; "recital" = Prologue A's kid
## magic recital, the same stage twenty years earlier. Read-and-cleared.
## Prologue B's beat carries state = {} in the chapter table and RELIES on
## reset_story() blanking this — see the note there.
var hall_phase: String = ""

## Which tome Fuji chose in her own library on the night she decided to go
## (Act 1 beat 3, "THE KIT"). Cosmetic in stats and enormous in meaning: it is
## the book she fights the rest of the game with. "" until she picks.
var fuji_tome: StringName = &""

# ---- the RPG layer (2026-07-28) ---------------------------------------------------
## member id -> CharacterSheet. Levels, EXP, the five stats, and the four
## equipped items. It lives HERE for exactly the reason the gun loadout does:
## Party.spawn() rebuilds every member from its PackedScene at every single
## door, so anything held on the body is gone by the next scene.
var sheets: Dictionary = {}

## item id -> count. One flat satchel shared by the whole party, FFVI-style —
## there is no per-character bag and there should not be, because "which cat is
## carrying the potion" is a chore, not a decision.
var inventory: Dictionary = {}

## Emitted when a member levels. Scenes listen and toast it however they can:
## the HUD only exists in combat zones, but every scene has a Theater.
signal levelled(member_id: StringName, level: int)
## Emitted whenever the satchel changes, so an open menu can redraw.
signal inventory_changed


func flag(flag_name: String) -> bool:
	return flags.get(flag_name, false)


func set_flag(flag_name: String) -> void:
	flags[flag_name] = true


# ---- sheets ------------------------------------------------------------------------
## The sheet for a member, created on first ask. Bodies with no growth table
## (kid_basil, basil_student — the prologue is safe and has no combat) get a
## NEUTRAL sheet rather than an assert, so every caller can ask unconditionally.
func sheet(member_id: StringName) -> CharacterSheet:
	if not sheets.has(member_id):
		sheets[member_id] = StatBlock.fresh(member_id)
	return sheets[member_id]


## Award EXP to EVERY member of the current roster — no split, no bench penalty.
## FFVI's benched-character problem is a save-file chore rather than a design,
## and a two-member party has nothing to gain from it.
func grant_kill(exp_value: int) -> void:
	if exp_value <= 0:
		return
	var party := get_node_or_null(^"/root/Party")
	var roster: Array = party.roster if party else []
	for id: StringName in roster:
		var s := sheet(id)
		if StatBlock.grant_exp(s, exp_value) > 0:
			levelled.emit(id, s.level)


# ---- the satchel -------------------------------------------------------------------
func add_item(item_id: StringName, count: int = 1) -> void:
	if item_id == &"" or count <= 0:
		return
	inventory[item_id] = int(inventory.get(item_id, 0)) + count
	inventory_changed.emit()


## Returns false if there were none, so callers never have to pre-check.
func take_item(item_id: StringName, count: int = 1) -> bool:
	var have := int(inventory.get(item_id, 0))
	if have < count:
		return false
	if have == count:
		inventory.erase(item_id)
	else:
		inventory[item_id] = have - count
	inventory_changed.emit()
	return true


func item_count(item_id: StringName) -> int:
	return int(inventory.get(item_id, 0))


## Satchel contents as (Item, count) pairs, gear first then consumables, each
## group alphabetical — a stable order, so the menu cursor doesn't jump when a
## count changes.
func satchel() -> Array:
	var out: Array = []
	for id: StringName in inventory:
		var it := Items.get_item(id)
		if it:
			out.append([it, inventory[id]])
	out.sort_custom(func(a, b):
		if a[0].kind != b[0].kind:
			return a[0].kind > b[0].kind
		return a[0].display_name < b[0].display_name)
	return out


## Wipe story state back to a fresh boot. set_flag() is one-way (there is no
## unset), so the dev chapter selector calls this before staging a beat —
## otherwise a BACKWARDS jump carries a later chapter's flags into an earlier
## scene and mis-dresses it (entering town_fest with prologue_festival_done
## already set skips the fountain cutscene you came to look at).
func reset_story() -> void:
	flags.clear()
	# "town", not "" — the declared default. overworld.gd matches this against
	# location ids and silently strands the chibi at player_start on no match.
	overworld_spawn = "town"
	town_spawn = ""
	interior_spawn = ""
	town_thesis_phase = ""
	bluff_phase = ""
	library_phase = ""
	hall_phase = ""
	# Blank, not "a fresh green beaker": the Player fills these on _ready when
	# it finds them empty, so a backwards chapter jump can't carry a late-game
	# plasma decoction into a scene that predates the gun.
	loaded = null
	spares = []
	ammo_left = 0
	fuji_tome = &""
	# Same rule as the loadout, and the same reason: a BACKWARDS chapter jump
	# must not carry a level-18 Fuji in a brass-bound ledger into a scene set
	# twenty years before she owned either.
	sheets.clear()
	inventory.clear()
