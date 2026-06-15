class_name HitboxComponent
extends Area2D

## Deals damage to any HurtboxComponent it overlaps while monitoring is enabled.
## Attackers toggle this on only during active attack frames (or leave it always-on
## for contact damage, like an enemy body).

@export var damage: int = 1


func _ready() -> void:
	area_entered.connect(_on_area_entered)


func _on_area_entered(area: Area2D) -> void:
	if area is HurtboxComponent:
		(area as HurtboxComponent).take_hit(damage, owner)
