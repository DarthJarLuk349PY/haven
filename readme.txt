HAVEN ARENA

Run from the repository root to start the web server:
    python main.py

Open http://localhost:8000 in your browser. Use `localhost` rather than
`127.0.0.1`; pygbag's browser resources can be blocked if the hostnames differ.
To install the supported web runner:
    python -m pip install pygbag==0.8.2

Run `python main.py --help` to see launcher options. If port 8000 is already
in use, choose another port:
    python main.py --port 8001
Then open http://localhost:8001.

Alternatively, start pygbag directly:
    python -m pygbag .


Game settings are loaded from `settings/settings.json`. Adjust the resolution
preset, fullscreen mode, target FPS, player health and combat values, enemy
spawn count, spawn limit, and spawn timing there. Enemy AI ranges and cooldowns
remain in `settings/enemyai.json`. Restart the game after editing settings.

Controls:
    WASD or arrow keys  Move
    Shift               Run
    Left mouse / F      Attack
    Ctrl / right mouse  Block (reduces frontal damage)
    E                   Spawn an enemy
    R                   Restart after defeat
    1-4                 Change the arena background
use pyhton main.py --help
Walk onto a glowing jump pad to launch upward. The player rises, falls under
gravity, and automatically bounces again if they land on a pad.
The pads use `bounce_pad/_bounce_pad.png`, and the window icon loads from
`game_icon/icon.png`.

Skeletons, minotaurs, and hellhounds spawn automatically. Each enemy can attack
and briefly block the player's attacks; defeating enemies removes them from the
arena.

Enemy behavior is configured in `settings/enemyai.json`. Skeletons use the
aggressive profile, minotaurs use defensive, and hellhounds use passive. Each
profile's detection range controls when an enemy notices and pursues the player;
attack range controls when it can hit, and attack cooldown is the delay between
attacks. Changes are read when the game starts.

The four backgrounds are loaded from `background_assets/PNG` and can be changed
without restarting.

The player sprites are from Ozzbit Games' free asset pack. The included license
allows personal, non-commercial projects, permits modifications, and requires
credit to Ozzbit Games.

Source Assest:

https://hsdsz.itch.io/cerberus-infernal-guardian-fantasy-rpg-005-2d-animated-boss-pack
https://hsdsz.itch.io/minotaur-berserker-fantasy-rpg-002-2d-animated-character-pack#google_vignette
https://dotto-e.itch.io/skeleton-platformer
https://ozzbit-games.itch.io/action-platformer-character-template
https://free-game-assets.itch.io/free-vampires-locations-battle-background-pack

