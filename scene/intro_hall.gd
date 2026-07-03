extends Cutscene

## Opening scene, part 3 — the lecture hall. Basil makes it to the podium... and
## Schweinler makes sure nobody ever forgets what's on his paws. The name is born.

@onready var basil: AnimatedSprite2D = $Basil
@onready var schweinler: AnimatedSprite2D = $Schweinler
@onready var audience: Node2D = $Audience


func _play() -> void:
	await card("THE ROYAL ACADEMY OF NATURAL MAGIC.", 1.8)
	await fade_in(0.8)
	await wait(0.6)
	await say("DEAN: ...AND NOW, PRESENTING HIS THESIS ON RE-ENCHANTMENT THEORY...")
	await say("DEAN: ...THE YOUNGEST PROFESSOR IN ACADEMY HISTORY -- PROFESSOR BASIL!")
	await wait(0.4)
	await say("BASIL: AHEM. TH-THANK YOU. AS I WAS SAYING-- MAGIC IS NOT GONE. IT IS MERELY SLEEPING, AND--")
	# Schweinler rises
	await hop(schweinler, 6.0, 0.25)
	schweinler.play("point_up")
	await say("SCHWEINLER: HOLD ON!! WHAT'S THAT SMELL?!")
	await say("BASIL: S-SCHWEINLER?!")
	await say("SCHWEINLER: EVERYONE!! LOOK AT HIS PAWS!! HE TRACKED IT ALL THE WAY UP THERE!!")
	basil.play("hurt")
	await wait(0.5)
	schweinler.play("laugh_down")
	await say("SCHWEINLER: PFFFT-- OINK-HAHAHA!! GREAT LECTURE...")
	await say("SCHWEINLER: ...PROFESSOR POOPY PAWS!!!")
	_crowd_laugh()
	basil.play("sad")                 # ears droop; his heart breaks
	await say("EVERYONE: HAHAHAHA!! POOPY PAWS!! HAHAHAHA!!")
	await say("BASIL: ...")
	await fade_out(1.4)
	await card("THE NAME STUCK.", 1.8)
	await card("THE LAUGHTER FOLLOWED HIM HOME. HE DID NOT GO BACK.", 2.2)
	await card("HE STOPPED GOING ANYWHERE AT ALL.", 2.0)
	await card("...YEARS LATER.", 1.8)
	finish()


## Everyone jiggles. Cruelty in motion.
func _crowd_laugh() -> void:
	for cat in audience.get_children():
		var tw := create_tween().set_loops(6)
		tw.tween_property(cat, "position:y", cat.position.y - 2, 0.09)
		tw.tween_property(cat, "position:y", cat.position.y, 0.09)
