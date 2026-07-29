class_name ItemPickup
extends Area2D

## A dropped item lying on the ground. Walking over it puts it in the satchel.
## Collision mask = the player body layer (2), same as Beaker.
##
## Deliberately NOT a second Beaker. A beaker is Basil's magazine and only he
## can carry one — `collect_beaker` is a method on his body, and the pickup asks
## the body whether there is room. An item goes into the party-wide satchel on
## `Game`, so this one needs no body at all: whoever is leading walks over it and
## the whole party has it. That difference is why the shared parts are small
## enough not to be worth a base class.

signal collected

## Set BEFORE the node enters the tree — _ready is what paints the tint and
## there is no property setter here (the Beaker convention).
@export var item_id: StringName = &"tonic"
@export var count: int = 1

@onready var sprite: Sprite2D = $Sprite2D


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	var it := Items.get_item(item_id)
	if sprite and it:
		# One shared flask sprite tinted per item, exactly as the beaker does it:
		# a green tonic on the snow reads from across the street with no new art.
		sprite.modulate = it.tint


## Only the LEADER can pick things up — `player` is the leader-only group the
## whole door/exit/pickup layer already gates on, so a follower wandering over a
## tonic does not silently pocket it while you are looking somewhere else.
func _on_body_entered(body: Node) -> void:
	if not body.is_in_group("player"):
		return
	var game := get_node_or_null(^"/root/Game")
	if game == null:
		return
	game.call("add_item", item_id, count)
	collected.emit()
	queue_free()
