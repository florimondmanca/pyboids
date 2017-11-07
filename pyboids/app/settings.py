"""App configuration."""
import os

DEBUG = False
CAPTION = "PyBoids - Steering Behaviour Simulator"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_DIR = os.path.join(BASE_DIR, 'static')

IMG_DIRS = [
    os.path.join(STATIC_DIR, 'img'),
]

FONT_DIRS = [
    os.path.join(STATIC_DIR, 'fonts'),
]
DEFAULT_FONT = 'hallo-sans.otf'

SOUND_DIRS = []

MUSIC_DIRS = []
