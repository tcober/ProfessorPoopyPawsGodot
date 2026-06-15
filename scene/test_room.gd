extends Node2D

## Vertical-slice room: floor + wall colliders, one player, one slime, a camera-following
## player, and a HUD bound to the player's HealthComponent.

@onready var player: Player = $Player
@onready var hud: HUD = $HUD


func _ready() -> void:
	hud.bind_health(player.health)
