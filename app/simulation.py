# pyboids by mancaf
# Implementing the Boid Flocking Behaviour algorithm
# in Python and Pygame

import pygame
from .flock import Flock
from . import params, utils
from time import time

def actionize(func, self, behaviour):
	def actionized():
		return func(self, behaviour)
	return actionized


class Simulation:
	def __init__(self, screen):
		self.running = True
		self.screen = screen
		self.clock = pygame.time.Clock()
		self.flock = Flock()
		self.to_update = pygame.sprite.Group()
		self.to_display = pygame.sprite.Group()

	def toggle_behaviour(self, behaviour):
		self.flock.behaviours[behaviour] = not self.flock.behaviours[behaviour]

	def update(self, motion_event, click_event):
		self.to_update.update(motion_event, click_event)

	def display(self):
		for sprite in self.to_display:
			sprite.display(self.screen)
		if params.DEBUG:
			pygame.draw.polygon(self.screen, pygame.Color("turquoise"), [
					(params.BOX_MARGIN, params.BOX_MARGIN),
					(params.SCREEN_WIDTH - params.BOX_MARGIN, params.BOX_MARGIN),
					(params.SCREEN_WIDTH - params.BOX_MARGIN, params.SCREEN_HEIGHT - params.BOX_MARGIN),
					(params.BOX_MARGIN, params.SCREEN_HEIGHT - params.BOX_MARGIN),
				], 1)

	def init_run(self):
		# add 40 boids to the flock
		for x in range(1, 11):
			for y in range(3, 7):
				self.flock.add_element(utils.grid_to_px((x, y)))

		self.to_update = pygame.sprite.Group(
			self.flock,
			utils.ToggleButton(
				pos=(0.2, 8),
				text="Adding : ",
				labels=self.flock.kinds,
				init_label=self.flock.add_kind,
				action=lambda: self.flock.switch_element())
		)
		# add behaviour toggle buttons
		for k, behaviour in enumerate(self.flock.behaviours):
			# v decorate to prevent a bug
			def do_action(self, behaviour):
				self.toggle_behaviour(behaviour)
			do_action = actionize(do_action, self, behaviour)
			# ^
			self.to_update.add(utils.ToggleButton(
				pos=(0.2, 0.3*(1+k)),
				text="{} : ".format(behaviour.title()),
				labels="off on".split(),
				init_label="off on".split()[self.flock.behaviours[behaviour]],
				action=do_action)
			)
		self.to_display = pygame.sprite.Group(
			self.to_update,
		)

	def run(self):
		key_to_function = {
			pygame.K_ESCAPE: lambda self, event: setattr(self, "running", False),
		}
		self.init_run()
		kt = 0
		avg_t = 0
		while self.running:
			self.clock.tick(params.FPS)
			t = time()
			motion_event, click_event = None, None
			self.screen.fill(params.SIMULATION_BACKGROUND)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
					return "PYGAME_QUIT"
				elif event.type == pygame.KEYDOWN and event.key in key_to_function:
					key_to_function[event.key](self, event)
				elif event.type == pygame.MOUSEBUTTONDOWN:
					click_event = event
				elif event.type == pygame.MOUSEMOTION:
					motion_event = event
			self.update(motion_event, click_event)
			self.display()
			t1 = time()
			pygame.display.flip()
			print("Flip: {}".format(1000*(time()-t1)))
			avg_t += time() - t
			kt += 1
			if kt == 5:
				avg_t /= 5
				print("FPS : {}\n".format(1/avg_t))
				avg_t = kt = 0

	def quit(self):
		self.running = False
