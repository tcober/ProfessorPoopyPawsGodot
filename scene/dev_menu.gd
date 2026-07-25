extends Node

## Autoloaded as `DevMenu`: press 0 ANYWHERE — title, cutscene, mid-meadow — to
## open the dev chapter selector and drop into any story beat with the right
## roster, phase, spawn anchor and flags already staged. The beat table lives in
## scene/chapters.gd; this file is the overlay and the state applier.
##
## Replaces the old "skip to the sandbox" hatch as the way around replaying the
## prologue (prologue_open's ESC still works, untouched).
##
## DEV ONLY: the whole thing is behind OS.is_debug_build(), so an exported build
## never builds the overlay and never polls the key.
##
## The tree is PAUSED while the menu is up (the project's first use of
## get_tree().paused — nothing else sets it). That is what stops the player body
## walking and the dialog box eating presses behind the overlay; cutscenes are
## coroutines awaiting timers/tweens, which pause and resume cleanly. This node
## and its overlay run PROCESS_MODE_ALWAYS so they keep going while paused.
##
## Input is POLLED in _process, never _input — the project-wide rule, because
## tools/shot.gd's synthesized presses exist only in the polled action state and
## never as InputEvents. `chapter_select` is a real InputMap action (key 0) for
## the same reason: a raw Input.is_key_pressed(KEY_0) would be undrivable.
##
## The overlay is built in code rather than hand-authored as a .tscn — the rows
## are generated from the table anyway, and it keeps the full-rect anchor idiom
## (anchors_preset alone does nothing at runtime) in one place.

const Chapters = preload("res://scene/chapters.gd")
const FONT = preload("res://assets/font/pixel_font.fnt")

const LAYER := 100                 # above dialog 20, theater 15, scene UI 10
const ROWS_PER_COL := 18           # 18 rows * ROW_H fits under 216 with margins
const ROW_H := 10                  # the font's lineHeight
const TOP := 20
const COL_X: Array[int] = [8, 196]
const COL_W := 180                 # ~30 chars at the 6px monospace advance

## The press that OPENS the menu must not also be read as a pick on the same
## frame — dialog_box.gd's SWALLOW_MS trick, in seconds.
const SWALLOW := 0.14

const BG := Color(0.055, 0.04, 0.115, 0.94)      # the dialog panel's night blue
const BRASS := Color(0.91, 0.74, 0.38)           # its lit bevel
const HILITE := Color(0.42, 0.28, 0.14)          # its shadow bevel
const GROUP_COL := Color(0.62, 0.56, 0.70)
const BEAT_COL := Color(0.95, 0.94, 0.97)

var _ui: CanvasLayer
var _bar: ColorRect
var _items: Array[Dictionary] = []    # {beat, label, selectable, col, row}
var _cursor := 0
var _swallow := 0.0


func _ready() -> void:
	if not OS.is_debug_build():
		set_process(false)
		return
	process_mode = Node.PROCESS_MODE_ALWAYS


func _process(delta: float) -> void:
	if _ui == null:
		if Input.is_action_just_pressed("chapter_select"):
			_open()
		return

	if _swallow > 0.0:
		_swallow -= delta
		return

	# 0 toggles. Deliberately NOT ui_cancel: autoloads process before the
	# current scene, so unpausing on ESC would hand the same still-pressed ESC
	# to prologue_open's skip in that very frame.
	if Input.is_action_just_pressed("chapter_select"):
		_close()
		return

	if Input.is_action_just_pressed("move_down") or Input.is_action_just_pressed("ui_down"):
		_step(1)
	elif Input.is_action_just_pressed("move_up") or Input.is_action_just_pressed("ui_up"):
		_step(-1)
	elif Input.is_action_just_pressed("move_right") or Input.is_action_just_pressed("ui_right"):
		_jump_column()
	elif Input.is_action_just_pressed("move_left") or Input.is_action_just_pressed("ui_left"):
		_jump_column()
	elif Input.is_action_just_pressed("attack") \
			or Input.is_action_just_pressed("interact") \
			or Input.is_action_just_pressed("ui_accept"):
		_launch(_items[_cursor]["beat"])


# --- open / close ------------------------------------------------------------

func _open() -> void:
	_build()
	_swallow = SWALLOW
	get_tree().paused = true


func _close() -> void:
	get_tree().paused = false
	if is_instance_valid(_ui):
		_ui.queue_free()
	_ui = null
	_items.clear()


func _launch(beat: Dictionary) -> void:
	_close()
	# reset first: set_flag is one-way, so a BACKWARDS jump would otherwise
	# carry a later chapter's flags into an earlier scene
	Game.reset_story()
	for f: String in beat["flags"]:
		Game.set_flag(f)
	for key: String in beat["state"]:
		Game.set(key, beat["state"][key])
	Party.set_roster(beat["roster"], beat["lead"])
	get_tree().change_scene_to_file(beat["scene"])


# --- the overlay -------------------------------------------------------------

func _build() -> void:
	_ui = CanvasLayer.new()
	_ui.layer = LAYER
	_ui.process_mode = Node.PROCESS_MODE_ALWAYS
	add_child(_ui)

	var bg := ColorRect.new()
	bg.color = BG
	# both the preset AND the explicit anchors — anchors_preset is editor
	# metadata, a node with only the preset loads zero-sized
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.anchor_right = 1.0
	bg.anchor_bottom = 1.0
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_ui.add_child(bg)

	_label("CHAPTER SELECT", 8, 4, BRASS, 160)
	# right-aligned across the full width rather than parked in column two's
	# lane — at 6px/char a legible hint is wider than a column
	var hint := _label("ARROWS MOVE   SPACE PICK   0 EXIT", 8, 4, GROUP_COL, 368)
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT

	# behind the rows: added before them, and CanvasLayer draws in tree order
	_bar = ColorRect.new()
	_bar.color = HILITE
	_bar.size = Vector2(COL_W, ROW_H)
	_bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_ui.add_child(_bar)

	_lay_out_rows()
	if not _items[_cursor]["selectable"]:
		_step(1)
	_sync()


## Column-major in chronological order. The split lands wherever it lands; if it
## lands mid-chapter, column two repeats the heading so it never opens on an
## orphaned beat.
func _lay_out_rows() -> void:
	var col := 0
	var row := 0
	var group := ""
	for beat: Dictionary in Chapters.BEATS:
		if col == 0 and row >= ROWS_PER_COL:
			col = 1
			row = 0
			if not Chapters.is_group(beat):
				_add_row({group = group + " (CONT.)"}, col, row)
				row += 1
		if Chapters.is_group(beat):
			group = beat["group"]
		_add_row(beat, col, row)
		row += 1


func _add_row(beat: Dictionary, col: int, row: int) -> void:
	var is_group := Chapters.is_group(beat)
	var text: String = beat["group"] if is_group else "  " + String(beat["name"])
	var label := _label(text, COL_X[col], TOP + row * ROW_H,
			GROUP_COL if is_group else BEAT_COL, COL_W)
	_items.append({
		beat = beat, label = label, selectable = not is_group,
		col = col, row = row,
	})


func _label(text: String, x: int, y: int, col: Color, w: int) -> Label:
	var l := Label.new()
	l.text = text
	l.position = Vector2(x, y)
	l.size = Vector2(w, ROW_H)
	l.clip_text = true          # a long row must never bleed into the next column
	l.add_theme_font_override("font", FONT)
	l.add_theme_font_size_override("font_size", 8)     # 1:1 at 384x216
	l.add_theme_color_override("font_color", col)
	l.add_theme_color_override("font_shadow_color", Color.BLACK)
	l.add_theme_constant_override("shadow_offset_x", 1)
	l.add_theme_constant_override("shadow_offset_y", 1)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_ui.add_child(l)
	return l


# --- navigation --------------------------------------------------------------

## The pixel font has no ">" glyph (a missing BMFont glyph draws blank), so the
## selection is a bar behind the row rather than a caret.
func _sync() -> void:
	var it := _items[_cursor]
	_bar.position = Vector2(COL_X[it["col"]] - 2, TOP + int(it["row"]) * ROW_H)


func _step(dir: int) -> void:
	var n := _items.size()
	var i := _cursor
	for _k in n:
		i = wrapi(i + dir, 0, n)
		if _items[i]["selectable"]:
			_cursor = i
			_sync()
			return


## Left and right both mean "the other column" — there are only two.
func _jump_column() -> void:
	var want_col: int = 1 - int(_items[_cursor]["col"])
	var want_row: int = _items[_cursor]["row"]
	var best := -1
	for i in _items.size():
		if not _items[i]["selectable"] or int(_items[i]["col"]) != want_col:
			continue
		# nearest selectable row in the other column, ties going to the first
		if best < 0 or absi(int(_items[i]["row"]) - want_row) \
				< absi(int(_items[best]["row"]) - want_row):
			best = i
	if best >= 0:
		_cursor = best
		_sync()
