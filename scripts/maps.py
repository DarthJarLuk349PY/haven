from pathlib import Path

import pygame


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKGROUND_SCENES = {
    "1": ("Terrace", "background_assets/PNG/1/terrace.png"),
    "2": ("Throne Room", "background_assets/PNG/2/throne room.png"),
    "3": ("Castle", "background_assets/PNG/3/castle.png"),
    "4": ("Dead Forest", "background_assets/PNG/4/dead forest.png"),

}


class Background:
    def __init__(self, size, scene="1"):
        self.size = size
        self.scene = None
        self.image = None
        self.set_scene(scene)

    def set_scene(self, scene):
        if scene not in BACKGROUND_SCENES:
            raise ValueError(f"Unknown background scene: {scene}")
        if scene == self.scene:
            return None

        _, relative_path = BACKGROUND_SCENES[scene]
        path = ROOT_DIR / relative_path
        image = pygame.image.load(str(path)).convert()
        self.image = pygame.transform.smoothscale(image, self.size)
        self.scene = scene

    @property
    def name(self):
        return BACKGROUND_SCENES[self.scene][0]

    def draw(self, surface):
        surface.blit(self.image, (0, 0))