import pygame
from math import floor


class Screen:
    def __init__(self, res):
        pygame.init()

        self.res = res
        self.screen = pygame.display.set_mode(res)
        self.scaling = None

    def change_res(self, res, world=None):
        self.res = res
        self.screen = pygame.display.set_mode(res)
        if world is not None:
            self.update_scaling(world)

    def update_scaling(self, world):
        width, height = self.res
        world_width, world_height = world.setup.world_size
        try:
            self.scaling = min((width / world_width), height / world_height)
        except ZeroDivisionError():
            raise RuntimeError("Attempted to update scaling using a world with"
                               " a 0 world_width or world_height. Have you"
                               "used a world without a setup size?")

    def draw_block(self, pos, colour):
        block_size = floor(self.scaling * 0.8)
        x, y = pos
        x *= int(self.scaling)
        y *= int(self.scaling)
        rect = pygame.Rect(x, y, block_size, block_size)
        pygame.draw.rect(self.screen, colour, rect)

    def draw_outline(self, pos, size, colour, thickness=1):
        x_size, y_size = size
        x_size *= self.scaling
        y_size *= self.scaling
        x, y = pos
        x *= self.scaling
        y *= self.scaling
        rect = pygame.Rect(x, y, int(x_size), int(y_size))
        pygame.draw.rect(self.screen, colour, rect, thickness)

    def flip(self):
        pygame.display.flip()
