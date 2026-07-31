# The dialogue book

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


### PROLOGUE A - THE WHIRLIGIG

| beat | screenplay | lines |
| --- | --- | --- |
| TITLE CARDS | [`prologue_open.md`](prologue_open.md) | 3 |
| A1 - FESTIVAL MORNING | [`house_fest.md`](house_fest.md) | 3 |
| A2 - MOM AT THE HEARTH | [`downstairs_fest.md`](downstairs_fest.md) | 38 |
| A3 - INTO THE FESTIVAL | [`town_fest.md`](town_fest.md) | 44 |
| A4 - THE GOOSE IN THE ORCHARD | [`town_fest.md`](town_fest.md) | 44 |
| A5 - RETURN THE RIBBON | [`town_fest.md`](town_fest.md) | 44 |
| A6 - I WANT TO GO HOME | [`town_fest.md`](town_fest.md) | 44 |
| A7 - MOM'S BLESSING | [`downstairs_fest.md`](downstairs_fest.md) | 38 |
| A8 - THE SOUTH GATE | [`town_fest.md`](town_fest.md) | 44 |
| A9 - THE BLUFF - THE MEET | [`bluff.md`](bluff.md) | 78 |
| A10 - GEAR SPRING CRANK | [`bluff.md`](bluff.md) | 78 |
| A11 - THE WHIRLIGIG FLIES | [`bluff.md`](bluff.md) | 78 |
| A12 - THE BREW | [`downstairs_fest.md`](downstairs_fest.md) | 38 |
| A13 - ACROSS TOWN | [`town_fest.md`](town_fest.md) | 44 |
| A14 - THE RECITAL | [`hall.md`](hall.md) | 29 |

### PROLOGUE B - POOPY PAWS

| beat | screenplay | lines |
| --- | --- | --- |
| B1 - THE WATCH | [`bluff.md`](bluff.md) | 78 |
| B2 - THE KISS | [`bluff.md`](bluff.md) | 78 |
| B3 - THE WALK HOME | [`town_thesis.md`](town_thesis.md) | 29 |
| B4 - EIGHT FIFTY-SEVEN | [`house_thesis.md`](house_thesis.md) | 10 |
| B5 - THE SQUELCH | [`town_thesis.md`](town_thesis.md) | 29 |
| B6 - THE NAMING | [`hall.md`](hall.md) | 29 |
| B7 - SHE CALLS | [`bluff.md`](bluff.md) | 78 |
| B8 - THE ACCIDENT | [`accident.md`](accident.md) | 8 |
| B9 - THE WRONG VOICE | [`bluff.md`](bluff.md) | 78 |
| B10 - THE VERDICT | [`sickroom.md`](sickroom.md) | 18 |
| B11 - THE CLINIC STEPS | [`town_thesis.md`](town_thesis.md) | 29 |

### THE EBB

| beat | screenplay | lines |
| --- | --- | --- |
| THE EBB NIGHT | *(no dialogue)* | — |
| FUJI'S LIBRARY | [`library.md`](library.md) | 76 |
| FUJI'S LIBRARY (WALK OUT) | [`library.md`](library.md) | 76 |
| LANTERNWOOD - EBB NIGHT | [`lanternwood.md`](lanternwood.md) | 53 |
| THE RESEARCH NIGHT | [`library.md`](library.md) | 76 |
| THE KIT | [`library.md`](library.md) | 76 |
| THE DEFENCE OF LANTERNWOOD | [`lanternwood.md`](lanternwood.md) | 53 |
| THE MOTION (MAYOR HOLLIS) | [`lanternwood.md`](lanternwood.md) | 53 |
| THE CROSSING (THE PIER) | [`lanternwood.md`](lanternwood.md) | 53 |
| THE WEST SHINGLE (LANDED) | *(no dialogue)* | — |

### SANDBOX

| beat | screenplay | lines |
| --- | --- | --- |
| THE LOFT | *(no dialogue)* | — |
| THE LAB | *(no dialogue)* | — |
| ALEMBIC TOWN | *(no dialogue)* | — |
| THE ACADEMY | *(no dialogue)* | — |
| THE OVERWORLD | *(no dialogue)* | — |
| WHISKER MEADOW | *(no dialogue)* | — |
| LANTERNWOOD (DAY) | [`lanternwood.md`](lanternwood.md) | 53 |

## Who says how much

| character | lines | scenes |
| --- | ---: | --- |
| Basil | 82 | [`bluff`](bluff.md), [`downstairs_fest`](downstairs_fest.md), [`hall`](hall.md), [`house_fest`](house_fest.md), [`house_thesis`](house_thesis.md), [`sickroom`](sickroom.md), [`town_fest`](town_fest.md), [`town_thesis`](town_thesis.md) |
| Fuji | 77 | [`lanternwood`](lanternwood.md), [`library`](library.md) |
| Kitty | 55 | [`bluff`](bluff.md), [`downstairs_fest`](downstairs_fest.md), [`hall`](hall.md), [`sickroom`](sickroom.md), [`town_thesis`](town_thesis.md) |
| Mayor Hollis | 29 | [`lanternwood`](lanternwood.md) |
| Mom | 18 | [`downstairs_fest`](downstairs_fest.md) |
| Schweinler | 16 | [`accident`](accident.md), [`hall`](hall.md), [`town_fest`](town_fest.md), [`town_thesis`](town_thesis.md) |
| Sage | 14 | [`town_fest`](town_fest.md) |
| Ridley | 11 | [`accident`](accident.md), [`bluff`](bluff.md), [`town_thesis`](town_thesis.md) |
| Goose | 9 | [`town_fest`](town_fest.md) |
| Professor Strix | 7 | [`hall`](hall.md), [`town_fest`](town_fest.md) |
| Dr. Ciconia | 5 | [`sickroom`](sickroom.md) |
| Pip | 5 | [`lanternwood`](lanternwood.md), [`town_fest`](town_fest.md) |
| ??? | 4 | [`bluff`](bluff.md) |
| Kitty's Mother | 4 | [`sickroom`](sickroom.md) |
| Mrs. Flockhart | 3 | [`town_fest`](town_fest.md) |
| Alder | 2 | [`lanternwood`](lanternwood.md) |
| Bramble | 2 | [`lanternwood`](lanternwood.md) |
| Dr. Feathers | 2 | [`house_thesis`](house_thesis.md) |
| Dean Strix | 1 | [`hall`](hall.md) |
| Gallery | 1 | [`hall`](hall.md) |

---

*389 lines across 12 scenes.*
