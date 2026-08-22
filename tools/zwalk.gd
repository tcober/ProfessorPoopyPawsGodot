extends SceneTree

## THE Z-ORDER WALKAROUND. Drives a body to every position in a scene where the
## layering doctrine can go wrong, crops the frame around it, and tiles the crops
## into CONTACT SHEETS you eyeball a hundred at a time.
##
##   /Applications/Godot.app/Contents/MacOS/Godot --path . \
##       --script tools/zwalk.gd -- res://scene/alembic_town.tscn /tmp/zwalk [beat:N]
##
## It must run WINDOWED (the same GL note as tools/shot.gd: --headless renders
## black on GL Compatibility), and it pins Engine.max_fps like every other tool
## here, because an occluded macOS window runs uncapped.
##
## WHY A HARNESS AND NOT A LIST OF SHOTS. Every z-order bug this project has had
## was found by standing in one specific place — pressed south into a cliff,
## in the NOTCH beside a band step, on the terrace below a mask strip, north of a
## trunk, south of a fence — and there are hundreds of those places in a stacked
## town. The positions are therefore DERIVED FROM THE MAP rather than typed: move
## a band and the harness follows it, and a new band cannot be forgotten.
##
## The four families it generates, one contact sheet each, named for the failure
## they hunt:
##   PRESSED   the cell NORTH of every face-band run, body shoved south. The
##             mask-band case: ~11px of sprite hangs past the physics box, and
##             the band's own top 12px must be re-drawn over it.
##   NOTCH     the cell beside every band STEP, at the lower run's level. Bands
##             staircase, so a body can stand level with a wall — and it must
##             NOT be masked there (masking it clips the character's face).
##   BELOW     the cell SOUTH of every run's foot. A body down there must not be
##             masked either; as upper-layer tiles this case sliced heads off.
##   PROPS     the four cells around every Tier-3 prop component. Walk-behind:
##             north of a trunk is BEHIND it, south is IN FRONT of it, and a
##             pressed body's sunk feet must not draw over a standable prop (the
##             2026-07-19 fence lesson).
##
## ADD `lint` AND IT MEASURES INSTEAD OF PHOTOGRAPHING:
##
##   /Applications/Godot.app/Contents/MacOS/Godot --path . \
##       --script tools/zwalk.gd -- res://scene/alembic_town.tscn /tmp/z lint [debug]
##
## Contact sheets work and they do not SCALE — a four-storey town derives ~300
## spots and nobody looks at the 290th as hard as the first. `lint` recovers the
## body's visible silhouette at every spot and asserts on it, exit code 1 on any
## finding. See _lint_all() for the method and for what each family asserts.
## `debug` prints the body / camera / window arithmetic for every capture.
##
## IT MUST BE DETERMINISTIC OR IT IS WORTHLESS, and for one day it was not: three
## identical runs over an unchanged town reported 8, 91 and 3 findings. A gate that
## answers differently every time trains you to ignore it, which is strictly worse
## than having no gate. Both causes were the harness measuring ITSELF —
## `_pin_pose()` and `_hard_camera()` carry the post-mortems.
##
## The two things it caught the day it was written, both in a town whose whole
## probe suite was green:
##   1. THE PRESSED FAMILY WAS NOT PRESSING. Teleporting a body one nudge into a
##      wall and awaiting the frame lets the solver push it back out, so every
##      one of the 111 `pressed` spots sat SIX PIXELS shy of the face it was
##      supposed to be flush against — the mask-band case was never once tested.
##      The first fix drove it there with velocity, which turned out to be a
##      NO-OP for a reason worth knowing; see _spot() for both halves.
##   2. A WALKABLE CELL UNDER AN OPAQUE TRUNK SHAFT IS AN INVISIBLE BODY. Alembic's
##      great tree carried a walkable `J` crown over its footprint's top rows; the
##      trunk sprite is y-sorted at the FOOT, so it draws over everything north of
##      it, and its shaft is ~35px of the 48px canvas. Standing on the crown's
##      centre column left 0 visible pixels. Walk-behind is only legal under
##      PERFORATED art — a leaf lobe, a lamp mantle, a crown — never under a
##      continuous mass.

const CROP := 96           ## px of game view per cell of the contact sheet
const COLS := 6            ## cells per contact-sheet row
const SETTLE := 6          ## frames to let the camera snap and the body settle
const MAX_PER_SHEET := 36
const SEAT := 6.0           ## px the requested spot is BIASED toward the face this
                            ## family wants the body seated against — see _spot()
const WIN := 64            ## game px of the occlusion window around the body
const DIFF := 24           ## per-channel delta that counts as "different pixel"

var _map: Dictionary
var _out := "/tmp/zwalk"
var _lint := false          ## `lint` arg: measure occlusion instead of tiling sheets
var _masks: Array = []      ## the props manifest's `mask` rects — see _read_masks()
var _prop_box: Array = []   ## Tier-3 art rects + sort keys — see _read_prop_boxes()
var _ref := {}              ## the body's UNOCCLUDED silhouette, measured in the open
var _fails: Array = []
var _debug := false
## Set when the run REFUSED — it could not measure this scene at all. Distinct from
## "found nothing", and the caller must not overwrite its exit code with 0.
var _refused := false


func _initialize() -> void:
	_run()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 2:
		push_error("usage: -- <scene.tscn> <out_dir_prefix> [beat:N] [lint]")
		quit(1)
		return
	Engine.max_fps = 60
	await process_frame
	_out = args[1]
	var scene_path := args[0]
	for i in range(2, args.size()):
		if args[i] == "lint":
			_lint = true
		if args[i] == "debug":
			_debug = true
		if args[i].begins_with("beat:"):
			var table: GDScript = load("res://scene/chapters.gd")
			var b: Dictionary = table.BEATS[int(args[i].split(":")[1])]
			scene_path = b["scene"]
			root.get_node("Game").call("reset_story")
			for f: String in b["flags"]:
				root.get_node("Game").call("set_flag", f)
			for k: String in b["state"]:
				root.get_node("Game").set(k, b["state"][k])
			root.get_node("Party").call("set_roster", b["roster"], b["lead"])
	change_scene_to_file(scene_path)
	for i in 70:                       # ride out the entry fade AND its lock
		await process_frame
	# A LINT THAT CANNOT RUN MUST NOT EXIT 0. A GDScript runtime error does not
	# unwind — "Invalid access to property 'map' on a null instance" prints, hands
	# back null and CARRIES ON — so a scene that failed to load used to walk the
	# whole harness over nulls, derive no spots, find no faults and report success.
	# Three scenes were in that state (the overworld, the lab, the library) and the
	# suite called all three green. Refuse loudly instead: the whole value of this
	# tool is that a silent pass means something.
	if current_scene == null:
		push_error("zwalk: '%s' did not load — nothing was linted" % scene_path)
		quit(1)
		return
	var scene_map: Variant = current_scene.get("map")
	if not (scene_map is Dictionary) or (scene_map as Dictionary).is_empty():
		push_error(("zwalk: %s exposes no `map` — this tool derives every spot from "
				+ "the grid, so there is nothing to lint here") % scene_path)
		quit(1)
		return
	_map = scene_map
	# PIN THE SCENE BUSY FOR THE WHOLE WALK. Teleporting a body across a town
	# drags it through every travel marker, every door and both lift landings, and
	# the first one that fires changes the scene and frees the body out from under
	# the harness. `_busy` is the flag TravelScene already gates every marker,
	# exit, announce and the lift ride on, so one assignment refuses all of them
	# and nothing has to know about this tool.
	current_scene.set("_busy", true)
	var families := _positions()
	if _lint:
		await _lint_all(families)
		# NOT an unconditional quit: _lint_all refuses (and sets its own exit code)
		# when it could not measure anything, and re-quitting here would paper a
		# refusal back over with 0 — the exact silent pass the refusals exist to end.
		if not _refused:
			quit(1 if not _fails.is_empty() else 0)
		return
	for name in families:
		var spots: Array = families[name]
		print("%s: %d spots" % [name, spots.size()])
		var page := 0
		while page * MAX_PER_SHEET < spots.size():
			var slice: Array = spots.slice(page * MAX_PER_SHEET,
					(page + 1) * MAX_PER_SHEET)
			await _sheet("%s_%s%d" % [_out, name, page], slice)
			page += 1
	quit()


# ---- THE OCCLUSION LINT --------------------------------------------------------------
## Contact sheets find z-order bugs by eye, which works and does not SCALE: a
## four-storey town derives ~300 spots and nobody looks at the 290th as hard as
## the first. So measure it instead.
##
## The body's visible silhouette is recovered by photographing each spot THREE
## times — sprite hidden, shown, hidden — and keeping the pixels that changed in
## the middle frame AND are identical in the outer two. The outer-two clause is
## what makes it robust in this game specifically: animated water, breathing
## windows and drifting smoke all move between captures, and every one of those
## pixels differs in frames 1 and 3 as well, so it drops out.
##
## Then the silhouette is compared against the body measured ALONE IN THE OPEN,
## and each family asserts the thing its name means:
##
##   PRESSED  the mask strip must eat the overhang. The props manifest is the
##            authority on where a strip exists, so an UNMASKED face is reported
##            separately from a masked one that leaks — the lift gate is
##            deliberately unmasked, and everything else that is, is a bug.
##   BELOW    nothing may clip the body. It is under the face, not on it.
##   NOTCH    same, and this is the one that regressed twice: masking the notch
##            clips the character's FACE against the wall beside it.
##   PROPS    walk-behind is directional. South of a prop must be UNOCCLUDED;
##            occlusion there means the body is drawn behind something it is
##            standing in front of.
func _lint_all(families: Dictionary) -> void:
	_read_masks()
	_read_prop_boxes()
	var party := root.get_node("Party")
	var body: Node2D = party.leader
	if not is_instance_valid(body):
		push_error("zwalk: this scene spawned no party body — nothing was linted")
		_refused = true
		quit(1)
		return
	var sprite := _sprite_of(body)
	# HIDE EVERY OTHER PARTY BODY for the whole run. The follower walks toward the
	# leader between captures, and its pixels would land in the window as noise.
	for m in party.members:
		if m != body and is_instance_valid(m):
			var s := _sprite_of(m)
			if s:
				s.visible = false
	_ref = await _silhouette(body, sprite, _open_cell())
	print("reference silhouette: %d px, bbox %d,%d..%d,%d (relative to origin)"
			% [_ref["n"], _ref["x0"], _ref["y0"], _ref["x1"], _ref["y1"]])
	if int(_ref["n"]) <= 250:
		# Was an assert, which printed and then let the run end with NO summary and
		# exit 0 — a scene reporting nothing looked exactly like a scene reporting
		# nothing wrong. The library measured a reference of ZERO px this way: its
		# open cell is not open, so every comparison after it was against nothing.
		push_error(("zwalk: the reference silhouette is %d px — the body is occluded "
				+ "where this scene's open cell was chosen, so nothing here can be "
				+ "measured against it") % int(_ref["n"]))
		_refused = true
		quit(1)
		return
	for name in families:
		print("\n--- %s: %d spots" % [name, (families[name] as Array).size()])
		for spot: Dictionary in families[name]:
			# `_busy` only silences a TravelScene. An INTERIOR wires its door
			# straight to body_entered, so teleporting the body across the room
			# walks it through that door, changes the scene and frees it — and
			# every remaining capture then measured a dead object and came back
			# clean. Stop on the spot rather than finish a run that means nothing.
			if not is_instance_valid(body):
				push_error(("zwalk: the body was freed during '%s' — a door or "
						+ "trigger fired mid-walk, so this run is INCOMPLETE and "
						+ "its silence means nothing") % name)
				_refused = true
				quit(1)
				return
			var got := await _silhouette(body, sprite, spot)
			_judge(name, spot, got)
	_drop_pass_behinds()
	print("\n=== %d finding(s)" % _fails.size())
	for f in _fails:
		print("  ", f)


## Seat the body and recover its visible silhouette, in game px relative to its
## own origin. `spot` may be a plain {"pos","push"} or a full family spot.
func _silhouette(body: Node2D, sprite: AnimatedSprite2D, spot: Dictionary) -> Dictionary:
	body.set_physics_process(true)
	for f in SETTLE:
		body.global_position = spot["pos"]
		body.velocity = Vector2.ZERO
		await physics_frame
	for f in SETTLE:                    # ...then let the solver seat it, unheld
		await physics_frame
	_pin_pose(body, sprite)
	var cam := _hard_camera(body)
	await process_frame
	var view := MapData.view_size()
	var scale := 0.0
	var caps: Array[Image] = []
	var rect := Rect2i()
	for pass_i in 3:
		sprite.visible = pass_i == 1
		RenderingServer.force_draw(true, 0.0)
		var frame := root.get_viewport().get_texture().get_image()
		if scale == 0.0:
			scale = float(frame.get_width()) / view.x
			var on_screen: Vector2 = (body.global_position
					- cam.get_screen_center_position() + view * 0.5) * scale
			if _debug:
				print("      DBG body=%s cam=%s on_screen=%s"
						% [body.global_position, cam.get_screen_center_position(),
						on_screen])
			var half := int(WIN * scale * 0.5)
			rect = Rect2i(Vector2i(on_screen) - Vector2i(half, half),
					Vector2i(half * 2, half * 2)).intersection(
					Rect2i(Vector2i.ZERO, frame.get_size()))
		caps.append(frame.get_region(rect))
	sprite.visible = true
	# THE CONSENSUS DIFF. A pixel belongs to the body iff the middle capture
	# differs from BOTH outer captures and the outer two agree with each other.
	var w := rect.size.x
	var h := rect.size.y
	var a := caps[0].get_data()
	var b := caps[1].get_data()
	var c2 := caps[2].get_data()
	var bpp := a.size() / (w * h)
	var n := 0
	var x0 := 9999
	var y0 := 9999
	var x1 := -9999
	var y1 := -9999
	for i in w * h:
		var o := i * bpp
		if not (_far(a, b, o) and _far(c2, b, o) and not _far(a, c2, o)):
			continue
		n += 1
		var px := i % w
		var py := i / w
		x0 = mini(x0, px)
		y0 = mini(y0, py)
		x1 = maxi(x1, px)
		y1 = maxi(y1, py)
	# back to game px relative to the body's own origin (the window is centred
	# on it, so the window's own centre is origin)
	var half_g := float(w) * 0.5
	return {"at": body.global_position,
			"n": int(round(n / (scale * scale))),
			"x0": int(round((x0 - half_g) / scale)),
			"y0": int(round((y0 - half_g) / scale)),
			"x1": int(round((x1 - half_g) / scale)),
			"y1": int(round((y1 - half_g) / scale)),
			"empty": n == 0}


## KILL THE CAMERA'S SMOOTHING OUTRIGHT — `reset_smoothing()` is not enough, and
## trusting it was the second half of the nondeterminism.
##
## Every measurement here is made in a window CENTRED ON THE BODY, and where that
## window sits is computed from `cam.get_screen_center_position()`. So a camera that
## has not arrived does not merely frame the shot loosely: it slides the window, and a
## silhouette measured 4px high in the window is reported as a body whose head is
## clipped by 4px. That is exactly the artefact this lint hunts, manufactured by the
## harness.
##
## And the residual is not a constant, so it does not cancel between the reference and
## the spots. Measured across two identical runs, the reference frame was teleported to
## the same pixel both times and the camera sat at (298.5, 422.2) in one and
## (297.8, 421.2) in the other — still chasing, from a different distance, because the
## number of idle frames that had elapsed is wall-clock, not frame count (gotcha 3: an
## occluded window runs uncapped). Same body, same map, different answer.
##
## With `position_smoothing_enabled = false` the camera IS the body, clamped to its
## limits, and `get_screen_center_position()` is exact on the frame it is read.
func _hard_camera(body: Node2D) -> Camera2D:
	var cam: Camera2D = null
	for c in body.get_children():
		if c is Camera2D:
			cam = c
	assert(cam != null, "the body has no Camera2D — nothing to frame the crop on")
	cam.position_smoothing_enabled = false
	cam.reset_smoothing()
	return cam


## FREEZE THE BODY IN ONE CANONICAL POSE, IMMEDIATELY BEFORE THE CAPTURE — and this
## is what made the lint NONDETERMINISTIC (three identical runs reported 8, 91 and 3
## findings). Pinning the pose once, up front, cannot work: `_process_move` calls
## `_play_directional(...)` EVERY PHYSICS FRAME, and `AnimatedSprite2D.play()` on the
## clip already showing resumes it. So the first seat pass un-paused the sprite and
## every spot afterwards was photographed at whatever frame the idle cycle happened to
## have reached — wall-clock, not frame count, because an occluded window's frames are
## not its seconds.
##
## Worse, and systematic rather than random: `push` is a direction, so the body FACES
## the way each family seats it. The reference is measured standing still (idle_down),
## so `below` (pushed north) was comparing a back view against a front view, `notch` a
## side view, and the props family all four. The head and foot lines of those clips do
## not agree to the pixel, and `_judge` reads a 2px disagreement as a clipped head.
##
## One pose for the reference and every spot makes the comparison mean what it says:
## the ONLY difference between the two silhouettes is what the scene drew over the
## body. Physics is switched off with it so nothing can re-drive the clip between the
## pin and the three captures — the seat is already finished by then, and `_silhouette`
## switches it back on before the next spot.
func _pin_pose(body: Node2D, sprite: AnimatedSprite2D) -> void:
	body.set_physics_process(false)
	sprite.animation = "idle_down"
	sprite.set_frame_and_progress(0, 0.0)
	sprite.flip_h = false
	sprite.pause()


func _far(p: PackedByteArray, q: PackedByteArray, o: int) -> bool:
	return (absi(p[o] - q[o]) > DIFF or absi(p[o + 1] - q[o + 1]) > DIFF
			or absi(p[o + 2] - q[o + 2]) > DIFF)


## THE PASS-BEHIND EXEMPTION, and it must agree with _check_art.py's rule exactly:
## two tools disagreeing about the same cell is how a real defect hides behind a
## green lint. Vanishing is NOT the defect — walking fully behind a great tree is
## the effect Alembic is built for, and Basil's hall flee is staged behind a
## curtain leg on purpose. Vanishing LONG ENOUGH TO GET LOST is: what the boardwalk
## town shipped was a ring deck running clear under an opaque shaft, every cell of
## the crossing invisible, no way over that did not leave the player gone.
##
## So the test is the length of the hidden RUN along a row: up to two cells is a
## step you pass through. Applied here as a post-pass over the findings rather than
## inside _judge, because a spot cannot know whether its NEIGHBOURS came out blank
## until they have all been captured.
## THE CELL PATTERN MUST TOLERATE EVERY FAMILY'S LABEL, and for a long time it did
## not. `pressed` labels its spot "press %d,%d h%d" — the run HEIGHT trails the cell —
## so a pattern anchoring the coordinates directly against " — THE BODY IS INVISIBLE"
## matched `notch`, `below` and `props` and silently missed EVERY pressed spot. The
## exemption above is therefore the one thing it must never be: family-dependent. An
## isolated pressed cell was reported as a hard finding while the identical situation
## in props was correctly waved through, which is how a sweep of fourteen scenes came
## back with sixteen "the body is invisible" failures of which fourteen were this.
func _drop_pass_behinds() -> void:
	var dark := {}                       # Vector2i -> the finding's index
	var rx := RegEx.new()
	rx.compile("(\\d+),(\\d+)(?: h\\d+)? — THE BODY IS INVISIBLE")
	for i in _fails.size():
		var m := rx.search(_fails[i])
		if m != null:
			dark[Vector2i(int(m.get_string(1)), int(m.get_string(2)))] = i
	var keep: Array = []
	for i in _fails.size():
		var cell: Vector2i = Vector2i(-1, -1)
		for c: Vector2i in dark:
			if dark[c] == i:
				cell = c
		if cell.x < 0:
			keep.append(_fails[i])
			continue
		var run := 1
		var d := 1
		while dark.has(Vector2i(cell.x - d, cell.y)):
			run += 1
			d += 1
		d = 1
		while dark.has(Vector2i(cell.x + d, cell.y)):
			run += 1
			d += 1
		if run <= 2:
			print("    pass-behind (run of %d): %s" % [run, _fails[i]])
			continue
		keep.append(_fails[i])
	_fails = keep


func _judge(family: String, spot: Dictionary, got: Dictionary) -> void:
	var label: String = spot["label"]
	if got["empty"]:
		_fails.append("%s  %s — THE BODY IS INVISIBLE HERE (0 px)" % [family, label])
		return
	var lost: int = int(_ref["n"]) - int(got["n"])
	var pct: float = 100.0 * lost / float(_ref["n"])
	var head: int = int(got["y0"]) - int(_ref["y0"])   # >0 = the head is clipped
	var foot: int = int(got["y1"]) - int(_ref["y1"])   # <0 = the feet are clipped
	var by_prop := _explained(got["at"])
	match family:
		"pressed":
			# The strip covers run_top..run_top+11 and the seated body's origin is
			# run_top-10, so a masked body must lose its bottom ~11 rows.
			#
			# A MANIFEST STRIP IS NOT THE ONLY LEGAL WAY TO COVER AN OVERHANG, so the
			# three non-leak outcomes are reported as themselves rather than lumped
			# under one line. There are exactly three things that can eat those 11px:
			# a Tier-3 mask strip (in the manifest, `mask_band`), the `_eave_lift`
			# UPPER-LAYER band a building facade mirrors onto itself, and ordinary
			# Tier-3 prop art sorting above the body. Only the first is in the
			# manifest, so `masked` says nothing about the other two — which is why an
			# unmasked face reading as covered is a note and not a finding.
			var masked: bool = spot.get("masked", false)
			if masked and foot > -4 and not by_prop:
				_fails.append(("pressed  %s — MASK LEAK: a strip covers this face "
						+ "but the body still draws %d px past its own foot line "
						+ "(lost only %.0f%%)") % [label, foot + 21, pct])
			elif not masked and foot <= -4:
				print("    covered without a manifest strip (eave-lift or prop art): %s"
						% label)
			elif not masked and not by_prop:
				# The overhang is genuinely uncovered. Legal — a flat-topped 2-row run
				# with no vertical face art has nothing to leak past — so it is a note.
				# It is printed because a face that GREW art and never gained a band
				# looks exactly like this, and nothing else in the suite would say so.
				print("    bare face, overhang uncovered: %s" % label)
		"below", "notch":
			# ONLY THE HEAD. A notch cell is, by the way zwalk derives it, ALWAYS
			# also the cell on top of the NEXT run down — the step is what makes it
			# a notch — so it is correctly masked at the feet, and asserting on
			# total hidden area there just reports the mask band working. The
			# failure this family exists for has always been the head: a strip that
			# clips a face against the wall beside it, or slices the top off
			# somebody hopping on the ground below.
			if head > 1 and not by_prop:
				_fails.append(("%s  %s — THE HEAD IS CLIPPED by %d px. A body "
						+ "beside or below a face must never be masked, and no prop "
						+ "art reaches it here.") % [family, label, head])
		"props":
			# INFORMATIONAL. Whether a walk-behind leaves enough of the body showing
			# is a question about the ART, and it is linted in Python against the
			# actual pixels (_check_art.py's walk-behind visibility rule) rather
			# than guessed at from a photograph.
			if pct > 8.0:
				print("    %s — %.0f%% hidden%s"
						% [label, pct, "" if by_prop else "  (NOT explained by any prop art)"])


## Every place the layering doctrine can go wrong, derived from the map itself.
func _positions() -> Dictionary:
	var solid: Dictionary = _map.solid
	var lines: PackedStringArray = _map.lines
	var cols := int(_map.cols)
	var rows := int(_map.rows)
	# Every maximal vertical run of SOLID cells that is at least 2 tall and has a
	# walkable cell due north of it — i.e. every face a body can be pressed onto.
	var runs: Array = []               # [tx, top_ty, height]
	for tx in cols:
		var ty := 0
		while ty < rows:
			if solid.has(Vector2i(tx, ty)):
				var h := 0
				while solid.has(Vector2i(tx, ty + h)):
					h += 1
				if h >= 2 and ty > 0 and not solid.has(Vector2i(tx, ty - 1)):
					runs.append([tx, ty, h])
				ty += h
			else:
				ty += 1
	var tops := {}
	for r: Array in runs:
		if not tops.has(r[0]):
			tops[r[0]] = []
		(tops[r[0]] as Array).append(r[1])
	var pressed: Array = []
	var notch: Array = []
	var below: Array = []
	# COLLAPSE THE RUNS INTO SEGMENTS FIRST. One spot per column gives 150 crops of
	# the same wall for a 44-cell band, which is noise you stop looking at. A
	# segment is consecutive columns sharing a top row — the exact grouping
	# mask_band itself emits a strip for — and the three places worth standing on
	# one are its MIDDLE and its two ENDS, because the overhang rule and the
	# tree_edge_return corners are both about what happens at an end.
	runs.sort_custom(func(a, b): return a[1] < b[1] or (a[1] == b[1] and a[0] < b[0]))
	var segs: Array = []               # [top_ty, tx0, cols, height]
	for r: Array in runs:
		if not segs.is_empty() and segs[-1][0] == r[1] \
				and segs[-1][1] + segs[-1][2] == r[0] and segs[-1][3] == r[2]:
			segs[-1][2] += 1
		else:
			segs.append([r[1], r[0], 1, r[2]])
	for sg: Array in segs:
		var ty: int = sg[0]
		var x0: int = sg[1]
		var n: int = sg[2]
		var h: int = sg[3]
		for tx in _pick(x0, n):
			var p := _spot(tx, ty - 1, Vector2.DOWN,
					"press %d,%d h%d" % [tx, ty, h])
			p["masked"] = _masked_at(tx, ty)
			pressed.append(p)
			# BELOW is seated NORTH, against the run's FOOT. A body loitering in the
			# middle of the cell below a fascia proves nothing; the case that sliced
			# heads off when the band was upper-layer tiles is the body tucked right
			# under the face, its head reaching UP into the strip.
			if not solid.has(Vector2i(tx, ty + h)) and ty + h < rows:
				below.append(_spot(tx, ty + h, Vector2.UP,
						"below %d,%d" % [tx, ty + h]))
	# NOTCH: a STEP is a neighbouring run starting exactly one row lower, and the
	# notch is the walkable cell beside this run at the neighbour's level.
	for r: Array in runs:
		var tx: int = r[0]
		var ty: int = r[1]
		for dx in [-1, 1]:
			var nb: Array = tops.get(tx + dx, [])
			if not nb.has(ty + 1):
				continue
			if not solid.has(Vector2i(tx + dx, ty)) and tx + dx >= 0 \
					and tx + dx < cols:
				# Seated SOUTH-AND-INTO the step: the notch artefact is a foot or a
				# coat-tail poking sideways over the neighbouring face, so the body
				# has to be at the very corner of its own cell rather than loose in
				# the middle of it.
				notch.append(_spot(tx + dx, ty, Vector2(-dx, 1.0).normalized(),
						"notch %d,%d" % [tx + dx, ty]))
	# PROPS: the four cells around every Tier-3 component. The manifest is the
	# source of truth for which chars are y-sorted art.
	var props: Array = []
	var seen := {}
	for chars in _prop_chars():
		for comp in _components(chars):
			var lo: Vector2i = comp[0]
			var hi: Vector2i = comp[1]
			# Seated TOWARD the prop from each side, because walk-behind is a
			# statement about the body touching the art: north of a trunk is behind
			# it, south is in front of it, and the pressed body's sunk feet must not
			# draw over a standable piece (the 2026-07-19 fence lesson).
			# The SIDE is in the label, because the assertion depends on it: south
			# of a walk-behind prop is in FRONT of it and must not be occluded,
			# north of it is behind and may be.
			for c in [[Vector2i((lo.x + hi.x) / 2, lo.y - 1), Vector2.DOWN, "N"],
					[Vector2i((lo.x + hi.x) / 2, hi.y + 1), Vector2.UP, "S"],
					[Vector2i(lo.x - 1, (lo.y + hi.y) / 2), Vector2.RIGHT, "W"],
					[Vector2i(hi.x + 1, (lo.y + hi.y) / 2), Vector2.LEFT, "E"]]:
				if seen.has(c[0]) or solid.has(c[0]):
					continue
				if c[0].x < 0 or c[0].y < 0 or c[0].x >= cols or c[0].y >= rows:
					continue
				seen[c[0]] = true
				props.append(_spot(c[0].x, c[0].y, c[1],
						"%s: %s %d,%d" % [c[2], chars, c[0].x, c[0].y]))
	return {"pressed": pressed, "notch": notch, "below": below, "props": props}


## The props manifest's `mask <png> <x> <y> <ysort>` rows, as pixel rects. The
## manifest is the AUTHORITY on where a depth strip exists — mask_band() writes
## it — so the lint never has to guess whether a face was meant to be masked, and
## the deliberately unmasked 3-cell gap at the lift gate reports as itself instead
## of as a bug.
func _read_masks() -> void:
	var path := "res://assets/tilesets/%s_props.txt" % _map_name()
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return
	while not f.eof_reached():
		var p := f.get_line().strip_edges().split(" ", false)
		if p.size() < 5 or p[0] != "mask":
			continue
		var tex: Texture2D = load("res://assets/tilesets/%s" % p[1])
		if tex == null:
			continue
		_masks.append(Rect2i(int(p[2]), int(p[3]),
				tex.get_width(), tex.get_height()))
	print("manifest carries %d mask strip(s)" % _masks.size())


func _masked_at(tx: int, ty: int) -> bool:
	for r: Rect2i in _masks:
		if r.has_point(Vector2i(tx * 16 + 8, ty * 16 + 2)):
			return true
	return false


## Every Tier-3 prop instance as {art: Rect2 in world px, sort: float} — the
## SAME arithmetic prop_spawner.gd does, because an approximation of it is worse
## than nothing here.
##
## Why the art rect and not the footprint: a prop occludes a body wherever its
## ART overlaps the body and it sorts above it, and the art is routinely NOT the
## footprint. `tree_hut` deliberately draws taller than its cells (the `rise`
## knob) so the cone stands up over the rows above; the market stall's awning is
## flush with its footprint but a body pressed north from the cell BELOW dips its
## feet into it; and `BoughLeaves` carries `base_inset=-16` precisely so the
## canopy sorts a tile south and overhangs whoever walks under it.
##
## All three of those are the walk-behind idiom working correctly, and all three
## were reported as faults by an earlier version of this lint that tested cell
## containment. A lint that cries wolf on the idiom is worse than no lint, so the
## test is now exact: occlusion is EXPLAINED if some prop's art rect meets the
## body's silhouette while sorting above it.
##
## Whether the art leaves enough of the body VISIBLE is a different question and
## is not answerable from here — it is a property of the pixels, so it is linted
## in Python where the pixels are (_check_art.py's walk-behind visibility rule).
func _read_prop_boxes() -> void:
	var path := "res://assets/tilesets/%s_props.txt" % _map_name()
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return
	while not f.eof_reached():
		var p := f.get_line().strip_edges().split(" ", false)
		if p.size() < 4 or p[0] != "prop":
			continue
		var top := -1
		var base_inset := 0.0
		var hframes := 1
		var each := false
		for opt in p.slice(4):
			if opt == "each":
				each = true
			elif opt.begins_with("anchor=top:"):
				top = int(opt.trim_prefix("anchor=top:"))
			elif opt.begins_with("base_inset="):
				base_inset = float(opt.trim_prefix("base_inset="))
			elif opt.begins_with("hframes="):
				hframes = int(opt.trim_prefix("hframes="))
		var tex: Texture2D = load("res://assets/tilesets/%s" % p[3])
		if tex == null:
			continue
		var fw := tex.get_width() / hframes
		var fh := tex.get_height()
		var rects: Array = []
		if each:
			for comp in _components(p[2]):
				rects.append(Rect2(comp[0].x * 16.0, comp[0].y * 16.0,
						(comp[1].x - comp[0].x + 1) * 16.0,
						(comp[1].y - comp[0].y + 1) * 16.0))
		else:
			rects.append(MapData.bbox_rect(_map, p[2]))
		for r: Rect2 in rects:
			var art_top: float = r.position.y + top if top >= 0 else r.end.y - fh
			_prop_box.append({
				"art": Rect2(r.get_center().x - fw * 0.5, art_top, fw, fh),
				"sort": r.end.y - base_inset - 20.0})
	print("map carries %d Tier-3 prop instance(s)" % _prop_box.size())


## Is this occlusion accounted for by a prop that legitimately sorts above the
## body and overlaps it? `body` is the origin; the silhouette rect comes from the
## reference measurement, so it is the real figure and not a guessed 22x38.
func _explained(body: Vector2) -> bool:
	var sil := Rect2(body.x + int(_ref["x0"]), body.y + int(_ref["y0"]),
			int(_ref["x1"]) - int(_ref["x0"]) + 1,
			int(_ref["y1"]) - int(_ref["y0"]) + 1)
	for d: Dictionary in _prop_box:
		if float(d["sort"]) > body.y and (d["art"] as Rect2).intersects(sil):
			return true
	return false


func _sprite_of(body: Node) -> AnimatedSprite2D:
	for c in body.get_children():
		if c is AnimatedSprite2D:
			return c
	return null


## A walkable cell with nothing solid within 3 tiles and no upper art anywhere
## near it — where the body can be measured unoccluded. The reference silhouette
## every other spot is judged against, so it must be genuinely clear; the lint
## asserts on the pixel count in case this picks somewhere shaded.
func _open_cell() -> Dictionary:
	var solid: Dictionary = _map.solid
	var cols := int(_map.cols)
	var rows := int(_map.rows)
	var best := Vector2i(-1, -1)
	var best_room := -1
	for ty in range(3, rows - 3):
		for tx in range(3, cols - 3):
			if solid.has(Vector2i(tx, ty)):
				continue
			var room := 99
			for dy in range(-3, 4):
				for dx in range(-3, 4):
					if solid.has(Vector2i(tx + dx, ty + dy)):
						room = mini(room, maxi(absi(dx), absi(dy)))
			if room > best_room:
				best_room = room
				best = Vector2i(tx, ty)
			if best_room >= 4:
				break
		if best_room >= 4:
			break
	assert(best.x >= 0, "no open cell to measure the body in")
	return {"pos": Vector2(best.x * 16 + 8, best.y * 16 + 8),
			"push": Vector2.ZERO, "label": "reference %d,%d" % [best.x, best.y]}


## A segment's middle and its two ends, de-duplicated for short segments.
func _pick(x0: int, n: int) -> Array:
	var out: Array = []
	for tx in [x0, x0 + n / 2, x0 + n - 1]:
		if not out.has(tx):
			out.append(tx)
	return out


## One photographed position, BIASED toward the face this family wants the body
## seated against. The solver then decides the final pixel: the requested spot puts
## the collision box a few px inside the wall, depenetration pushes it back out, and
## what it lands on is flush by construction rather than by the author's arithmetic.
##
## IT USED TO SET `velocity` FOR A FEW FRAMES INSTEAD, AND THAT WAS A NO-OP. A
## PartyMember re-derives its velocity from an Intent EVERY physics frame —
## `_gather_intent()` reads the Input axes (all zero under a --script tool),
## `_process_move()` writes `velocity` — so an assignment made before
## `await physics_frame` is overwritten before move_and_slide ever sees it. The
## PRESSED family happened to be seated correctly anyway, by luck: a body teleported
## to a cell's CENTRE already overlaps the solid cell south of it by 2px, because the
## box bottom sits at origin+10 in a 16px cell. The NOTCH family did not — its whole
## point is a body at the sideways CORNER of its cell, and it was sitting in the
## middle of it, testing nothing. Same class of bug as tools/academy_probe.gd's
## "moved 0 px": drive a body with polled input or with geometry, never by writing
## velocity at it.
func _spot(tx: int, ty: int, push: Vector2, label: String) -> Dictionary:
	return {"pos": Vector2(tx * 16 + 8, ty * 16 + 8) + push.normalized() * SEAT,
			"push": push, "label": label}


## The chars named by the scene's Tier-3 props manifest — the y-sorted art whose
## walk-behind reads are what the PROPS family checks.
func _prop_chars() -> Array:
	var out: Array = []
	var path := "res://assets/tilesets/%s_props.txt" % _map_name()
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return out
	while not f.eof_reached():
		var parts := f.get_line().strip_edges().split(" ", false)
		if parts.size() >= 4 and parts[0] == "prop" and not out.has(parts[2]):
			out.append(parts[2])
	return out


func _map_name() -> String:
	return (current_scene.get("MAP_PATH") as String).get_file().get_basename()


func _components(chars: String) -> Array:
	var lines: PackedStringArray = _map.lines
	var pending := {}
	for y in int(_map.rows):
		for x in (lines[y] as String).length():
			if chars.contains((lines[y] as String)[x]):
				pending[Vector2i(x, y)] = true
	var out: Array = []
	for start in pending.keys():
		if not pending.has(start):
			continue
		pending.erase(start)
		var comp: Array[Vector2i] = [start]
		var lo: Vector2i = start
		var hi: Vector2i = start
		var i := 0
		while i < comp.size():
			var c: Vector2i = comp[i]
			i += 1
			lo = Vector2i(mini(lo.x, c.x), mini(lo.y, c.y))
			hi = Vector2i(maxi(hi.x, c.x), maxi(hi.y, c.y))
			for n in [Vector2i(c.x + 1, c.y), Vector2i(c.x - 1, c.y),
					Vector2i(c.x, c.y + 1), Vector2i(c.x, c.y - 1)]:
				if pending.has(n):
					pending.erase(n)
					comp.append(n)
		out.append([lo, hi])
	return out


## Drive the body to each spot, crop the frame around it, tile the crops.
func _sheet(path: String, spots: Array) -> void:
	var party := root.get_node("Party")
	var body: Node2D = party.leader
	if not is_instance_valid(body):
		push_error("the leader was freed — a trigger fired mid-walk")
		return
	# same smoothing kill as the lint: a lagging camera slides every crop off the
	# body, and a contact sheet whose cells are not where the caption says they are
	# is worse than no contact sheet
	var cam := _hard_camera(body)
	var view := MapData.view_size()
	var rows := int(ceil(float(spots.size()) / COLS))
	var sheet: Image = null
	var scale := 1.0
	for i in spots.size():
		var spot: Dictionary = spots[i]
		# HOLD the body there for a few frames: one teleport is not enough, the
		# camera glides and the body depenetrates out of a wall over 2-3 steps.
		#
		# THE LAST FRAME MUST NOT RE-TELEPORT, and that was a real defect in this
		# harness. Assigning global_position and then awaiting means the frame that
		# runs move_and_slide sees the body INSIDE the wall and depenetrates it;
		# whatever it lands on is what gets photographed. So the requested spot is
		# a nudge, the settled spot is the truth, and the two differ by however far
		# the solver pushed. `PRESSED` in particular is only testing the mask-band
		# case if the settled box bottom ends up ON the run's top edge — which is
		# why the delta is printed rather than assumed. See _spot().
		for f in SETTLE:
			body.global_position = spot["pos"]
			body.velocity = Vector2.ZERO
			await physics_frame
		# Now let it SETTLE without being re-placed. The spot is already biased INTO
		# the face this family wants it against (see _spot), so depenetration is what
		# seats it flush — writing `velocity` here did nothing at all, because a
		# PartyMember re-derives velocity from its Intent every physics frame.
		for f in SETTLE:
			await physics_frame
		var slip: Vector2 = body.global_position - spot["pos"]
		if absf(slip.x) > 0.6 or absf(slip.y) > 0.6:
			spot["label"] = "%s  [settled %+d,%+d]" % [spot["label"],
					roundi(slip.x), roundi(slip.y)]
		cam.reset_smoothing()
		await process_frame
		RenderingServer.force_draw()
		var frame := root.get_viewport().get_texture().get_image()
		if sheet == null:
			scale = float(frame.get_width()) / view.x
			sheet = Image.create(int(COLS * CROP * scale),
					int(rows * CROP * scale), false, frame.get_format())
			sheet.fill(Color(0.06, 0.05, 0.11))
		# where the body actually IS on screen — the camera clamps at the map
		# edges, so it is NOT always the centre of the frame
		var on_screen: Vector2 = (body.global_position
				- cam.get_screen_center_position() + view * 0.5) * scale
		var half := CROP * scale * 0.5
		var want := Rect2i(Vector2i(on_screen - Vector2(half, half)),
				Vector2i(int(CROP * scale), int(CROP * scale)))
		var src := want.intersection(Rect2i(Vector2i.ZERO, frame.get_size()))
		if src.size.x <= 0 or src.size.y <= 0:
			continue
		# SHIFT THE DESTINATION BY WHATEVER THE CLIP TOOK. Near a map edge the
		# camera stops following, so the body is off-centre and `want` hangs off
		# the frame; blitting the clipped rect at the cell's corner anyway slides
		# every one of those crops sideways and the body stops being where the
		# sheet says it is — which is worse than a missing crop, because you read
		# the wrong cell and trust it.
		var dst := Vector2i(int((i % COLS) * CROP * scale),
				int((i / COLS) * CROP * scale)) + (src.position - want.position)
		sheet.blit_rect(frame, src, dst)
	if sheet != null:
		sheet.save_png(path + ".png")
		print("  wrote ", path, ".png  (", spots.size(), " spots)")
		var f := FileAccess.open(path + ".txt", FileAccess.WRITE)
		for i in spots.size():
			f.store_line("%d,%d  %s" % [i % COLS, i / COLS, spots[i]["label"]])
