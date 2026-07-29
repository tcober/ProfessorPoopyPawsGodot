extends Node2D

## THE TITLE SCREEN. Boots the game: NEW GAME, CONTINUE (when there is a save),
## and QUIT.
##
## AUTHORED FRESH, not recovered. There was a title screen before the 2026-07-12
## combat-first cut and it is still in git history; the build-fresh doctrine says
## nothing narrative comes back out of git, so this is a new one on the current
## pipelines. It costs no new art either: the backdrop is drawn in code from the
## same duo-tone the winter town uses — a deep violet-slate field, a drift of
## snow falling through it, and the title in the shipped pixel font.
##
## Input is POLLED, like every other menu in the project: tools/shot.gd's
## synthesized presses exist only in the polled action state, so an _input-driven
## title screen could never be screenshotted or probed.

const FONT = preload("res://assets/font/pixel_font.fnt")
const FIRST_SCENE := "res://scene/prologue_open.tscn"

## The Narshe palette's own values, so the title sits in the same world as the
## game behind it rather than looking like a different product.
const SKY_TOP := Color(0.055, 0.045, 0.11)
const SKY_BOT := Color(0.16, 0.16, 0.28)
const SNOW := Color(0.86, 0.90, 0.98)
const BRASS := Color(0.91, 0.74, 0.38)
const TEXT := Color(0.95, 0.94, 0.97)
const DIM := Color(0.55, 0.50, 0.64)

const FLAKES := 70
const VIEW := Vector2(384.0, 216.0)

var _rows: Array[Label] = []
var _actions: Array[String] = []
var _cursor := 0
var _swallow := 0.25
var _flakes: Array = []                # [pos, speed, drift, size]
var _t := 0.0
var _leaving := false

@onready var _bar: ColorRect = $UI/Bar


func _ready() -> void:
	randomize()
	for i in FLAKES:
		_flakes.append([
			Vector2(randf() * VIEW.x, randf() * VIEW.y),
			8.0 + randf() * 16.0,          # fall speed
			randf() * TAU,                 # drift phase
			1.0 if randf() < 0.7 else 2.0, # near flakes are fatter
		])
	_build_menu()
	queue_redraw()


func _process(delta: float) -> void:
	_t += delta
	for f in _flakes:
		f[0].y += f[1] * delta
		f[0].x += sin(_t * 0.6 + f[2]) * 6.0 * delta
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


## The backdrop, drawn rather than authored: a vertical wash and the snow.
## _draw runs under the UI CanvasLayer, so the text always sits on top.
func _draw() -> void:
	var bands := 24
	for i in bands:
		var t := float(i) / float(bands - 1)
		draw_rect(Rect2(0.0, t * VIEW.y, VIEW.x, VIEW.y / bands + 1.0),
			SKY_TOP.lerp(SKY_BOT, t))
	for f in _flakes:
		# Far flakes are dimmer as well as smaller — two cues, so the depth
		# reads at 1x where a size difference alone is one pixel.
		draw_rect(Rect2(f[0].floor(), Vector2(f[3], f[3])),
			Color(SNOW.r, SNOW.g, SNOW.b, 0.35 if f[3] < 2.0 else 0.7))


func _build_menu() -> void:
	var ui: CanvasLayer = $UI
	_label(ui, "PROFESSOR", 96, 46, BRASS, 24)
	_label(ui, "POOPY PAWS", 96, 74, BRASS, 24)
	_label(ui, "a science cat, a librarian, and a world gone quiet",
		46, 104, DIM, 8)

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
		_rows.append(_label(ui, labels[i], 150, 138 + i * 14, TEXT, 8))
	if SaveGame.has_save():
		_label(ui, SaveGame.summary(), 150, 138 + labels.size() * 14 + 4, DIM, 8)
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
	_sync()


func _sync() -> void:
	for i in _rows.size():
		_rows[i].add_theme_color_override("font_color", BRASS if i == _cursor else TEXT)
	_bar.position = Vector2(146.0, 138.0 + _cursor * 14.0)
	_bar.size = Vector2(96.0, 10.0)


func _pick() -> void:
	match _actions[_cursor]:
		"new":
			_leaving = true
			# A NEW GAME starts from nothing, and says so out loud: reset_story
			# is the same wipe the dev chapter selector uses, so a fresh run can
			# never inherit a previous one's flags through a title screen.
			Game.reset_story()
			get_tree().change_scene_to_file.call_deferred(FIRST_SCENE)
		"continue":
			var scene := SaveGame.load_into(get_tree())
			if scene == "":
				return                       # unreadable//versioned save: stay put
			_leaving = true
			get_tree().change_scene_to_file.call_deferred(scene)
		"quit":
			get_tree().quit()
