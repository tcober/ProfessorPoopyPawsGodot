#!/usr/bin/env python3
"""The sound-effect pipeline — one-shot UI and dialogue sounds, synthesized by
the same doctrine as the music: stdlib-only, deterministic, never hand-edited
after the fact, regenerate -> `godot --headless --import`.

The register is the SNES menu vocabulary: short square/triangle blips with a
pitch glide and a fast envelope, nothing longer than half a second. Every
sound is mono (a menu has no stereo position) and NON-looping — the .import
pins loop_mode=0 where the music pins Forward.

  sfx_cursor    menu cursor move — one dry tick
  sfx_accept    confirm — a rising fourth, two quick notes
  sfx_back      cancel/close — the accept inverted, falling and quieter
  sfx_open      a menu opening — three-note up-arpeggio over a breath of noise
  sfx_chime     "something was made/recorded" — save, a successful mix
  sfx_refuse    "no" — two dull low buzzes
  sfx_advance   dialogue advance — a tiny click, nearly subliminal
  sfx_door      scene travel — a low whump under a noise swish
  sfx_voice_*   the talk blips (a/b/c) — three timbres of Star-Fox-style
                syllable, pitched per speaker at runtime (scene/sfx.gd VOICES,
                pitch_scale does the casting; the wav is one neutral syllable)

Voice design: a blip reads as a VOICE, not a beep, because the pitch falls
across the syllable (speech declines), the wave is lowpassed round, and a
quiet upper partial sits in for a formant. a = the standard cat (rounded
pulse), b = the lighter voices (triangle + octave), c = the gruff old-animal
reed (slow-vibrato saw).
"""
import math
import os
import struct
from array import array

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "audio")
RATE = 32000
TAU = math.tau


def _seg(buf, t0, dur, f0, f1=None, wave="pulse", duty=0.5, vol=0.5,
         attack=0.004, release=0.03, soft=1.0, vib_rate=0.0, vib_depth=0.0):
    """One tone into buf: linear pitch glide f0->f1 over dur, attack/release
    envelope, optional one-pole lowpass and vibrato. The whole synth."""
    if f1 is None:
        f1 = f0
    n0 = int(t0 * RATE)
    n = int((dur + release) * RATE)
    if n0 + n > len(buf):
        buf.extend(0.0 for _ in range(n0 + n - len(buf)))
    ph = 0.0
    y = 0.0
    state = (n0 * 2654435761 + int(f0 * 977)) & 0x7FFFFFFF or 1
    sin = math.sin
    for i in range(n):
        t = i / RATE
        f = f0 + (f1 - f0) * min(t / dur, 1.0)
        if vib_depth:
            f *= 1.0 + vib_depth * sin(TAU * vib_rate * t)
        if t < dur:
            env = min(t / attack, 1.0)
        else:
            env = max(0.0, 1.0 - (t - dur) / release)
        ph += f / RATE
        p = ph - int(ph)
        if wave == "pulse":
            v = 1.0 if p < duty else -1.0
        elif wave == "tri":
            v = 4.0 * p - 1.0 if p < 0.5 else 3.0 - 4.0 * p
        elif wave == "saw":
            v = 2.0 * p - 1.0
        elif wave == "sine":
            v = sin(TAU * p)
        else:                                   # noise — xorshift, deterministic
            state ^= (state << 13) & 0x7FFFFFFF
            state ^= state >> 17
            state ^= (state << 5) & 0x7FFFFFFF
            v = state / 1073741823.5 - 1.0
        if soft < 1.0:
            y += soft * (v - y)                 # one-pole lowpass
            v = y
        buf[n0 + i] += vol * env * v


def _write(name, buf):
    """Normalize to a common peak and write a mono 16-bit non-looping WAV.
    No smpl chunk — a sound effect must never loop."""
    peak = max((abs(v) for v in buf), default=1.0)
    k = 0.8 / (peak or 1.0)
    pcm = array("h", (int(max(-1.0, min(1.0, v * k)) * 32767) for v in buf))
    data = pcm.tobytes()
    fmt = struct.pack("<HHIIHH", 1, 1, RATE, RATE * 2, 2, 16)
    riff_len = 4 + (8 + len(fmt)) + (8 + len(data))
    path = os.path.join(OUT, name)
    with open(path, "wb") as f:
        f.write(struct.pack("<4sI4s", b"RIFF", riff_len, b"WAVE"))
        f.write(struct.pack("<4sI", b"fmt ", len(fmt)) + fmt)
        f.write(struct.pack("<4sI", b"data", len(data)) + data)
    _ensure_import(name)
    print(f"  {name}  {len(buf) / RATE * 1000:.0f}ms")


_IMPORT = """[remap]

importer="wav"
type="AudioStreamWAV"

[deps]

source_file="res://assets/audio/{name}"

[params]

force/8_bit=false
force/mono=false
force/max_rate=false
force/max_rate_hz=44100
edit/trim=false
edit/normalize=false
edit/loop_mode=0
edit/loop_begin=0
edit/loop_end=-1
compress/mode=0
"""


def _ensure_import(name):
    """Written only when missing — Godot fills in uid/path on first import and
    that fill-in must survive regeneration (the _gen_music.py rule)."""
    p = os.path.join(OUT, name + ".import")
    if not os.path.exists(p):
        with open(p, "w") as f:
            f.write(_IMPORT.format(name=name))


# ---- the menu set --------------------------------------------------------------

def cursor():
    b = []
    _seg(b, 0.0, 0.03, 1700, 1480, wave="pulse", duty=0.25, vol=0.5,
         attack=0.002, release=0.02, soft=0.6)
    _write("sfx_cursor.wav", b)


def accept():
    b = []
    _seg(b, 0.00, 0.045, 1040, wave="pulse", duty=0.3, vol=0.45,
         attack=0.002, release=0.03, soft=0.6)
    _seg(b, 0.05, 0.09, 1390, wave="pulse", duty=0.3, vol=0.5,
         attack=0.002, release=0.06, soft=0.6)
    _write("sfx_accept.wav", b)


def back():
    b = []
    _seg(b, 0.00, 0.04, 1240, wave="pulse", duty=0.4, vol=0.4,
         attack=0.002, release=0.025, soft=0.5)
    _seg(b, 0.045, 0.07, 930, wave="pulse", duty=0.4, vol=0.38,
         attack=0.002, release=0.05, soft=0.5)
    _write("sfx_back.wav", b)


def open_menu():
    b = []
    _seg(b, 0.0, 0.14, 40, wave="noise", vol=0.16, attack=0.01,
         release=0.06, soft=0.25)
    for k, f in enumerate((660, 990, 1320)):
        _seg(b, k * 0.035, 0.035, f, wave="pulse", duty=0.3, vol=0.4,
             attack=0.002, release=0.05, soft=0.6)
    _write("sfx_open.wav", b)


def chime():
    """The 'it went in the record' sparkle — save, a successful mix. Two
    passes of the same four-note figure, the second quiet and late for an
    echo the wav carries itself (no runtime reverb exists to lean on)."""
    notes = (1318.5, 1568.0, 1975.5, 2637.0)          # E6 G6 B6 E7
    b = []
    for vol, t0 in ((0.45, 0.0), (0.16, 0.22)):
        for k, f in enumerate(notes):
            _seg(b, t0 + k * 0.07, 0.02, f, wave="sine", vol=vol,
                 attack=0.002, release=0.26)
            _seg(b, t0 + k * 0.07, 0.02, f * 2.0, wave="sine", vol=vol * 0.25,
                 attack=0.002, release=0.18)
    _write("sfx_chime.wav", b)


def refuse():
    b = []
    for t0 in (0.0, 0.11):
        _seg(b, t0, 0.07, 225, 205, wave="pulse", duty=0.5, vol=0.5,
             attack=0.003, release=0.03, soft=0.35)
    _write("sfx_refuse.wav", b)


def advance():
    b = []
    _seg(b, 0.0, 0.012, 40, wave="noise", vol=0.25, attack=0.001,
         release=0.01, soft=0.3)
    _seg(b, 0.0, 0.02, 1000, 780, wave="sine", vol=0.35, attack=0.002,
         release=0.02)
    _write("sfx_advance.wav", b)


def door():
    b = []
    _seg(b, 0.0, 0.16, 40, wave="noise", vol=0.5, attack=0.05,
         release=0.1, soft=0.12)
    _seg(b, 0.02, 0.15, 300, 170, wave="sine", vol=0.4, attack=0.02,
         release=0.09)
    _write("sfx_door.wav", b)


# ---- the voices ----------------------------------------------------------------

def voice_a():
    """Attacks ~9ms and a rounder lowpass than the menu set on purpose: a blip
    fires every ~75ms for whole conversations, and a clicky edge at that rate
    is a typewriter, not a voice. The peak normalizer can't see waveform
    energy, so the pulse also needs the deepest filter of the three."""
    b = []
    _seg(b, 0.0, 0.065, 300, 235, wave="pulse", duty=0.35, vol=0.55,
         attack=0.009, release=0.035, soft=0.35)
    _seg(b, 0.0, 0.065, 900, 705, wave="pulse", duty=0.25, vol=0.07,
         attack=0.009, release=0.025, soft=0.5)
    _write("sfx_voice_a.wav", b)


def voice_b():
    b = []
    _seg(b, 0.0, 0.06, 430, 370, wave="tri", vol=0.6,
         attack=0.008, release=0.03, soft=0.55)
    _seg(b, 0.0, 0.06, 860, 740, wave="sine", vol=0.14,
         attack=0.008, release=0.025)
    _write("sfx_voice_b.wav", b)


def voice_c():
    b = []
    _seg(b, 0.0, 0.08, 205, 168, wave="saw", vol=0.55,
         attack=0.010, release=0.04, soft=0.26, vib_rate=28.0, vib_depth=0.04)
    _write("sfx_voice_c.wav", b)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("sfx:")
    cursor()
    accept()
    back()
    open_menu()
    chime()
    refuse()
    advance()
    door()
    voice_a()
    voice_b()
    voice_c()
