extends SceneTree

## Poses the status tells for eyeballing — the visual companion to
## tools/status_probe.gd, which only proves the mechanics. Stages a row of
## slimes in the meadow (awake green, ASLEEP green with Zs, awake BIG, ASLEEP
## big, FROZEN, BURNING) in front of the leader and screenshots it.
##
## Must run WINDOWED (same GL note as tools/shot.gd):
##   /Applications/Godot.app/Contents/MacOS/Godot --path . \
##       --script tools/status_shot.gd -- /tmp/status.png

const SlimeScene := preload("res://entities/enemies/slime.tscn")
const BigSlimeScene := preload("res://entities/enemies/big_slime.tscn")


func _initialize() -> void:
	_run()


func _run() -> void:
	Engine.max_fps = 60
	var args := OS.get_cmdline_user_args()
	var out: String = args[0] if args.size() > 0 else "/tmp/status.png"
	var want_mix := args.size() > 1 and args[1] == "mix"

	await process_frame
	change_scene_to_file("res://scene/meadow.tscn")
	await process_frame
	await process_frame

	if want_mix:
		await _shoot_mix_menu(out)
		return
	if args.size() > 1 and args[1] == "bolts":
		await _shoot_bolts(out)
		return

	var party := root.get_node("Party")
	var leader: Node2D = party.leader
	var world: Node2D = current_scene.get_node("World")

	# Clear the field and the follower so nothing wanders into frame.
	for m in party.members:
		if m != leader:
			m.queue_free()
	for child in world.get_children():
		if child is Slime:
			child.queue_free()
	await process_frame

	# A tidy row across the camera, well clear of the leader.
	var specimens := [
		[SlimeScene, Vector2(-64, -34), {}],
		[SlimeScene, Vector2(-20, -34), {"drowse": 9}],
		[BigSlimeScene, Vector2(28, -34), {}],
		[BigSlimeScene, Vector2(80, -34), {"drowse": 9}],
		[SlimeScene, Vector2(-44, 24), {"chill": 9}],
		[SlimeScene, Vector2(4, 24), {"burn": 9}],
	]
	for spec in specimens:
		var slime: Node2D = (spec[0] as PackedScene).instantiate()
		world.add_child(slime)
		slime.global_position = leader.global_position + (spec[1] as Vector2)
		# Unkillable + inert so nothing chases or dies while the pose settles.
		var health = slime.get_node("HealthComponent")
		health.max_health = 99999
		health.current_health = 99999
		slime.detect_range = 0.0
		await process_frame
		var effect: Dictionary = spec[2]
		if not effect.is_empty():
			slime.get_node("StatusComponent").apply(effect)

	# Let the tints, the paused bounce and the Zs settle in.
	for i in 30:
		await process_frame

	await _save(out)


## Stage a full coat and open the mixing bench mid-selection, so the shot shows
## the row colours, the picked marker and the live result preview at once.
func _shoot_mix_menu(out: String) -> void:
	var game := root.get_node("Game")
	var coat: Array[Compound] = [
		Alchemy.make(Compound.Kind.FLAME),
		Alchemy.make(Compound.Kind.FROST),
		Alchemy.make(Compound.Kind.BASE),
	]
	game.spares = coat

	var menu := root.get_node("MixMenu")
	menu._open()
	menu._swallow = 0.0
	menu._first = 0            # flame picked...
	menu._cursor = 1           # ...cursor on frost: the plasma recipe, previewed
	menu._rebuild_rows()
	menu._sync()
	for i in 6:
		await process_frame
	await _save(out)


## One bolt of each compound in flight, plus a tinted HUD (plasma loaded, a
## frost and a flame spare in the coat) — the things that only exist at runtime.
func _shoot_bolts(out: String) -> void:
	var game := root.get_node("Game")
	var leader: Node2D = root.get_node("Party").leader
	var world: Node2D = current_scene.get_node("World")

	var coat: Array[Compound] = [
		Alchemy.make(Compound.Kind.FROST),
		Alchemy.make(Compound.Kind.FLAME),
	]
	game.spares = coat
	leader.set("loaded", Alchemy.make(Compound.Kind.PLASMA))
	leader.beakers_changed.emit(game.spares, leader.get("max_beakers"))
	leader.loaded_changed.emit(leader.get("loaded"))

	# Fired east along four lanes so each bolt is mid-flight in the same frame.
	var kinds := [Compound.Kind.BASE, Compound.Kind.FROST,
			Compound.Kind.FLAME, Compound.Kind.PLASMA]
	for i in kinds.size():
		var bolt: LaserBolt = load("res://entities/projectiles/laser_bolt.tscn").instantiate()
		bolt.direction = Vector2.RIGHT
		bolt.shooter = leader
		bolt.apply_compound(Alchemy.make(kinds[i]))
		bolt.speed = 60.0          # slowed so all four stay on screen for the shot
		bolt.lifetime = 9.0
		world.add_child(bolt)
		# East of the leader in open grass — spawning west of him walked all
		# four bolts straight into his sprite by the time the shot was taken.
		bolt.global_position = leader.global_position + Vector2(40.0, -30.0 + i * 20.0)

	for i in 40:
		await process_frame
	await _save(out)


func _save(out: String) -> void:
	await process_frame
	RenderingServer.force_draw()
	var img := get_root().get_texture().get_image()
	img.save_png(out)
	print("wrote ", out, " ", img.get_size())
	quit(0)
