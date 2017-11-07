"""Simulation parameters."""
import os
import pygame
import pygame.freetype
import pygame.gfxdraw
pygame.init()
pygame.freetype.init()

# General parameters
DEBUG = False
CAPTION = "PyBoids - Steering Behaviour Simulator"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(BASE_DIR, 'assets', 'img')
FONTS_DIR = os.path.join(BASE_DIR, 'assets', 'fonts')

# Screen and viewing parameters
SCREEN_HEIGHT, SCREEN_WIDTH = 720, 960
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
COL = SCREEN_WIDTH // 12
ROW = SCREEN_HEIGHT // 9
FPS = 30
MENU_BACKGROUND = pygame.Color("slate gray")
SIMULATION_BACKGROUND = pygame.Color("dark slate gray")
FONTS = {
    "hallo-sans-light": pygame.freetype.Font(
        os.path.join(FONTS_DIR, *["hallo-sans", "Hallo sans light.otf"])),
    "hallo-sans-bold": pygame.freetype.Font(
        os.path.join(FONTS_DIR, *["hallo-sans", "Hallo sans black.otf"])),
    "hallo-sans": pygame.freetype.Font(
        os.path.join(FONTS_DIR, *["hallo-sans", "Hallo sans.otf"])),
    "quicksand": pygame.freetype.Font(
        os.path.join(FONTS_DIR, *["quicksand", "Quicksand-Regular.otf"])),
    "quicksand-bold": pygame.freetype.Font(
        os.path.join(FONTS_DIR, *["quicksand", "Quicksand-Bold.otf"])),
    "quicksand-light": pygame.freetype.Font(
        os.path.join(FONTS_DIR, *["quicksand", "Quicksand-Light.otf"])),
}
FONT_SIZES = {
    "body": 17,
    "h1": 128,
    "h2": 48,
    "h3": 32,
    "h4": 28,
    "h5": 24,
}
FONT_COLOR = pygame.Color("white")
BODY_FONT = (FONTS["hallo-sans"], FONT_SIZES["body"], )
H1_FONT = (FONTS["quicksand-light"], FONT_SIZES["h1"])
H2_FONT = (FONTS["hallo-sans"], FONT_SIZES["h2"])
H3_FONT = (FONTS["quicksand"], FONT_SIZES["h3"])
H4_FONT = (FONTS["hallo-sans"], FONT_SIZES["h4"])
H5_FONT = (FONTS["hallo-sans"], FONT_SIZES["h5"])

# Boid staying inside the screen box
BOX_MARGIN = 200  # pixels
STEER_INSIDE = 6.  # speed impulse when out of margins
# Boid steering parameters
BOID_MAX_FORCE = 10.
BOID_MAX_SPEED = 7.
# Boid seek parameters
R_SEEK = 100
# Boid flee parameters
R_FLEE = 200
# Boid wandering parameters
WANDER_DIST = 4.5
WANDER_RADIUS = 3.0
WANDER_ANGLE = 1.0  # degrees
# Boid obstacle avoidance parameters
MAX_SEE_AHEAD = 50  # pixels
MAX_AVOID_FORCE = 10.
# Boid separation parameters
SEPARATION_DIST = 70
MAX_SEPARATION_FORCE = 8.
# Leader following parameters
LEADER_BEHIND_DIST = 10  # pixels
LEADER_AHEAD_DIST = 40
# Obstacles parameters
OBSTACLE_DEFAULT_RADIUS = 40
# Boid alignment parameters
ALIGN_RADIUS = 200
# Boid cohesion parameters
COHERE_RADIUS = 300
# multi-threading parameters
N_CPU = os.cpu_count()
