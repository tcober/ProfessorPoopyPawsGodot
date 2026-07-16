extends Node2D

## The accident, SHOWN (Prologue B; setup rework 2026-07-16) — a side-view
## set-piece cut between the watch call and the sickroom, now with CAUSE:
## Schweinler is roadside showing off the brand-new machine to Ridley the
## badger, Ridley warns him it looks dangerous, Schweinler climbs on anyway
## — and loses control the moment the engine catches, exactly as Kitty
## happens to pedal around the bend. Wobble, motion lines, the drift across
## the centerline, a hard cut on the moment itself (poof + a white screen
## flash, never a contact frame), then the quiet aftermath under a darker
## sky — Ridley standing helpless by the wreck he predicted. (He carries
## what he saw into the fountain scene's blunt "perspective" speech.)
##
## No party, no map: plain sprites and its own Theater. Every beat either
## auto-runs on tweens/waits or advances on attack (probe-passable — the
## probe just mashes through the say() lines).

const FX_SHEET := preload("res://assets/prologue_fx.png")

const FX_SPARK0 := 2
const FX_SPARK1 := 3
const FX_POOF := 17
const FX_LINES := 18

const ATV_PARKED := 4                # the rider-less frame (stack cold)

## The lane (must match accident_bg's road band, y 154-200): Kitty rides the
## NEAR side, the machine bolts down the FAR side and drifts into hers.
const LANE_KITTY := 170.0
const LANE_ATV := 159.0
const IMPACT_X := 172.0

const DIM_AFTERMATH := Color(0.68, 0.66, 0.86)   # the sun is gone

var _anim_t := 0.0
var _kitty_riding := false
var _atv_driving := false

@onready var theater: Theater = $Theater
@onready var kitty: Sprite2D = $Kitty
@onready var atv: Sprite2D = $Atv
@onready var schw_stand: Sprite2D = $SchwStand
@onready var ridley: Sprite2D = $Ridley


func _ready() -> void:
	theater.fade.modulate.a = 1.0        # open on black; the roadside fades in
	kitty.position = Vector2(-40.0, LANE_KITTY)
	# the setup trio stages HIGH, on the far shoulder — the dialog box owns
	# the bottom ~60px of the view, and the reveal beat needs the machine
	# (and both pigs) visible above it; the mount tween drops the rig down
	# onto the lane proper
	atv.frame = ATV_PARKED
	atv.position = Vector2(268.0, 147.0)
	schw_stand.position = Vector2(314.0, 138.0)
	ridley.position = Vector2(346.0, 137.0)
	_run()


func _process(delta: float) -> void:
	# pedal / engine cadence once each is rolling
	_anim_t += delta
	if _kitty_riding:
		kitty.frame = int(_anim_t / 0.16) % 2
	if _atv_driving:
		atv.frame = int(_anim_t / 0.12) % 2


func _run() -> void:
	await theater.wait(0.4)
	await theater.clear(1.2)
	# ---- the setup: pride, a warning, and a saddle he can't quite reach
	await theater.say("Schweinler", "Feast your eyes, Ridley. Father had it shipped from the CAPITAL. The fastest machine in the kingdom.")
	ridley.frame = 2                     # act pair: pointing at it
	await theater.say("Ridley", "It's got a lot of... pipes. Schweinler, that thing looks DANGEROUS. Have you actually driven it?")
	schw_stand.frame = 4                 # emote pair: the laugh
	await theater.say("Schweinler", "DRIVEN it? You don't DRIVE a machine like this. You POINT it. Watch.")
	theater.close_dialog()
	# he climbs on — the standing pig becomes the rider baked into the frames
	await theater.wait(0.5)
	schw_stand.visible = false
	atv.frame = 0
	var mount_tw := create_tween()
	mount_tw.tween_property(atv, "position:y", LANE_ATV, 0.25) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	await mount_tw.finished
	_atv_driving = true
	await theater.say("", "The engine catches on the first try. Nobody expects that. Including the machine.")
	theater.close_dialog()
	# ---- and IMMEDIATELY loses control — as Kitty rounds the bend
	_atv_driving = false
	atv.frame = 2                        # the swerve
	var lines := WorldFx.sheet_sprite(FX_SHEET, FX_LINES)
	add_child(lines)
	lines.position = atv.position + Vector2(30.0, -4.0)
	var wobble := create_tween().set_loops()
	wobble.tween_property(atv, "rotation", 0.06, 0.16)
	wobble.tween_property(atv, "rotation", -0.08, 0.2)
	wobble.tween_property(atv, "rotation", 0.05, 0.18)
	var lurch := create_tween()
	lurch.tween_property(atv, "position:x", 236.0, 0.9)
	# Kitty, bell bright, exactly the wrong moment
	_kitty_riding = true
	var bell := WorldFx.sheet_sprite(FX_SHEET, FX_SPARK0)
	bell.position = Vector2(16.0, -12.0)
	kitty.add_child(bell)
	var bell_tw := bell.create_tween().set_loops()
	bell_tw.tween_callback(func() -> void: bell.frame = FX_SPARK1).set_delay(0.3)
	bell_tw.tween_callback(func() -> void: bell.frame = FX_SPARK0).set_delay(0.3)
	var ride := create_tween()
	ride.tween_property(kitty, "position:x", 118.0, 1.4).set_ease(Tween.EASE_OUT)
	await theater.say("Ridley", "SCHWEINLER! The BRAKE! Where's the BRAKE?!")
	theater.close_dialog()
	if lurch.is_running():
		await lurch.finished
	if ride.is_running():
		await ride.finished
	bell.queue_free()
	_kitty_riding = false
	kitty.frame = 2                      # the brace, eyes wide
	await theater.wait(0.3)
	# the last stretch runs uninterrupted: drift across the centerline
	var tw3 := create_tween().set_parallel()
	tw3.tween_property(atv, "position:x", IMPACT_X + 34.0, 0.6)
	tw3.tween_property(atv, "position:y", LANE_KITTY, 0.6)
	tw3.tween_property(kitty, "position:x", IMPACT_X - 26.0, 0.6)
	await tw3.finished
	wobble.kill()
	lines.queue_free()
	# the cut: one toned beat of light, then black — never a contact frame
	$Poof.position = Vector2(IMPACT_X, LANE_KITTY - 8.0)
	$Poof.visible = true
	$Flash.modulate.a = 0.9
	var flash_tw := create_tween()
	flash_tw.tween_property($Flash, "modulate:a", 0.0, 0.14)
	await theater.wait(0.09)
	await theater.black(0.06)
	$Poof.visible = false
	kitty.visible = false
	atv.visible = false
	ridley.visible = false
	await theater.wait(1.6)              # the silence holds
	# the aftermath, held for weight — later, darker, quieter. Ridley has
	# run to the wreck; Schweinler stays frozen on the stopped machine
	# (he's baked into the skid frame) — the line comes from there
	$Dim.color = DIM_AFTERMATH
	atv.rotation = 0.0
	$BikeDown.position = Vector2(IMPACT_X - 40.0, LANE_KITTY + 10.0)
	$BikeDown.visible = true
	kitty.frame = 3                      # still, on the road
	kitty.position = Vector2(IMPACT_X + 8.0, LANE_KITTY + 12.0)
	kitty.visible = true
	atv.frame = 3
	atv.position = Vector2(IMPACT_X + 70.0, LANE_KITTY + 2.0)
	atv.visible = true
	ridley.frame = 0
	ridley.position = Vector2(IMPACT_X + 106.0, 152.0)
	ridley.visible = true
	await theater.clear(1.6)
	await theater.wait(1.0)
	await theater.say("Schweinler", "...I didn't see her. I swear I - the machine just - I didn't SEE her!")
	await theater.say("Ridley", "...I'll get the doctor. Don't touch her. Don't touch ANYTHING.")
	theater.close_dialog()
	await theater.wait(1.4)
	await theater.black(1.4)
	Game.set_flag("prologue_accident")
	get_tree().change_scene_to_file("res://scene/sickroom.tscn")
