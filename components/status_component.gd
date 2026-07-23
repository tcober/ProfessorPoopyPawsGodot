class_name StatusComponent
extends Node

## Reusable status-ailment container. Entities compose this next to their
## HealthComponent/HurtboxComponent and feed it the `effect` payload that rides
## along HurtboxComponent.hit.
##
## Three ailments, deliberately distinct so they never feel like reskins:
##
##   SLEEP  — Fuji's blow dart. A BUILDUP: each dart adds drowse, and the body
##            only drops once drowse crosses `drowse_threshold`, so a bigger
##            enemy simply raises the threshold and takes more darts. Long,
##            total (still AND harmless), and it does NOT wake on being hit —
##            the sleeper takes normal damage and keeps sleeping out its timer.
##            That is the whole point: it is the SETUP tool.
##   FREEZE — Basil's frost compound. Immediate, partial, short: every hit
##            slows via `move_scale()`, and a third stacked chill locks the
##            body solid for `freeze_time`. The mirror of sleep, not a copy.
##   BURN   — Basil's flame compound. Damage over time; disables nothing.
##
## Drowse and chill DECAY (`drowse_decay`/`chill_decay`), so you cannot chip
## something asleep with one dart a minute — the buildup has to be committed to.
##
## Burn ticks go STRAIGHT to the HealthComponent, never back through
## take_hit(): the hurtbox's invincible_time gate would swallow most of them.

signal disabled_changed(is_disabled: bool)

## Darts to sleep. The one knob a bigger enemy raises (BigSlime uses 5).
@export var drowse_threshold: int = 2
@export var drowse_decay: float = 0.4     # per second, AFTER the grace window
@export var sleep_time: float = 4.0

## Frost hits to freeze solid; every hit slows in the meantime.
@export var chill_threshold: int = 3
@export var chill_decay: float = 0.5      # per second, AFTER the grace window
@export var chill_slow: float = 0.55      # movement multiplier while chilled
@export var freeze_time: float = 1.2

## Seconds of held buildup before decay starts eating it again.
##
## Without this the threshold lies: decay runs between the darts of a burst, so
## a "2 dart" enemy would take three (1.0 decays to 0.993 before the second
## dart lands, and 1.993 < 2). The grace window has to outlast one attack cycle
## — Fuji's dart alone is a 0.42s planted pose plus travel — so a committed
## burst counts exactly as advertised, while a dart every ten seconds still
## decays to nothing.
@export var buildup_grace: float = 1.5

## Burn ticks 1 damage every `burn_period` seconds.
@export var burn_period: float = 0.5

@export var health_component: HealthComponent

var _drowse: float = 0.0
var _chill: float = 0.0
var _drowse_grace: float = 0.0
var _chill_grace: float = 0.0
var _sleep_left: float = 0.0
var _freeze_left: float = 0.0
var _burn_left: int = 0
var _burn_timer: float = 0.0


func _ready() -> void:
	# Same fallback as HurtboxComponent: a hand-authored .tscn that forgets
	# node_paths=PackedStringArray("health_component") loads the export as null.
	if health_component == null:
		health_component = get_node_or_null(^"../HealthComponent") as HealthComponent


func _process(delta: float) -> void:
	var was_disabled := is_disabled()

	if _sleep_left > 0.0:
		_sleep_left -= delta
	elif _drowse > 0.0:
		if _drowse_grace > 0.0:
			_drowse_grace -= delta
		else:
			_drowse = maxf(_drowse - drowse_decay * delta, 0.0)

	if _freeze_left > 0.0:
		_freeze_left -= delta
	elif _chill > 0.0:
		if _chill_grace > 0.0:
			_chill_grace -= delta
		else:
			_chill = maxf(_chill - chill_decay * delta, 0.0)

	if _burn_left > 0:
		_burn_timer -= delta
		if _burn_timer <= 0.0:
			_burn_timer = burn_period
			_burn_left -= 1
			if health_component:
				health_component.take_damage(1)

	if is_disabled() != was_disabled:
		disabled_changed.emit(not was_disabled)


## Fold one hit's status payload in. Keys are additive counts:
## {"drowse": 1} / {"chill": 1} / {"burn": 4}.
func apply(effect: Dictionary) -> void:
	if effect.is_empty():
		return
	var was_disabled := is_disabled()

	if effect.has("drowse") and _sleep_left <= 0.0:
		_drowse += float(effect["drowse"])
		_drowse_grace = buildup_grace
		if _drowse >= float(drowse_threshold):
			_drowse = 0.0
			_sleep_left = sleep_time

	if effect.has("chill") and _freeze_left <= 0.0:
		_chill += float(effect["chill"])
		_chill_grace = buildup_grace
		if _chill >= float(chill_threshold):
			_chill = 0.0
			_freeze_left = freeze_time

	if effect.has("burn"):
		# Re-applying refreshes rather than stacking — a held trigger would
		# otherwise pile up an unkillable tick queue.
		_burn_left = maxi(_burn_left, int(effect["burn"]))
		if _burn_timer <= 0.0:
			_burn_timer = burn_period

	if is_disabled() != was_disabled:
		disabled_changed.emit(not was_disabled)


## Asleep or frozen solid: the body must not move and must not deal contact damage.
func is_disabled() -> bool:
	return _sleep_left > 0.0 or _freeze_left > 0.0


func is_asleep() -> bool:
	return _sleep_left > 0.0


func is_frozen() -> bool:
	return _freeze_left > 0.0


func is_burning() -> bool:
	return _burn_left > 0


## Movement multiplier — chill drags before it locks.
func move_scale() -> float:
	return chill_slow if _chill > 0.0 else 1.0


## How close this body is to dropping, 0..1 — drives the drowsy tell so the
## buildup is legible instead of a hidden counter.
func drowse_ratio() -> float:
	if drowse_threshold <= 0:
		return 0.0
	return clampf(_drowse / float(drowse_threshold), 0.0, 1.0)
