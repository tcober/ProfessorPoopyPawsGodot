class_name Beaker
extends Area2D

## A refill pickup for the laser gun. When the player walks over it, it tops up their
## ammo by `ammo_amount` and disappears. Collision mask = player body (2).

signal collected

@export var ammo_amount: int = 3


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node) -> void:
	if body is Player:
		(body as Player).refill_ammo(ammo_amount)
		collected.emit()
		queue_free()
