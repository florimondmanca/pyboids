# pyboids by mancaf
# Implementing the Boid Flocking Behaviour algorithm
# in Python and Pygame

import pygame
import numpy as np
from random import random
import threading, queue
from . import params, utils
from .boid import Boid

class Flock(pygame.sprite.Sprite):
	"""
	Flock() -> Flock
	Represents a set of boids that obey to certain behaviours.
	"""
	def __init__(self):
		super().__init__()
		self.boids = pygame.sprite.Group()
		self.behaviours = {
			"seek": True,
			"flee": False,
			"wander": False
		}

	def add_boid(self, pos):
		leader = len(self.boids) == 0
		self.boids.add(Boid(
			pos=np.array(pos, dtype=np.float64),
			vel=np.array([params.V_LIM*(2*(random()<0.5) - 1)*(0.5+0.5*random()), params.V_LIM*(2*(random()<0.5) - 1)*(0.5+0.5*random())], dtype=np.float64),
			leader=leader
			)
		)

	def find_neighbors(self, boid, radius):
		neighbors = []
		for other_boid in self.boids:
			if other_boid != boid:
				if boid.dist(other_boid) < radius:
					neighbors.append(other_boid)
		return neighbors

	def remain_in_screen(self):
		for boid in self.boids:
			if boid.pos[0] > params.SCREEN_WIDTH - params.MARGIN:
				boid.steer(np.array([-params.V_B, 0.]))
			if boid.pos[0] < params.MARGIN:
				boid.steer(np.array([params.V_B, 0.]))
			if boid.pos[1] < params.MARGIN:
				boid.steer(np.array([0., params.V_B]))
			if boid.pos[1] > params.SCREEN_HEIGHT - params.MARGIN:
				boid.steer(np.array([0., -params.V_B]))

	def seek(self, target):
		""" Makes all boids seek to go to a target. """
		target = np.array(target, dtype=np.float64)
		for boid in self.boids:
			boid.steer(utils.normalize(target - boid.pos) * params.V_LIM - boid.vel)

	def flee(self, target):
		""" Makes all boids fly away from a target. """
		target = np.array(target, dtype=np.float64)
		for boid in self.boids:
			boid.steer(utils.normalize(boid.pos - target) * params.V_LIM - boid.vel)

	def wander(self):
		""" Makes the boids randomly wander around. """
		for i, boid in enumerate(self.boids):
			# calculate circle center
			circle_center = utils.normalize(boid.vel) * params.WANDER_DIST
			# calculate displacement force
			c, s = np.cos(boid.wandering_angle), np.sin(boid.wandering_angle)
			displacement = np.dot(np.array([[c, -s], [s, c]]), utils.normalize(boid.vel) * params.WANDER_RADIUS)
			boid.steer(circle_center + displacement)
			boid.wandering_angle += params.WANDER_ANGLE * (2*np.random.rand() - 1)

	def parallel_update_boids(self, q):
		while not q.empty():
			boid = q.get()
			boid.update()
			q.task_done()

	def update(self, motion_event, click_event):
		# add boid if required by a click
		if click_event and click_event.button == 3:
			self.add_boid(click_event.pos)
		# apply steering effets
		target = pygame.mouse.get_pos()
		if self.behaviours["seek"]:
			self.seek(target)
		if self.behaviours["flee"]:
			self.flee(target)
		if self.behaviours["wander"]:
			self.wander()
		self.remain_in_screen()
		# update all boids using multithreading
		q = queue.Queue()
		for boid in self.boids:
			q.put(boid)
		for i in range(params.N_CPU):
			threading.Thread(target=self.parallel_update_boids, args=[q]).start()
		q.join()

	def display(self, screen):
		for boid in self.boids:
			boid.display(screen)
