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
			"pursue": False,
			"escape": False,
			"wander": True,
			"avoid collision": True,
			"follow leader": False,
		}
		self.kinds = ["normal-boid", "leader-boid", "obstacle"]
		self.add_kind = "normal-boid"

	def switch_element(self):
		self.kinds = np.roll(self.kinds, -1)
		self.add_kind = self.kinds[0]

	def add_element(self, pos):
		""" Adds a normal boid, a leader boid or an obstacle at pos based on the current add_kind value. """
		angle = np.pi * (2*np.random.rand() - 1)
		vel = params.BOID_MAX_SPEED * np.array([np.cos(angle), np.sin(angle)])
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

	def seek_single(self, target_pos, boid):
		d = boid.dist_pos(target_pos)
		boid.steer(utils.normalize(target_pos - boid.pos) * params.BOID_MAX_SPEED * (d / params.R_SEEK if d < params.R_SEEK else 1) - boid.vel)

	def seek(self, target_boid):
		""" Makes all normal boids seek to go to a target. """
		for boid in self.normal_boids:
			self.seek_single(target_boid, boid)

	def flee_single(self, target_pos, boid):
		if boid.dist_pos(target_pos) < params.R_FLEE:
				boid.steer(utils.normalize(boid.pos - target_pos) * params.BOID_MAX_SPEED - boid.vel)

	def flee(self, target_boid):
		""" Makes all normal boids fly away from a target. """
		for boid in self.normal_boids:
			self.flee_single(target_boid, boid)

	def pursue_single(self, target_pos, target_vel, boid):
		t = int(utils.norm(target_pos - boid.pos) / params.BOID_MAX_SPEED)
		future_pos = target_pos + t*target_vel
		self.seek_single(future_pos, boid)

	def pursue(self, target_boid):
		""" Makes all normal boids pursue a target boid, anticipating its future position. """
		for boid in self.normal_boids:
			self.pursue_single(target_boid.pos, target_boid.vel, boid)

	def escape_single(self, target_pos, target_vel, boid):
		t = int(utils.norm(target_pos - boid.pos) / params.BOID_MAX_SPEED)
		future_pos = target_pos + t*target_vel
		self.flee_single(future_pos, boid)

	def escape(self, target_boid):
		""" Makes all normal boids escape from a target boid, anticipating its future position. """
		for boid in self.normal_boids:
			self.escape_single(target_boid.pos, target_boid.vel, boid)

	def wander(self):
		""" Makes all boids wander around randomly. """
		for boid in self.boids:
			nvel = utils.normalize(boid.vel)
			# calculate circle center
			circle_center = nvel * params.WANDER_DIST
			# calculate displacement force
			c, s = np.cos(boid.wandering_angle), np.sin(boid.wandering_angle)
			displacement = np.dot(np.array([[c, -s], [s, c]]), nvel * params.WANDER_RADIUS)
			boid.steer(circle_center + displacement)
			boid.wandering_angle += params.WANDER_ANGLE * (2*np.random.rand() - 1)

	def find_most_threatening_obstacle(self, boid, aheads):
		most_threatening = None
		for obstacle in self.obstacles:
			if any(utils.norm(obstacle.pos - ahead) <= obstacle.radius for ahead in aheads) and (most_threatening is None or boid.dist(obstacle) < boid.dist(most_threatening)):
				most_threatening = obstacle
		return most_threatening

	def avoid_collision(self):
		""" Avoids collisions between boids and obstacles. """
		for boid in self.boids:
			ahead = boid.pos + boid.vel / params.BOID_MAX_SPEED * params.MAX_SEE_AHEAD
			ahead2 = boid.pos + boid.vel / params.BOID_MAX_SPEED / 2 * params.MAX_SEE_AHEAD
			most_threatening = self.find_most_threatening_obstacle(boid, [ahead, ahead2, boid.pos])
			if most_threatening is not None:
				boid.steer(utils.normalize(ahead - most_threatening.pos) * params.MAX_AVOID_FORCE)

	def separate_single(self, boid):
		n_neighbors = 0
		force = np.zeros(2)
		for other_boid in self.normal_boids:
			if other_boid != boid and boid.dist(other_boid) <= params.SEPARATION_RADIUS:
				force -= other_boid.pos - boid.pos
				n_neighbors += 1
		if n_neighbors:
			force /= n_neighbors
		boid.steer(utils.normalize(force) * params.MAX_SEPARATION_FORCE)

	def follow_leader(self, leader):
		""" Makes all normal boids follow a leader, staying at a certain distance from it, moving away when they're in the leader's path, and avoiding cluttering of boids behind the leader. """
		nvel = utils.normalize(leader.vel) * params.LEADER_BEHIND_DIST
		behind = leader.pos - nvel
		ahead = leader.pos + nvel
		for boid in self.normal_boids:
			self.seek_single(behind, boid)
			self.separate_single(boid)
			self.escape_single(ahead, leader.vel, boid)

	def parallel_update_boids(self, q):
		while not q.empty():
			boid = q.get()
			boid.update()
			q.task_done()

	def parallel_update_boids_func(self, q):
		while not q.empty():
			func, args = q.get()
			func(*args)
			q.task_done()

	def update(self, motion_event, click_event):
		# add element if required by a click
		if click_event and click_event.button == 3:
			self.add_element(click_event.pos)
		# apply steering effets using multithreading
		func_q = queue.Queue()
		if self.leader_boid:
			target = self.leader_boid.sprite
			if self.behaviours["pursue"]:
				func_q.put((self.pursue, [target]))
			if self.behaviours["escape"]:
				func_q.put((self.escape, [target]))
			if self.behaviours["follow leader"]:
				func_q.put((self.follow_leader, [target]))
		if self.behaviours["wander"]:
			func_q.put((self.wander, []))
		if self.behaviours["avoid collision"]:
			func_q.put((self.avoid_collision, []))
		func_q.put((self.remain_in_screen, []))
		for i in range(params.N_CPU):
			threading.Thread(target=self.parallel_update_boids_func, args=[func_q]).start()
		func_q.join()
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
