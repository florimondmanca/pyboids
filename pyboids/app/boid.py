"""Boid class."""
import pygame
import numpy as np
from . import utils
from . import params
from . import assets


class Boid(pygame.sprite.Sprite):
    """A normal boid.

    Parameters
    ----------
    pos : np.array
    vel : np.array
    """

    image_file = 'normal-boid.png'

    def __init__(self, pos=None, vel=None):
        super().__init__()
        if pos is None:
            pos = np.zeros(2)
        if vel is None:
            vel = np.zeros(2)
        self.base_image, self.rect = assets.image_with_rect(self.image_file)
        self.image = self.base_image
        self._pos = pos
        self.vel = vel
        self.rect.center = self._pos
        self.steering = np.zeros(2)
        self.mass = 20
        self.wandering_angle = np.pi * (2 * np.random.rand() - 1)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos):
        self._pos = pos
        self.rect.center = tuple(pos)

    def rotate(self):
        angle = -np.rad2deg(np.angle(self.vel[0] + 1j * self.vel[1]))
        self.image = pygame.transform.rotate(self.base_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def steer(self, force, alt_max=None):
        """Add a force to the current steering force."""
        # limit the steering each time we add a force
        if alt_max is not None:
            self.steering += utils.truncate(force / self.mass, alt_max)
        else:
            self.steering += utils.truncate(
                force / self.mass, params.BOID_MAX_FORCE)

    def update(self):
        self.vel = utils.truncate(
            self.vel + self.steering, params.BOID_MAX_SPEED)
        self.pos = self._pos + self.vel
        self.rotate()

    def display(self, screen, debug=False):
        screen.blit(self.image, self.rect)
        if debug:
            pygame.draw.line(
                screen, pygame.Color("red"),
                tuple(self.pos), tuple(self.pos + 2 * self.vel))
            pygame.draw.line(
                screen, pygame.Color("blue"), tuple(self.pos),
                tuple(self.pos + 30 * self.steering))

    def reset_frame(self):
        self.steering = np.zeros(2)


class LeaderBoid(Boid):
    """A boid that others boids want to follow."""

    image_file = 'leader-boid.png'
