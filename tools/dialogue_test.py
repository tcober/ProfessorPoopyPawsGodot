#!/usr/bin/env python3
"""Round-trip tests for tools/dialogue.py.

    python3 tools/dialogue_test.py

WHY THIS EXISTS. dialogue.py writes into the game's source files. The thing that
must never happen is a wrong write — a line landing in the wrong scene, in the
wrong character's mouth, or on top of a piece of code — and every one of those is
invisible in the tool's own output. So the safety properties are asserted here
instead of assumed:

  * an edit lands, and lands ONCE — one changed line in one file, nothing else
  * a no-op apply writes nothing at all
  * a scene that shifted under the book is re-anchored ONLY when the shape proves
    it is the same scene
  * a scene whose SHAPE changed is refused whole, with nothing written
  * export is idempotent, so the book never churns in git

IT WORKS ON THE REAL TREE, because a fixture would not be the thing under test —
the parser's whole job is to cope with how these particular scenes are written.
So it edits `scene/` and `docs/dialogue/` and restores them with `git checkout`
between cases, and REFUSES TO RUN if either is dirty. Commit or stash first.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOL = os.path.join(HERE, "dialogue.py")

FAILS = []


def run(*args):
    r = subprocess.run([sys.executable, TOOL, *args], capture_output=True,
                       text=True, cwd=ROOT)
    return r.stdout.strip() + r.stderr.strip()


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True,
                          cwd=ROOT).stdout.strip()


def touched():
    """git's numstat over the scene sources, e.g. '1\t1\tscene/hall.gd'."""
    return git("diff", "--numstat", "--", "scene")


def reset():
    git("checkout", "scene")
    run("export")


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        return fh.read()


def write(path, text):
    # Read first, THEN open for writing. `open(p,"w").write(open(p).read())`
    # truncates before it reads and silently empties the file — it cost an hour
    # of chasing a tool bug that was never in the tool.
    with open(os.path.join(ROOT, path), "w", encoding="utf-8") as fh:
        fh.write(text)


def first_line(path):
    """The first actual line of dialogue in a book (a `> ` row)."""
    return [ln for ln in read(path).split("\n") if ln.startswith("> ")][0]


def book_for(scene_stem):
    """The book belonging to a scene, whichever side of the stage/dialogue split.

    Hardcoding `sickroom.md` broke the day sickroom was split into a stage and a
    dialogue file and its book became `sickroom_dialogue.md`. The tests have to
    survive a scene being split, because splitting scenes is the thing they are
    partly here to protect.
    """
    for name in (scene_stem + "_dialogue.md", scene_stem + ".md"):
        if os.path.exists(os.path.join(ROOT, "docs", "dialogue", name)):
            return "docs/dialogue/" + name
    raise AssertionError("no book for scene %r — run `dialogue.py export`" % scene_stem)


def ok(cond, label):
    print(("  PASS  " if cond else "  FAIL  ") + label)
    if not cond:
        FAILS.append(label)


# ---- the cases ---------------------------------------------------------------------

def t_export_is_idempotent():
    before = read(book_for("library"))
    run("export")
    ok(before == read(book_for("library")),
       "export is idempotent (the book does not churn in git)")


def t_noop_apply_writes_nothing():
    out = run("apply")
    ok(touched() == "" and "0 line(s)" in out, "a no-op apply touches no .gd at all")


def t_one_edit_lands_once():
    p = book_for("lanternwood")
    write(p, read(p).replace("> Seconded. Carried. Minuted.",
                             "> Seconded. Carried. MINUTED."))
    run("apply")
    ok(touched() == "1\t1\tscene/lanternwood.gd",
       "one edit changes exactly one line of exactly one .gd")
    ok('"Seconded. Carried. MINUTED."' in read("scene/lanternwood.gd"),
       "...and the new words are really in the source")
    reset()


def t_reanchors_when_the_scene_shifts():
    p = book_for("hall")
    line = first_line(p)
    write(p, read(p).replace(line, line + " (edited)", 1))
    src = read("scene/hall.gd").split("\n")
    src.insert(5, "# a comment that shifts every line number below it")
    write("scene/hall.gd", "\n".join(src))
    out = run("apply")
    ok("re-anchored by position" in out and "1 line(s) rewritten" in out,
       "a shifted scene is re-anchored by position, not refused")
    reset()


def t_refuses_a_shape_change():
    p = book_for("sickroom")
    rows = read(p).split("\n")
    i = [k for k, ln in enumerate(rows) if ln.startswith("> ")][2]
    del rows[i - 1:i + 1]                       # drop a heading and its line
    write(p, "\n".join(rows))
    out = run("apply")
    ok("REFUSED" in out and touched() == "",
       "a line deleted from the book is refused, and NOTHING is written")
    ok("part company" in out or "runs" in out,
       "...and the refusal says where the two stopped agreeing")
    reset()


def t_refuses_a_hard_wrap():
    p = book_for("accident")
    rows = read(p).split("\n")
    i = [k for k, ln in enumerate(rows) if ln.startswith("> ")][0]
    rows.insert(i + 1, "> a hard-wrapped continuation")
    write(p, "\n".join(rows))
    out = run("apply")
    ok("REFUSED" in out and "ONE `> ` line" in out and touched() == "",
       "a hard-wrapped line is refused rather than silently joined")
    reset()


def t_speaker_heading_is_a_label():
    p = book_for("sickroom")
    line = first_line(p)
    write(p, read(p).replace("**BASIL**", "**FUJI**", 1)
                    .replace(line, line + " (reworded)", 1))
    out = run("apply")
    ok("Headings are labels" in out and "1 line(s) rewritten" in out,
       "editing a **SPEAKER** heading warns, and still applies the words")
    reset()


def t_bulk_rewrite():
    p = book_for("accident")
    write(p, re.sub(r"^> (.*)$", lambda m: "> Z" + m.group(1), read(p), flags=re.M))
    out = run("apply")
    ok("REFUSED" not in out and read("scene/accident.gd").count('"Z') >= 8,
       "rewriting every line of a scene at once applies cleanly")
    reset()


def t_stage_directions_are_not_dialogue():
    """`*— 0.6s pause —*` rows are derived, and must be inert to the parser.

    They sit between lines and look like content. If parse_book ever picked one up
    the counts would drift and every apply would refuse; if _book_shape did, the
    speaker check would go off. Both are asserted here rather than assumed, because
    a new row type in the renderer is exactly how that would happen.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("dialogue", TOOL)
    d = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(d)

    book_path = book_for("sickroom")
    book = read(book_path)
    ok("*— " in book, "the book really does carry stage directions")
    # The SOURCE this book came from — `sickroom.gd` is the stage since the split
    # and holds no dialogue at all, so naming it here compared a book against an
    # empty extraction and passed for the wrong reason.
    scene = os.path.join(ROOT, "scene",
                         os.path.basename(book_path)[:-3] + ".gd")
    sections, _, _ = d.extract(scene)
    live = [ln for s in sections for ln in s.lines]
    ok(len(d.parse_book(book)) == len(live),
       "stage directions are not counted as dialogue by parse_book")
    ok(len(d._book_shape(book)) == len(live),
       "...nor by the speaker-shape check")


def t_npc_lines_get_the_right_speaker():
    """Every NPC block's lines belong to the name declared above them, in scope.

    The regression this pins: `_speaker_near` used to search OUTWARD symmetrically,
    which looks right and is wrong on the commonest idiom in the game. town_fest's
    cast is a list of `{"name": ..., "lines": [...]}` dicts, so from the SECOND line
    of a block the NEXT character's name is nearer than its own — six lines came out
    in the wrong mouth. Attribution is the one thing a screenplay cannot be sloppy
    about, so it is checked here independently of the code that produces it.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("dialogue", TOOL)
    d = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(d)

    declare = re.compile(r'(?:"name":\s*|display_name\s*=\s*|_villager\(\s*)"([^"]+)"')
    checked, bad = 0, []
    for path in d.gd_files():
        with open(path, encoding="utf-8") as fh:
            src = fh.read().split("\n")
        funcs = d._func_bounds(src)
        sections, _, _ = d.extract(path)
        for sec in sections:
            for ln in sec.lines:
                if ln.kind != d.NPC:
                    continue
                checked += 1
                lo = next((a for a, b, _ in funcs if a <= ln.lineno - 1 < b), 0)
                want = ""
                for j in range(ln.lineno - 2, lo - 1, -1):
                    m = declare.search(src[j])
                    if m:
                        want = m.group(1)
                        break
                if want and want != ln.speaker:
                    bad.append("%s:%d %r != %r"
                               % (os.path.basename(path), ln.lineno, ln.speaker, want))
    ok(checked > 40, "there are NPC line blocks to check (%d)" % checked)
    ok(not bad, "every NPC line is attributed to the name declared above it%s"
                % ("" if not bad else " — " + "; ".join(bad[:3])))


def t_every_line_has_a_speaker():
    """A line with no name renders as an empty heading and reads as nobody's."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("dialogue", TOOL)
    d = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(d)
    nameless = []
    for path in d.gd_files():
        sections, _, _ = d.extract(path)
        for sec in sections:
            for ln in sec.lines:
                if ln.kind in (d.SAY, d.NPC) and not ln.speaker:
                    nameless.append("%s:%d" % (os.path.basename(path), ln.lineno))
    ok(not nameless, "every spoken line has a named speaker%s"
                     % ("" if not nameless else " — " + ", ".join(nameless[:4])))


def t_check_is_clean_at_rest():
    ok("in sync" in run("check"), "check reports in sync on an untouched tree")


def t_check_catches_an_unapplied_edit():
    p = book_for("bluff")
    line = first_line(p)
    write(p, read(p).replace(line, line + " !", 1))
    ok("unapplied edit" in run("check"), "check catches prose that was never applied")
    reset()


def t_check_catches_unclaimed_prose():
    """The audit that stops this tool silently omitting a line — see dialogue.py."""
    src = read("scene/accident.gd").split("\n")
    src.insert(len(src) - 1, 'var _unseen := "A brand new way of saying a line."')
    write("scene/accident.gd", "\n".join(src))
    out = run("check")
    ok("no rule claims it" in out,
       "check flags a prose literal no extraction rule understands")
    reset()


CASES = [
    t_export_is_idempotent,
    t_noop_apply_writes_nothing,
    t_one_edit_lands_once,
    t_reanchors_when_the_scene_shifts,
    t_refuses_a_shape_change,
    t_refuses_a_hard_wrap,
    t_speaker_heading_is_a_label,
    t_bulk_rewrite,
    t_stage_directions_are_not_dialogue,
    t_npc_lines_get_the_right_speaker,
    t_every_line_has_a_speaker,
    t_check_is_clean_at_rest,
    t_check_catches_an_unapplied_edit,
    t_check_catches_unclaimed_prose,
]


def main():
    dirty = git("status", "--porcelain", "--", "scene", "docs/dialogue")
    if dirty:
        print("dialogue tests: REFUSING to run — these cases edit scene/ and "
              "docs/dialogue/ and restore them with `git checkout`, which would "
              "throw away your work. Commit or stash first:\n" + dirty)
        return 2

    print("dialogue round-trip:")
    reset()
    try:
        for case in CASES:
            case()
    finally:
        reset()

    print("dialogue round-trip: %s"
          % ("ALL PASS" if not FAILS else "%d FAILED" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
