class_name Beaker
extends Area2D

## A spare magazine for the laser gun. Walking over it pockets it (up to the
## player's max_beakers — when his paws are full it stays on the grass).
## Reloading pours it in. Collision mask = player body (2).

signal collected


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node) -> void:
	if body is Player and (body as Player).collect_beaker():
		collected.emit()
		queue_free()
