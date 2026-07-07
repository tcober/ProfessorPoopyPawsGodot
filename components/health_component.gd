class_name HealthComponent
extends Node

## Reusable HP container. Entities compose this and listen to its signals.
## HP is measured in half-hearts: 6 = 3 full hearts.

signal health_changed(current: int, max_health: int)
signal died

@export var max_health: int = 6

var current_health: int


func _ready() -> void:
	current_health = max_health


func take_damage(amount: int) -> void:
	if current_health <= 0:
		return
	current_health = maxi(current_health - amount, 0)
	health_changed.emit(current_health, max_health)
	if current_health == 0:
		died.emit()


func refill() -> void:
	current_health = max_health
	health_changed.emit(current_health, max_health)
