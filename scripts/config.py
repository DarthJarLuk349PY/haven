import json
import math
from dataclasses import dataclass
from pathlib import Path


SETTINGS_PATH = Path(__file__).resolve().parents[1] / "settings" / "settings.json"


@dataclass(frozen=True)
class PlayerSettings:
    max_health: int
    walk_speed: float
    run_speed: float
    attack_damage: int
    attack_range: float
    attack_cooldown: float
    attack_windup: float
    attack_duration: float


@dataclass(frozen=True)
class JumpPadSettings:
    count: int
    radius: float
    launch_velocity: float
    gravity: float


@dataclass(frozen=True)
class GameSettings:
    width: int
    height: int
    fullscreen: bool
    fps: int
    title: str
    volume: float
    initial_enemy_count: int
    max_enemies: int
    spawn_interval: float
    initial_spawn_delay: float
    player: PlayerSettings
    jump_pads: JumpPadSettings


def _positive_number(section, key, *, integer=False):
    value = section.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Setting '{key}' must be a positive number")
    if not math.isfinite(value) or value <= 0 or (integer and not isinstance(value, int)):
        raise ValueError(f"Setting '{key}' must be a positive {'integer' if integer else 'number'}")
    return value


def load_game_settings(path=SETTINGS_PATH):
    with Path(path).open(encoding="utf-8") as settings_file:
        data = json.load(settings_file)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")

    game_settings = data.get("game_settings")
    if not isinstance(game_settings, dict):
        raise ValueError(f"{path} must contain a 'game_settings' object")

    presets = game_settings.get("presets")
    if not isinstance(presets, dict):
        raise ValueError(f"{path} must contain game_settings.presets")
    preset_name = game_settings.get("resolution_preset")
    preset = presets.get(preset_name)
    if not isinstance(preset, dict):
        raise ValueError(f"Unknown resolution preset: {preset_name}")

    width = _positive_number(preset, "width", integer=True)
    height = _positive_number(preset, "height", integer=True)
    if width < 320 or height < 240:
        raise ValueError("Display width must be at least 320 and height at least 240")

    fullscreen = game_settings.get("fullscreen")
    if not isinstance(fullscreen, bool):
        raise ValueError("Setting 'fullscreen' must be true or false")
    title = game_settings.get("window_title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Setting 'window_title' must be a non-empty string")

    spawning = game_settings.get("spawning")
    player = game_settings.get("player")
    jump_pads = game_settings.get("jump_pads")
    if not isinstance(spawning, dict) or not isinstance(player, dict):
        raise ValueError("Settings must include 'spawning' and 'player' objects")
    if not isinstance(jump_pads, dict):
        raise ValueError("Settings must include a 'jump_pads' object")

    initial_enemy_count = _positive_number(
        spawning, "initial_enemy_count", integer=True
    )
    max_enemies = _positive_number(spawning, "max_enemies", integer=True)
    if initial_enemy_count > max_enemies:
        raise ValueError("initial_enemy_count cannot exceed max_enemies")

    volume = game_settings.get("volume")
    if isinstance(volume, bool) or not isinstance(volume, (int, float)):
        raise ValueError("Setting 'volume' must be a number from 0 to 1")
    if not math.isfinite(volume) or not 0 <= volume <= 1:
        raise ValueError("Setting 'volume' must be a number from 0 to 1")

    attack_duration = _positive_number(player, "attack_duration")
    attack_windup = _positive_number(player, "attack_windup")
    if attack_windup >= attack_duration:
        raise ValueError("player.attack_windup must be shorter than attack_duration")

    return GameSettings(
        width=width,
        height=height,
        fullscreen=fullscreen,
        fps=_positive_number(game_settings, "fps", integer=True),
        title=title.strip(),
        volume=float(volume),
        initial_enemy_count=initial_enemy_count,
        max_enemies=max_enemies,
        spawn_interval=_positive_number(spawning, "interval_seconds"),
        initial_spawn_delay=_positive_number(spawning, "initial_delay_seconds"),
        player=PlayerSettings(
            max_health=_positive_number(player, "max_health", integer=True),
            walk_speed=_positive_number(player, "walk_speed"),
            run_speed=_positive_number(player, "run_speed"),
            attack_damage=_positive_number(player, "attack_damage", integer=True),
            attack_range=_positive_number(player, "attack_range"),
            attack_cooldown=_positive_number(player, "attack_cooldown"),
            attack_windup=attack_windup,
            attack_duration=attack_duration,
        ),
        jump_pads=JumpPadSettings(
            count=_positive_number(jump_pads, "count", integer=True),
            radius=_positive_number(jump_pads, "radius"),
            launch_velocity=_positive_number(jump_pads, "launch_velocity"),
            gravity=_positive_number(jump_pads, "gravity"),
        ),
    )
