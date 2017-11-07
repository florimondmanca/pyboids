"""App configuration."""
import os

DEBUG = False
CAPTION = "PyBoids - Steering Behaviour Simulator"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Assets configuration
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
IMG_DIRS = [
    os.path.join(ASSETS_DIR, 'img'),
]
FONT_DIRS = [
    os.path.join(ASSETS_DIR, 'fonts'),
]
DEFAULT_FONT = 'hallo-sans.otf'
SOUND_DIRS = []
MUSIC_DIRS = []
