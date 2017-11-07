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

    def __init__(self, pos=None, vel=None, mass=20):
        super().__init__()
        if pos is None:
            pos = np.zeros(2)
        if vel is None:
            vel = np.zeros(2)
        self.base_image, self.rect = assets.image_with_rect(self.image_file)
        self.image = self.base_image
        self.pos = pos
        self.vel = vel
        self.mass = mass
        self.steering = np.zeros(2)
        self.wandering_angle = utils.randrange(-np.pi, np.pi)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos):
        self._pos = pos
        self.rect.center = tuple(pos)

    @property
    def vel(self):
        return self._vel

    @vel.setter
    def vel(self, vel):
        self._vel = vel
        self._rotate_image()

    def steer(self, force, alt_max=None):
        """Add a force to the current steering force."""
        # limit the steering each time we add a force
        if alt_max is not None:
            self.steering += utils.truncate(force / self.mass, alt_max)
        else:
            self.steering += utils.truncate(
                force / self.mass, params.BOID_MAX_FORCE)

    def _rotate_image(self):
        """Rotate base image using the velocity and assign to image."""
        angle = -np.rad2deg(np.angle(self.vel[0] + 1j * self.vel[1]))
        self.image = pygame.transform.rotate(self.base_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        self.vel = utils.truncate(
            self.vel + self.steering, params.BOID_MAX_SPEED)
        self.pos = self.pos + self.vel

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
