# pyboids by mancaf
# Implementing the Boid Flocking Behaviour algorithm
# in Python and Pygame

import os
import pygame
import numpy as np
import math
from . import params


def load_image_only(*path):
    """
    Loads the image using the full path to the image.
    Manages alpha conversion (e.g. png's).
    """
    image = pygame.image.load(os.path.join(params.IMG_DIR, *list(path)))
    if image.get_alpha() is None:
        image = image.convert()
    else:
        image = image.convert_alpha()
    return image


def load_image(*path):
    """
    Loads the image using the full path to the image and also
    returns the image's rect.
    """
    image = load_image_only(*path)
    return image, image.get_rect()


def mktext(text, font):
    """ Renders a text of given 'text' and font
    (a tuple (pygame.freetype.Font, size)) """
    return font[0].render(text, fgcolor=params.FONT_COLOR, size=font[1])


def px_to_grid(px_pos):
    """ Converts pixel position to grid position """
    return px_pos[0] / params.COL, px_pos[1] / params.ROW


def grid_to_px(grid_pos):
    """ Converts grid position to pixel position """
    return grid_pos[0] * params.COL, grid_pos[1] * params.ROW


def norm(vector):  # must be as fast as possible
    return math.sqrt(vector[0]**2 + vector[1]**2)


def norm2(vector):  # square norm
    return vector[0] * vector[0] + vector[1] * vector[1]


def normalize(vector, pre_n=None):
    n = pre_n if pre_n is not None else norm(vector)
    if n < 1e-13:
        return np.zeros(2)
    else:
        return np.array(vector) / n


def truncate(vector, max_norm):
    n = norm(vector)
    if n > max_norm:
        return normalize(vector, pre_n=n) * max_norm
    else:
        return vector


class Message(pygame.sprite.Sprite):
    """
    Message(pos, text="", font=params.BODY_FONT) -> Message
    A simple text sprite.
    pos is (col, row) with col a float from 0.0 to 12.0 and row a
    float from 0.0 to 9.0
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

    def display(self, screen):
        screen.blit(self.image, self.rect)


class TempMessage(Message):
    """
    TempMessage(pos, text="", font=params.H4_FONT, duration=100) -> TempMessage
    A message that only displays for a certain amount of time
    (duration given in number of frames - default is 150 frames).
    """
    def __init__(self, pos, text="", font=params.H4_FONT, duration=100):
        super().__init__(pos, text, font)
        self.duration = duration
        self.counter = 0

    def update(self, motion_event, click_event):
        self.counter += 1
        if self.counter == self.duration:
            self.kill()


class FPSMessage(Message):
    """
    FPSMessage(pos, text="", font=params.BODY_FONT, n_frames=40) -> FPSMessage
    A message that displays the FPS. Updates every 'n_frames' frames.
    """
    def __init__(self, pos, text="", font=params.BODY_FONT, n_frames=40):
        Message.__init__(self, pos, text, font)
        self.n_frames = n_frames
        self.counter = 0
        self.time = 0

    def update(self, time):
        self.counter += 1
        self.time += time
        if self.counter == self.n_frames:
            self.time /= self.n_frames
            self.text = "FPS: {}".format(round(1 / self.time, 1))
            self.counter = 0
            self.time = 0


class Button(Message):
    """
    Button(pos, text="", font=params.BODY_FONT, action=None) -> Rect
    Derives from Message.
    A text button sprite that underlines itself under hover.
    It can be associated with an action that is triggered by click.
    """
    def __init__(self, pos, text="", font=params.BODY_FONT, action=None):
        super().__init__(pos, text, font)
        self.hover = False  # True when mouse hovers the button
        self.action = action

    def update(self, motion_event, click_event):
        if motion_event:
            if self.hover and not self.rect.collidepoint(motion_event.pos):
                self.hover = False
            elif not self.hover and self.rect.collidepoint(motion_event.pos):
                self.hover = True
        if self.action and click_event and self.hover:
            self.action()

    def display(self, screen):
        super().display(screen)
        if self.action and self.hover:
            pygame.draw.line(
                screen, params.FONT_COLOR,
                (self.rect.bottomleft[0], self.rect.bottomleft[1] + 5),
                (self.rect.bottomright[0], self.rect.bottomright[1] + 5)
            )


class ToggleButton(Button):
    """
    ToggleButton(pos, text="", font=params.BODY_FONT,
    action=None, labels=[""], init_label="") -> ToggleButton
    Derives from Button.
    A button sprite which has a series of labels that gets updated on click.
    Each click changes the label in a circular manner.
    """
    def __init__(self, pos, text="", font=params.BODY_FONT,
                 action=None, labels="", init_label=""):
        self.phrase = text
        self.labels = labels  # list of strings
        self.label = init_label.replace("-", " ").title()
        super().__init__(pos, text=text + self.label, font=font, action=action)
        if self.labels:
            self.labels = np.roll(labels, -labels.index(init_label))
        self.rect.midleft = grid_to_px(pos)

    def toggle(self):
        self.labels = np.roll(self.labels, -1)
        self.label = self.labels[0].replace("-", " ").title()
        self.text = self.phrase + self.label

    def update(self, motion_event, click_event):
        super().update(motion_event, click_event)
        if click_event and self.hover and len(self.labels) > 0:
            self.toggle()
