from scripts.animation import load_strip
from scripts.enemy import Enemy


class Hellhound(Enemy):
    def __init__(self, x, y):
        super().__init__(
            x,
            y,
            max_health=200,
            speed=165,
            damage=16,
            scale=0.28,
            ai_profile="passive",
        )
        self.animations = {
            "idle": load_strip(
                "enemy_assets/3head_/idle.png", 800, 800, frame_count=10
            ),
            "walk": load_strip(
                "enemy_assets/3head_/idle.png", 800, 800, frame_count=10, row=1
            ),
            "attack": load_strip(
                "enemy_assets/3head_/howl.png", 800, 800, frame_count=10
            ),
        }
