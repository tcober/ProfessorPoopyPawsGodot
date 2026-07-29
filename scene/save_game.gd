class_name SaveGame
extends Object

## Save and load a run. All static, no instance, no autoload — it is pure
## serialization over state that already lives on `Game` and `Party`.
##
## WHAT A SAVE IS: everything `Game.reset_story()` clears, plus the roster and
## the scene you were standing in. That correspondence is deliberate and worth
## keeping — `reset_story` is already the authoritative list of "what a run is",
## so a field added there and forgotten here shows up as a save that quietly
## loses something. The round-trip test in tools/save_probe.gd is what actually
## enforces it.
##
## JSON rather than ResourceSaver, for three reasons: a save that can be opened
## in a text editor is debuggable; `ResourceSaver` on a Resource with a script
## embeds a res:// script path, so renaming a file breaks old saves; and a
## malformed JSON parse returns an error instead of executing anything.
##
## Autoloads are reached by NODE PATH, never by identifier, so this file stays
## safe to `load()` from a `--script` tool (which compiles before autoloads are
## registered).

const SAVE_PATH := "user://save_1.json"
## Bumped whenever the shape below changes incompatibly. A save from a different
## version is REFUSED rather than half-read: a partially-applied save is a much
## worse bug than a missing one, because it looks like it worked.
const VERSION := 1


static func _game(tree: SceneTree) -> Node:
	return tree.root.get_node_or_null(^"Game")


static func _party(tree: SceneTree) -> Node:
	return tree.root.get_node_or_null(^"Party")


static func has_save() -> bool:
	return FileAccess.file_exists(SAVE_PATH)


static func delete() -> void:
	if has_save():
		DirAccess.remove_absolute(ProjectSettings.globalize_path(SAVE_PATH))


# ---- write ---------------------------------------------------------------------------

static func save(tree: SceneTree) -> bool:
	var game := _game(tree)
	var party := _party(tree)
	if game == null or party == null:
		return false

	var sheets := {}
	for id: StringName in game.get("sheets"):
		var s: CharacterSheet = game.get("sheets")[id]
		if s.neutral:
			continue                             # prologue bodies carry no state
		# gear keys are Item.Kind ints; JSON object keys must be strings, and
		# come back as strings, so they are normalised on both sides.
		var gear := {}
		for slot: int in s.gear:
			gear[str(slot)] = String(s.gear[slot])
		sheets[String(id)] = {
			"level": s.level,
			"exp": s.exp_total,
			"base": s.base.duplicate(),
			"gear": gear,
		}

	var inventory := {}
	for id: StringName in game.get("inventory"):
		inventory[String(id)] = game.get("inventory")[id]

	# The gun loadout is stored as compound KINDS, not as Compound resources:
	# every Compound in the game is rebuilt by Alchemy.make() from its kind, so
	# the kind is the only irreducible part and the rest is derived on load.
	var spares: Array = []
	for c in game.get("spares"):
		spares.append(int(c.kind))
	var loaded = game.get("loaded")

	var data := {
		"version": VERSION,
		"scene": tree.current_scene.scene_file_path if tree.current_scene else "",
		"flags": game.get("flags").keys(),
		"routers": {
			"overworld_spawn": game.get("overworld_spawn"),
			"town_spawn": game.get("town_spawn"),
			"interior_spawn": game.get("interior_spawn"),
			"town_thesis_phase": game.get("town_thesis_phase"),
			"bluff_phase": game.get("bluff_phase"),
			"library_phase": game.get("library_phase"),
			"hall_phase": game.get("hall_phase"),
		},
		"fuji_tome": String(game.get("fuji_tome")),
		"sheets": sheets,
		"inventory": inventory,
		"loadout": {
			"loaded": int(loaded.kind) if loaded else -1,
			"spares": spares,
			"ammo_left": game.get("ammo_left"),
		},
		"roster": Array(party.get("roster")).map(func(id): return String(id)),
		"leader": String(party.get("leader_id")),
	}

	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f == null:
		push_error("save failed: %s" % FileAccess.get_open_error())
		return false
	f.store_string(JSON.stringify(data, "\t"))
	f.close()
	return true


# ---- read ----------------------------------------------------------------------------

## Parse the save WITHOUT applying it — the title screen wants to show what is
## in it (who, what level, where) before committing to loading it.
static func peek() -> Dictionary:
	if not has_save():
		return {}
	var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if f == null:
		return {}
	var parsed = JSON.parse_string(f.get_as_text())
	f.close()
	if typeof(parsed) != TYPE_DICTIONARY:
		return {}
	if int(parsed.get("version", -1)) != VERSION:
		return {}                                # refuse, never half-read
	return parsed


## Apply a save to Game and Party and return the scene to change to, or "" if
## there was nothing usable. Does NOT change the scene itself: the caller owns
## that, because it has to be deferred out of whatever signal it came from.
static func load_into(tree: SceneTree) -> String:
	var data := peek()
	if data.is_empty():
		return ""
	var game := _game(tree)
	var party := _party(tree)
	if game == null or party == null:
		return ""

	# Start from a clean run, then apply — otherwise loading over a session in
	# progress ORs the two together, and a flag from the abandoned run survives
	# into the loaded one. (Exactly the hazard reset_story exists for.)
	game.call("reset_story")

	for f in data.get("flags", []):
		game.call("set_flag", String(f))
	for k: String in data.get("routers", {}):
		game.set(k, data["routers"][k])
	game.set("fuji_tome", StringName(data.get("fuji_tome", "")))

	var sheets := {}
	for id: String in data.get("sheets", {}):
		var row: Dictionary = data["sheets"][id]
		var s := CharacterSheet.make(StringName(id), int(row.get("level", 1)))
		s.exp_total = int(row.get("exp", 0))
		StatBlock.apply_growth(s)
		# Trust the table over the file for base stats: growth is authored data,
		# so a save written before a balance pass should pick up the new numbers
		# rather than pin a character to the old ones forever.
		for slot_s: String in row.get("gear", {}):
			s.gear[int(slot_s)] = StringName(row["gear"][slot_s])
		sheets[StringName(id)] = s
	game.set("sheets", sheets)

	var inv := {}
	for id: String in data.get("inventory", {}):
		inv[StringName(id)] = int(data["inventory"][id])
	game.set("inventory", inv)

	var loadout: Dictionary = data.get("loadout", {})
	var loaded_kind := int(loadout.get("loaded", -1))
	game.set("loaded", Alchemy.make(loaded_kind) if loaded_kind >= 0 else null)
	var spares: Array[Compound] = []
	for k in loadout.get("spares", []):
		spares.append(Alchemy.make(int(k)))
	game.set("spares", spares)
	game.set("ammo_left", int(loadout.get("ammo_left", 0)))

	var roster: Array[StringName] = []
	for id in data.get("roster", []):
		roster.append(StringName(id))
	if not roster.is_empty():
		party.call("set_roster", roster, StringName(data.get("leader", roster[0])))

	var scene := String(data.get("scene", ""))
	return scene if ResourceLoader.exists(scene) else ""


## A one-line "LANTERNWOOD - FUJI LV4" for the title screen's CONTINUE row.
static func summary() -> String:
	var data := peek()
	if data.is_empty():
		return ""
	var where := String(data.get("scene", "")).get_file().get_basename().replace("_", " ").to_upper()
	var best := ""
	var best_level := 0
	for id: String in data.get("sheets", {}):
		var lv := int(data["sheets"][id].get("level", 1))
		if lv >= best_level:
			best_level = lv
			best = id.to_upper()
	if best == "":
		return where
	return "%s - %s LV%d" % [where, best, best_level]
