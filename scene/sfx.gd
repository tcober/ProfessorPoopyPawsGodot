extends Node

## SFX — one-shot sounds, the Music autoload's little sibling. The wavs come
## out of assets/_gen_sfx.py (regenerate -> `godot --headless --import`, same
## as art). A small round-robin pool of players, so a cursor tick can never
## cut off a chime; everything processes while PAUSED because the pause
## modals are the main customers. Deliberately references no other autoload,
## so a --script probe can never poison its compile.
##
## THE TALK BLIPS are the Star Fox trick: one neutral synthesized syllable per
## timbre, cast per speaker through pitch_scale. VOICES pins the named cast
## (a = the standard cat, b = the lighter voices, c = the gruff old-animal
## reed); anyone unlisted gets a stable voice hashed off their name, so a
## one-scene stranger still sounds like themselves the whole conversation.
## Each blip jitters a few percent around the speaker's pitch — that wobble,
## not the wav, is what reads as speech.

const DIR := "res://assets/audio/"

## key -> [file, volume_db]. Volumes are the mix: the blips sit under the
## dialog text, the advance tick is nearly subliminal, the chime carries.
const SOUNDS := {
	"cursor": ["sfx_cursor.wav", -8.0],
	"accept": ["sfx_accept.wav", -7.0],
	"back": ["sfx_back.wav", -9.0],
	"open": ["sfx_open.wav", -8.0],
	"chime": ["sfx_chime.wav", -7.0],
	"refuse": ["sfx_refuse.wav", -8.0],
	"advance": ["sfx_advance.wav", -14.0],
	"door": ["sfx_door.wav", -10.0],
	"voice_a": ["sfx_voice_a.wav", -12.0],
	"voice_b": ["sfx_voice_b.wav", -13.0],
	"voice_c": ["sfx_voice_c.wav", -12.0],
}

## speaker (lowercased) -> [timbre, base pitch]. Kids sit high, the mayor is
## an old elk, the goose is a goose.
const VOICES := {
	"basil": ["voice_a", 1.0],
	"fuji": ["voice_b", 1.12],
	"kitty": ["voice_b", 1.24],
	"sage": ["voice_b", 1.18],
	"mom": ["voice_b", 0.94],
	"kitty's mother": ["voice_b", 0.88],
	"schweinler": ["voice_c", 1.18],
	"mayor hollis": ["voice_c", 0.78],
	"professor strix": ["voice_c", 0.92],
	"dean strix": ["voice_c", 0.92],
	"dr. ciconia": ["voice_c", 1.0],
	"dr. feathers": ["voice_b", 1.05],
	"ridley": ["voice_a", 0.84],
	"goose": ["voice_c", 1.5],
}

const POOL := 6

var _streams := {}
var _players: Array[AudioStreamPlayer] = []
var _next := 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for key: String in SOUNDS:
		_streams[key] = load(DIR + SOUNDS[key][0])
	for i in POOL:
		var p := AudioStreamPlayer.new()
		p.bus = "Master"
		add_child(p)
		_players.append(p)


func play(key: String, pitch: float = 1.0, vol_offset: float = 0.0) -> void:
	if not _streams.has(key):
		return
	var p := _players[_next]
	_next = (_next + 1) % POOL
	p.stream = _streams[key]
	p.volume_db = SOUNDS[key][1] + vol_offset
	p.pitch_scale = pitch
	p.play()


# --- the menu verbs ------------------------------------------------------------

func ui_move() -> void:
	play("cursor")


func ui_accept() -> void:
	play("accept")


func ui_back() -> void:
	play("back")


func ui_open() -> void:
	play("open")


func ui_chime() -> void:
	play("chime")


func ui_refuse() -> void:
	play("refuse")


# --- dialogue and doors --------------------------------------------------------

func talk_advance() -> void:
	play("advance")


func door() -> void:
	play("door")


## One syllable of a speaker's voice. Unknown names hash to a stable pitch so
## a voice can't drift mid-conversation; the per-blip jitter is what talks.
func talk_blip(speaker: String) -> void:
	var timbre := "voice_a"
	var base := 1.0
	var key := speaker.to_lower()
	if VOICES.has(key):
		timbre = VOICES[key][0]
		base = VOICES[key][1]
	elif key != "":
		base = 0.9 + float(abs(key.hash()) % 7) * 0.05
	# Pitching a blip up moves it into the ear's most sensitive band, so the
	# high voices (Kitty, the goose) read louder at the same volume_db. Trade
	# dB for pitch above 1.0 only — the low voices are dull, not loud.
	var cast := base * randf_range(0.94, 1.06)
	play(timbre, cast, minf(0.0, -6.0 * (cast - 1.0)))
