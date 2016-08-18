# pyboids by mancaf
# Implementing the Boid Flocking Behaviour algorithm
# in Python and Pygame

import pygame
from . import params
from .flock import Flock
from .boid import Boid
from . import utils

key_to_function = {
	# insert lambda hooks here
}
button_to_function = {
	# insert lambda hooks here
}

class Simulation:
	running = True
	screen = pygame.display.set_mode(params.SCREEN_SIZE)
	pygame.display.set_caption(params.CAPTION)
	clock = pygame.time.Clock()
	flock = Flock()
	to_update = pygame.sprite.Group()
	to_display = pygame.sprite.Group()

	def update(self, motion_event, click_event):
		self.to_update.update(motion_event, click_event)

	def display(self):
		for sprite in self.to_display:
			sprite.display(self.screen)

	def main(self):
		self.menu()

	def run(self):
		print("Running")
		pass

	def menu(self):
		self.to_update.add(
			utils.Button(pos=(6, 5), text="Start", font=params.H3_FONT, action=lambda: self.run()),
			utils.Button(pos=(6, 8), text="Quit", font=params.H3_FONT, action=lambda: self.quit())
		)
		self.to_display.add(
			self.to_update,
			utils.Message(pos=(6, 2), text=params.TITLE, font=params.H1_FONT),
			utils.Message(pos=(6, 2.75), text=params.SUBTITLE),
		)
		while self.running:
			motion_event, click_event = None, None
			self.screen.fill(params.BACKGROUND)
			self.clock.tick(params.FPS)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
				elif event.type == pygame.KEYDOWN and event.key in key_to_function:
					key_to_function[event.key](self, event)
				elif event.type == pygame.MOUSEBUTTONDOWN:
					click_event = event
				elif event.type == pygame.MOUSEMOTION:
					motion_event = event
			self.update(motion_event, click_event)
			self.display()
			pygame.display.flip()
		pygame.quit()

	def quit(self):
		self.running = False