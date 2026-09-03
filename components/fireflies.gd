class_name Fireflies
extends Node2D

## THE FIREFLIES (2026-08-23, the permanent-dusk pass). A field of drifting,
## blinking motes for the two Alembic scenes — the one piece of the dusk that
## MOVES, which is what makes the stillness of everything else read as evening
## instead of as a dark palette.
##
## Reuses the Ebb's magic-spark cells (prologue_fx row 1, cells 20/21) with a
## chartreuse modulate — the mint spark tinted (0.72, 1.0, 0.38) IS firefly
## green, so no new art. ADD blend (the magic-mote idiom; a firefly is a light,
## not a lit thing) — and the scene's CanvasModulate multiplies it like
## everything else, which is correct: dusk dims fireflies too, they just start
## from glow.
##
## Each mote is spawned as a child of the scene's y-sorted World at its GROUND
## point with the art lifted via sprite `offset` (the airborne idiom) — so a
## mote near a building's foot passes in front of it and one behind a body
## sorts behind, for free. Motes wander a slow per-mote Lissajous loop around
## their home point and BLINK: mostly off, on for ~0.8s at a time, with the
## phases hashed per mote so the field never metronomes.
##
## Scene wiring: add_child a Fireflies node to $World's PARENT (it spawns its
## motes into `world`), hand it the world node + one or more Rect2 regions in
## world px, and it seeds `count` motes across them. `dim` scales+fades a
## region's motes (the canopy's below-deck field — smaller and dimmer is what
## says thirty feet down).

const FX_SHEET := preload("res://assets/prologue_fx.png")
const FX_A := 20
const FX_B := 21
const TINT := Color(0.72, 1.0, 0.38)

var _motes: Array[Sprite2D] = []
var _t := 0.0


## Seed `count` motes over `region` (world px), parented into `world`.
## `dim` < 1.0 shrinks and fades them — the below-the-deck depth cue.
func seed(world: Node2D, region: Rect2, count: int, dim := 1.0,
		lift_min := 6.0, lift_max := 26.0) -> void:
	var mat := CanvasItemMaterial.new()
	mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	for i in count:
		var s := WorldFx.sheet_sprite(FX_SHEET, FX_A)
		s.material = mat
		s.modulate = TINT
		s.modulate.a = 0.0
		s.scale = Vector2.ONE * (0.75 + 0.25 * _h(i, 3)) * dim
		var home := Vector2(
				region.position.x + region.size.x * _h(i, 1),
				region.position.y + region.size.y * _h(i, 2))
		s.position = home
		s.offset = Vector2(0.0, -(lift_min + (lift_max - lift_min) * _h(i, 4)))
		s.set_meta("home", home)
		s.set_meta("phase", TAU * _h(i, 5))
		s.set_meta("rate", 0.35 + 0.5 * _h(i, 6))
		s.set_meta("dim", dim)
		world.add_child(s)
		_motes.append(s)


## A stable per-mote hash in [0, 1) — no RNG, so a scene reload seeds the same
## field and a probe can screenshot it twice and diff.
func _h(i: int, salt: int) -> float:
	var v := (i * 2654435761 + salt * 40503) & 0xFFFF
	return float(v) / 65536.0


func _process(delta: float) -> void:
	_t += delta
	for s in _motes:
		if not is_instance_valid(s):
			continue
		var ph: float = s.get_meta("phase")
		var rate: float = s.get_meta("rate")
		var home: Vector2 = s.get_meta("home")
		var u := _t * rate + ph
		# the wander: a slow open Lissajous around home — never a visible orbit
		s.position = home + Vector2(sin(u) * 14.0 + sin(u * 0.37) * 8.0,
				sin(u * 0.81 + 1.3) * 7.0)
		s.offset.y += sin(u * 1.7) * 0.06
		# the blink: on for ~a quarter of a slow cycle, dark otherwise — and the
		# frame alternates while lit (the Ebb twinkle)
		var cyc := fmod(u * 0.55, TAU) / TAU
		if cyc < 0.28:
			var k := sin(cyc / 0.28 * PI)          # ease in and out of the glow
			s.modulate.a = k * 0.9 * float(s.get_meta("dim"))
			s.frame = FX_A if int(u * 9.0) % 2 == 0 else FX_B
		else:
			s.modulate.a = 0.0
