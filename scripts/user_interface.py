import sys

import pygame


class UserInterface:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.width, self.height = self.screen.get_size()
        self.font = pygame.font.Font(None, 28)
        self.button_font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 64)
        self.is_web = sys.platform in ("emscripten", "wasi")
        self.menu_buttons = []
        self.active_controls = {}

    def draw_menu(self, state):
        titles = {
            "menu": ("Haven Arena", "Choose an option"),
            "paused": ("Paused", "The arena is paused"),
            "game_over": ("You were defeated", "Try again or return to the menu"),
            "controls": ("Controls", "Input differs by platform"),
            "quit": ("Thanks for playing", "You can close this browser tab"),
        }
        menus = {
            "menu": (("Play", "start"), ("Controls", "controls"), ("Quit", "quit")),
            "paused": (
                ("Resume", "resume"),
                ("Controls", "controls"),
                ("Main Menu", "main_menu"),
                ("Quit", "quit"),
            ),
            "game_over": (
                ("Try Again", "retry"),
                ("Main Menu", "main_menu"),
                ("Quit", "quit"),
            ),
            "controls": (("Back", "back"),),
            "quit": (),
        }
        title, subtitle = titles[state]
        buttons = menus[state]
        details = self._control_details() if state == "controls" else ()

        panel_width = min(560, self.width - 32)
        button_height = 52
        panel_height = 150 + len(details) * 32 + len(buttons) * (button_height + 12)
        panel = pygame.Rect(
            (self.width - panel_width) // 2,
            (self.height - panel_height) // 2,
            panel_width,
            panel_height,
        )

        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((5, 9, 14, 190))
        pygame.draw.rect(overlay, (18, 27, 35, 245), panel, border_radius=18)
        pygame.draw.rect(overlay, (77, 161, 164, 255), panel, 2, border_radius=18)
        self.screen.blit(overlay, (0, 0))

        self._draw_text(title, self.large_font, (245, 232, 210), self.width // 2, panel.y + 42, True)
        self._draw_text(
            subtitle, self.font, (190, 210, 213), self.width // 2, panel.y + 83, True
        )

        content_y = panel.y + 112
        for line in details:
            self._draw_text(
                line, self.font, (225, 230, 228), panel.centerx, content_y, True
            )
            content_y += 32

        button_width = min(340, panel_width - 44)
        button_x = panel.centerx - button_width // 2
        self.menu_buttons = []
        for label, action in buttons:
            rect = pygame.Rect(button_x, content_y, button_width, button_height)
            pygame.draw.rect(
                self.screen, (36, 76, 82), rect, border_radius=10
            )
            pygame.draw.rect(
                self.screen, (96, 182, 180), rect, 2, border_radius=10
            )
            self._draw_text(
                label,
                self.button_font,
                (248, 245, 232),
                rect.centerx,
                rect.centery,
                True,
            )
            self.menu_buttons.append((action, rect))
            content_y += button_height + 12

        if state == "quit":
            hint = "Close this browser tab to exit"
        else:
            hint = "Tap a button" if self.is_web else "Click a button or press Enter"
        self._draw_text(
            hint, self.font, (165, 181, 185), panel.centerx, panel.bottom - 22, True
        )

    def handle_menu_event(self, event, state):
        if event.type == pygame.KEYDOWN:
            if state == "game_over" and event.key == pygame.K_r:
                return "retry"
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.menu_buttons[0][0] if self.menu_buttons else None
            if event.key == pygame.K_ESCAPE:
                return {
                    "paused": "resume",
                    "controls": "back",
                    "game_over": "main_menu",
                    "menu": "quit",
                }.get(state)

        if event.type not in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button != 1:
            return None

        pos = self._event_position(event)
        for action, rect in self.menu_buttons:
            if rect.collidepoint(pos):
                return action
        return None

    def handle_game_event(self, event):
        if not self.is_web:
            return False, None

        finger_down = event.type == pygame.FINGERDOWN
        mouse_down = event.type == pygame.MOUSEBUTTONDOWN
        if finger_down or (mouse_down and event.button in (1, 3)):
            pos = self._event_position(event)
            pointer = self._pointer_id(event)
            for name, rect in self._touch_rects().items():
                if rect.collidepoint(pos):
                    self.active_controls[pointer] = name
                    if name == "attack":
                        return True, "attack"
                    if name == "pause":
                        return True, "pause"
                    return True, None
            if mouse_down and event.button == 3:
                self.active_controls[pointer] = "block"
                return True, None
            self.active_controls[pointer] = "attack"
            return True, "attack"

        finger_up = event.type == pygame.FINGERUP
        mouse_up = event.type == pygame.MOUSEBUTTONUP
        if finger_up or mouse_up:
            pointer = self._pointer_id(event)
            return self.active_controls.pop(pointer, None) is not None, None

        return False, None

    @property
    def virtual_keys(self):
        keys = set()
        key_controls = {
            "left": (pygame.K_a, pygame.K_LEFT),
            "right": (pygame.K_d, pygame.K_RIGHT),
            "up": (pygame.K_w, pygame.K_UP),
            "down": (pygame.K_s, pygame.K_DOWN),
            "run": (pygame.K_LSHIFT, pygame.K_RSHIFT),
        }
        for action in self.active_controls.values():
            keys.update(key_controls.get(action, ()))
        return keys

    def is_pressed(self, action):
        return action in self.active_controls.values()

    def clear_controls(self):
        self.active_controls.clear()

    def draw_touch_controls(self):
        if not self.is_web:
            return

        controls = self._touch_rects()
        labels = {
            "left": "<",
            "right": ">",
            "up": "UP",
            "down": "DN",
            "run": "RUN",
            "attack": "ATK",
            "block": "BLK",
            "pause": "II",
        }
        active = set(self.active_controls.values())
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for name, rect in controls.items():
            color = (60, 155, 151, 210) if name in active else (13, 25, 32, 155)
            pygame.draw.rect(overlay, color, rect, border_radius=14)
            pygame.draw.rect(
                overlay, (143, 222, 209, 220), rect, 2, border_radius=14
            )
            image = self.button_font.render(
                labels[name], True, (248, 248, 235)
            )
            overlay.blit(image, image.get_rect(center=rect.center))
        self.screen.blit(overlay, (0, 0))

    def _control_details(self):
        if self.is_web:
            return (
                "Use the on-screen arrows to move and RUN to sprint.",
                "ATK attacks, BLK blocks, and II pauses the game.",
                "You can also tap the arena to attack.",
            )
        return (
            "WASD or arrow keys: move",
            "Shift: run   |   Left mouse or F: attack",
            "Ctrl or right mouse: block   |   Esc: pause",
            "E: spawn an enemy   |   1-4: change the scene",
            "R: restart after defeat",
        )

    def _touch_rects(self):
        size = max(48, min(72, round(min(self.width, self.height) * 0.09)))
        margin = 22
        base_x = margin
        base_y = self.height - size * 3 - 28
        center_x = base_x + size + 6
        right_x = self.width - margin - size
        action_x = right_x - size - 10
        bottom_y = self.height - margin - size
        return {
            "up": pygame.Rect(center_x, base_y, size, size),
            "left": pygame.Rect(base_x, base_y + size + 6, size, size),
            "down": pygame.Rect(center_x, base_y + size + 6, size, size),
            "right": pygame.Rect(base_x + 2 * (size + 6), base_y + size + 6, size, size),
            "run": pygame.Rect(action_x, bottom_y - size - 10, size, size),
            "block": pygame.Rect(action_x, bottom_y, size, size),
            "attack": pygame.Rect(right_x, bottom_y, size, size),
            "pause": pygame.Rect(right_x, 92, size, size),
        }

    def _event_position(self, event):
        if event.type in (pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION):
            return round(event.x * self.width), round(event.y * self.height)
        return event.pos

    @staticmethod
    def _pointer_id(event):
        if event.type in (pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION):
            return ("finger", getattr(event, "touch_id", 0), event.finger_id)
        return ("mouse", event.button)

    def _draw_text(self, text, font, color, x, y, center=False):
        image = font.render(text, True, color)
        rect = image.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(image, rect)
