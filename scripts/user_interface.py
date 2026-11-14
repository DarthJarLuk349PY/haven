import pygame


class UserInterface:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 28)
        self.large_font = pygame.font.Font(None, 64)
        self.width, self.height = game.screen.get_size()
        self.screen = game.screen