# pyboids by mancaf
# Implementing the Boid Flocking Behaviour algorithm
# in Python and Pygame

import pygame
from random import random
from . import params, utils
from .boid import Boid

class Flock(pygame.sprite.Sprite):
	boids = pygame.sprite.Group()
	default_speed = 10

	def __init__(self):
		super().__init__()

	def add_boid(self, pos):
		self.boids.add(Boid(
			pos=utils.Vector2(pos),
			vel=utils.Vector2(self.default_speed*(2*random() - 1), self.default_speed*(2*random() - 1))
			)
		)

	def update(self, motion_event, click_event):
		if click_event:
			self.add_boid(click_event.pos)
		self.boids.update(motion_event, click_event)

	def display(self, screen):
		for boid in self.boids:
			boid.display(screen)