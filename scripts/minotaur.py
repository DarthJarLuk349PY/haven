from scripts.animation import load_strip
from scripts.enemy import Enemy


class Minotaur(Enemy):
    def __init__(self, x, y):
        super().__init__(
            x,
            y,
            max_health=500,
            speed=88,
            damage=22,
            attack_range=100,
            scale=0.56,
            ai_profile="defensive",
        )
        self.animations = {
            "idle": load_strip(
                "enemy_assets/minotor/other_1.png", 400, 300, frame_count=10
            ),
            "walk": load_strip(
                "enemy_assets/minotor/walk.png", 300, 300, frame_count=10
            ),
            "attack": load_strip(
                "enemy_assets/minotor/roll.png", 400, 300, frame_count=10
            ),
        }