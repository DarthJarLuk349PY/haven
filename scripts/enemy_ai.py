import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


SETTINGS_PATH = Path(__file__).resolve().parents[1] / "settings" / "enemyai.json"
PROFILE_NAMES = ("aggressive", "defensive", "passive")
PROFILE_FIELDS = ("detection_range", "attack_range", "attack_cooldown")


@dataclass(frozen=True)
class AIProfile:
    detection_range: float
    attack_range: float 
    attack_cooldown: float


@lru_cache(maxsize=1)
def load_ai_profiles():
    with SETTINGS_PATH.open(encoding="utf-8") as settings_file:
        settings = json.load(settings_file)

    if not isinstance(settings, dict):
        raise ValueError(f"{SETTINGS_PATH} must contain a JSON object")
    profiles_data = settings.get("enemy_ai")
    if not isinstance(profiles_data, dict):
        raise ValueError(f"{SETTINGS_PATH} must contain an 'enemy_ai' object")

    profiles = {}
    for name in PROFILE_NAMES:
        values = profiles_data.get(name)
        if not isinstance(values, dict):
            raise ValueError(f"Missing enemy AI profile '{name}' in {SETTINGS_PATH}")

        parsed_values = {}
        for field in PROFILE_FIELDS:
            value = values.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(
                    f"Enemy AI setting '{name}.{field}' must be a positive number"
                )
            if not math.isfinite(value) or value <= 0:
                raise ValueError(
                    f"Enemy AI setting '{name}.{field}' must be a positive finite number"
                )
            parsed_values[field] = float(value)

        profiles[name] = AIProfile(**parsed_values)

    return profiles


class EnemyAI:
    ATTACK_WINDUP = 0.22
    ATTACK_DURATION = 0.38
    BLOCK_DURATION = 0.28
    BLOCK_COOLDOWN = 1.25

    def __init__(self, profile_name):
        if profile_name not in PROFILE_NAMES:
            raise ValueError(f"Unknown enemy AI profile: {profile_name}")
        self.profile = load_ai_profiles()[profile_name]

    def update(self, enemy, target, dt):
        dx = target.x - enemy.x
        dy = target.y - enemy.y
        distance = math.hypot(dx, dy)
        enemy.facing = 1 if dx >= 0 else -1
        enemy.block_timer = max(0, enemy.block_timer - dt)
        enemy.block_cooldown = max(0, enemy.block_cooldown - dt)

        if enemy.attack_hit_timer is not None:
            enemy.attack_hit_timer -= dt
            if enemy.attack_hit_timer <= 0:
                hit_distance = math.hypot(target.x - enemy.x, target.y - enemy.y)
                if target.alive and hit_distance <= self.profile.attack_range:
                    target.take_damage(enemy.damage, enemy.x)
                enemy.attack_hit_timer = None

        enemy.attack_timer = max(0, enemy.attack_timer - dt)
        if enemy.attack_timer > 0:
            enemy.blocking = False
            return "attack"

        enemy.blocking = False

        if not target.alive or distance > self.profile.detection_range:
            return "idle"

        if (
            target.attack_timer > 0
            and distance <= self.profile.attack_range + 50
            and enemy.block_cooldown <= 0
        ):
            enemy.block_timer = self.BLOCK_DURATION
            enemy.block_cooldown = self.BLOCK_COOLDOWN
        enemy.blocking = enemy.block_timer > 0

        if enemy.blocking:
            return "idle"

        if distance > self.profile.attack_range:
            if distance:
                enemy.x += dx / distance * enemy.speed * dt
                enemy.y += dy / distance * enemy.speed * dt
            return "walk"

        if enemy.attack_cooldown <= 0:
            enemy.attack_timer = self.ATTACK_DURATION
            enemy.attack_hit_timer = self.ATTACK_WINDUP
            enemy.attack_cooldown = self.profile.attack_cooldown
            return "attack"

        return "idle"
