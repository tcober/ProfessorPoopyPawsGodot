extends Sprite2D

## Brief blast at the gun muzzle when the laser fires. Pops outward and fades, then frees.

@export var life: float = 0.15

var _t: float = 0.0


func _process(delta: float) -> void:
	_t += delta
	var k := _t / life
	if k >= 1.0:
		queue_free()
		return
	scale = Vector2.ONE * lerpf(0.7, 1.7, k)
	modulate.a = 1.0 - k
