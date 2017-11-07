"""App configuration."""
import os

DEBUG = False
CAPTION = "PyBoids - Steering Behaviour Simulator"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, *["static", "img"])
FONTS_DIR = os.path.join(BASE_DIR, *["static", "fonts"])
