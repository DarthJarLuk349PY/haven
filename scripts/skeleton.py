from scripts.animation import load_strip
from scripts.enemy import Enemy


class Skeleton(Enemy):
    def __init__(self, x, y):
        super().__init__(
            x,
            y,
            max_health=75,
            speed=145,
            damage=12,
            attack_range=68,
            scale=2,
            ai_profile="aggressive",
        )
        self.animations = {
            "idle": load_strip(
                "enemy_assets/skeleton/skeletonIdle-Sheet64x64 (1).png",
                64,
                64,
                frame_count=3,
            ),
            "walk": load_strip(
                "enemy_assets/skeleton/skeletonMove-Sheet64x64 (1).png",
                64,
                64,
                frame_count=8,
            ),
            "attack": load_strip(
                "enemy_assets/skeleton/skeletonHurt-Sheet64x64 (1).png",
                64,
                64,
                frame_count=6,
            ),
        }