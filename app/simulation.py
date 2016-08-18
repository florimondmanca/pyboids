# pyboids by mancaf
# Implementing the Boid Flocking Behaviour algorithm
# in Python and Pygame

import pygame
from .flock import Flock
from .boid import Boid
from . import params, utils

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

	def init_run(self):
		self.to_update = pygame.sprite.Group(
			self.flock,
		)
		for k, behaviour in enumerate(self.flock.behaviours):
			def do_action(self, behaviour):
				self.toggle_behaviour(behaviour)
			do_action = actionize(do_action, self, behaviour)
			self.to_update.add(utils.ToggleButton(
				pos=(1*(k+1), 0.2),
				text="{} : ".format(behaviour.title()),
				action=do_action,
				init_active=self.flock.behaviours[behaviour])
			)
		self.to_display = pygame.sprite.Group(
			self.to_update,
		)

	def run(self):
		key_to_function = {
			pygame.K_ESCAPE: lambda self, event: setattr(self, "running", False),
		}
		self.init_run()
		while self.running:
			motion_event, click_event = None, None
			self.screen.fill(params.SIMULATION_BACKGROUND)
			self.clock.tick(params.FPS)
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
			pygame.display.flip()

	def quit(self):
		self.running = False
