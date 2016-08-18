# pyboids by mancaf
# Implementing the Boid Flocking Behaviour algorithm
# in Python and Pygame

import pygame
from . import params
from . import utils

class Flock(pygame.sprite.Sprite):
	_pos = utils.Vector2()
	_vel = utils.Vector2()

	def __init__(self, pos=None, vel=None):
		super().__init__()
		self.image, self.rect = utils.load_image("boid.png")
		if pos is not None:
			self._pos = pos
		if vel is not None:
			self._vel = vel

	def _get_pos(self):
		return self._pos
	def _set_pos(self, pos):
		self._pos = pos
		self.rect.center = pos.data

	def _get_vel(self):
		return self._vel
	def _set_vel(self, vel):
		self._vel = vel

	def update(self):
		pass

	def display(self, screen):
		screen.blit(self.image, self.rect)
