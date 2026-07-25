extends Node2D

## The game's opening (2026-07-12): title card over black, the era cards, then
## Prologue A begins — kid Basil, alone on the roster, waking AT HOME on
## festival morning (scene/house_fest.tscn; the home-start pacing pass — the
## player walks down, sees Mom, and steps into the festival themselves). ESC
## skips the whole prologue straight into the adult combat build (the
## dev/impatience hatch; a real chapter-select can replace it later).

@onready var theater: Theater = $Theater


func _ready() -> void:
	theater.fade.modulate.a = 1.0     # born black — the cards play over it
	_run()


func _run() -> void:
	await theater.wait(0.7)
	await theater.card("PROFESSOR POOPY PAWS", 2.4)
	await theater.card("Alembic Town.  The Founding Festival.", 2.0)
	await theater.card("Years and years ago.", 1.8)
	Party.set_roster([&"kid_basil"])
	get_tree().change_scene_to_file("res://scene/house_fest.tscn")


func _process(_delta: float) -> void:
	# Polled, like everything (the shot.gd gotcha).
	if Input.is_action_just_pressed("ui_cancel"):
		Game.set_flag("prologue_done")
		Game.set_flag("ebb_done")     # the skip jumps past the Ebb night too
		Party.set_roster([&"basil", &"fuji"], &"basil")
		get_tree().change_scene_to_file("res://scene/house.tscn")
