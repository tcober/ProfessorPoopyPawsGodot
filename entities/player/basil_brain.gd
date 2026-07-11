class_name BasilBrain
extends AIBrain

## Basil the follower: a gunner boxed in by 4-way facing. He sidles along the
## shorter axis until the target sits on a cardinal, then fires — the recoil
## skid pushes him back out of danger (emergent kiting). Dry mag with a spare
## in the coat = plant and pour; dry everything = he just follows (he restocks
## by walking over meadow beakers — collect_beaker fires on body contact).

@export var fire_range: float = 110.0
@export var min_range: float = 36.0     # closer than this, back off before firing
@export var aim_tolerance: float = 6.0  # off-axis slack that still counts as lined up


func _combat(target: Node2D, intent: PartyMember.Intent) -> void:
	var basil := member as Player
	if basil.ammo <= 0:
		if basil.beakers > 0:
			intent.secondary = true   # the reload ritual
		else:
			_follow(Party.leader.global_position - member.global_position, intent)
		return
	var d := target.global_position - member.global_position
	var adx := absf(d.x)
	var ady := absf(d.y)
	if adx > aim_tolerance and ady > aim_tolerance:
		# Walk the shorter axis to line the target up on a cardinal.
		intent.move = Vector2(0.0, signf(d.y)) if ady < adx else Vector2(signf(d.x), 0.0)
		return
	var aim := Vector2(signf(d.x), 0.0) if adx >= ady else Vector2(0.0, signf(d.y))
	var dist := d.length()
	if dist < min_range:
		intent.move = -aim
	elif dist > fire_range:
		# The latch holds targets past gun range (recoil skids out there) —
		# walk the cardinal back in.
		intent.move = aim
	# Firing is independent of the retreat: cornered against a wall he shoots
	# the pinning slime instead of grinding into the bricks forever (the bolt
	# spawns 16px out, so point-blank still connects).
	if dist <= fire_range and _cool <= 0.0:
		intent.face = aim
		intent.attack = true
		_cool = attack_cooldown
