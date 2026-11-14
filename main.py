from pathlib import Path

import pygame

from scripts.config import load_game_settings
from scripts.jump_pads import JumpPadField
from scripts.maps import BACKGROUND_SCENES, Background
from scripts.player import Player
from scripts.spawner import EnemySpawner


class Game:
    def __init__(self):
        self.config = load_game_settings()
        pygame.init()
        pygame.display.set_caption(self.config.title)
        flags = pygame.FULLSCREEN if self.config.fullscreen else 0
        self.screen = pygame.display.set_mode(
            (self.config.width, self.config.height), flags
        )
        icon_path = Path(__file__).resolve().parent / "game_icon" / "icon.png"
        icon = pygame.image.load(str(icon_path)).convert_alpha()
        pygame.display.set_icon(pygame.transform.smoothscale(icon, (32, 32)))
        self.width, self.height = self.screen.get_size()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.large_font = pygame.font.Font(None, 64)
        self.background = Background((self.width, self.height))
        self.jump_pads = JumpPadField(
            self.width, self.height, self.config.jump_pads
        )
        self.elapsed_time = 0
        self.reset()

    def reset(self):
        self.player = Player(
            self.width / 2,
            self.height / 2,
            settings=self.config.player,
            world_size=(self.width, self.height),
        )
        self.enemies = []
        self.spawner = EnemySpawner(
            max_enemies=self.config.max_enemies,
            spawn_interval=self.config.spawn_interval,
            initial_delay=self.config.initial_spawn_delay,
        )
        for _ in range(self.config.initial_enemy_count):
            self.enemies.append(self.spawner.spawn(self.width, self.height))
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_f):
                    self.player.start_attack(pygame.mouse.get_pos()[0])
                elif event.key == pygame.K_e:
                    if sum(enemy.alive for enemy in self.enemies) < self.config.max_enemies:
                        self.enemies.append(
                            self.spawner.spawn(self.width, self.height)
                        )
                elif event.key == pygame.K_r and not self.player.alive:
                    self.reset()
                elif event.unicode in BACKGROUND_SCENES:
                    self.background.set_scene(event.unicode)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.player.start_attack(event.pos[0])

    def update(self, dt):
        self.elapsed_time += dt
        keys = pygame.key.get_pressed()
        self.enemies = [enemy for enemy in self.enemies if enemy.alive]

        if self.player.alive:
            for enemy in self.enemies:
                enemy.update(dt, self.player)

            blocking = (
                keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL] or pygame.mouse.get_pressed()[2]
            )
            self.player.update(
                dt, keys, self.enemies, blocking, jump_pads=self.jump_pads
            )

            spawned = self.spawner.update(dt, self.enemies, self.width, self.height)
            if spawned is not None:
                self.enemies.append(spawned)

    def draw(self):
        self.background.draw(self.screen)
        self.jump_pads.draw(self.screen, self.elapsed_time)

        for enemy in self.enemies:
            enemy.draw(self.screen)
        self.player.draw(self.screen)

        self._draw_hud()
        if not self.player.alive:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            self._draw_text(
                "You were defeated",
                self.large_font,
                (245, 220, 210),
                self.width // 2,
                self.height // 2 - 24,
                center=True,
            )
            self._draw_text(
                "Press R to try again",
                self.font,
                (235, 235, 235),
                self.width // 2,
                self.height // 2 + 28,
                center=True,
            )

        pygame.display.flip()

    def _draw_hud(self):
        pygame.draw.rect(self.screen, (18, 24, 28), (0, 0, self.width, 80))
        pygame.draw.rect(self.screen, (80, 35, 40), (22, 23, 240, 20), border_radius=5)
        health_width = round(236 * self.player.health / self.player.max_health)
        if health_width:
            pygame.draw.rect(
                self.screen,
                (205, 65, 65),
                (24, 25, health_width, 16),
                border_radius=4,
            )
        self._draw_text(
            f"Health {self.player.health}/{self.player.max_health}",
            self.font,
            (245, 245, 245),
            280,
            21,
        )
        self._draw_text(
            f"Enemies: {len(self.enemies)}",
            self.font,
            (245, 245, 245),
            self.width - 160,
            21,
        )
        self._draw_text(
            "WASD move | Shift run | Click/F attack | Ctrl block | E spawn | Step on pads to bounce",
            self.font,
            (205, 215, 215),
            22,
            52,
        )
        self._draw_text(
            f"Scene: {self.background.name} (1-4)",
            self.font,
            (205, 215, 215),
            self.width - 300,
            52,
        )

    def _draw_text(self, text, font, color, x, y, center=False):
        image = font.render(text, True, color)
        rect = image.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(image, rect)

    def run(self):
        while self.running:
            dt = min(self.clock.tick(self.config.fps) / 1000, 0.05)
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()

if __name__ == "__main__":
    Game().run()
