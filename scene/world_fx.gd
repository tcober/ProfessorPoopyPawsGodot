class_name WorldFx
extends Object

## Runtime-FX parenting for y-sorted World nodes (2026-07-12 polish pass).
## FX added to a scene ROOT draw over the whole world — every runtime visual
## that shares space with bodies belongs in $World instead, in one of two
## shapes:
##  - GROUND DECALS (paw prints, puddle splashes, a dropped bag) must lose
##    y-sort to EVERY body whose art can overlap them: the node origin sits
##    DECAL_BIAS px NORTH of the visual center (the art offset points back
##    south) AND the node is moved to child index 0. Bodies key at
##    feet − 20, so the northmost overlapping body (feet touching the decal's
##    top edge, center − 8) keys at center − 28 — the bias must exceed 28
##    (feet offset 20 + half a 16px cell) or a body standing ON the decal
##    renders under it.
##  - AIRBORNE FX (ribbons, sleeping Zs, a perched bird) ground-anchor the
##    ORIGIN on the point they float over and lift the ART via the sprite
##    offset only — theater.hop's move-the-sprite rule — so world depth sorts
##    by the ground beneath them.
## Sprites use the sheet idiom (hframes strip + .frame), so callers keep
## animating by mutating .frame. Assumes the World node sits at the scene
## origin (every prologue scene does), so global points assign to `position`
## directly.

const DECAL_BIAS := 32.0


static func sheet_sprite(sheet: Texture2D, cell: int, hframes := 16) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = sheet
	s.hframes = hframes
	s.frame = cell
	s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	return s


static func decal(world: Node2D, sheet: Texture2D, cell: int, center: Vector2) -> Sprite2D:
	var s := sheet_sprite(sheet, cell)
	s.position = center - Vector2(0.0, DECAL_BIAS)
	s.offset = Vector2(0.0, DECAL_BIAS)
	world.add_child(s)
	world.move_child(s, 0)
	return s


static func airborne(world: Node2D, sheet: Texture2D, cell: int,
		ground: Vector2, lift: float) -> Sprite2D:
	var s := sheet_sprite(sheet, cell)
	s.position = ground
	s.offset = Vector2(0.0, -lift)
	world.add_child(s)
	return s
