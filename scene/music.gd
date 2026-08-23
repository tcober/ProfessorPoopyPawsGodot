extends Node

## MUSIC — the soundtrack autoload. The four looping tracks come out of
## assets/_gen_music.py (regenerate -> `godot --headless --import`, same as
## art). Which track plays is a pure function of the CURRENT SCENE, polled
## here every frame — so no scene file wires its own music, the dev chapter
## selector gets the right track for free, and a scene NOT in the table keeps
## whatever is already playing (the SNES door rule: the town theme follows
## you into a house).
##
## An empty-string entry means fade to silence (the accident, the Ebb quake,
## the cold-open cards — beats that music would undercut). Story scenes that
## ever need a hand on the fader can call Music.play()/Music.stop() directly.
##
## Crossfades are stepped by hand in _process — the project's menus poll for
## the same reason — and the node processes while PAUSED so the pause modals
## don't stop the band. Deliberately references no other autoload, so a
## --script probe can never poison its compile.

const TRACKS := {
	"title": "res://assets/audio/title_theme.wav",
	"overworld": "res://assets/audio/overworld_theme.wav",
	"town": "res://assets/audio/town_theme.wav",
	"ebb": "res://assets/audio/ebb_theme.wav",
}

const SCENE_TRACKS := {
	"res://scene/title.tscn": "title",
	"res://scene/overworld.tscn": "overworld",
	"res://scene/overworld_bright.tscn": "overworld",
	"res://scene/meadow.tscn": "overworld",
	"res://scene/alembic_town.tscn": "town",
	"res://scene/academy.tscn": "town",
	"res://scene/academy_library.tscn": "town",
	"res://scene/hall.tscn": "town",
	"res://scene/house.tscn": "town",
	"res://scene/house_fest.tscn": "town",
	"res://scene/house_fever.tscn": "town",
	"res://scene/house_thesis.tscn": "town",
	"res://scene/downstairs.tscn": "town",
	"res://scene/downstairs_fest.tscn": "town",
	"res://scene/downstairs_fever.tscn": "town",
	"res://scene/momroom.tscn": "town",
	"res://scene/sickroom.tscn": "town",
	"res://scene/town_fest.tscn": "town",
	"res://scene/town_fever.tscn": "town",
	"res://scene/town_thesis.tscn": "town",
	"res://scene/bluff.tscn": "town",
	"res://scene/lanternwood.tscn": "ebb",
	"res://scene/library.tscn": "ebb",
	"res://scene/ebb.tscn": "",
	"res://scene/accident.tscn": "",
	"res://scene/prologue_open.tscn": "",
}

const FADE := 1.4                  # seconds, full crossfade
const VOL_DB := -9.0               # the music's place under dialog and sfx

var _players: Array[AudioStreamPlayer] = []
var _level := [0.0, 0.0]           # fade position per player, 0..1
var _target := [0.0, 0.0]
var _active := -1                  # player index carrying _current, -1 = none
var _current := ""


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for i in 2:
		var p := AudioStreamPlayer.new()
		p.bus = "Master"
		add_child(p)
		_players.append(p)


func _process(delta: float) -> void:
	var sc := get_tree().current_scene
	if sc != null and SCENE_TRACKS.has(sc.scene_file_path):
		var want: String = SCENE_TRACKS[sc.scene_file_path]
		if want != _current:
			play(want)
	for i in 2:
		if _level[i] == _target[i]:
			continue
		_level[i] = move_toward(_level[i], _target[i], delta / FADE)
		_players[i].volume_db = VOL_DB + linear_to_db(maxf(_level[i], 0.001))
		if _level[i] == 0.0 and i != _active:
			_players[i].stop()


## Crossfade to a named track ("" fades to silence). Re-requesting the track
## already playing is a no-op, so scenes and the poll above can both call this
## without fighting.
func play(track: String) -> void:
	if track == _current:
		return
	_current = track
	if track == "" or not TRACKS.has(track):
		for i in 2:
			_target[i] = 0.0
		_active = -1
		return
	var next := 0 if _active != 0 else 1
	var p := _players[next]
	p.stream = load(TRACKS[track])
	p.volume_db = VOL_DB + linear_to_db(0.001)
	p.play()
	_target[next] = 1.0
	if _active >= 0:
		_target[_active] = 0.0
	_active = next


func stop() -> void:
	play("")
