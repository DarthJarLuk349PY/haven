import math
from pathlib import Path

import pygame


ROOT_DIR = Path(__file__).resolve().parents[1]


class JumpPad:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def contains(self, x, y):
        dx = x - self.x
        dy = y - self.y
        return dx * dx + dy * dy <= self.radius * self.radius


class JumpPadField:
    POSITIONS = ((0.2, 0.3), (0.5, 0.68), (0.8, 0.3), (0.5, 0.42))

    def __init__(self, width, height, settings):
        if settings.count > len(self.POSITIONS):
            raise ValueError(f"Jump pad count cannot exceed {len(self.POSITIONS)}")
        self.pads = [
            JumpPad(
                round(width * x_ratio),
                round(96 + max(0, height - 130) * y_ratio),
                settings.radius,
            )
            for x_ratio, y_ratio in self.POSITIONS[: settings.count]
        ]
        self.launch_velocity = settings.launch_velocity
        self.gravity = settings.gravity
        image_path = ROOT_DIR / "bounce_pad" / "_bounce_pad.png"
        pad_image = pygame.image.load(str(image_path)).convert_alpha()
        pad_size = round(settings.radius * 2)
        self.pad_image = pygame.transform.smoothscale(
            pad_image, (pad_size, pad_size)
        )

    def pad_at(self, x, y):
        return next((pad for pad in self.pads if pad.contains(x, y)), None)

    def draw(self, surface, elapsed_time):
        pulse = round(3 + 3 * (1 + math.sin(elapsed_time * 4)) / 2)
        for pad in self.pads:
            center = (round(pad.x), round(pad.y))
            pygame.draw.circle(
                surface, (16, 36, 43), center, round(pad.radius) + 5
            )
            pygame.draw.circle(
                surface, (28, 112, 124), center, round(pad.radius), 4
            )
            pygame.draw.circle(
                surface, (62, 177, 174), center, round(pad.radius) - pulse, 2
            )
            surface.blit(self.pad_image, self.pad_image.get_rect(center=center))
            tip_y = round(pad.y - pad.radius * 0.3)
            pygame.draw.polygon(
                surface,
                (166, 242, 222),
                (
                    (round(pad.x), tip_y),
                    (round(pad.x - pad.radius * 0.28), round(pad.y)),
                    (round(pad.x - pad.radius * 0.1), round(pad.y)),
                    (round(pad.x - pad.radius * 0.1), round(pad.y + pad.radius * 0.28)),
                    (round(pad.x + pad.radius * 0.1), round(pad.y + pad.radius * 0.28)),
                    (round(pad.x + pad.radius * 0.1), round(pad.y)),
                    (round(pad.x + pad.radius * 0.28), round(pad.y)),
                ),
            )
