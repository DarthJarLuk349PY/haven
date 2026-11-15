import random

from scripts.hellhound import Hellhound
from scripts.minotaur import Minotaur
from scripts.skeleton import Skeleton


class EnemySpawner:
    SPAWN_MARGIN = 120

    def __init__(self, max_enemies=10, spawn_interval=3.5, initial_delay=1.0):
        self.max_enemies = max_enemies
        self.spawn_interval = spawn_interval
        self.timer = initial_delay
        self.next_enemy = 0

    def spawn(self, width, height):
        margin = min(self.SPAWN_MARGIN, width // 2)
        x, y = random.randint(margin, width - margin), height // 2

        enemy_types = (Skeleton, Minotaur, Hellhound)
        enemy_type = enemy_types[self.next_enemy % len(enemy_types)]
        self.next_enemy += 1
        return enemy_type(x, y)

    def update(self, dt, enemies, width, height):
        self.timer -= dt 
        if self.timer > 0:
            return None

        self.timer = self.spawn_interval
        if sum(enemy.alive for enemy in enemies) >= self.max_enemies:
            return None
        return self.spawn(width, height)
