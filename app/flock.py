# pyboids by mancaf
# Implementing the Boid Flocking Behaviour algorithm
# in Python and Pygame

import pygame
import numpy as np
from random import random
import threading, queue
from . import params, utils
from . import boid
from .obstacle import Obstacle

class Flock(pygame.sprite.Sprite):
	"""
	Flock() -> Flock
	Represents a set of boids that obey to certain behaviours.
	"""
	def __init__(self):
		super().__init__()
		self.normal_boids = pygame.sprite.Group()
		self.leader_boid = pygame.sprite.GroupSingle()
		self.boids = pygame.sprite.Group()
		self.obstacles = pygame.sprite.Group()
		self.behaviours = {
			"seek": False,
			"flee": False,
			"pursue": False,
			"escape": False,
			"wander": False
		}
		self.kinds = ["normal-boid", "leader-boid", "obstacle"]
		self.add_kind = "normal-boid"

	def switch_element(self):
		self.kinds = np.roll(self.kinds, -1)
		self.add_kind = self.kinds[0]

	def add_element(self, pos):
		""" Adds a normal boid, a leader boid or an obstacle at pos based on the current add_kind value. """
		vel = np.array([params.BOID_MAX_SPEED*(2*(random()<0.5) - 1)*(0.5+0.5*random()), params.BOID_MAX_SPEED*(2*(random()<0.5) - 1)*(0.5+0.5*random())], dtype=np.float64)
		if self.add_kind == "normal-boid":
			self.normal_boids.add(boid.Boid(pos=np.array(pos), vel=vel))
			self.boids.add(self.normal_boids)
		elif self.add_kind == "leader-boid":
			self.boids.remove(self.leader_boid)
			self.leader_boid.add(boid.LeaderBoid(pos=np.array(pos), vel=vel))
			self.boids.add(self.leader_boid)
		elif self.add_kind == "obstacle":
			self.obstacles.add(Obstacle(pos=pos))
		print("There are now {} boids and {} obstacles.".format(len(self.boids), len(self.obstacles)))

	def remain_in_screen(self):
		for boid in self.boids:
			if boid.pos[0] > params.SCREEN_WIDTH - params.BOX_MARGIN:
				boid.steer(np.array([-params.STEER_INSIDE, 0.]))
			if boid.pos[0] < params.BOX_MARGIN:
				boid.steer(np.array([params.STEER_INSIDE, 0.]))
			if boid.pos[1] < params.BOX_MARGIN:
				boid.steer(np.array([0., params.STEER_INSIDE]))
			if boid.pos[1] > params.SCREEN_HEIGHT - params.BOX_MARGIN:
				boid.steer(np.array([0., -params.STEER_INSIDE]))

	def seek(self, target_boid):
		""" Makes all normal boids seek to go to a target. """
		for boid in self.normal_boids:
			d = boid.dist(target_boid)
			boid.steer(utils.normalize(target_boid.pos - boid.pos) * params.BOID_MAX_SPEED * (d / params.R_SEEK if d < params.R_SEEK else 1) - boid.vel)

	def flee(self, target_boid):
		""" Makes all normal boids fly away from a target. """
		for boid in self.normal_boids:
			if boid.dist(target_boid) < params.R_FLEE:
				boid.steer(utils.normalize(boid.pos - target_boid.pos) * params.BOID_MAX_SPEED - boid.vel)

	def pursue(self, target_boid):
		""" Makes all normal boids pursue a target boid, anticipating its future position. """
		for boid in self.normal_boids:
			t = int(utils.norm(target_boid.pos - boid.pos) / params.BOID_MAX_SPEED)
			print(t)
			future_pos = target_boid.pos + t * target_boid.vel
			d = boid.dist_pos(future_pos)
			boid.steer(utils.normalize(future_pos - boid.pos) * params.BOID_MAX_SPEED * (d / params.R_SEEK if d < params.R_SEEK else 1) - boid.vel)

	def escape(self, target_boid):
		""" Makes all normal boids escape from a target boid, anticipating its future position. """
		for boid in self.normal_boids:
			t = int(utils.norm(target_boid.pos - boid.pos) / params.BOID_MAX_SPEED)
			future_pos = target_boid.pos + t*target_boid.vel
			if boid.dist_pos(future_pos) < params.R_FLEE:
				boid.steer(utils.normalize(boid.pos - future_pos) * params.BOID_MAX_SPEED - boid.vel)

	def wander(self):
		""" Makes all boids wander around randomly. """
		for boid in self.boids:
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
		# add element if required by a click
		if click_event and click_event.button == 3:
			self.add_element(click_event.pos)
		# apply steering effets
		target = self.leader_boid.sprite
		if self.behaviours["seek"]:
			self.seek(target)
		if self.behaviours["flee"]:
			self.flee(target)
		if self.behaviours["pursue"]:
			self.pursue(target)
		if self.behaviours["escape"]:
			self.escape(target)
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
		for obstacle in self.obstacles:
			obstacle.display(screen)
		for boid in self.boids:
			boid.display(screen)
