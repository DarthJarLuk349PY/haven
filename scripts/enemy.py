import pygame

from scripts.combat import Combatant
from scripts.enemy_ai import EnemyAI


class Enemy(Combatant):
    def __init__(
        self, x, y, max_health, speed, damage, attack_range, scale, ai_profile
    ):
        super().__init__(x, y, max_health)
        self.speed = speed
        self.damage = damage
        self.attack_range = attack_range
        self.scale = scale
        self.ai = EnemyAI(ai_profile)
        self.state = "idle"
        self.frame = 0
        self.animation_timer = 0
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_hit_timer = None
        self.block_timer = 0
        self.block_cooldown = 0
        self.hit_flash = 0
        self.dead = False
        self._animation_state = "idle"

    def update(self, dt, target):
        if not self.alive:
            self.dead = True
            return

        self.hit_flash = max(0, self.hit_flash - dt)
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.state = self.ai.update(self, target, dt)
        self._reset_animation_on_state_change()
        self._advance_animation(dt)

    def take_damage(self, amount, attacker_x):
        damage = super().take_damage(amount, attacker_x)
        if damage:
            self.hit_flash = 0.14
        if not self.alive:
            self.dead = True
        return damage

    def _advance_animation(self, dt):
        self.animation_timer += dt
        frames = self.animations.get(self.state, self.animations["idle"])
        frame_time = 0.09 if self.state == "attack" else 0.12
        if self.animation_timer >= frame_time:
            self.animation_timer %= frame_time
            if self.state == "attack":
                self.frame = min(self.frame + 1, len(frames) - 1)
            else:
                self.frame = (self.frame + 1) % len(frames)
        if self.frame >= len(frames):
            self.frame = 0

    def _reset_animation_on_state_change(self):
        if self.state != self._animation_state:
            self._animation_state = self.state
            self.frame = 0
            self.animation_timer = 0

    def draw(self, surface):
        image = self.animations[self.state][self.frame]
        if self.facing < 0:
            image = pygame.transform.flip(image, True, False)
        size = (
            max(1, round(image.get_width() * self.scale)),
            max(1, round(image.get_height() * self.scale)),
        )
        image = pygame.transform.scale(image, size)
        if self.hit_flash:
            image = image.copy()
            image.fill((255, 90, 90, 95), special_flags=pygame.BLEND_RGBA_ADD)
        image_rect = image.get_rect(center=(round(self.x), round(self.y)))
        surface.blit(image, image_rect)

        bar_width = 58 if self.scale < 1 else 72
        bar_rect = pygame.Rect(
            round(self.x - bar_width / 2), image_rect.top - 11, bar_width, 7
        )
        pygame.draw.rect(surface, (70, 30, 30), bar_rect, border_radius=3)
        health_width = round(bar_width * self.health / self.max_health)
        if health_width:
            pygame.draw.rect(
                surface,
                (205, 65, 65),
                (bar_rect.x, bar_rect.y, health_width, bar_rect.height),
                border_radius=3,
            )
        if self.blocking:
            pygame.draw.circle(
                surface, (255, 205, 90), (round(self.x), round(self.y)), 42, 3
            )
