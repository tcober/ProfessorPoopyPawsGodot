class_name FujiBrain
extends AIBrain

## Fuji the follower: a melee scrapper who OPENS WITH THE PIPE. Out past tome
## range she blows darts as she closes; up close she swings — the swing's own
## lunge (fuji.gd STATE_BOOK) carries her through the target.
##
## The darting is the point of the sleep buildup. Walking the whole way in
## empty-pawed wastes the approach, and darts cost nothing but the planted pose;
## by the time she arrives the target is often already under, which is exactly
## the setup-then-payoff the player does by hand when Fuji is the leader.
##
## She stops darting once a target is asleep — more drowse on a sleeper is
## thrown away (StatusComponent ignores it), and the pipe pose would keep her
## standing still outside swing range for no gain.

@export var swing_range: float = 16.0    # book_reach 12 + a margin
@export var dart_range: float = 100.0    # don't bother from across the meadow
@export var dart_cooldown: float = 0.9

var _dart_cool: float = 0.0


func _physics_process(delta: float) -> void:
	super(delta)
	# Decays in the brain's own process for the same reason `_cool` does: the
	# member skips think() during kit states, and the dart pose IS a kit state,
	# so pausing this would stretch her cadence by the whole animation.
	_dart_cool = maxf(_dart_cool - delta, 0.0)


func _combat(target: Node2D, intent: PartyMember.Intent) -> void:
	var to_target := target.global_position - member.global_position
	var dist := to_target.length()

	if dist > swing_range:
		intent.move = to_target.normalized()
		if _dart_cool <= 0.0 and dist <= dart_range \
				and not member.is_airborne() and not _is_asleep(target):
			intent.face = to_target
			intent.secondary = true      # fuji.gd maps secondary -> the blow pipe
			_dart_cool = dart_cooldown
		return

	if _cool <= 0.0 and not member.is_airborne():
		# The body drops attack edges mid-hop (only reachable right after a
		# mid-hop leader swap) — don't spend the cooldown on one.
		intent.face = to_target
		intent.attack = true
		_cool = attack_cooldown


## Duck-typed: not every enemy has to carry a StatusComponent.
func _is_asleep(target: Node2D) -> bool:
	var status := target.get_node_or_null(^"StatusComponent")
	return status != null and status.is_asleep()
