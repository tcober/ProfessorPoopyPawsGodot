extends Node2D

## Title screen: the autumn-forest poster (assets/_gen_title.py), Basil idling on the
## path under falling leaves. Fire/accept starts the intro; ESC jumps straight in.


func _ready() -> void:
	var tw := create_tween().set_loops()
	tw.tween_property($UI/Prompt, "modulate:a", 0.15, 0.7).set_trans(Tween.TRANS_SINE)
	tw.tween_property($UI/Prompt, "modulate:a", 1.0, 0.7).set_trans(Tween.TRANS_SINE)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("attack") or event.is_action_pressed("ui_accept"):
		get_tree().change_scene_to_file("res://scene/intro_house.tscn")
	elif event.is_action_pressed("ui_cancel"):
		get_tree().change_scene_to_file("res://scene/overworld.tscn")
