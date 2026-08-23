extends Node

## Autoloaded as `PartyMenu`: press I (or START) anywhere to open the party
## screen — levels and stats, the four equipment slots, and the satchel.
##
## THREE PANES, ONE SCREEN, 384x216: the roster on the left, the selected
## member's stats in the middle, their gear on the right. Same contract as the
## mixing bench — always show what you are about to get and what you are about
## to lose before taking anything.
##
## The chrome (CanvasLayer at 100, PROCESS_MODE_ALWAYS, the swallow timer, the
## backdrop, the pixel font, the selection bar) comes from scene/overlay.gd,
## shared with DevMenu and MixMenu. This is the project's THIRD get_tree().paused
## user, so it must be listed in Overlay.MODALS — otherwise it and the bench
## would happily open on top of each other and whichever closed first would
## unpause the tree under the other.
##
## Input is POLLED in _process, never _input: tools/shot.gd's synthesized presses
## exist only in the polled action state, so an _input-driven menu is untestable.

const ROW_H := Overlay.ROW_H
const BRASS := Overlay.BRASS
const DIM := Overlay.DIM
const TEXT := Overlay.TEXT
const BAD := Overlay.BAD

const TOP := 26
const ROSTER_X := 10
const ROSTER_W := 104
const STATS_X := 122
const STATS_W := 116
const GEAR_X := 244
const GEAR_W := 130
## Two lines per roster entry (name+level, then hearts) — a member is a block,
## not a row, so the cursor bar has to be two rows tall over that pane.
const ROSTER_STRIDE := 20

## Cursor modes. Cancel walks back down this list; from MEMBER it closes.
enum { M_MEMBER, M_SLOT, M_PICK, M_ITEM }

## The gear pane lists the four slots, then a row that opens the satchel, then
## SAVE. So the cursor runs 0..5 and only 0..3 are slots.
const ITEMS_ROW := 4
const SAVE_ROW := 5

var _ui: CanvasLayer
var _bar: ColorRect
var _mode := M_MEMBER
var _member := 0
var _slot := 0
var _choice := 0
var _swallow := 0.0
var _note := ""                      # transient feedback ("NOTHING TO EQUIP")

var _roster_rows: Array[Label] = []
var _stat_rows: Array[Label] = []
var _gear_rows: Array[Label] = []
var _choice_rows: Array[Label] = []
var _title: Label
var _desc: Label
var _hint: Label

## Whatever the right pane is currently listing, rebuilt on every _sync: either
## the equip candidates for the focused slot or the satchel's consumables.
var _candidates: Array = []


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


## The modal contract's half of the bargain — Overlay.any_open() asks every
## entry in Overlay.MODALS this, and asserts the method exists.
func is_open() -> bool:
	return _ui != null


## IS THERE A PARTY TO OPEN A PARTY MENU ON? This autoload processes ALWAYS and in
## every scene, so `I` used to open the menu on the TITLE SCREEN — where the roster
## has never been spawned, every sheet is empty, and `SAVE GAME` on row 5 wrote a
## perfectly valid save whose `scene` was res://scene/title.tscn. One keypress on the
## boot screen overwrote the player's run with a save that loads straight back to the
## boot screen, and the summary line under CONTINUE then said "TITLE - LV1".
##
## The predicate is the party itself rather than a scene whitelist: `Party.members` is
## filled by Party.spawn() and emptied by set_roster(), so it is exactly "is there a
## body in the world right now", which is also the only state this menu can describe.
func _has_party() -> bool:
	for m in Party.members:
		if is_instance_valid(m):
			return true
	return false


func _process(delta: float) -> void:
	if _ui == null:
		if Input.is_action_just_pressed("menu") \
				and not Overlay.any_open(get_tree(), self) \
				and _has_party():
			_open()
		return

	if _swallow > 0.0:
		_swallow -= delta
		return

	if Input.is_action_just_pressed("menu") or Input.is_action_just_pressed("ui_cancel"):
		_back()
	elif Input.is_action_just_pressed("move_down") or Input.is_action_just_pressed("ui_down"):
		_step(1)
	elif Input.is_action_just_pressed("move_up") or Input.is_action_just_pressed("ui_up"):
		_step(-1)
	elif Input.is_action_just_pressed("attack") \
			or Input.is_action_just_pressed("interact") \
			or Input.is_action_just_pressed("ui_accept"):
		_accept()


# --- open / close --------------------------------------------------------------------

func _open() -> void:
	_mode = M_MEMBER
	_member = 0
	_slot = 0
	_choice = 0
	_note = ""
	_build()
	_swallow = Overlay.SWALLOW
	Sfx.ui_open()
	get_tree().paused = true


func _close() -> void:
	get_tree().paused = false
	if is_instance_valid(_ui):
		_ui.queue_free()
	_ui = null
	_roster_rows.clear()
	_stat_rows.clear()
	_gear_rows.clear()
	_choice_rows.clear()


func _back() -> void:
	_note = ""
	Sfx.ui_back()
	match _mode:
		M_MEMBER:
			_close()
		M_SLOT:
			_mode = M_MEMBER
			_sync()
		_:
			_mode = M_SLOT
			_choice = 0
			_sync()


# --- the roster ----------------------------------------------------------------------

## Ids only. The menu must work in a scene with no bodies in it at all (a
## cutscene, the title), so nothing here may assume Party.members is populated —
## sheets live on Game precisely because bodies do not survive a door.
func _roster() -> Array:
	var party := get_node_or_null(^"/root/Party")
	if party == null:
		return []
	var out: Array = []
	for id: StringName in party.roster:
		if not Game.sheet(id).neutral:
			out.append(id)
	return out


func _member_id() -> StringName:
	var r := _roster()
	if r.is_empty():
		return &""
	return r[clampi(_member, 0, r.size() - 1)]


## The live body for a member, or null if this scene has none. Used for HP
## readouts and for actually applying a potion.
func _body(id: StringName) -> Node:
	for m in get_tree().get_nodes_in_group("party"):
		if m.get("member_id") == id:
			return m
	return null


# --- cursor --------------------------------------------------------------------------

func _row_count() -> int:
	match _mode:
		M_MEMBER:
			return _roster().size()
		M_SLOT:
			return SAVE_ROW + 1
		_:
			return maxi(_candidates.size(), 1)


func _step(dir: int) -> void:
	var n := _row_count()
	if n <= 0:
		return
	_note = ""
	Sfx.ui_move()
	match _mode:
		M_MEMBER:
			_member = wrapi(_member + dir, 0, n)
		M_SLOT:
			_slot = wrapi(_slot + dir, 0, n)
		_:
			_choice = wrapi(_choice + dir, 0, n)
	_sync()


func _accept() -> void:
	_note = ""
	match _mode:
		M_MEMBER:
			if _roster().is_empty():
				return
			Sfx.ui_accept()
			_mode = M_SLOT
			_slot = 0
		M_SLOT:
			if _slot == SAVE_ROW:
				if SaveGame.save(get_tree()):
					_note = "SAVED."
					Sfx.ui_chime()
				else:
					_note = "COULD NOT WRITE THE SAVE."
					Sfx.ui_refuse()
			elif _slot == ITEMS_ROW:
				Sfx.ui_accept()
				_mode = M_ITEM
			else:
				Sfx.ui_accept()
				_mode = M_PICK
			_choice = 0
		M_PICK:
			_equip()
			Sfx.ui_accept()
		M_ITEM:
			if _use():
				Sfx.ui_accept()
			else:
				Sfx.ui_refuse()
	_sync()


# --- the two verbs -------------------------------------------------------------------

## Candidate 0 is always "(none)" — unequipping has to be reachable, and a
## separate key for it would be a second thing to teach.
func _equip() -> void:
	var id := _member_id()
	if id == &"":
		return
	var sheet := Game.sheet(id)
	var slot: int = Item.SLOTS[_slot]
	var pick: Item = _candidates[_choice] if _choice < _candidates.size() else null

	var removed := sheet.equip(slot, pick.id if pick else &"")
	# The satchel is the source of truth for "do I own this": equipping MOVES an
	# item out of it and un-equipping puts one back. Without that, one tonic-belt
	# could be worn by both cats at once.
	if pick:
		Game.take_item(pick.id)
	if removed:
		Game.add_item(removed.id)
	_refresh_body(id)
	_mode = M_SLOT


## True when the item was actually drunk — _accept keys the accept/refuse
## sound off it, so a "NOT HERE" note can never arrive with a happy blip.
func _use() -> bool:
	var id := _member_id()
	if id == &"" or _candidates.is_empty():
		return false
	var it: Item = _candidates[_choice]
	var body := _body(id)
	if body == null:
		_note = "NOT HERE TO DRINK IT."
		return false
	var health = body.get("health")
	if health == null:
		return false
	if health.current_health >= health.max_health:
		_note = "%s IS ALREADY WELL." % _name_of(id)
		return false
	if not Game.take_item(it.id):
		return false
	health.current_health = mini(health.current_health + it.heal, health.max_health)
	health.health_changed.emit(health.current_health, health.max_health)
	_note = "%s DRINKS THE %s." % [_name_of(id), it.display_name]
	if Game.item_count(it.id) <= 0:
		_choice = maxi(_choice - 1, 0)
	return true


## Re-apply a sheet to the live body after gear changed, so a +VIT hat raises
## max HP the moment it is worn rather than at the next door. Hearts already
## filled are kept; the new headroom arrives empty, which is the honest read.
func _refresh_body(id: StringName) -> void:
	var body := _body(id)
	if body == null:
		return
	var health = body.get("health")
	if health == null:
		return
	var base: int = body.get("base_max_health")
	var sheet := Game.sheet(id)
	health.max_health = base + sheet.stat("vit")
	health.current_health = mini(health.current_health, health.max_health)
	health.health_changed.emit(health.current_health, health.max_health)


# --- the overlay ---------------------------------------------------------------------

func _build() -> void:
	_ui = Overlay.build_layer(self)
	_title = Overlay.label(_ui, "PARTY", ROSTER_X, 8, BRASS, 200)
	Overlay.label(_ui, "STATS", STATS_X, 14, DIM, STATS_W)
	Overlay.label(_ui, "EQUIPMENT", GEAR_X, 14, DIM, GEAR_W)

	# The bar is added BEFORE the rows: a CanvasLayer draws in tree order, so a
	# bar added afterwards would paint over its own row's text.
	_bar = Overlay.bar(_ui, Vector2(ROSTER_W + 4, ROW_H))

	for i in 4:
		_roster_rows.append(Overlay.label(_ui, "", ROSTER_X, TOP + i * ROSTER_STRIDE,
			TEXT, ROSTER_W))
		_roster_rows.append(Overlay.label(_ui, "", ROSTER_X, TOP + i * ROSTER_STRIDE + ROW_H,
			DIM, ROSTER_W))
	for i in CharacterSheet.STATS.size() + 2:          # five stats + HP + EXP
		_stat_rows.append(Overlay.label(_ui, "", STATS_X, TOP + i * ROW_H, TEXT, STATS_W))
	for i in SAVE_ROW + 1:
		_gear_rows.append(Overlay.label(_ui, "", GEAR_X, TOP + i * ROW_H, TEXT, GEAR_W))
	for i in 6:
		_choice_rows.append(Overlay.label(_ui, "", GEAR_X, TOP + (SAVE_ROW + 2 + i) * ROW_H,
			TEXT, GEAR_W))

	_desc = Overlay.label(_ui, "", ROSTER_X, 182, DIM, 364)
	_hint = Overlay.label(_ui, "", ROSTER_X, 196, DIM, 364)
	_sync()


## Redraw the whole panel every input frame. At this row count that is far
## cheaper than tracking dirty state, and it means a level-up or a pickup landing
## while the menu is open can never leave a stale row on screen.
func _sync() -> void:
	if _ui == null:
		return
	var roster := _roster()
	_member = clampi(_member, 0, maxi(roster.size() - 1, 0))
	var id := _member_id()
	var sheet := Game.sheet(id) if id != &"" else null

	_draw_roster(roster)
	_draw_stats(id, sheet)
	_draw_gear(sheet)
	_rebuild_candidates(id, sheet)
	_draw_candidates()
	_place_bar(roster)
	_draw_footer()


func _draw_roster(roster: Array) -> void:
	for i in _roster_rows.size():
		_roster_rows[i].text = ""
	for i in roster.size():
		if i * 2 + 1 >= _roster_rows.size():
			break
		var mid: StringName = roster[i]
		var s := Game.sheet(mid)
		_roster_rows[i * 2].text = "%-8s %s" % [_name_of(mid), s.label()]
		_roster_rows[i * 2].add_theme_color_override("font_color",
			BRASS if i == _member else TEXT)
		var body := _body(mid)
		if body:
			var health = body.get("health")
			_roster_rows[i * 2 + 1].text = "  HP %d/%d" % [health.current_health, health.max_health]
		else:
			_roster_rows[i * 2 + 1].text = "  -"


func _draw_stats(id: StringName, sheet: CharacterSheet) -> void:
	for l in _stat_rows:
		l.text = ""
	if sheet == null:
		return
	for i in CharacterSheet.STATS.size():
		var key: String = CharacterSheet.STATS[i]
		var base: int = sheet.base.get(key, 0)
		var total := sheet.stat(key)
		var line := "%-4s %2d" % [key.to_upper(), total]
		# Show the gear's contribution separately: a menu that only prints the
		# total makes it impossible to tell what the hat is doing.
		if total != base:
			line += "  (%+d)" % (total - base)
		_stat_rows[i].text = line
	var n := CharacterSheet.STATS.size()
	var body := _body(id)
	if body:
		var health = body.get("health")
		_stat_rows[n].text = "HP  %2d/%d" % [health.current_health, health.max_health]
	var prog := StatBlock.level_progress(sheet)
	_stat_rows[n + 1].text = ("EXP  MAX" if StatBlock.exp_to_next(sheet.level) <= 0
		else "EXP %d/%d" % [prog.x, prog.y])


func _draw_gear(sheet: CharacterSheet) -> void:
	for l in _gear_rows:
		l.text = ""
	if sheet == null:
		return
	for i in Item.SLOTS.size():
		var slot: int = Item.SLOTS[i]
		var worn := sheet.equipped(slot)
		_gear_rows[i].text = "%-7s %s" % [Item.SLOT_NAMES[slot],
			worn.display_name if worn else "-"]
		# While the candidate list is up the selection bar has moved off this
		# pane, so the row being changed marks itself — otherwise the player is
		# choosing a hat with nothing on screen saying "hat".
		var editing := _mode == M_PICK and i == _slot
		_gear_rows[i].add_theme_color_override("font_color",
			BRASS if editing else (worn.tint if worn else DIM))
	_gear_rows[ITEMS_ROW].text = "SATCHEL..."
	_gear_rows[ITEMS_ROW].add_theme_color_override("font_color", TEXT)
	_gear_rows[SAVE_ROW].text = "SAVE GAME"
	_gear_rows[SAVE_ROW].add_theme_color_override("font_color", BRASS)


func _rebuild_candidates(id: StringName, sheet: CharacterSheet) -> void:
	_candidates = []
	if sheet == null:
		return
	if _mode == M_PICK:
		_candidates.append(null)                       # "(none)" — unequip
		var slot: int = Item.SLOTS[_slot]
		for entry in Game.satchel():
			var it: Item = entry[0]
			if it.kind == slot and it.usable_by(id):
				_candidates.append(it)
	elif _mode == M_ITEM:
		for entry in Game.satchel():
			var it: Item = entry[0]
			if it.kind == Item.Kind.CONSUMABLE:
				_candidates.append(it)
	_choice = clampi(_choice, 0, maxi(_candidates.size() - 1, 0))


func _draw_candidates() -> void:
	for l in _choice_rows:
		l.text = ""
	if _mode != M_PICK and _mode != M_ITEM:
		return
	if _candidates.is_empty():
		_choice_rows[0].text = "(NOTHING)"
		_choice_rows[0].add_theme_color_override("font_color", DIM)
		return
	for i in mini(_candidates.size(), _choice_rows.size()):
		var it: Item = _candidates[i]
		if it == null:
			_choice_rows[i].text = "(NONE)"
			_choice_rows[i].add_theme_color_override("font_color", DIM)
			continue
		var n := Game.item_count(it.id)
		_choice_rows[i].text = ("%s x%d" % [it.display_name, n]) if n > 1 else it.display_name
		_choice_rows[i].add_theme_color_override("font_color", it.tint)


func _place_bar(roster: Array) -> void:
	if _bar == null:
		return
	match _mode:
		M_MEMBER:
			_bar.visible = not roster.is_empty()
			_bar.size = Vector2(ROSTER_W + 4, ROW_H * 2)
			_bar.position = Vector2(ROSTER_X - 2, TOP + _member * ROSTER_STRIDE)
		M_SLOT:
			_bar.visible = true
			_bar.size = Vector2(GEAR_W + 4, ROW_H)
			_bar.position = Vector2(GEAR_X - 2, TOP + _slot * ROW_H)
		_:
			_bar.visible = not _candidates.is_empty()
			_bar.size = Vector2(GEAR_W + 4, ROW_H)
			_bar.position = Vector2(GEAR_X - 2,
				TOP + (SAVE_ROW + 2 + mini(_choice, _choice_rows.size() - 1)) * ROW_H)


func _draw_footer() -> void:
	var focus: Item = null
	if (_mode == M_PICK or _mode == M_ITEM) and _choice < _candidates.size():
		focus = _candidates[_choice]
	elif _mode == M_SLOT and _slot < Item.SLOTS.size():
		var sheet := Game.sheet(_member_id())
		focus = sheet.equipped(Item.SLOTS[_slot])

	if _note != "":
		_desc.text = _note
		_desc.add_theme_color_override("font_color", BRASS)
	elif focus:
		var worn := focus.worn_summary()
		_desc.text = focus.description + ("   " + worn if worn != "" else "")
		_desc.add_theme_color_override("font_color", DIM)
	else:
		_desc.text = ""

	match _mode:
		M_MEMBER:
			_hint.text = "UP/DOWN PICK A CAT   SPACE OPEN   I CLOSE"
		M_SLOT:
			_hint.text = "SPACE CHANGE / SAVE   I BACK"
		M_PICK:
			_hint.text = "SPACE EQUIP   I BACK"
		M_ITEM:
			_hint.text = "SPACE USE   I BACK"


## Display names live here rather than on the sheet: the sheet is save data and
## should not carry UI strings, and there are exactly two cats.
func _name_of(id: StringName) -> String:
	match id:
		&"basil":
			return "BASIL"
		&"fuji":
			return "FUJI"
	return String(id).to_upper()
