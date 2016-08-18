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

def normalize(vector):
    n = np.sqrt(np.dot(vector, vector))
    if n < 1e-13:
        return np.zeros(2)
    else:
        return np.array(vector) / n

def truncate(vector, max_norm):
    n = np.sqrt(np.dot(vector, vector))
    if n > max_norm:
        return normalize(vector) * max_norm
    else:
        return vector


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
        self._text = text
        self.font = font
        self.image, self.rect = mktext(text, font)
        self.rect.center = grid_to_px(pos)

    def get_text(self):
        return self._text
    def set_text(self, text):
        self._text = text
        self.image, rect = mktext(text, self.font)
        rect.topleft = self.rect.topleft
        self.rect = rect
    text = property(get_text, set_text)

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

class ToggleButton(Button):
    """
    ToggleButton(pos, text="", font=params.BODY_FONT, action=None, switch_alt="ON OFF", init_active=True)
    Derives from Button.
    A button sprite which displays a phrase and a switch associated to that phrase. The switch text can be provided as a string with two words separated by a space, eg "ON OFF" (default) or "1 0".
    """
    def __init__(self, pos, text="", font=params.BODY_FONT, action=None, switch_alt="ON OFF", init_active=True):
        on, off = switch_alt.split()
        self.switch_text = {True: on, False: off}
        self.on = init_active
        self.phrase = text
        super().__init__(pos, text=text + self.switch_text[init_active], font=font, action=action)
        self.rect.midleft = grid_to_px(pos)

    def toggle(self):
        self.on = not self.on
        self.text = self.phrase + self.switch_text[self.on]

    def update(self, motion_event, click_event):
        super().update(motion_event, click_event)
        if click_event and self.hover:
            self.toggle()
