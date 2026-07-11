class_name FujiBrain
extends AIBrain

## Fuji the follower: a melee scrapper. Closes to tome range and swings —
## the swing's own lunge (fuji.gd STATE_BOOK) carries her through the target.

@export var swing_range: float = 16.0   # book_reach 12 + a margin


func _combat(target: Node2D, intent: PartyMember.Intent) -> void:
	var to_target := target.global_position - member.global_position
	if to_target.length() > swing_range:
		intent.move = to_target.normalized()
	elif _cool <= 0.0:
		intent.face = to_target
		intent.attack = true
		_cool = attack_cooldown
