#!/usr/bin/env python3
"""The dialogue book: every spoken line in the game, as a screenplay you can edit.

WHY THIS EXISTS. Every word any character says is a string literal somewhere in
a .gd file, wrapped in `await theater.say("Fuji", "...")` and surrounded by
tweens, flags and phase routers. That is the right place for it to LIVE — a line
is a beat, and a beat is code — but it is a miserable place to WRITE in: finding
one line means grepping 290 call sites across eighteen files, and reading a
scene means reading a scene's implementation.

So this makes the other view. `export` walks the scenes and writes
docs/dialogue/*.md — one screenplay per scene, in source order, grouped by beat,
with the speaker in front of every line and a file:line pointer beside it.
`apply` reads those files back and writes your edits into the .gd, in place,
touching nothing but the text inside the quotes.

    python3 tools/dialogue.py export     # .gd -> docs/dialogue/*.md
    python3 tools/dialogue.py apply      # docs/dialogue/*.md -> .gd
    python3 tools/dialogue.py check      # neither side has drifted (for CI)

THE .GD FILES STAY THE SOURCE OF TRUTH. The markdown is a projection of them,
regenerated whenever they change. `apply` is not a merge and does not try to be —
a dialogue tool that guesses is a tool that silently puts Fuji's line in Basil's
mouth. It writes only after two checks pass:

  1. the book and the scene hold the same NUMBER of lines, said by the same
     PEOPLE, in the same ORDER; and
  2. the exact literal it exported is still sitting at the exact span it is about
     to overwrite.

If the anchors moved but the shape still matches — somebody added a comment above
the beat — it re-anchors by position and says so, rather than stranding an
afternoon's prose in a file it refuses to read. If the shape itself changed, it
refuses that file whole and writes nothing.

WHAT YOU CAN CHANGE: the WORDS of any line, card or hint. That is the list.

Adding, deleting or reordering lines is a structural edit and belongs in the .gd:
a run of say() calls has close_dialog() and wait() beats threaded between them
that carry the timing of the scene, and deciding where those go is directing
rather than writing. `apply` reports exactly where the book and the scene parted
company instead of guessing.

Python, not GDScript, and stdlib only — same as assets/_check_art.py, and for
the same reason: it has to run without opening the engine.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, "docs", "dialogue")

# Where dialogue lives. The narrative KIT is excluded on purpose: theater.gd and
# dialog_box.gd carry the machinery that says lines, never lines themselves, and
# npc.gd holds the pose ladder rather than anybody's words.
SOURCE_DIRS = ["scene"]
SKIP_FILES = {
    "theater.gd",          # the kit — say()/converse() themselves
    "dialog_box.gd",       # the box
    "chapters.gd",         # the beat table (its strings are beat NAMES)
    "dev_menu.gd",         # dev tool chrome
    "mix_menu.gd",         # menu chrome
    "party_menu.gd",       # menu chrome
    "save_game.gd",        # serialization
    "game.gd",             # autoload state
    "party.gd",            # autoload state
    "overlay.gd",          # menu chrome
    "map_data.gd",         # loaders
    "tiled_map.gd",
    "painted_map.gd",
    "prop_spawner.gd",
    "world_fx.gd",
    "travel_scene.gd",     # shared driver; its strings are scene paths
    "overworld_location.gd",
    "hud.gd",
    "title.gd",            # menu chrome
}

# A line's kind decides how it is labelled in the book and how strict apply is.
SAY, CARD, HINT, NPC, TABLE = "say", "card", "hint", "npc", "table"

KIND_LABEL = {
    CARD: "CARD",
    HINT: "ON-SCREEN HINT",
}


# ---- the scanner -------------------------------------------------------------------
# GDScript strings in this project are all double-quoted with `\"` and `\\` as the
# only escapes (verified across the tree — there are no ''-strings and no """ blocks).
# The scanner still has to know where a string ENDS before it can decide that a `#`
# starts a comment, or a line like  say("Fuji", "...#1 in my heart")  loses its tail.

def scan_strings(src_line):
    """[(start, end, raw)] for each string literal on one source line.

    `start`/`end` bound the literal's CONTENTS — the span between the quotes, which
    is exactly what apply() splices. Stops at the first unquoted `#`.
    """
    out = []
    i = 0
    n = len(src_line)
    while i < n:
        ch = src_line[i]
        if ch == "#":
            break
        if ch == '"':
            start = i + 1
            j = start
            while j < n:
                if src_line[j] == "\\":
                    j += 2
                    continue
                if src_line[j] == '"':
                    break
                j += 1
            if j >= n:                      # unterminated — a continuation we can't read
                break
            out.append((start, j, src_line[start:j]))
            i = j + 1
            continue
        i += 1
    return out


def unescape(raw):
    """Source literal -> what the player reads."""
    return raw.replace('\\"', '"').replace("\\\\", "\\")


def escape(text):
    """What the player reads -> source literal."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


# ---- the model ---------------------------------------------------------------------

class Line:
    __slots__ = ("kind", "speaker", "text", "raw", "path", "lineno", "col", "end", "note")

    def __init__(self, kind, speaker, raw, path, lineno, col, end, note=""):
        self.kind = kind
        self.speaker = speaker
        self.raw = raw
        self.text = unescape(raw)
        self.path = path
        self.lineno = lineno
        self.col = col
        self.end = end
        self.note = note

    @property
    def anchor(self):
        return "%s:%d:%d" % (os.path.basename(self.path), self.lineno, self.col)


class Section:
    def __init__(self, func, blurb):
        self.func = func
        self.blurb = blurb
        self.lines = []


# ---- extraction --------------------------------------------------------------------

SAY_RE = re.compile(r"\.say\s*\($")
CARD_RE = re.compile(r"\.card\s*\($")
HINT_RE = re.compile(r"\.hint\s*\($")
FUNC_RE = re.compile(r"^func\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
# `line = "..."` / `"line": "..."` — dialogue routed through a data table
# (bluff's MEET_PARTS, library's STACKS) rather than said at the call site.
TABLE_KEY_RE = re.compile(r'(?:^|[\s,{])"?(line|locked_text)"?\s*[:=]\s*$')
# What opens a run of bare string literals that are somebody's dialogue.
LINES_OPEN_RE = re.compile(r"(PackedStringArray\s*\(\s*\[|_villager\s*\(|lines\s*=\s*\[)")
NAME_RE = re.compile(r'(?:display_name\s*=\s*|"name"\s*:\s*)"([^"]+)"')
VILLAGER_RE = re.compile(r'_villager\s*\(\s*"([^"]+)"')
CONST_RE = re.compile(r"^(?:const|static var)\s+([A-Z_][A-Z0-9_]*)")
DICT_KEY_RE = re.compile(r'^\s*"?([a-z_]+)"?\s*[:=]\s*\{')


def _blurb_above(src, idx):
    """The doc block immediately above line `idx` (0-based), as one string.

    `##` is the project's doc-comment convention and is preferred, but a plain `#`
    block above a beat is just as often the sentence that says what the beat IS —
    and a table of contents whose rows are bare function names is not worth
    printing.
    """
    j = idx - 1
    # Skip blank lines on the way up. The project's `# ---- romance (sunset) ----`
    # banner comments sit a blank line above the func they head, and they are the
    # single best beat label in the file — stopping at the blank line threw them
    # all away and left the contents page a list of bare function names.
    while j >= 0 and not src[j].strip():
        j -= 1
    marker = "##" if j >= 0 and src[j].lstrip().startswith("##") else "#"
    out = []
    while j >= 0 and src[j].lstrip().startswith(marker):
        out.append(src[j].lstrip()[len(marker):].strip())
        j -= 1
    out.reverse()
    # Blank-separated paragraphs collapse to the first one: the book wants the
    # sentence that says what the beat IS, not the whole design note beside it.
    para = []
    for piece in out:
        if not piece and para:
            break
        if piece:
            para.append(piece)
    text = " ".join(para)
    # `---- romance (sunset): the watch ----` -> `romance (sunset): the watch`
    return re.sub(r"\s*-{3,}\s*$", "", re.sub(r"^\s*-{3,}\s*", "", text)).strip()


RECEIVER_RE = re.compile(r"\b([A-Za-z_]\w*)\s*\.\s*lines\s*=")


def _speaker_of_receiver(src, code):
    """`_kitty.lines = PackedStringArray([...])` -> "Kitty".

    A villager's name and its dialogue are routinely set in DIFFERENT functions —
    bluff spawns Kitty in `_spawn_kitty` and re-arms her lines in `_meet_kitty`,
    the mayor is named in `_spawn_mayor` and re-scripted at the end of
    `_the_motion` — so searching near the block finds nothing. The variable the
    lines are hung on is the link, and it is file-scoped.
    """
    m = RECEIVER_RE.search(code)
    if not m:
        return ""
    who = re.search(r"\b%s\s*\.\s*display_name\s*=\s*\"([^\"]+)\""
                    % re.escape(m.group(1)), "\n".join(src))
    return who.group(1) if who else ""


def _speaker_near(src, idx, lo, hi):
    """An NPC's name, hunted outward from line `idx` inside [lo, hi).

    Both directions, because the two idioms disagree about order: town_fest sets
    `"name":` above its `"lines":`, and lanternwood's mayor builds his lines
    BEFORE the NPC he hangs them on exists.
    """
    for probe in range(1, 40):
        for j in (idx - probe, idx + probe):
            if not (lo <= j < hi):
                continue
            m = VILLAGER_RE.search(src[j]) or NAME_RE.search(src[j])
            if m:
                return m.group(1)
    # Whoever was speaking just above. town_fest re-arms the goose's idle lines at
    # the end of the beat in which the goose has just said four things, and the
    # variable holding it is a function PARAMETER (`_goose_startle(goose: NPC)`),
    # so neither the receiver nor a nearby display_name can name it.
    for j in range(idx - 1, lo - 1, -1):
        m = re.search(r'\.say\s*\(\s*"([^"]+)"', src[j])
        if m:
            return m.group(1)
    # Last resort, the `_sage_lines()` idiom: a function that exists to return one
    # character's dialogue is named after that character, and nothing inside it
    # ever spells the name out.
    m = re.match(r"^func\s+_([a-z]+)_lines\b", src[lo] if lo < len(src) else "")
    if m:
        return m.group(1).capitalize()
    return ""


def _func_bounds(src):
    """[(start, end, name)] for every top-level func, end-exclusive."""
    starts = [(i, m.group(1)) for i, ln in enumerate(src) for m in [FUNC_RE.match(ln)] if m]
    out = []
    for k, (i, name) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else len(src)
        out.append((i, end, name))
    return out


# ---- indirect dialogue -------------------------------------------------------------
# Not every line is a literal sitting at a say() call. Two idioms route it:
#
#   1. A LOCAL HELPER. `_look("H", "The fire's fine.")` and
#      `_door_hint("Not yet. The flask first-")` are dialogue; the say() that
#      delivers them is inside the helper, with a PARAMETER where the words go.
#   2. A DATA TABLE. bluff's MEET_PARTS and library's STACKS hold their prose
#      under a `line` key and the beat reads it out by index.
#
# Both were silently absent from the first draft of this book — five of Fuji's
# library lines and a hint among them — which is the whole reason `check` now
# audits for unclaimed prose instead of trusting this list to be complete.

FUNC_SIG_RE = re.compile(r"^func\s+([A-Za-z_]\w*)\s*\((.*?)\)\s*(?:->|:)")
SINK_SAY_LIT = re.compile(r'\.say\s*\(\s*"([^"]*)"\s*,\s*([A-Za-z_]\w*)\s*[,)]')
SINK_SAY_VAR = re.compile(r'\.say\s*\(\s*[A-Za-z_]\w*\s*,\s*([A-Za-z_]\w*)\s*[,)]')
SINK_HINT = re.compile(r"\.hint\s*\(\s*([A-Za-z_]\w*)\s*[,)]")
SINK_CARD = re.compile(r"\.card\s*\(\s*([A-Za-z_]\w*)\s*[,)]")
TABLE_SAY_RE = re.compile(r'\.say\s*\(\s*"([^"]*)"\s*,\s*([A-Z_][A-Z0-9_]*)\b')
TABLE_HINT_RE = re.compile(r"\.hint\s*\(\s*([A-Z_][A-Z0-9_]*)\b")


def _params(sig):
    """Parameter NAMES in order, from a func signature's arg text."""
    out = []
    for part in _split_args(sig):
        name = part.strip().split(":")[0].split("=")[0].strip()
        if name:
            out.append(name)
    return out


def _split_args(text):
    """Top-level comma split, respecting nesting and string literals."""
    out, buf, depth, i, n = [], [], 0, 0, len(text)
    while i < n:
        ch = text[i]
        if ch == '"':
            j = i + 1
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == '"':
                    break
                j += 1
            buf.append(text[i:j + 1])
            i = j + 1
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    if "".join(buf).strip():
        out.append("".join(buf))
    return out


def helper_sinks(src, funcs):
    """{helper_name: (arg_index, kind, speaker)} for local dialogue helpers."""
    sinks = {}
    for lo, hi, name in funcs:
        m = FUNC_SIG_RE.match(src[lo])
        if not m:
            continue
        names = _params(m.group(2))
        body = "\n".join(src[lo:hi])
        found = None
        s = SINK_SAY_LIT.search(body)
        if s and s.group(2) in names:
            found = (names.index(s.group(2)), SAY, s.group(1))
        if found is None:
            s = SINK_SAY_VAR.search(body)
            if s and s.group(1) in names:
                found = (names.index(s.group(1)), SAY, "")
        if found is None:
            s = SINK_HINT.search(body)
            if s and s.group(1) in names:
                found = (names.index(s.group(1)), HINT, "")
        if found is None:
            s = SINK_CARD.search(body)
            if s and s.group(1) in names:
                found = (names.index(s.group(1)), CARD, "")
        if found is not None:
            sinks[name] = found
    return sinks


def table_sinks(src):
    """{TABLE_NAME: (kind, speaker)} for tables read out into say()/hint()."""
    out = {}
    joined = "\n".join(src)
    for spk, table in TABLE_SAY_RE.findall(joined):
        out.setdefault(table, (SAY, spk))
    for table in TABLE_HINT_RE.findall(joined):
        out.setdefault(table, (HINT, ""))
    return out


def extract(path):
    """Every dialogue-bearing literal in one .gd file, in source order."""
    with open(path, encoding="utf-8") as fh:
        src = fh.read().split("\n")

    funcs = _func_bounds(src)
    sinks = helper_sinks(src, funcs)
    tables = table_sinks(src)
    # A helper's own body must not be mined as a call site: `_look`'s signature
    # mentions `_look`, and its `say("Fuji", line)` is the sink, not a line.
    sink_bodies = {name: (lo, hi) for lo, hi, name in funcs if name in sinks}

    def enclosing(idx):
        for lo, hi, name in funcs:
            if lo <= idx < hi:
                return lo, hi, name
        return 0, len(src), ""

    def helper_hit(code, idx):
        """(col, end, raw, kind, speaker) if this line calls a dialogue helper."""
        for name, (arg_i, kind, spk) in sinks.items():
            lo, hi = sink_bodies[name]
            if lo <= idx < hi:
                continue                       # the helper's own body
            m = re.search(r"\b%s\s*\(" % re.escape(name), code)
            if not m:
                continue
            open_at = m.end()
            depth, j = 1, open_at
            while j < len(code) and depth:
                if code[j] in "([{":
                    depth += 1
                elif code[j] in ")]}":
                    depth -= 1
                j += 1
            if depth:
                return "TRUNCATED"             # call wraps lines — caller reports it
            args = _split_args(code[open_at:j - 1])
            if arg_i >= len(args):
                continue
            # locate the literal inside that argument, back in source coordinates
            off = open_at + sum(len(a) + 1 for a in args[:arg_i])
            lits = scan_strings(code[off:off + len(args[arg_i])])
            if len(lits) != 1:
                continue
            c, e, lit = lits[0]
            return (off + c, off + e, lit, kind, spk)
        return None

    lines = []
    depth_ctx = []          # stack of "are we inside a lines list?" flags
    lines_owner = ""        # who the currently-open lines block belongs to
    pending_say = None      # a say( whose text literal is on the next line
    table_name = ""         # the const/dict currently being read
    table_key = ""

    for idx, raw_line in enumerate(src):
        stripped = raw_line.strip()

        m = CONST_RE.match(raw_line)
        if m:
            table_name = m.group(1)
        m = DICT_KEY_RE.match(raw_line)
        if m:
            table_key = m.group(1)

        strings = scan_strings(raw_line)
        code_only = raw_line.split("#")[0]

        # --- a say( left hanging on the previous line
        if pending_say is not None and strings:
            col, end, lit = strings[0]
            lines.append(Line(SAY, pending_say, lit, path, idx + 1, col, end))
            pending_say = None
            continue

        # --- an INLINE lines list, all on one line:
        #       _kitty.lines = PackedStringArray(["Sunset waits for nobody."])
        #     The multi-line form is handled by the bracket tracker below; this one
        #     never opens a block, so without this it is simply not dialogue as far
        #     as the parser is concerned. Found by the unclaimed-prose audit.
        m_open = LINES_OPEN_RE.search(code_only)
        if m_open and strings and "]" in code_only[m_open.end() - 1:]:
            br = code_only.find("[", m_open.start())
            if br >= 0:
                close = code_only.rfind("]")
                inline = [(c, e, s) for (c, e, s) in strings if br < c < close]
                if inline:
                    lo, hi, _ = enclosing(idx)
                    who = (_speaker_of_receiver(src, code_only)
                           or _speaker_near(src, idx, lo, hi))
                    for col, end, lit in inline:
                        lines.append(Line(NPC, who, lit, path, idx + 1, col, end))
                    _track_brackets(code_only, depth_ctx)
                    continue

        # --- bare list elements inside an NPC lines block
        in_lines_block = bool(depth_ctx) and depth_ctx[-1]
        if in_lines_block and strings:
            bare = re.fullmatch(r'\s*"(?:[^"\\]|\\.)*"\s*,?\s*', code_only)
            if bare:
                lo, hi, _ = enclosing(idx)
                who = lines_owner or _speaker_near(src, idx, lo, hi)
                for col, end, lit in strings:
                    lines.append(Line(NPC, who, lit, path, idx + 1, col, end))
                _track_brackets(code_only, depth_ctx)
                continue

        # --- a local dialogue helper: _look("H", "the line"), _door_hint("...")
        if strings:
            hit = helper_hit(code_only, idx)
            if hit == "TRUNCATED":
                lines.append(Line(SAY, "", strings[0][2], path, idx + 1,
                                  strings[0][0], strings[0][1],
                                  note="MULTILINE-HELPER-CALL"))
                _track_brackets(code_only, depth_ctx)
                continue
            if hit:
                col, end, lit, kind, spk = hit
                lines.append(Line(kind, spk, lit, path, idx + 1, col, end))
                _track_brackets(code_only, depth_ctx)
                continue

        # --- say / card / hint at a call site
        consumed = set()
        for k, (col, end, lit) in enumerate(strings):
            before = code_only[:col - 1]
            if SAY_RE.search(before):
                if k + 1 < len(strings):
                    c2, e2, lit2 = strings[k + 1]
                    between = code_only[end + 1:c2 - 1]
                    if re.fullmatch(r"\s*,\s*", between):
                        lines.append(Line(SAY, lit, lit2, path, idx + 1, c2, e2))
                        consumed.add(k)
                        consumed.add(k + 1)
                        continue
                # `say("Fuji",` with the text wrapped onto the next line
                if code_only.rstrip().endswith(","):
                    pending_say = lit
                    consumed.add(k)
                continue
            if k in consumed:
                continue
            if CARD_RE.search(before):
                lines.append(Line(CARD, "", lit, path, idx + 1, col, end))
                consumed.add(k)
                continue
            if HINT_RE.search(before):
                lines.append(Line(HINT, "", lit, path, idx + 1, col, end))
                consumed.add(k)
                continue
            if TABLE_KEY_RE.search(before):
                label = table_name + (" · " + table_key if table_key else "")
                kind, spk = tables.get(table_name, (TABLE, ""))
                if kind == TABLE:
                    lines.append(Line(TABLE, "", lit, path, idx + 1, col, end, note=label))
                else:
                    # The table IS read out by a say()/hint() somewhere, so this
                    # is an ordinary line that merely lives in a table.
                    lines.append(Line(kind, spk, lit, path, idx + 1, col, end, note=label))
                consumed.add(k)
                continue

        # --- bracket bookkeeping for lines blocks
        opens_lines = bool(LINES_OPEN_RE.search(code_only))
        if opens_lines:
            lines_owner = _speaker_of_receiver(src, code_only)
        _track_brackets(code_only, depth_ctx, opens_lines)
        if not (depth_ctx and depth_ctx[-1]):
            lines_owner = ""

    # group into sections by enclosing func
    sections = []
    by_func = {}
    for ln in lines:
        lo, _, name = enclosing(ln.lineno - 1)
        if name not in by_func:
            sec = Section(name or "tables and constants",
                          _blurb_above(src, lo) if name else "")
            by_func[name] = sec
            sections.append(sec)
        by_func[name].lines.append(ln)
    return sections, _blurb_above(src, _first_code(src)), src


# ---- the unclaimed-prose audit ------------------------------------------------------
# THE FAILURE MODE THIS FILE HAS IS SILENT OMISSION, and it already happened once:
# the first draft understood say()/card()/hint() and nothing else, so five of Fuji's
# library lines and a door hint were simply not in the book — and a book that is
# missing a line looks exactly like a book that is complete.
#
# So the parser is not trusted to be exhaustive. Every string literal in a scene file
# that READS LIKE PROSE and was not claimed by any rule above is reported. A new
# dialogue idiom fails the check instead of quietly not appearing, and the fix is
# either a new rule or a line in IGNORE_PROSE saying why it is not dialogue.

# Literals that read like sentences but are not anybody's words.
IGNORE_PROSE = {
    # scene/prologue_open.gd — ESC-skip plumbing, not spoken
    "res://scene/house_fest.tscn",
}
PROSE_SKIP_RE = re.compile(
    r"^(res://|user://|\w+/[\w/]+\.\w+$|[A-Za-z_]\w*(\s*,\s*[A-Za-z_]\w*)*$)")


def looks_like_prose(text, code_before=""):
    """Is this literal somebody's words, rather than a path/anchor/clip name?"""
    # An assert's failure message is prose written AT the programmer. It reads
    # exactly like a line of dialogue to any heuristic, and it is not one.
    if "assert(" in code_before or code_before.rstrip().endswith("push_error("):
        return False
    if text in IGNORE_PROSE or len(text) < 12 or " " not in text:
        return False
    if PROSE_SKIP_RE.match(text):
        return False
    if not any(c.islower() for c in text):
        return False
    words = [w for w in re.split(r"\s+", text) if w]
    return len(words) >= 3 or text.rstrip()[-1:] in ".!?-,"


def unclaimed(path):
    """[(lineno, text)] — prose-looking literals no rule picked up."""
    sections, _, src = extract(path)
    claimed = {(ln.lineno, ln.col) for s in sections for ln in s.lines}
    out = []
    for idx, row in enumerate(src):
        # An assert can span lines; look back a little for the call that opened it.
        window = "\n".join(src[max(0, idx - 2):idx + 1])
        for col, _end, raw in scan_strings(row):
            if (idx + 1, col) in claimed:
                continue
            text = unescape(raw)
            if looks_like_prose(text, window):
                out.append((idx + 1, text))
    return out


def _first_code(src):
    """Index just past the file's leading `##` header block."""
    i = 0
    while i < len(src) and not src[i].startswith("##"):
        i += 1
    while i < len(src) and src[i].startswith("##"):
        i += 1
    return i


def _track_brackets(code, stack, opens_lines=False):
    """Push/pop the 'inside a dialogue list' flag as brackets open and close."""
    for ch in code:
        if ch in "([":
            stack.append(opens_lines and ch == "[")
        elif ch in ")]":
            if stack:
                stack.pop()


# ---- the book ----------------------------------------------------------------------

def _slug(func):
    """GitHub's heading-anchor slug for a `## \`_func\`` heading."""
    return re.sub(r"[^a-z0-9-]", "", func.strip("_").replace("_", "-").replace(" ", "-").lower())


BANNER = """<!-- GENERATED by tools/dialogue.py — but you are meant to edit the
     lines below. Change the words after `> `, then run:

         python3 tools/dialogue.py apply

     and the edit lands in the .gd file named beside each line. Rewrite the
     words freely; do NOT add, delete or reorder lines (that is a change to the
     scene, and belongs in the .gd). See docs/dialogue/README.md. -->
"""


def render(path, sections, header, rel):
    title = os.path.basename(path)[:-3].replace("_", " ").upper()
    # The header blurb is NOT a blockquote, deliberately. `> ` is the dialogue
    # marker in this format and nothing else may wear it — a scene summary that
    # looked like a line was the first thing to trip the round-trip tests, and a
    # writer would have hit it next.
    out = ["# " + title, "", BANNER, "`%s`" % rel, ""]
    if header:
        out += ["*%s*" % header, ""]

    total = sum(len(s.lines) for s in sections)
    out += ["*%d lines.*" % total, ""]

    # A table of contents, because one room hosts several beats: bluff.md is the
    # whirligig meet AND the romance AND both thesis-day calls, 78 lines of it, and
    # without this you scroll to find out which is which.
    if len(sections) > 1:
        out += ["| beat | lines |", "| --- | ---: |"]
        for sec in sections:
            # First 78 characters, not the first SENTENCE: this codebase opens a
            # doc comment with a two-word thesis ("The book.", "A stack.") and
            # spends the rest of the line saying what it means.
            label = " ".join(sec.blurb.split())
            label = (label[:78].rstrip() + "…") if len(label) > 78 else label
            out.append("| [`%s`](#%s)%s | %d |"
                       % (sec.func, _slug(sec.func),
                          " — " + label if label else "", len(sec.lines)))
        out.append("")
    out += ["---", ""]

    for sec in sections:
        out += ["## `%s`" % sec.func, ""]
        if sec.blurb:
            out += ["*%s*" % sec.blurb, ""]
        for ln in sec.lines:
            if ln.kind == SAY:
                head = "**%s**" % ln.speaker.upper()
            elif ln.kind == NPC:
                who = ln.speaker.upper() if ln.speaker else "VILLAGER"
                head = "**%s** *(idle line — this block is a list)*" % who
            elif ln.kind == TABLE:
                head = "**%s** *(via `%s`)*" % (ln.speaker.upper() or "LINE", ln.note)
            else:
                head = "**%s**" % KIND_LABEL[ln.kind]
            out.append("%s  <sub>`%s`</sub>" % (head, ln.anchor))
            out.append("> " + ln.text)
            out.append("")
    return "\n".join(out).rstrip() + "\n"


BLOCK_RE = re.compile(r"^\*\*(.+?)\*\*.*?<sub>`([^`]+)`</sub>\s*$")


def _book_shape(text):
    """[(kind, speaker)] read back off a book's headings.

    The re-anchoring path's whole safety argument: two scenes with the same number
    of lines said by the same people in the same order are the same scene with the
    line numbers moved. Anything else and apply refuses.
    """
    out = []
    for row in text.split("\n"):
        m = BLOCK_RE.match(row)
        if not m:
            continue
        head = m.group(1).strip()
        rest = row[m.end(1) + 2:]          # whatever follows the `**SPEAKER**`
        if head == "CARD":
            out.append((CARD, ""))
        elif head == "ON-SCREEN HINT":
            out.append((HINT, ""))
        elif "(idle line" in rest:
            # render() prints VILLAGER when it could not work out whose block it is;
            # normalise it back to "unknown" so the two sides compare equal.
            out.append((NPC, "" if head == "VILLAGER" else head.lower()))
        elif "(via " in rest and head == "LINE":
            out.append((TABLE, ""))
        else:
            out.append((SAY, head.lower()))
    return out


def parse_book(text):
    """[(anchor, new_text)] from a rendered book."""
    out = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        m = BLOCK_RE.match(lines[i])
        if not m:
            i += 1
            continue
        anchor = m.group(2)
        i += 1
        body = []
        while i < len(lines) and lines[i].startswith("> "):
            body.append(lines[i][2:])
            i += 1
        if body:
            out.append((anchor, body))
    return out


# ---- commands ----------------------------------------------------------------------

def gd_files():
    out = []
    for sub in SOURCE_DIRS:
        d = os.path.join(ROOT, sub)
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".gd") and fn not in SKIP_FILES:
                out.append(os.path.join(d, fn))
    return out


def build_all():
    """path -> (sections, header, rel, book_text), skipping files with no dialogue."""
    books = {}
    for path in gd_files():
        sections, header, _ = extract(path)
        if not any(s.lines for s in sections):
            continue
        sections = [s for s in sections if s.lines]
        rel = os.path.relpath(path, ROOT)
        books[path] = (sections, header, rel, render(path, sections, header, rel))
    return books


def _beat_blocks(text):
    """Top-level `{...}` blocks of the BEATS array, brace-matched.

    A regex cannot do this and the first draft proved it: `name = [^}]+?}` stops at
    the first `}` it meets, which is the one closing a beat's own
    `state = {town_spawn = "home"}` — so every beat that routes a spawn or a phase
    (fourteen of them, including the whole of Act 1) silently vanished from the
    index, and an index that is missing rows looks exactly like an index.
    """
    out = []
    depth, start, i, n = 0, None, 0, len(text)
    while i < n:
        ch = text[i]
        if ch == '"':                                   # skip string literals whole
            i += 1
            while i < n and text[i] != '"':
                i += 2 if text[i] == "\\" else 1
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                out.append(text[start:i + 1])
                start = None
        i += 1
    return out


def _strip_comments(src):
    """Blank out `#` comments, so the doc block's `{group = "HEADER"}` EXAMPLE is
    not read as a chapter. It was, and the index grew a phantom heading."""
    out = []
    for row in src.split("\n"):
        keep, i, n = [], 0, len(row)
        while i < n:
            if row[i] == "#":
                break
            if row[i] == '"':
                keep.append(row[i])
                i += 1
                while i < n and row[i] != '"':
                    keep.append(row[i])
                    i += 2 if row[i] == "\\" else 1
            keep.append(row[i] if i < n else "")
            i += 1
        out.append("".join(keep))
    return "\n".join(out)


def chapter_index(books):
    """The story-order index, taken from chapters.gd so it can't drift from the game."""
    src = open(os.path.join(ROOT, "scene", "chapters.gd"), encoding="utf-8").read()
    body = _strip_comments(src)
    body = body.split("BEATS: Array[Dictionary] = [", 1)[-1]
    out = []
    for block in _beat_blocks(body):
        g = re.search(r'group\s*=\s*"([^"]+)"', block)
        if g:
            out.append(("group", g.group(1), ""))
            continue
        nm = re.search(r'name\s*=\s*"([^"]+)"', block)
        sc = re.search(r'scene\s*=\s*"res://scene/([a-z_]+)\.tscn"', block)
        if nm and sc:
            out.append(("beat", nm.group(1), sc.group(1)))
    return out


README = """# The dialogue book

Every word anybody says in this game, as a screenplay instead of as code.

**This directory is generated.** `tools/dialogue.py export` rebuilds it from the
`.gd` files; those stay the source of truth. But you are meant to WRITE in here —
edit the words, then push them back:

```sh
python3 tools/dialogue.py export     # code  -> book   (refresh after any .gd edit)
python3 tools/dialogue.py apply      # book  -> code   (your rewrites land in the .gd)
python3 tools/dialogue.py check      # is anything out of sync?
```

## How to edit

A line looks like this:

```
**FUJI**  <sub>`library.gd:190:32`</sub>
> One more chapter, then bed. ...Which means coffee.
```

Change the text after `> `. That is the whole workflow. The `<sub>` tag is the
address `apply` writes back to — leave it alone, and leave the `**SPEAKER**`
line alone (the speaker is a separate argument in the code; renaming it here
does nothing).

**One line of dialogue is one `> ` line, however long.** Don't hard-wrap it; your
editor's soft wrap is fine and markdown renders it wrapped anyway.

### What you can and can't do here

| | |
| --- | --- |
| Rewrite the words of any line, card or hint | **yes** — this is the point |
| Add, delete or reorder lines | **no** — do it in the `.gd`, then re-export |

The second one is not the tool being timid. A run of `say()` calls has
`close_dialog()` and `wait()` beats threaded between them that carry the timing
of the scene; inserting a line means deciding where those go, which is directing,
not writing. `apply` tells you exactly where the book and the scene parted
company instead of guessing.

### If the scene changes while you are writing

Adding a comment to a `.gd` shifts every line number below it, so the `<sub>`
addresses go stale. That is fine and `apply` handles it: as long as the book and
the scene still hold the same lines said by the same people in the same order, it
re-anchors by position and prints a note saying it did.

It only refuses when the *shape* changed — a line added, removed or moved to
another speaker. Then nothing is written to that file, and the message says where
the two stopped agreeing. Re-run `export` and redo that scene's wording.

**So: `apply` before you go rearranging a scene.** An unapplied edit lives only in
the `.md`, and `export` overwrites it.

### `%s` and friends

A few lines carry `%s` or `%d`. Code fills those in — keep them, or the line
prints the placeholder.

## The scenes, in story order

Taken from `scene/chapters.gd`, so it is the order the dev chapter selector
(press `0` in a debug build) walks them in.

**Several beats share one screenplay.** A room hosts more than one beat — the
bluff is the whirligig meet *and* the kiss *and* both thesis-day calls — so its
file holds all of them, one `##` section each, and each file opens with a table
of contents. The line count in the table below is the whole file's, not the beat's.
"""


def write_readme(books):
    by_stem = {}
    for path, (_, _, rel, _) in books.items():
        by_stem[os.path.basename(path)[:-3]] = rel
    counts = {}
    for path, (sections, _, _, _) in books.items():
        counts[os.path.basename(path)[:-3]] = sum(len(s.lines) for s in sections)

    out = [README]
    seen = set()
    for kind, label, stem in chapter_index(books):
        if kind == "group":
            out.append("\n### %s\n" % label)
            out.append("| beat | screenplay | lines |")
            out.append("| --- | --- | --- |")
            continue
        if stem in by_stem:
            out.append("| %s | [`%s.md`](%s.md) | %d |"
                       % (label, stem, stem, counts.get(stem, 0)))
            seen.add(stem)
        else:
            out.append("| %s | *(no dialogue)* | — |" % label)

    orphans = sorted(set(by_stem) - seen)
    if orphans:
        out.append("\n### Not in the chapter table\n")
        out.append("| screenplay | lines |")
        out.append("| --- | --- |")
        for stem in orphans:
            out.append("| [`%s.md`](%s.md) | %d |" % (stem, stem, counts.get(stem, 0)))

    # The cast, by how much they actually say. Useful on its own — it is the only
    # place in the repo you can see that Kitty has 55 lines and Alder has two.
    cast = {}
    where = {}
    for path, (sections, _, _, _) in books.items():
        stem = os.path.basename(path)[:-3]
        for sec in sections:
            for ln in sec.lines:
                if ln.kind in (SAY, NPC) and ln.speaker:
                    cast[ln.speaker] = cast.get(ln.speaker, 0) + 1
                    where.setdefault(ln.speaker, set()).add(stem)
    out.append("\n## Who says how much\n")
    out.append("| character | lines | scenes |")
    out.append("| --- | ---: | --- |")
    for name in sorted(cast, key=lambda k: (-cast[k], k)):
        scenes = ", ".join("[`%s`](%s.md)" % (s, s) for s in sorted(where[name]))
        out.append("| %s | %d | %s |" % (name, cast[name], scenes))

    out.append("\n---\n")
    out.append("*%d lines across %d scenes.*\n"
               % (sum(counts.values()), len(books)))
    return "\n".join(out)


def cmd_export(quiet=False):
    books = build_all()
    os.makedirs(OUT_DIR, exist_ok=True)
    written = 0
    for path, (_, _, _, text) in sorted(books.items()):
        dest = os.path.join(OUT_DIR, os.path.basename(path)[:-3] + ".md")
        old = open(dest, encoding="utf-8").read() if os.path.exists(dest) else None
        if old != text:
            open(dest, "w", encoding="utf-8").write(text)
            written += 1
    readme = write_readme(books)
    dest = os.path.join(OUT_DIR, "README.md")
    old = open(dest, encoding="utf-8").read() if os.path.exists(dest) else None
    if old != readme:
        open(dest, "w", encoding="utf-8").write(readme)
        written += 1
    # sweep books whose scene lost all its dialogue
    keep = {os.path.basename(p)[:-3] + ".md" for p in books} | {"README.md"}
    for fn in sorted(os.listdir(OUT_DIR)):
        if fn.endswith(".md") and fn not in keep:
            os.remove(os.path.join(OUT_DIR, fn))
            written += 1
    if not quiet:
        total = sum(sum(len(s.lines) for s in b[0]) for b in books.values())
        print("dialogue book: %d lines across %d scenes (%d file(s) updated)"
              % (total, len(books), written))
        for path, rows in sorted(audit_all().items()):
            print("  WARNING  %s: %d prose literal(s) not in the book —"
                  % (os.path.basename(path), len(rows)))
            for lineno, text in rows:
                print("           %s:%d  %s" % (os.path.basename(path), lineno, text[:70]))
    return books


def audit_all():
    """path -> unclaimed prose, for every scene file that has any."""
    out = {}
    for path in gd_files():
        rows = unclaimed(path)
        if rows:
            out[path] = rows
    return out


def _divergence(edits, current):
    """A human sentence about where a book and its scene stopped agreeing."""
    for i, ((anchor, _), ln) in enumerate(zip(edits, current)):
        if anchor != ln.anchor:
            return ("they agree for %d line(s) and part company at book entry %d "
                    "(`%s`), which the scene now has at `%s`"
                    % (i, i + 1, anchor, ln.anchor))
    return "the book runs %d line(s) past the scene" % abs(len(edits) - len(current))


def cmd_apply():
    """Push edits from the book into the .gd files."""
    books = build_all()
    changed_files = 0
    changed_lines = 0
    problems = []
    notes = []

    for path, (sections, _, _, _) in sorted(books.items()):
        stem = os.path.basename(path)[:-3]
        book_path = os.path.join(OUT_DIR, stem + ".md")
        if not os.path.exists(book_path):
            continue
        edits = parse_book(open(book_path, encoding="utf-8").read())
        current = [ln for s in sections for ln in s.lines]

        # A COUNT MISMATCH IS ALWAYS STRUCTURAL. Adding or deleting a `> ` line in
        # the book means adding or deleting a statement in the scene, and where the
        # close_dialog()/wait() beats around it go is a directing decision this tool
        # has no business making. Say where it diverged rather than just "no".
        if len(edits) != len(current):
            problems.append(
                "%s.md has %d line(s), %s has %d — %s. Lines cannot be added or "
                "removed from the book; edit the .gd, then re-export."
                % (stem, len(edits), os.path.basename(path), len(current),
                   _divergence(edits, current)))
            continue

        wrapped = [a for (a, b) in edits if len(b) != 1]
        if wrapped:
            problems.append("%s.md: `%s` spans several `> ` lines. One line of "
                            "dialogue is ONE `> ` line, however long — let it wrap on "
                            "screen instead." % (stem, wrapped[0]))
            continue

        book_shape = _book_shape(open(book_path, encoding="utf-8").read())
        live_shape = [(ln.kind, ln.speaker.lower()) for ln in current]

        # FAST PATH: the anchors still point where they did. Fully verified — the
        # exact literal is re-read out of the source before anything is written.
        exact = all(a == ln.anchor for (a, _), ln in zip(edits, current))

        if exact and book_shape != live_shape:
            # Nothing is at risk (the text edits below are still anchored exactly),
            # but a rewritten **SPEAKER** heading does nothing at all — the speaker
            # is a separate argument in the .gd. Silently ignoring that would look
            # to the writer exactly like it had worked.
            for i, (b, live) in enumerate(zip(book_shape, live_shape)):
                if b != live:
                    notes.append("%s.md: the speaker on entry %d says %r, the scene "
                                 "says %r. Headings are labels — change the speaker "
                                 "in %s. The words were still applied."
                                 % (stem, i + 1, b[1].upper() or b[0],
                                    live[1].upper() or live[0], os.path.basename(path)))
                    break

        if not exact:
            # The scene shifted (a comment added above, a beat moved). Rather than
            # strand an afternoon's prose in a file it refuses to read, re-anchor by
            # POSITION — but only once the shape of the scene proves it is the same
            # scene: same number of lines, same speaker saying each of them, in the
            # same order. A reorder or a rewrite fails that and is refused.
            if book_shape != live_shape:
                problems.append(
                    "%s: the scene changed under the book (%s) and the speakers no "
                    "longer line up, so nothing was written. Re-export — your "
                    "unapplied wording in %s.md will be overwritten, so copy it out "
                    "first if you want it."
                    % (os.path.basename(path), _divergence(edits, current), stem))
                continue
            notes.append("%s: anchors had shifted; re-anchored by position "
                         "(speakers verified)." % os.path.basename(path))

        src = open(path, encoding="utf-8").read().split("\n")
        pending = []
        bad = False
        for (anchor, body), ln in zip(edits, current):
            new_text = body[0]
            if new_text == ln.text:
                continue
            # The last word before writing: the literal really is still sitting at
            # the span we are about to overwrite.
            row = src[ln.lineno - 1]
            if row[ln.col:ln.end] != ln.raw:
                problems.append("%s: %s moved under the book — re-export."
                                % (os.path.basename(path), anchor))
                bad = True
                break
            pending.append((ln.lineno - 1, ln.col, ln.end, escape(new_text)))
        if bad or not pending:
            continue

        # Right to left within a row, so earlier spans keep their columns.
        for lineno, col, end, rep in sorted(pending, key=lambda p: (-p[0], -p[1])):
            row = src[lineno]
            src[lineno] = row[:col] + rep + row[end:]
        open(path, "w", encoding="utf-8").write("\n".join(src))
        changed_files += 1
        changed_lines += len(pending)

    for n in notes:
        print("  note     " + n)
    for p in problems:
        print("  REFUSED  " + p)
    print("dialogue apply: %d line(s) rewritten in %d file(s)%s"
          % (changed_lines, changed_files,
             ", %d refusal(s)" % len(problems) if problems else ""))
    if changed_lines:
        cmd_export(quiet=True)
        print("            book re-exported so the anchors match the new source")
    return 1 if problems else 0


def cmd_check():
    """Fail if the book is stale, or if it carries edits nobody applied."""
    books = build_all()
    stale = []
    for path, (sections, _, _, text) in sorted(books.items()):
        stem = os.path.basename(path)[:-3]
        dest = os.path.join(OUT_DIR, stem + ".md")
        if not os.path.exists(dest):
            stale.append("%s.md missing — run `export`" % stem)
            continue
        on_disk = open(dest, encoding="utf-8").read()
        if on_disk == text:
            continue
        edits = parse_book(on_disk)
        current = [ln for s in sections for ln in s.lines]
        if len(edits) == len(current) and all(
                a == ln.anchor for (a, _), ln in zip(edits, current)):
            diff = sum(1 for (_, b), ln in zip(edits, current)
                       if len(b) == 1 and b[0] != ln.text)
            if diff:
                stale.append("%s.md has %d unapplied edit(s) — run `apply`" % (stem, diff))
                continue
        stale.append("%s.md is out of date — run `export`" % stem)

    # The audit runs even when the book is perfectly in sync: "in sync" only means
    # the book matches what the parser SAW, and the bug worth catching is a line
    # the parser never saw at all.
    for path, rows in sorted(audit_all().items()):
        for lineno, text in rows:
            stale.append("%s:%d reads like dialogue but no rule claims it — teach "
                         "tools/dialogue.py the idiom, or add it to IGNORE_PROSE: %r"
                         % (os.path.relpath(path, ROOT), lineno, text[:60]))

    for s in stale:
        print("  FAIL  " + s)
    if not stale:
        print("dialogue book: in sync, and every prose literal is accounted for")
    return 1 if stale else 0


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "export"
    if cmd == "export":
        cmd_export()
        return 0
    if cmd == "apply":
        return cmd_apply()
    if cmd == "check":
        return cmd_check()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
