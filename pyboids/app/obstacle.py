"""Obstacle class."""
import pygame
import numpy as np
from . import utils, params


class Obstacle(pygame.sprite.Sprite):
    """A circular obstacle for boids to avoid."""

    def __init__(self, pos=None, radius=params.OBSTACLE_DEFAULT_RADIUS):
        super().__init__()
        self.image, self.rect = utils.load_image_and_rect("obstacle-circle.png")
        self.image = pygame.transform.smoothscale(
            self.image, (2 * radius, 2 * radius))
        self.pos = pos if pos is not None else np.zeros(2)
        self.radius = radius
        self.rect = self.image.get_rect(center=self.pos)

    def display(self, screen):
        screen.blit(self.image, self.rect)
