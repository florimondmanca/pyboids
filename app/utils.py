# pyboids by mancaf
# Implementing the Boid Flocking Behaviour algorithm
# in Python and Pygame

import os
import pygame
import numpy as np
from . import params


def load_image(*path):
    """
    Loads the image using the full path to the image.
    Manages alpha conversion (e.g. png's).
    """
    image = pygame.image.load(os.path.join(params.IMG_DIR, *list(path)))
    if image.get_alpha() is None:
        image = image.convert()
    else:
        image = image.convert_alpha()
    return image, image.get_rect()

def mktext(text, font):
    """ Renders a text of given 'text' and font (a tuple (pygame.freetype.Font, size)) """
    return font[0].render(text, fgcolor=params.FONT_COLOR, size=font[1])

def px_to_grid(px_pos):
    """ Converts pixel position to grid position """
    return px_pos[0] / params.COL, px_pos[1] / params.ROW

def grid_to_px(grid_pos):
    """ Converts grid position to pixel position """
    return grid_pos[0] * params.COL, grid_pos[1] * params.ROW


class Message(pygame.sprite.Sprite):
    """
    Message(pos, text="", font=params.BODY_FONT) -> Message
    A simple text sprite.
    pos is (col, row) with col a float from 0.0 to 12.0 and row a float from 0.0 to 9.0
    """
    image = None  # Surface
    rect = None  # Rect

    def __init__(self, pos, text="", font=params.BODY_FONT):
        super().__init__()
        self.image, self.rect = mktext(text, font)
        self.rect.center = grid_to_px(pos)

    def update(self, motion_event, click_event):
        pass

    def display(self, screen):
        screen.blit(self.image, self.rect)


class Button(Message):
    """
    Button(pos, text="", font=params.BODY_FONT, action=None) -> Rect
    Derives from Message.
    A text button sprite that underlines itself under hover. It can be associated with an action that is triggered by click.
    """
    hover = False  # bool
    action = lambda *args, **kwargs: None  # function

    def __init__(self, pos, text="", font=params.BODY_FONT, action=None):
        super().__init__(pos, text, font)
        self.hover = False  # True when mouse hovers the button
        if action is not None:
            self.action = action

    def update(self, motion_event, click_event):
        if motion_event:
            if self.hover and not self.rect.collidepoint(motion_event.pos):
                self.hover = False
            elif not self.hover and self.rect.collidepoint(motion_event.pos):
                self.hover = True
        if click_event and self.hover:
            self.action()

    def display(self, screen):
        super().display(screen)
        if self.hover:
            pygame.draw.line(screen,
                params.FONT_COLOR,
                (self.rect.bottomleft[0], self.rect.bottomleft[1] + 5),
                (self.rect.bottomright[0], self.rect.bottomright[1] + 5)
            )


class Vector2:
    def __init__(self, x=0, y=0):
        self._data = np.array([x, y])

    def get_x(self):
        return self._data[0]
    def set_x(self, x):
        self._data[0] = x
    x = property(get_x, set_x)

    def get_y(self):
        return self._data[1]
    def set_y(self, x):
        self._data[1] = y
    y = property(get_y, set_y)

    @property
    def data(self):
        return tuple(self._data)

    def copy(self):
        return Vector2(self.x, self.y)

    def __add__(self, other):
        self._data += other._data

    def __sub__(self, other):
        self._data -= other._data

    def __mul__(self, other):
        self._data *= other  # other is scalar

    def __truediv__(self, other):
        self._data /= other  # other is scalar
