extends Node

## Autoloaded as `MixMenu`: press M anywhere to open Basil's mixing bench and
## fuse two of the spare beakers in his coat into one better compound.
##
## The rules live in resources/alchemy.gd; this file is the overlay, the
## two-step selection, and the commit. Two spares become ONE — that cost is the
## whole design, so the menu always shows what you are about to get (and what
## you are about to lose) before it takes anything.
##
## Modelled on scene/dev_menu.gd, which is the project's in-code overlay idiom,
## and reuses all of it: CanvasLayer at layer 100, PROCESS_MODE_ALWAYS, the
## SWALLOW timer so the opening press isn't read as a pick, full-rect anchors
## set BOTH by preset and explicitly (the preset alone is editor metadata and
## loads zero-sized), the pixel font at size 8, and a selection BAR rather than
## a caret because the font has no ">" glyph.
##
## Unlike DevMenu this is NOT behind OS.is_debug_build() — it is a real game
## menu. It IS the project's second get_tree().paused user, so the two guard
## against each other: whichever is open refuses the other, otherwise closing
## one would unpause the tree out from under the one still on screen.
##
## Input is POLLED in _process, never _input — the project-wide rule, because
## tools/shot.gd's synthesized presses exist only in the polled action state.

const FONT = preload("res://assets/font/pixel_font.fnt")

const LAYER := 100
const ROW_H := 10
const TOP := 34
const LEFT := 16
const WIDTH := 352
const MAX_ROWS := 3          # Player.max_beakers — a full coat

## Same as dialog_box.gd's SWALLOW_MS trick, in seconds.
const SWALLOW := 0.14

const BG := Color(0.055, 0.04, 0.115, 0.94)
const BRASS := Color(0.91, 0.74, 0.38)
const HILITE := Color(0.42, 0.28, 0.14)
const DIM := Color(0.62, 0.56, 0.70)
const TEXT := Color(0.95, 0.94, 0.97)
const BAD := Color(0.86, 0.44, 0.44)

var _ui: CanvasLayer
var _bar: ColorRect
var _rows: Array[Label] = []
var _result: Label
var _hint: Label
var _cursor := 0
var _first := -1            # index of the first picked beaker, -1 = none picked
var _swallow := 0.0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


func is_open() -> bool:
	return _ui != null


func _process(delta: float) -> void:
	if _ui == null:
		# DevMenu owns the tree while it is up; opening on top of it would
		# leave whichever closes first unpausing the other.
		if Input.is_action_just_pressed("mix") and not _dev_menu_open():
			_open()
		return

	if _swallow > 0.0:
		_swallow -= delta
		return

	if Input.is_action_just_pressed("mix") or Input.is_action_just_pressed("ui_cancel"):
		if _first >= 0:
			_first = -1          # back out of the pair before backing out of the menu
			_sync()
		else:
			_close()
		return

	if Input.is_action_just_pressed("move_down") or Input.is_action_just_pressed("ui_down"):
		_step(1)
	elif Input.is_action_just_pressed("move_up") or Input.is_action_just_pressed("ui_up"):
		_step(-1)
	elif Input.is_action_just_pressed("attack") \
			or Input.is_action_just_pressed("interact") \
			or Input.is_action_just_pressed("ui_accept"):
		_pick()


func _dev_menu_open() -> bool:
	var dev := get_node_or_null(^"/root/DevMenu")
	return dev != null and dev.get("_ui") != null


# --- open / close ------------------------------------------------------------

func _open() -> void:
	_first = -1
	_cursor = 0
	_build()
	_swallow = SWALLOW
	get_tree().paused = true


func _close() -> void:
	get_tree().paused = false
	if is_instance_valid(_ui):
		_ui.queue_free()
	_ui = null
	_rows.clear()


# --- the mix -----------------------------------------------------------------

func _pick() -> void:
	if Game.spares.size() < 2:
		return
	if _first < 0:
		_first = _cursor
		_step(1)                 # move off the one just picked
		_sync()
		return
	if _cursor == _first:
		_first = -1              # picking the same beaker twice cancels
		_sync()
		return

	var a: Compound = Game.spares[_first]
	var b: Compound = Game.spares[_cursor]
	var out := Alchemy.mix(a, b)
	if out == null:
		_sync()                  # refusal already shown; nothing is consumed
		return

	# Remove the higher index first so the lower one doesn't shift under us.
	var hi := maxi(_first, _cursor)
	var lo := mini(_first, _cursor)
	Game.spares.remove_at(hi)
	Game.spares.remove_at(lo)
	Game.spares.insert(lo, out)

	_first = -1
	_cursor = lo
	_notify_player()
	_rebuild_rows()
	_sync()


## The HUD listens to the Player, and the Player's spares ARE Game.spares — so
## the coat is already correct, but nothing has told the HUD to redraw.
func _notify_player() -> void:
	for m in get_tree().get_nodes_in_group("party"):
		if m is Player:
			(m as Player).beakers_changed.emit(Game.spares, (m as Player).max_beakers)


# --- the overlay -------------------------------------------------------------

func _build() -> void:
	_ui = CanvasLayer.new()
	_ui.layer = LAYER
	_ui.process_mode = Node.PROCESS_MODE_ALWAYS
	add_child(_ui)

	var bg := ColorRect.new()
	bg.color = BG
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.anchor_right = 1.0
	bg.anchor_bottom = 1.0
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_ui.add_child(bg)

	_label("MIXING BENCH", LEFT, 8, BRASS, 200)
	_hint = _label("", LEFT, 20, DIM, WIDTH)

	_bar = ColorRect.new()
	_bar.color = HILITE
	_bar.size = Vector2(WIDTH, ROW_H)
	_bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_ui.add_child(_bar)

	_rebuild_rows()
	# Parked below a FULL coat (max_beakers) rather than below the current rows,
	# so the preview line doesn't hop up the panel as beakers are consumed.
	_result = _label("", LEFT, TOP + MAX_ROWS * ROW_H + 10, TEXT, WIDTH)
	_sync()


func _rebuild_rows() -> void:
	for l in _rows:
		l.queue_free()
	_rows.clear()
	for i in Game.spares.size():
		_rows.append(_label("", LEFT, TOP + i * ROW_H, TEXT, WIDTH))
	_cursor = clampi(_cursor, 0, maxi(Game.spares.size() - 1, 0))


func _label(text: String, x: int, y: int, col: Color, w: int) -> Label:
	var l := Label.new()
	l.text = text
	l.position = Vector2(x, y)
	l.size = Vector2(w, ROW_H)
	l.clip_text = true
	l.add_theme_font_override("font", FONT)
	l.add_theme_font_size_override("font_size", 8)
	l.add_theme_color_override("font_color", col)
	l.add_theme_color_override("font_shadow_color", Color.BLACK)
	l.add_theme_constant_override("shadow_offset_x", 1)
	l.add_theme_constant_override("shadow_offset_y", 1)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_ui.add_child(l)
	return l


func _step(dir: int) -> void:
	var n := Game.spares.size()
	if n == 0:
		return
	_cursor = wrapi(_cursor + dir, 0, n)
	_sync()


## Redraw every row, the selection bar, the hint and the preview. Cheap enough
## at three rows that recomputing the whole panel beats tracking dirty state.
func _sync() -> void:
	if _ui == null:
		return
	for i in _rows.size():
		var c: Compound = Game.spares[i]
		var mark := "*" if i == _first else " "
		_rows[i].text = "%s %s" % [mark, _describe(c)]
		# Each row wears its compound's own colour, so the coat reads the same
		# in here as it does on the HUD.
		_rows[i].add_theme_color_override("font_color", c.tint if c else TEXT)

	if _rows.is_empty():
		_bar.visible = false
	else:
		_bar.visible = true
		_bar.position = Vector2(LEFT - 2, TOP + _cursor * ROW_H)

	if Game.spares.size() < 2:
		_hint.text = "NEED TWO SPARE BEAKERS TO MIX.   M EXIT"
	elif _first < 0:
		_hint.text = "PICK THE FIRST BEAKER.   SPACE PICK   M EXIT"
	else:
		_hint.text = "PICK THE SECOND.   SPACE MIX   M BACK"

	if _result == null:
		return
	if _first < 0 or _first == _cursor or Game.spares.size() < 2:
		_result.text = ""
		return
	var a: Compound = Game.spares[_first]
	var b: Compound = Game.spares[_cursor]
	var out := Alchemy.mix(a, b)
	if out == null:
		_result.text = "= " + Alchemy.refusal(a, b)
		_result.add_theme_color_override("font_color", BAD)
	else:
		_result.text = "= " + _describe(out)
		_result.add_theme_color_override("font_color", out.tint)


func _describe(c: Compound) -> String:
	if c == null:
		return "-"
	var dmg := c.hit_damage()
	return "%s  (%d DMG x%d SHOTS)" % [c.display_name, dmg, c.charges]
