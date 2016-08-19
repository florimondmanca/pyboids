# pyboids by mancaf
# Implementing the Boid Flocking Behaviour algorithm
# in Python and Pygame

import pygame
import numpy as np
from . import utils, params

class Boid(pygame.sprite.Sprite):
	""" A normal boid that can seek after, fly away from, or pursue a target boid """
	def __init__(self, pos=None, vel=None, name="normal-boid.png"):
		super().__init__()
		self.base_image, self.rect = utils.load_image(name)
		self.image = self.base_image
		self._pos = pos if pos is not None else np.zeros(2)
		self.vel = vel if vel is not None else np.zeros(2)
		self.rect.center = self._pos
		self.steering = np.zeros(2)
		self.mass = 1
		self.wandering_angle = np.pi*(2*np.random.rand() - 1)

	def get_pos(self):
		return self._pos
	def set_pos(self, pos):
		self._pos = pos
		self.rect.center = tuple(pos)
	pos = property(get_pos, set_pos)

	def rotate(self):
		self.image = pygame.transform.rotate(self.base_image, -np.rad2deg(np.angle(self.vel[0] + 1j*self.vel[1])))
		self.rect = self.image.get_rect(center=self.rect.center)

	def steer(self, force):
		""" Adds a force to the current steering force """
		# limit the steering each time we add a force
		self.steering += utils.truncate(force/self.mass, 2*params.BOID_MAX_FORCE)

	def dist(self, other):
		if other is None:
			return float("inf")
		else:
			return np.sqrt(np.dot(self.pos - other.pos, self.pos - other.pos))

	def dist_pos(self, pos):
		return np.sqrt(np.dot(self.pos - pos, self.pos - pos))

	def update(self):
		# limit the velocity
		self.vel = utils.truncate(self.vel + self.steering, params.BOID_MAX_SPEED)
		# integrate
		self.pos = self._pos + self.vel
		# rotate sprite
		self.rotate()

	def display(self, screen):
		screen.blit(self.image, self.rect)
		if params.DEBUG:
			pygame.draw.line(screen, pygame.Color("red"),
				tuple(self.pos), tuple(self.pos + 4*self.vel))
			pygame.draw.line(screen, pygame.Color("blue"), tuple(self.pos), tuple(self.pos + 20*self.steering))
		self.steering = np.zeros(2)


class LeaderBoid(Boid):
	""" A boid that others boids want to follow (seek) """
	def __init__(self, pos=None, vel=None):
		super().__init__(pos, vel, name="leader-boid.png")
