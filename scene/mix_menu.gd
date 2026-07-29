extends Node

## Autoloaded as `MixMenu`: press M anywhere to open Basil's mixing bench and
## fuse two of the spare beakers in his coat into one better compound.
##
## The rules live in resources/alchemy.gd; this file is the overlay, the
## two-step selection, and the commit. Two spares become ONE — that cost is the
## whole design, so the menu always shows what you are about to get (and what
## you are about to lose) before it takes anything.
##
## The chrome — CanvasLayer at layer 100, PROCESS_MODE_ALWAYS, the SWALLOW
## timer, the full-rect backdrop, the pixel font, the selection BAR — now comes
## from scene/overlay.gd, shared with DevMenu. It used to be a hand-copy of
## dev_menu.gd's, which is how the guard below ended up half-implemented.
##
## Unlike DevMenu this is NOT behind OS.is_debug_build() — it is a real game
## menu. It IS the project's second get_tree().paused user, so the two guard
## against each other via Overlay.any_open(): whichever is open refuses the
## other, otherwise closing one would unpause the tree out from under the one
## still on screen.
##
## Input is POLLED in _process, never _input — the project-wide rule, because
## tools/shot.gd's synthesized presses exist only in the polled action state.

## The look, the swallow timer and the one-modal-at-a-time rule live in
## scene/overlay.gd, shared with DevMenu. Only the LAYOUT is this menu's own.
const ROW_H := Overlay.ROW_H
const TOP := 34
const LEFT := 16
const WIDTH := 352
const MAX_ROWS := 3          # Player.max_beakers — a full coat

const BRASS := Overlay.BRASS
const DIM := Overlay.DIM
const TEXT := Overlay.TEXT
const BAD := Overlay.BAD

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


## The modal contract's half of the bargain (Overlay.any_open asks every entry
## in Overlay.MODALS this, and asserts the method exists).
func is_open() -> bool:
	return _ui != null


func _process(delta: float) -> void:
	if _ui == null:
		# Overlay.any_open is the shared modal rule (see overlay.gd): whichever
		# is up owns the paused tree, and opening on top of it would leave the
		# first to close unpausing the game under the other.
		if Input.is_action_just_pressed("mix") \
				and not Overlay.any_open(get_tree(), self):
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


# --- open / close ------------------------------------------------------------

func _open() -> void:
	_first = -1
	_cursor = 0
	_build()
	_swallow = Overlay.SWALLOW
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
	_ui = Overlay.build_layer(self)

	Overlay.label(_ui, "MIXING BENCH", LEFT, 8, BRASS, 200)
	_hint = Overlay.label(_ui, "", LEFT, 20, DIM, WIDTH)

	_bar = Overlay.bar(_ui, Vector2(WIDTH, ROW_H))

	_rebuild_rows()
	# Parked below a FULL coat (max_beakers) rather than below the current rows,
	# so the preview line doesn't hop up the panel as beakers are consumed.
	_result = Overlay.label(_ui, "", LEFT, TOP + MAX_ROWS * ROW_H + 10, TEXT, WIDTH)
	_sync()


func _rebuild_rows() -> void:
	for l in _rows:
		l.queue_free()
	_rows.clear()
	for i in Game.spares.size():
		_rows.append(Overlay.label(_ui, "", LEFT, TOP + i * ROW_H, TEXT, WIDTH))
	_cursor = clampi(_cursor, 0, maxi(Game.spares.size() - 1, 0))


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
	# One row per spare is an invariant every read below depends on. Anything
	# that edits Game.spares while the bench is up (a dev-menu reset_story, a
	# pickup landing on the same frame) would otherwise index past the array.
	if _rows.size() != Game.spares.size():
		_rebuild_rows()
		if _first >= Game.spares.size():
			_first = -1
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
