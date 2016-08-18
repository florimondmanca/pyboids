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
	max_speed = 10

	def __init__(self):
		super().__init__()
		self.boids = pygame.sprite.Group()
		self.behaviours = {
			"seek": True,
		}

	def add_boid(self, pos):
		leader = len(self.boids) == 0
		self.boids.add(Boid(
			pos=np.array(pos, dtype=np.float64),
			vel=np.array([self.max_speed*(2*(random()<0.5) - 1)*(0.5+0.5*random()), self.max_speed*(2*(random()<0.5) - 1)*(0.5+0.5*random())], dtype=np.float64),
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

	def seek(self, seek_pos):
		""" Makes all boids seek after a given 'seek_pos' position, eg the mouse's position. """
		seek_pos = np.array([seek_pos[0], seek_pos[1]], dtype=np.float64)
		for boid in self.boids:
			boid.steer(utils.normalize(seek_pos - boid.pos) * self.max_speed - boid.vel)

	def toggle_seek(self):
		self.behaviours["seek"] = not self.behaviours["seek"]

	def parallel_update_funcs(self, q):
		while not q.empty():
			operation = q.get()
			operation()
			q.task_done()

	def parallel_update_boids(self, q):
		while not q.empty():
			boid = q.get()
			boid.update()
			q.task_done()

	def update(self, motion_event, click_event):
		if click_event:
			self.add_boid(click_event.pos)
		if self.behaviours["seek"]:
			self.seek(pygame.mouse.get_pos())
		self.remain_in_screen()
		q = queue.Queue()
		for boid in self.boids:
			q.put(boid)
		for i in range(params.N_CPU):
			threading.Thread(target=self.parallel_update_boids, args=[q]).start()
		q.join()

	def display(self, screen):
		for boid in self.boids:
			boid.display(screen)
