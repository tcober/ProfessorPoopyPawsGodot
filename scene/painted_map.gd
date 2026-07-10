class_name PaintedMap
extends Object

## Runtime collision for every scene, painted or tiled: sets one invisible
## physics-only tile (assets/collision_tileset.tres, full-square polygon on
## world layer 1) at every solid cell of a MapData map — the 16px grid's only
## appearance in physics. Painted scenes draw Ground/Overlay sprites over it;
## tiled scenes stamp their visible layers from the same map via TiledMap.

static func build_collision(map: Dictionary, layer: TileMapLayer) -> void:
	for cell: Vector2i in map.solid:
		layer.set_cell(cell, 0, Vector2i.ZERO)
