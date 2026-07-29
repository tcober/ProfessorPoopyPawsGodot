class_name Overlay
extends RefCounted

## Shared chrome for the project's two modal overlays — DevMenu (the chapter
## selector) and MixMenu (the mixing bench). Both are built in code rather than
## hand-authored as .tscn (their rows are generated from data anyway), both sit
## at layer 100 under PROCESS_MODE_ALWAYS, and both PAUSE the tree.
##
## Extracted 2026-07-25. The two files had been carrying byte-identical copies
## of everything below — _label() to the character, the palette, the
## build-CanvasLayer-with-a-full-rect-backdrop dance, the swallow timer — and
## that is precisely how the modal contract came to be written down in two
## places and implemented in one: mix_menu refused to open over dev_menu, and
## dev_menu opened straight over an open bench, unpausing the tree under it.
## any_open() below makes that guard symmetric BY CONSTRUCTION.
##
## What genuinely differs between the two — row layout, per-row colour, what a
## pick does — stays in the caller. This owns the look and the modal rule.

const FONT = preload("res://assets/font/pixel_font.fnt")

const LAYER := 100                 # above dialog 20, theater 15, scene UI 10
const ROW_H := 10                  # the font's lineHeight

## The press that OPENS a menu must not also be read as a pick on the same
## frame — dialog_box.gd's SWALLOW_MS trick, in seconds.
const SWALLOW := 0.14

const BG := Color(0.055, 0.04, 0.115, 0.94)      # the dialog panel's night blue
const BRASS := Color(0.91, 0.74, 0.38)           # its lit bevel
const HILITE := Color(0.42, 0.28, 0.14)          # its shadow bevel
const DIM := Color(0.62, 0.56, 0.70)
const TEXT := Color(0.95, 0.94, 0.97)
const BAD := Color(0.86, 0.44, 0.44)

## Every autoload that can hold the tree paused. Kept here rather than in either
## menu so neither can add itself to one list and forget the other.
const MODALS: Array[StringName] = [&"DevMenu", &"MixMenu"]


## THE MODAL CONTRACT: at most one of these may be open, because each pauses the
## tree on open and unpauses on close — a second one closing first would unpause
## the game under the one still covering the screen.
##
## Looked up by node name rather than by the autoload identifier so the same
## call works from both sides regardless of registration order (DevMenu is
## registered before MixMenu).
##
## Asks each modal through its own is_open() rather than reading a private
## field off it. Reaching in for `_ui` worked, but it made the contract depend
## on two files happening to spell one variable the same way — which is the
## exact class of drift this file was extracted to end. The assert names a
## modal that forgot the method instead of silently reporting it closed.
static func any_open(tree: SceneTree, except: Node = null) -> bool:
	for modal in MODALS:
		var node := tree.root.get_node_or_null(NodePath(modal))
		if node == null or node == except:
			continue
		assert(node.has_method("is_open"),
				"modal %s must expose is_open()" % modal)
		if node.call("is_open"):
			return true
	return false


## The overlay's CanvasLayer plus its full-rect backdrop, parented to `owner`.
static func build_layer(owner: Node) -> CanvasLayer:
	var ui := CanvasLayer.new()
	ui.layer = LAYER
	ui.process_mode = Node.PROCESS_MODE_ALWAYS
	owner.add_child(ui)

	var bg := ColorRect.new()
	bg.color = BG
	# both the preset AND the explicit anchors — anchors_preset is editor
	# metadata, a node with only the preset loads zero-sized
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.anchor_right = 1.0
	bg.anchor_bottom = 1.0
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui.add_child(bg)
	return ui


static func label(ui: CanvasLayer, text: String, x: int, y: int, col: Color,
		w: int) -> Label:
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
	ui.add_child(l)
	return l


## The selection bar. The pixel font has no ">" glyph (a missing BMFont glyph
## draws blank), so the selection is a bar BEHIND the row rather than a caret —
## which means it must be added before the rows are, since a CanvasLayer draws
## in tree order.
static func bar(ui: CanvasLayer, size: Vector2) -> ColorRect:
	var r := ColorRect.new()
	r.color = HILITE
	r.size = size
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui.add_child(r)
	return r
