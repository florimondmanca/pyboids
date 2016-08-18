# pyboids by mancaf
# Implementing the Boid Flocking Behaviour algorithm
# in Python and Pygame

import pygame
import numpy as np
from . import utils, params

class Boid(pygame.sprite.Sprite):
	def __init__(self, pos=None, vel=None, leader=False):
		super().__init__()
		self.base_image, self.rect = utils.load_image("boid.png")
		self.image = self.base_image
		self._pos = pos if pos is not None else np.zeros(2)
		self.vel = vel if vel is not None else np.zeros(2)
		self.rect.center = self._pos
		self.steering = np.zeros(2)
		self.leader = leader
		self.mass = 1
		self.max_force = 1
		self.max_vel = params.V_LIM
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
		self.steering += force / self.mass

	def update(self):
		# limit the steering force
		self.steering = utils.truncate(self.steering, self.max_force)
		# limit the velocity
		self.vel = utils.truncate(self.vel + self.steering, self.max_vel)
		# integrate
		self.pos = self._pos + self.vel
		# rotate sprite
		self.rotate()

	def dist(self, other):
		return np.sqrt(np.dot(self._pos - other.pos, self._pos - other.pos))

	def display(self, screen):
		screen.blit(self.image, self.rect)
		if params.DEBUG:
			pygame.draw.line(screen, pygame.Color("red"),
				tuple(self.pos), tuple(self.pos + 4*self.vel))
			pygame.draw.line(screen, pygame.Color("blue"), tuple(self.pos), tuple(self.pos + 4*self.steering))
		self.steering = np.zeros(2)

