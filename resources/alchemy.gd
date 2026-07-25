class_name Alchemy
extends Object

## The compound registry and the mixing bench. Pure data + pure functions, no
## node and no autoload — Game holds the loadout, this decides what a beaker IS
## and what two of them make together.
##
## THE MIXING RULES. Three of them, and between them they answer every pair the
## mix menu can offer, so nothing the player can select is undefined:
##
##   1. SAME + SAME       -> CONCENTRATE.  Potency up, charges unchanged.
##   2. BASE + anything   -> DILUTE.       Charges up, potency unchanged.
##   3. FLAME + FROST     -> PLASMA.       The unstable premium.
##
## BASE + BASE is a tie between rules 1 and 2; the same-kind rule wins, so it
## concentrates. Rule 2 is the load-bearing one: green is the inert SOLVENT, so
## the common drop stays worth picking up all game instead of becoming trash the
## moment you own a red one. It is also the only rule that is real chemistry
## rather than game logic, which is the point.
##
## Anything left over (FLAME+PLASMA, FROST+PLASMA) is INERT: mix() returns null
## and the menu refuses the pair rather than silently eating two beakers.

const MAX_POTENCY := 2
const MAX_CHARGES := 12

## Green. What the gun has always fired.
const GREEN := Color(0.52, 0.96, 0.60)
## Blue, red, purple. One hue per kind, carried by bolt + pickup + HUD alike.
const BLUE := Color(0.47, 0.82, 1.00)
const RED := Color(1.00, 0.55, 0.28)
const PURPLE := Color(0.78, 0.51, 1.00)


static func make(kind: Compound.Kind) -> Compound:
	var c := Compound.new()
	c.kind = kind
	match kind:
		Compound.Kind.BASE:
			c.display_name = "REAGENT BASE"
			c.damage = 2
			c.charges = 6
			c.speed = 700.0
			c.lifetime = 1.2
			c.fire_recover = 0.24
			c.tint = GREEN
		Compound.Kind.FROST:
			# Trades damage for control. Chill slows on every hit and stacks
			# into a short hard freeze — immediate and partial, where Fuji's
			# sleep is slow and total. They must never feel like one status.
			c.display_name = "HOARFROST DRAUGHT"
			c.damage = 1
			c.charges = 6
			c.speed = 520.0
			c.lifetime = 1.2
			c.fire_recover = 0.26
			c.effect = {"chill": 1}
			c.tint = BLUE
		Compound.Kind.FLAME:
			# A sprayer, not a rifle: the short lifetime IS the range limit
			# (~60px at this speed), paid for with a fast cadence and a burn
			# that keeps ticking after you have moved on to the next target.
			c.display_name = "CINDER TINCTURE"
			c.damage = 1
			c.charges = 6
			c.speed = 380.0
			c.lifetime = 0.16
			c.fire_recover = 0.12
			c.effect = {"burn": 4}
			c.spray = true
			c.tint = RED
		Compound.Kind.PLASMA:
			# The premium. Kills a slime in one hit and punches through the
			# one behind it, but three shots and the beaker is dry.
			c.display_name = "PLASMA DECOCTION"
			c.damage = 4
			c.charges = 3
			c.speed = 800.0
			c.lifetime = 1.2
			c.fire_recover = 0.30
			c.pierce = true
			c.tint = PURPLE
	return c


## What two beakers make, or null if the pair is inert. Never mutates its
## arguments — the menu previews a result before committing to it.
static func mix(a: Compound, b: Compound) -> Compound:
	if a == null or b == null:
		return null

	# Rule 1: same kind concentrates. Checked FIRST so BASE+BASE resolves here
	# rather than diluting itself.
	if a.kind == b.kind:
		if a.potency >= MAX_POTENCY and b.potency >= MAX_POTENCY:
			return null                     # already as concentrated as it gets
		var out := make(a.kind)
		out.potency = mini(maxi(a.potency, b.potency) + 1, MAX_POTENCY)
		out.charges = maxi(a.charges, b.charges)
		out.display_name = "CONC. " + out.display_name
		return out

	# Rule 3: the one real recipe. Checked before dilution so it can't be
	# reached by either ordering of the arguments.
	if _pair_is(a, b, Compound.Kind.FLAME, Compound.Kind.FROST):
		return make(Compound.Kind.PLASMA)

	# Rule 2: green is the solvent — it stretches the other reagent thinner.
	if a.kind == Compound.Kind.BASE or b.kind == Compound.Kind.BASE:
		var other: Compound = b if a.kind == Compound.Kind.BASE else a
		if other.charges >= MAX_CHARGES:
			return null                     # any thinner and it stops working
		var thinned := make(other.kind)
		thinned.potency = other.potency
		thinned.charges = mini(other.charges * 2, MAX_CHARGES)
		thinned.display_name = "DIL. " + thinned.display_name
		return thinned

	return null


## A human-readable reason the menu can show for a refused pair.
static func refusal(a: Compound, b: Compound) -> String:
	if a == null or b == null:
		return ""
	if a.kind == b.kind:
		return "ALREADY FULLY CONCENTRATED"
	if a.kind == Compound.Kind.BASE or b.kind == Compound.Kind.BASE:
		return "ALREADY FULLY DILUTED"
	return "INERT - NOTHING HAPPENS"


static func _pair_is(a: Compound, b: Compound, x: Compound.Kind, y: Compound.Kind) -> bool:
	return (a.kind == x and b.kind == y) or (a.kind == y and b.kind == x)
