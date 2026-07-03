class_name PaintedMap
extends Object

## Runtime collision for painted scenes: sets one invisible physics-only tile
## (assets/collision_tileset.tres, full-square polygon on world layer 1) at
## every solid cell of a MapData map. The visible world is the painted Ground
## and Overlay sprites; this layer is the only place the 32px grid still exists.

static func build_collision(map: Dictionary, layer: TileMapLayer) -> void:
	for cell: Vector2i in map.solid:
		layer.set_cell(cell, 0, Vector2i.ZERO)
