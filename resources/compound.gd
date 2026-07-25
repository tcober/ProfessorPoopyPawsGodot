class_name Compound
extends Resource

## One beaker's worth of chemistry — what Basil's gun becomes when he pours it in.
##
## This is CHEMISTRY, not magic. The world is drained and stays drained; a
## reagent that burns or freezes owes nothing to the Ebb. Everyone else calls
## the stuff in his coat "potions"; he knows better. Keep the in-world naming
## on that side of the line.
##
## Beakers were a counted resource (`beakers: int`) until the compounds landed.
## Now each spare carries its kind, and mixing two of them makes a third — so
## the magazine you pour is a CHOICE, not just a refill.
##
## Four kinds ship. Their whole behaviour is data on this Resource, and
## LaserBolt reads it off the instance the way it already reads `direction` and
## `shooter`, so one bolt scene serves all four:
##
##   BASE   green   the laser he has always had. Damage 2, 6 rounds, no status.
##   FROST  blue    chills on hit, stacking into a brief hard freeze.
##   FLAME  red     short range and fast, leaves the target burning.
##   PLASMA purple  BASE+FROST fused: heavy, pierces, only 3 rounds.

enum Kind { BASE, FROST, FLAME, PLASMA }

@export var kind: Kind = Kind.BASE
@export var display_name: String = "REAGENT BASE"

## Gun behaviour. `potency` is a damage multiplier applied on top of `damage`,
## which is how "concentrating" a compound works without inventing new kinds.
@export var damage: int = 2
@export var potency: int = 1
@export var charges: int = 6
@export var speed: float = 700.0
@export var lifetime: float = 1.2
@export var fire_recover: float = 0.24
@export var pierce: bool = false

## Draw the bolt as a widening, fading gout instead of a hard bolt. Flame's
## short lifetime is its range limit, and a tinted bolt that simply blinks out
## at 60px reads as a stubby laser — swelling and thinning as it goes is what
## makes it read as fire, and it costs no new art.
@export var spray: bool = false

## The status payload each bolt carries into HurtboxComponent.take_hit.
@export var effect: Dictionary = {}

## Bolt + pickup + HUD colour. One hue per kind — the beaker in the coat, the
## pip row, and the bolt in flight all read as the same substance.
@export var tint: Color = Color.WHITE


func hit_damage() -> int:
	return damage * potency


func total_charges() -> int:
	return charges
