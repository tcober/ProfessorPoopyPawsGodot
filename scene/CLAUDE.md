# scene/ — rooms, cutscenes, autoloads and the tile drivers

Load the skill that matches what you're touching:

- cutscenes, dialogue, phases, flags, walk-gates, doors → **`story-scenes`**
- the overworld, towns, zones, travel markers → **`world-and-zones`**
- `party.gd` and follower behaviour → **`party-ai`**
- `party_menu.gd`, `save_game.gd`, `title.gd` → **`rpg-systems`**
- `tiled_map.gd` / `painted_map.gd` / `map_data.gd` → **`art-pipeline`**

The rules that bite here:

1. **State that must survive a door lives on `Game`** — `Party.spawn()` rebuilds every
   body at every scene change.
2. **A save is exactly what `reset_story()` clears, plus roster and current scene.** Add
   a `Game` field → update both, same commit.
3. **Never add a narrator box** (`say("")`). A card may ONLY state how much time passed.
4. **Prefer one scene with N phases** (a `Game.*_phase` router) over a new scene file.
   Note `Game.library_phase == ""` still MEANS `"ebb"` — name the phase explicitly at
   every call site.
5. **The narrative kit must never reference autoload identifiers**, or `--script` probes
   poison their own compile. Same reason `chapters.gd` is `class_name`-free.
6. There are exactly **three** `get_tree().paused` modals — `DevMenu`, `MixMenu`,
   `party_menu`. A new one must be in `Overlay.MODALS`.

Autoload order (`project.godot`): `Game` → `Party` → `DevMenu` → `MixMenu` →
`PartyMenu` → `Sfx` → `Music`. `Game` must stay first — everything else reads story
state off it. `Music` picks its track by scene path (`music.gd SCENE_TRACKS`) — a new
scene that wants music is one entry there, never a call from the scene. One-shot
sounds come from `Sfx` (`scene/sfx.gd`): menus call its `ui_*` verbs, travel calls
`door()`, and the dialog box blips speakers through `talk_blip()` — looked up by
PATH there, because the narrative kit never names an autoload.
Boot scene is `res://scene/title.tscn`.
