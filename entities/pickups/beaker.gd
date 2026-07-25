class_name Beaker
extends Area2D

## A spare magazine for the laser gun. Walking over it pockets it (up to the
## player's max_beakers — when his paws are full it stays on the grass).
## Reloading pours it in. Collision mask = player body (2).
##
## A beaker has a KIND: what is actually in the glass decides what the gun
## fires once it is poured. The sprite is one shared flask tinted to the
## compound's colour, so a red one on the grass reads as flame from across the
## meadow without a second piece of art.

signal collected

@export var kind: Compound.Kind = Compound.Kind.BASE

@onready var sprite: Sprite2D = $Sprite2D


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	if sprite:
		sprite.modulate = Alchemy.make(kind).tint


## Re-colour after spawn (meadow.gd rolls a kind per refill).
func set_kind(new_kind: Compound.Kind) -> void:
	kind = new_kind
	if is_node_ready() and sprite:
		sprite.modulate = Alchemy.make(kind).tint


func _on_body_entered(body: Node) -> void:
	if body is Player and (body as Player).collect_beaker(kind):
		collected.emit()
		queue_free()
