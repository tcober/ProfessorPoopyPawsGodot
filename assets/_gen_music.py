#!/usr/bin/env python3
"""The music pipeline — four looping SNES-register tracks, composed as note
tables and synthesized to WAV by the same doctrine as the art: stdlib-only,
deterministic, never hand-edited after the fact.

The register is early-90s Square: a small fixed voice ensemble (pulse lead
with delayed vibrato, triangle harp/bass, soft detuned pad, echo on a musical
delay), each track a short hand-composed loop rather than anything generative.
The four tracks and where scene/music.gd plays them:

  title_theme.wav      "Golden Hour"     — the FF-prelude move: a two-octave
                       harp arpeggio rolling under a plaintive lead, over the
                       lament-bass descent (A G F E D C B E). Am, 72bpm.
  overworld_theme.wav  "Wide Is the World" — heroic dotted-rhythm travel
                       theme, walking bass, light noise kit. F, 108bpm.
  town_theme.wav       "Kettle and Vine" — a gentle waltz for hearths and
                       market lanes. G, 3/4, 100bpm.
  ebb_theme.wav        "The Quiet"       — the drained world: a music-box
                       fragment lost in a one-second echo over a bare drone,
                       wind underneath. Em, 58bpm.

LOOPING: each track renders its loop length plus a 4s tail (releases + echo
decay past the loop point), then FOLDS the tail back onto the loop's head —
so bar 1 already carries bar 16's reverb and the seam is inaudible. The WAV
embeds a smpl loop chunk AND the generator writes a .import pinning
edit/loop_mode=Forward (belt and suspenders — either alone loops in Godot).
The .import is only written when missing, so Godot's uid/path fill-in
survives regeneration.

Pure-python synthesis at 32000Hz (the SNES's own rate) takes ~10-30s per
track; it runs once per composition change, like every other generator.
"""
import math
import os
import struct
from array import array

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "audio")
RATE = 32000
TAU = math.tau

# ---- notes ---------------------------------------------------------------------

_OFF = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def N(name):
    """'A4' / 'C#5' / 'Bb3' -> midi number."""
    off = _OFF[name[0]]
    i = 1
    if name[i] == "#":
        off += 1
        i += 1
    elif name[i] == "b":
        off -= 1
        i += 1
    return 12 * (int(name[i:]) + 1) + off


def hz(midi):
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)


# ---- the synth -----------------------------------------------------------------
# An instrument is a dict: wave (pulse/tri/saw/sine/noise) + ADSR + optional
# delayed vibrato + a one-pole lowpass (soft<1) + detune voices. Values are in
# seconds and fractions; gain is the channel's place in the mix, set once per
# track and never per note (velocity scales it).


def _render_note(buf, start_s, freq, dur_s, inst, vel):
    a = inst.get("attack", 0.008)
    d = inst.get("decay", 0.12)
    s = inst.get("sustain", 0.8)
    r = inst.get("release", 0.18)
    wave = inst["wave"]
    duty = inst.get("duty", 0.5)
    vib_rate = inst.get("vib_rate", 5.5)
    vib_depth = inst.get("vib_depth", 0.0)
    vib_delay = inst.get("vib_delay", 0.25)
    soft = inst.get("soft", 1.0)
    gain = inst.get("gain", 0.3) * vel
    voices = inst.get("voices", ((1.0, 1.0),))

    n0 = int(start_s * RATE)
    end = min(n0 + int((dur_s + r) * RATE), len(buf))
    sin = math.sin
    for (fmul, gmul) in voices:
        f0 = freq * fmul
        g = gain * gmul
        ph = 0.0
        y = 0.0
        state = (n0 * 2654435761 + int(f0 * 977)) & 0x7FFFFFFF or 1
        for i in range(n0, end):
            t = (i - n0) / RATE
            if t < a:
                env = t / a
            elif t < a + d:
                env = 1.0 - (1.0 - s) * (t - a) / d
            elif t < dur_s:
                env = s
            else:
                env = s * (1.0 - (t - dur_s) / r)
                if env <= 0.0:
                    break
            f = f0
            if vib_depth and t > vib_delay:
                f = f0 * (1.0 + vib_depth * sin(TAU * vib_rate * (t - vib_delay)))
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
            buf[i] += g * env * v


def seq(pairs, start=0.0):
    """Compact melody entry: [(dur_beats, note_or_None[, vel]), ...] consumed
    left to right from `start`. None is a rest. Returns event tuples."""
    ev = []
    b = start
    for p in pairs:
        dur, note = p[0], p[1]
        if note is not None:
            ev.append((b, dur, note, p[2] if len(p) > 2 else 1.0))
        b += dur
    return ev


_QUAL = {"maj": (0, 4, 7), "min": (0, 3, 7), "dim": (0, 3, 6), "sus4": (0, 5, 7)}


def arp_bar(root_name, qual, bar_start):
    """One bar of the prelude figure: 16ths, two octaves up (8) then down (7),
    with the bar's last 16th left as a breath. Root names the arp's low note."""
    r = N(root_name)
    iv = _QUAL[qual]
    lad = [r + o + i for o in (0, 12, 24) for i in iv][:8]
    ev = []
    for k in range(8):
        ev.append((bar_start + k * 0.25, 0.26, lad[k], 1.0))
    for k in range(7):
        ev.append((bar_start + 2.0 + k * 0.25, 0.26, lad[6 - k], 0.9))
    return ev


def render_track(path, bpm, beats, channels, echo_delay_beats, echo_fb, echo_lvl):
    """Mix channels (each: inst/events/pan/echo-send), run the echo bus, fold
    the tail over the loop head, normalize, write a looping WAV."""
    spb = 60.0 / bpm
    loop = int(round(beats * spb * RATE))
    tail = int(RATE * 4.0)
    total = loop + tail
    dry_l = [0.0] * total
    dry_r = [0.0] * total
    bus = [0.0] * total

    for ch in channels:
        mono = [0.0] * total
        inst = ch["inst"]
        for (b, dur, note, vel) in ch["events"]:
            midi = N(note) if isinstance(note, str) else note
            _render_note(mono, b * spb, hz(midi), dur * spb, inst, vel)
        pan = ch.get("pan", 0.0)
        gl = math.cos((pan + 1.0) * math.pi / 4.0)
        gr = math.sin((pan + 1.0) * math.pi / 4.0)
        send = ch.get("echo", 0.0)
        for i in range(total):
            v = mono[i]
            if v:
                dry_l[i] += v * gl
                dry_r[i] += v * gr
                if send:
                    bus[i] += v * send

    # the echo: one feedback delay on a musical subdivision, right side heard
    # half a delay late for width — the SNES echo block, near enough.
    dly = max(1, int(echo_delay_beats * spb * RATE))
    for i in range(dly, total):
        bus[i] += echo_fb * bus[i - dly]
    half = dly // 2
    for i in range(total):
        e = bus[i]
        if e:
            dry_l[i] += echo_lvl * e
            if i + half < total:
                dry_r[i + half] += echo_lvl * e

    # fold the tail back over the head — this is what makes the loop seamless
    for i in range(tail):
        dry_l[i] += dry_l[loop + i]
        dry_r[i] += dry_r[loop + i]

    peak = max(max(abs(v) for v in dry_l[:loop]), max(abs(v) for v in dry_r[:loop]))
    k = 0.88 / (peak or 1.0)
    pcm = array("h", bytes(4 * loop))
    for i in range(loop):
        pcm[2 * i] = int(max(-1.0, min(1.0, dry_l[i] * k)) * 32767)
        pcm[2 * i + 1] = int(max(-1.0, min(1.0, dry_r[i] * k)) * 32767)
    _write_wav(path, pcm, loop)
    print(f"  {os.path.basename(path)}  {loop / RATE:.1f}s loop")


def _write_wav(path, pcm, frames):
    """16-bit stereo WAV with a smpl chunk looping the whole file."""
    data = pcm.tobytes()
    fmt = struct.pack("<HHIIHH", 1, 2, RATE, RATE * 4, 4, 16)
    smpl = struct.pack("<9I", 0, 0, 1000000000 // RATE, 60, 0, 0, 0, 1, 0) \
        + struct.pack("<6I", 0, 0, 0, frames - 1, 0, 0)
    riff_len = 4 + (8 + len(fmt)) + (8 + len(data)) + (8 + len(smpl))
    with open(path, "wb") as f:
        f.write(struct.pack("<4sI4s", b"RIFF", riff_len, b"WAVE"))
        f.write(struct.pack("<4sI", b"fmt ", len(fmt)) + fmt)
        f.write(struct.pack("<4sI", b"data", len(data)) + data)
        f.write(struct.pack("<4sI", b"smpl", len(smpl)) + smpl)


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
edit/loop_mode=2
edit/loop_begin=0
edit/loop_end=-1
compress/mode=0
"""


def _ensure_import(name):
    """Written only when missing — Godot fills in uid/path on first import and
    that fill-in must survive regeneration."""
    p = os.path.join(OUT, name + ".import")
    if not os.path.exists(p):
        with open(p, "w") as f:
            f.write(_IMPORT.format(name=name))


# ---- the instruments (shared across tracks; gain is set per channel) -----------

def lead(**kw):
    base = dict(wave="pulse", duty=0.25, attack=0.02, decay=0.25, sustain=0.72,
                release=0.22, vib_depth=0.007, vib_rate=5.2, vib_delay=0.28,
                soft=0.55, gain=0.26)
    base.update(kw)
    return base


def harp(**kw):
    base = dict(wave="tri", attack=0.004, decay=0.30, sustain=0.0, release=0.10,
                gain=0.30)
    base.update(kw)
    return base


def bass(**kw):
    base = dict(wave="tri", attack=0.01, decay=0.10, sustain=0.85, release=0.15,
                gain=0.34)
    base.update(kw)
    return base


def pad(**kw):
    base = dict(wave="pulse", duty=0.5, attack=0.6, decay=0.4, sustain=0.7,
                release=0.9, soft=0.25, gain=0.075,
                voices=((1.0, 1.0), (1.004, 0.8)))
    base.update(kw)
    return base


# =================================================================================
# TITLE — "Golden Hour" (Am, 72bpm, 16 bars of 4/4, 53.3s)
# The lament-bass descent in 2-bar strides: Am  Em/G  F  C/E  Dm  Am/C  Bdim  E.
# The harp rolls the prelude figure over it; the lead keeps to long plaintive
# steps and lands the loop on G# so the pull back to Am IS the loop point.
# =================================================================================

def title_theme():
    chords = [("A3", "min"), ("E3", "min"), ("F3", "maj"), ("C3", "maj"),
              ("D3", "min"), ("A3", "min"), ("B3", "dim"), ("E3", "maj")]
    arp = []
    for ci, (root, qual) in enumerate(chords):
        arp += arp_bar(root, qual, ci * 8.0)
        arp += arp_bar(root, qual, ci * 8.0 + 4.0)
    # bar 15 suspends the dominant (sus4), bar 16 resolves it to E major —
    # so the last thing before the seam is the pull back home to Am
    arp = [e for e in arp if not (56.0 <= e[0] < 60.0)] + arp_bar("E3", "sus4", 56.0)

    melody = seq([
        (4, None),                                       # b1   the harp alone
        (2, None), (0.5, "E4"), (0.5, "G4"), (1, "A4"),  # b2   pickup
        (3, "B4"), (0.5, "A4"), (0.5, "G4"),             # b3   Em/G
        (3, "E4"), (1, None),                            # b4
        (2, "A4"), (1, "C5"), (1, "D5"),                 # b5   F
        (3, "C5"), (1, "A4"),                            # b6
        (2, "E5"), (1, "D5"), (1, "C5"),                 # b7   C/E
        (4, "G4"),                                       # b8
        (1.5, "F4"), (0.5, "G4"), (2, "A4"),             # b9   Dm
        (2.5, "D5"), (0.5, "C5"), (1, "A4"),             # b10
        (2, "E5"), (2, "C5"),                            # b11  Am/C
        (4, "A4"),                                       # b12
        (2, "B4"), (2, "D5"),                            # b13  Bdim
        (2, "F5"), (1, "E5"), (1, "D5"),                 # b14
        (2, "B4"), (1, "A4"), (1, "B4"),                 # b15  Esus4
        (3, "G#4"), (1, None),                           # b16  -> Am, the seam
    ])

    bass_ev = seq([(8, n) for n in
                   ("A2", "G2", "F2", "E2", "D2", "C2", "B1", "E2")])

    pads = []
    triads = [("A3", "C4", "E4"), ("G3", "B3", "E4"), ("A3", "C4", "F4"),
              ("G3", "C4", "E4"), ("F3", "A3", "D4"), ("E3", "A3", "C4"),
              ("F3", "B3", "D4"), ("E3", "B3", "E4")]
    for ci, tri in enumerate(triads):
        for note in tri:
            pads.append((ci * 8.0, 7.8, note, 1.0))

    render_track(os.path.join(OUT, "title_theme.wav"), 72, 64, [
        dict(inst=harp(gain=0.20), events=arp, pan=-0.35, echo=0.5),
        dict(inst=lead(), events=melody, pan=0.12, echo=0.75),
        dict(inst=bass(gain=0.32), events=bass_ev, pan=0.0, echo=0.0),
        dict(inst=pad(), events=pads, pan=0.35, echo=0.2),
    ], echo_delay_beats=0.75, echo_fb=0.4, echo_lvl=0.42)


# =================================================================================
# OVERWORLD — "Wide Is the World" (F, 108bpm, 16 bars, 35.6s)
# A section heroic (dotted rhythms, fourth-leaps), B section lyrical and higher,
# peaking bar 14 before it hands back to the A. Walking triangle bass in
# root-fifth-octave, brushed noise kit underneath.
# =================================================================================

def overworld_theme():
    melody = seq([
        (1.5, "F4"), (0.5, "G4"), (2, "A4"),              # b1
        (1.5, "C5"), (0.5, "Bb4"), (1, "A4"), (1, "G4"),  # b2
        (1, "Bb4"), (1, "D5"), (1.5, "C5"), (0.5, "Bb4"), # b3
        (2, "A4"), (2, "F4"),                             # b4
        (1.5, "D5"), (0.5, "E5"), (2, "F5"),              # b5
        (1, "D5"), (1, "Bb4"), (2, "G4"),                 # b6
        (1.5, "A4"), (0.5, "G4"), (1, "E4"), (1, "G4"),   # b7
        (3, "F4"), (1, "C5"),                             # b8  pickup lifts to B
        (2, "D5"), (1, "E5"), (1, "F5"),                  # b9
        (1.5, "D5"), (0.5, "C5"), (2, "Bb4"),             # b10
        (1, "A4"), (1, "C5"), (2, "F5"),                  # b11
        (2, "E5"), (1, "C5"), (1, "G4"),                  # b12
        (1.5, "F5"), (0.5, "E5"), (2, "D5"),              # b13
        (1, "Bb4"), (1, "D5"), (2, "G5"),                 # b14  the peak
        (1.5, "E5"), (0.5, "D5"), (1, "E5"), (1, "D5"),   # b15
        (1, "C5"), (1, "A4"), (2, "F4"),                  # b16
    ])

    roots = ["F2", "F2", "Bb2", "F2", "D2", "Bb2", "C2", "F2",
             "D2", "Bb2", "F2", "C2", "D2", "G2", "C2", "F2"]
    bass_ev = []
    for bi, r in enumerate(roots):
        m = N(r)
        for k, off in enumerate((0, 7, 12, 7)):
            bass_ev.append((bi * 4.0 + k, 0.9, m + off, 1.0 if k == 0 else 0.8))

    guides = [("A3", "C4"), ("A3", "C4"), ("Bb3", "D4"), ("A3", "C4"),
              ("A3", "D4"), ("Bb3", "D4"), ("G3", "C4"), ("A3", "C4"),
              ("A3", "D4"), ("Bb3", "D4"), ("A3", "C4"), ("G3", "C4"),
              ("A3", "D4"), ("Bb3", "D4"), ("G3", "C4"), ("A3", "C4")]
    pads = [(bi * 4.0, 3.8, n, 1.0) for bi, pair in enumerate(guides) for n in pair]

    hat = dict(wave="noise", attack=0.001, decay=0.03, sustain=0.0, release=0.02,
               soft=0.9, gain=0.05)
    snare = dict(wave="noise", attack=0.001, decay=0.09, sustain=0.0, release=0.05,
                 soft=0.5, gain=0.10)
    hats = [(b * 0.5, 0.05, 84, 1.0 if b % 2 == 0 else 0.6) for b in range(128)]
    snares = [(bi * 4.0 + bt, 0.1, 60, 1.0) for bi in range(16) for bt in (1.0, 3.0)]

    render_track(os.path.join(OUT, "overworld_theme.wav"), 108, 64, [
        dict(inst=lead(duty=0.125, gain=0.28, vib_depth=0.006), events=melody,
             pan=0.1, echo=0.5),
        dict(inst=bass(), events=bass_ev, pan=0.0, echo=0.0),
        dict(inst=pad(gain=0.06), events=pads, pan=-0.35, echo=0.15),
        dict(inst=hat, events=hats, pan=0.4, echo=0.0),
        dict(inst=snare, events=snares, pan=-0.15, echo=0.15),
    ], echo_delay_beats=0.5, echo_fb=0.3, echo_lvl=0.3)


# =================================================================================
# TOWN — "Kettle and Vine" (G, 3/4, 100bpm, 16 bars, 28.8s)
# A waltz: triangle root on the downbeat, two soft off-beat stabs, a lilting
# lead. The second eight is the same tune reaching higher and settling home.
# =================================================================================

def town_theme():
    melody = seq([
        (1, "B4"), (1, "A4"), (1, "G4"),                  # b1  G
        (2, "E4"), (1, "G4"),                             # b2  Em
        (1, "E5"), (1, "D5"), (1, "C5"),                  # b3  C
        (2, "B4"), (1, "G4"),                             # b4  G
        (1, "A4"), (1, "C5"), (1, "E5"),                  # b5  Am
        (2, "F#5"), (1, "D5"),                            # b6  D
        (1, "B4"), (1, "D5"), (1, "G4"),                  # b7  G
        (3, "A4"),                                        # b8  D
        (1, "B4"), (1, "A4"), (1, "G4"),                  # b9  G
        (2, "E4"), (1, "G4"),                             # b10 Em
        (1, "C5"), (1, "E5"), (1, "G5"),                  # b11 C — the reach
        (2, "D5"), (1, "B4"),                             # b12 G
        (1, "C5"), (1, "B4"), (1, "A4"),                  # b13 Am
        (2, "F#4"), (1, "A4"),                            # b14 D
        (3, "G4"),                                        # b15 G
        (1, "D5"), (1, "B4"), (1, "A4"),                  # b16 turn back to b1
    ])

    prog = [("G2", ("B3", "D4")), ("E2", ("G3", "B3")), ("C2", ("E3", "G3")),
            ("G2", ("B3", "D4")), ("A2", ("C4", "E4")), ("D2", ("F#3", "A3")),
            ("G2", ("B3", "D4")), ("D2", ("F#3", "A3")),
            ("G2", ("B3", "D4")), ("E2", ("G3", "B3")), ("C2", ("E3", "G3")),
            ("G2", ("B3", "D4")), ("A2", ("C4", "E4")), ("D2", ("F#3", "A3")),
            ("G2", ("B3", "D4")), ("G2", ("B3", "D4"))]
    bass_ev = []
    stabs = []
    for bi, (root, dyad) in enumerate(prog):
        b0 = bi * 3.0
        bass_ev.append((b0, 1.4, root, 1.0))
        for bt in (1.0, 2.0):
            for n in dyad:
                stabs.append((b0 + bt, 0.4, n, 1.0))

    render_track(os.path.join(OUT, "town_theme.wav"), 100, 48, [
        dict(inst=lead(duty=0.5, gain=0.24, vib_depth=0.005, soft=0.45),
             events=melody, pan=0.1, echo=0.4),
        dict(inst=bass(gain=0.30), events=bass_ev, pan=0.0, echo=0.0),
        dict(inst=harp(gain=0.10, decay=0.20), events=stabs, pan=-0.3, echo=0.25),
    ], echo_delay_beats=0.5, echo_fb=0.3, echo_lvl=0.25)


# =================================================================================
# EBB — "The Quiet" (Em, 58bpm, 12 bars, 49.7s)
# What a drained world sounds like: a music-box phrase with long rests, a bare
# fifth drone that sinks E -> C -> A -> B under it, wind, and a one-beat echo
# doing most of the talking. Deliberately the emptiest mix in the set.
# =================================================================================

def ebb_theme():
    box = harp(gain=0.22, decay=0.8, release=0.3)
    melody = seq([
        (2, "E5"), (2, None),                             # b1
        (1.5, "G5"), (0.5, "F#5"), (2, "E5"),             # b2
        (4, None),                                        # b3
        (2, "B4"), (2, None),                             # b4
        (1, "E5"), (1, "G5"), (2, "B5"),                  # b5
        (3, "A5"), (1, "G5"),                             # b6
        (2, "G5"), (2, "E5"),                             # b7  over C
        (1, "D5"), (2, "E5"), (1, None),                  # b8
        (2, "C5"), (1, "B4"), (1, "A4"),                  # b9  over A
        (3, "E5"), (1, None),                             # b10
        (2, "F#5"), (2, "D#5"),                           # b11 over B — the ache
        (4, "B4"),                                        # b12 -> Em, the seam
    ])

    drone_inst = dict(wave="tri", attack=1.5, decay=0.5, sustain=0.8,
                      release=2.0, gain=0.15, voices=((1.0, 1.0), (1.002, 0.7)))
    drones = []
    for (b0, dur, low, fifth) in [(0, 24, "E2", "B2"), (24, 8, "C2", "G2"),
                                  (32, 8, "A1", "E2"), (40, 8, "B1", "F#2")]:
        drones.append((b0, dur - 0.5, low, 1.0))
        drones.append((b0, dur - 0.5, fifth, 0.7))

    wind = dict(wave="noise", attack=2.5, decay=1.0, sustain=0.6, release=2.5,
                soft=0.04, gain=0.10)
    winds = [(4.0, 8.0, 45, 1.0), (28.0, 10.0, 45, 0.8)]

    render_track(os.path.join(OUT, "ebb_theme.wav"), 58, 48, [
        dict(inst=box, events=melody, pan=0.15, echo=1.0),
        dict(inst=drone_inst, events=drones, pan=-0.1, echo=0.0),
        dict(inst=wind, events=winds, pan=0.3, echo=0.2),
    ], echo_delay_beats=1.0, echo_fb=0.5, echo_lvl=0.55)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("music:")
    title_theme()
    overworld_theme()
    town_theme()
    ebb_theme()
    for name in ("title_theme.wav", "overworld_theme.wav",
                 "town_theme.wav", "ebb_theme.wav"):
        _ensure_import(name)
