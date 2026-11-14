import asyncio
import sys
from pathlib import Path

import pygame

from scripts.config import load_game_settings
from scripts.jump_pads import JumpPadField
from scripts.maps import BACKGROUND_SCENES, Background
from scripts.player import Player
from scripts.spawner import EnemySpawner
from scripts.user_interface import UserInterface


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
        self.is_web = sys.platform in ("emscripten", "wasi")
        self.background = Background((self.width, self.height))
        self.jump_pads = JumpPadField(
            self.width, self.height, self.config.jump_pads
        )
        self.ui = UserInterface(self)
        self.state = "menu"
        self.menu_return_state = "menu"
        self.elapsed_time = 0
        self.reset()
        self.state = "menu"

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
                continue

            if self.state != "playing":
                action = self.ui.handle_menu_event(event, self.state)
                if action is not None:
                    self._handle_menu_action(action)
                continue

            if self.is_web:
                handled, action = self.ui.handle_game_event(event)
                if action == "pause":
                    self.state = "paused"
                    self.ui.clear_controls()
                elif action == "attack":
                    self.player.start_attack(
                        self.player.x + self.player.facing
                    )
                if handled:
                    continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "paused"
                    self.ui.clear_controls()
                elif event.key in (pygame.K_SPACE, pygame.K_f):
                    self.player.start_attack(pygame.mouse.get_pos()[0])
                elif event.key == pygame.K_e:
                    if sum(enemy.alive for enemy in self.enemies) < self.config.max_enemies:
                        self.enemies.append(
                            self.spawner.spawn(self.width, self.height)
                        )
                elif event.unicode in BACKGROUND_SCENES:
                    self.background.set_scene(event.unicode)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.player.start_attack(event.pos[0])

    def _handle_menu_action(self, action):
        if action in ("start", "retry"):
            self.reset()
            self.state = "playing"
        elif action == "resume":
            self.state = "playing"
        elif action == "controls":
            self.menu_return_state = self.state
            self.state = "controls"
        elif action == "back":
            self.state = self.menu_return_state
        elif action == "main_menu":
            self.state = "menu"
        elif action == "quit":
            if self.is_web:
                self.state = "quit"
            else:
                self.running = False
        self.ui.clear_controls()

    def update(self, dt):
        if self.state != "playing":
            return

        self.elapsed_time += dt
        keys = pygame.key.get_pressed()
        self.enemies = [enemy for enemy in self.enemies if enemy.alive]

        if self.player.alive:
            for enemy in self.enemies:
                enemy.update(dt, self.player)

            blocking = (
                keys[pygame.K_LCTRL]
                or keys[pygame.K_RCTRL]
                or pygame.mouse.get_pressed()[2]
                or self.ui.is_pressed("block")
            )
            self.player.update(
                dt,
                keys,
                self.enemies,
                blocking,
                jump_pads=self.jump_pads,
                virtual_keys=self.ui.virtual_keys,
            )

            spawned = self.spawner.update(dt, self.enemies, self.width, self.height)
            if spawned is not None:
                self.enemies.append(spawned)
        elif self.state == "playing":
            self.state = "game_over"
            self.ui.clear_controls()

    def draw(self):
        self.background.draw(self.screen)
        self.jump_pads.draw(self.screen, self.elapsed_time)

        if self.state in ("playing", "paused", "game_over"):
            for enemy in self.enemies:
                enemy.draw(self.screen)
            self.player.draw(self.screen)
            self._draw_hud()

        if self.state == "playing":
            self.ui.draw_touch_controls()
        else:
            self.ui.draw_menu(self.state)

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
        controls = (
            "On-screen controls: move | RUN | ATK | BLK | II pauses"
            if self.is_web
            else "WASD move | Shift run | Click/F attack | Ctrl block | Esc pause"
        )
        self._draw_text(
            controls,
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

    async def run(self):
        while self.running:
            dt = min(self.clock.tick(self.config.fps) / 1000, 0.05)
            self.handle_events()
            self.update(dt)
            self.draw()
            await asyncio.sleep(0)
        pygame.quit()


async def main():
    game = Game()
    await game.run()


def run_web(port):
    import subprocess

    app_dir = Path(__file__).resolve().parent
    print(
        f"Starting the web game. Open http://localhost:{port} in your browser.",
        flush=True,
    )
    return subprocess.call(
        [sys.executable, "-m", "pygbag", "--port", str(port), str(app_dir)]
    )


def run_terminal():
    import argparse

    parser = argparse.ArgumentParser(
        description="Launch Haven Arena for desktop or in a web browser."
    )
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--desktop", action="store_true", help="Run the desktop game")
    modes.add_argument("--web", action="store_true", help="Run the web game")
    parser.add_argument(
        "--port", type=int, default=8000, help="Web server port (default: 8000)"
    )
    args = parser.parse_args()

    if args.desktop:
        asyncio.run(main())
        return 0
    if args.web:
        return run_web(args.port)
    if not sys.stdin.isatty():
        parser.error("Choose --desktop or --web when running without an interactive terminal.")

    while True:
        print("Choose a version to launch:\n  1) Desktop\n  2) Web")
        choice = input("Enter 1 or 2: ").strip().lower()
        if choice in ("1", "desktop", "d"):
            asyncio.run(main())
            return 0
        if choice in ("2", "web", "w"):
            return run_web(args.port)
        print("Please enter 1 for Desktop or 2 for Web.")


if __name__ == "__main__":
    if sys.platform in ("emscripten", "wasi"):
        asyncio.run(main())
    else:
        raise SystemExit(run_terminal())
