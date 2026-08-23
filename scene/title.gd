extends Node2D

## THE TITLE SCREEN. Boots the game: NEW GAME, CONTINUE (when there is a save),
## and QUIT.
##
## REBUILT 2026-08-22 to the user's own opening-screen sketch: an autumn
## beechwood corridor (assets/_gen_title_art.py bakes the painting AND the
## stacked cream title), adult Basil walking INTO the camera on the leaf
## carpet — the real walk_down sprite, so the opening screen is the game's
## actual art — and a drift of falling leaves where the old screen had snow.
## The menu sits bottom-left under the title block. Music comes from the
## Music autoload (scene/music.gd), which keys the title theme off this
## scene's path — nothing to wire here.
##
## Input is POLLED, like every other menu in the project: tools/shot.gd's
## synthesized presses exist only in the polled action state, so an
## _input-driven title screen could never be screenshotted or probed.

const FONT = preload("res://assets/font/pixel_font.fnt")
const BG = preload("res://assets/title_bg.png")
const FIRST_SCENE := "res://scene/prologue_open.tscn"

## The backdrop's own palette, so the chrome sits in the painting.
const BRASS := Color(0.95, 0.78, 0.40)
const TEXT := Color(0.95, 0.90, 0.67)
const DIM := Color(0.78, 0.62, 0.44)

## Leaf colors off the carpet/canopy ramps — two golds, a crimson, a pale.
const LEAF_COLS: Array[Color] = [
	Color(0.94, 0.78, 0.40), Color(0.88, 0.59, 0.25),
	Color(0.76, 0.31, 0.20), Color(0.97, 0.90, 0.64),
]

const LEAVES := 44
const VIEW := Vector2(384.0, 216.0)

var _rows: Array[Label] = []
var _actions: Array[String] = []
var _cursor := 0
var _swallow := 0.25
var _leaves: Array = []                # [pos, fall speed, drift phase, color]
var _t := 0.0
var _leaving := false

@onready var _bar: ColorRect = $UI/Bar


func _ready() -> void:
	randomize()
	for i in LEAVES:
		_leaves.append([
			Vector2(randf() * VIEW.x, randf() * VIEW.y),
			9.0 + randf() * 14.0,          # a leaf falls slower than snow
			randf() * TAU,
			LEAF_COLS[randi() % LEAF_COLS.size()],
		])
	_build_menu()
	queue_redraw()


func _process(delta: float) -> void:
	_t += delta
	for f in _leaves:
		f[0].y += f[1] * delta
		f[0].x += sin(_t * 0.8 + f[2]) * 14.0 * delta   # the sway IS the leaf
		if f[0].y > VIEW.y:
			f[0].y = -2.0
			f[0].x = randf() * VIEW.x
	queue_redraw()

	if _leaving:
		return
	# The press that LOADED this scene must not also be read as a pick on the
	# first frame — the dialog box's swallow trick, and the reason a title
	# screen reached from a game-over would otherwise pick NEW GAME instantly.
	if _swallow > 0.0:
		_swallow -= delta
		return
	if Input.is_action_just_pressed("move_down") or Input.is_action_just_pressed("ui_down"):
		_step(1)
	elif Input.is_action_just_pressed("move_up") or Input.is_action_just_pressed("ui_up"):
		_step(-1)
	elif Input.is_action_just_pressed("attack") \
			or Input.is_action_just_pressed("interact") \
			or Input.is_action_just_pressed("ui_accept"):
		_pick()


## The painting, then the falling leaves. _draw runs under this node's
## children (Basil) and under the UI CanvasLayer, so the walk and the text
## always sit on top.
func _draw() -> void:
	draw_texture(BG, Vector2.ZERO)
	for f in _leaves:
		# A falling leaf tumbles: it reads wide on one half of its sway and
		# tall on the other — two pixels either way, flat color, no dither.
		var wide := sin(_t * 0.8 + f[2]) > 0.0
		draw_rect(Rect2(f[0].floor(),
			Vector2(2.0, 1.0) if wide else Vector2(1.0, 2.0)), f[3])


func _build_menu() -> void:
	var ui: CanvasLayer = $UI
	_label(ui, "a science cat, a librarian, and a world gone quiet",
		12, 130, TEXT, 8)

	_actions = ["new"]
	var labels := ["NEW GAME"]
	if SaveGame.has_save():
		# CONTINUE goes FIRST when there is a save and starts selected: someone
		# with a run in progress is overwhelmingly likely to want it, and putting
		# NEW GAME under a resting cursor is how saves get lost.
		_actions = ["continue", "new"]
		labels = ["CONTINUE", "NEW GAME"]
	_actions.append("quit")
	labels.append("QUIT")

	for i in labels.size():
		_rows.append(_label(ui, labels[i], 20, 152 + i * 15, TEXT, 8))
	if SaveGame.has_save():
		_label(ui, SaveGame.summary(), 20, 152 + labels.size() * 15 + 3, DIM, 8)
	_sync()


func _label(ui: CanvasLayer, text: String, x: int, y: int, col: Color,
		size: int) -> Label:
	var l := Label.new()
	l.text = text
	l.position = Vector2(x, y)
	l.add_theme_font_override("font", FONT)
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", col)
	l.add_theme_color_override("font_shadow_color", Color.BLACK)
	l.add_theme_constant_override("shadow_offset_x", 1)
	l.add_theme_constant_override("shadow_offset_y", 1)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui.add_child(l)
	return l


func _step(dir: int) -> void:
	_cursor = wrapi(_cursor + dir, 0, _rows.size())
	Sfx.ui_move()
	_sync()


func _sync() -> void:
	for i in _rows.size():
		_rows[i].add_theme_color_override("font_color", BRASS if i == _cursor else TEXT)
	_bar.position = Vector2(16.0, 152.0 + _cursor * 15.0)
	_bar.size = Vector2(100.0, 11.0)


func _pick() -> void:
	match _actions[_cursor]:
		"new":
			_leaving = true
			Sfx.ui_accept()
			# A NEW GAME starts from nothing, and says so out loud: reset_story
			# is the same wipe the dev chapter selector uses, so a fresh run can
			# never inherit a previous one's flags through a title screen.
			Game.reset_story()
			get_tree().change_scene_to_file.call_deferred(FIRST_SCENE)
		"continue":
			var scene := SaveGame.load_into(get_tree())
			if scene == "":
				Sfx.ui_refuse()
				return                       # unreadable//versioned save: stay put
			_leaving = true
			Sfx.ui_accept()
			get_tree().change_scene_to_file.call_deferred(scene)
		"quit":
			get_tree().quit()
