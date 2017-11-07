"""Utility functions and classes."""
import os
import pygame
import numpy as np
import math
from . import params


def load_image(path, base=None):
    """Load the image using the full path to the image.

    Manages alpha conversion (e.g. png's).
    """
    if base is None:
        base = params.IMG_DIR
    file_path = os.path.join(base, path)
    image = pygame.image.load(file_path)
    if image.get_alpha() is None:
        image = image.convert()
    else:
        image = image.convert_alpha()
    return image


def load_image_and_rect(*path):
    """Load the image using the full path to the image.

    Also returns the image's rect.
    """
    image = load_image(*path)
    return image, image.get_rect()


def mktext(text, font):
    """Render a text.

    Parameters
    ----------
    text : str
    font : tuple (pygame.font.Font, size)
    """
    return font[0].render(text, fgcolor=params.FONT_COLOR, size=font[1])


def px_to_grid(px_pos):
    """Convert pixel position to grid position."""
    return px_pos[0] / params.COL, px_pos[1] / params.ROW


def grid_to_px(grid_pos):
    """Convert grid position to pixel position."""
    return grid_pos[0] * params.COL, grid_pos[1] * params.ROW


def norm(vector):
    """Compute the norm of a vector."""
    return math.sqrt(vector[0]**2 + vector[1]**2)


def norm2(vector):
    """Compute the square norm of a vector."""
    return vector[0] * vector[0] + vector[1] * vector[1]


def normalize(vector, pre_computed=None):
    """Return the normalized version of a vector.

    Parameters
    ----------
    vector : np.array
    pre_computed : float, optional
        The pre-computed norm for optimization. If not given, the norm
        will be computed.
    """
    n = pre_computed if pre_computed is not None else norm(vector)
    if n < 1e-13:
        return np.zeros(2)
    else:
        return np.array(vector) / n


def truncate(vector, max_length):
    """Truncate the length of a vector to a maximum value."""
    n = norm(vector)
    if n > max_length:
        return normalize(vector, pre_computed=n) * max_length
    else:
        return vector


class Message(pygame.sprite.Sprite):
    """A simple text message sprite.

    Message(pos, text="", font=params.BODY_FONT) -> Message

    Parameters
    ----------
    pos : (float, float)
    text : str
    font : (pygame.font.Font, size)
        Default is BODY_FONT.
    """

    image = None
    rect = None

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
    """A message that disappears after some time.

    TempMessage(pos, text="", font=params.H4_FONT, duration=100) -> TempMessage

    Parameters
    ----------
    pos : (float, float)
    text : str
    font : (pygame.font.Font, size), optional
        Default is H4_FONT.
    duration : int, optional
        Number of frames. Default is 100.

    See also
    --------
    Message
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
    """A message that displays the FPS.

    Parameters
    ----------
        Default is BODY_FONT.
    refresh_every : int, optional
        Number of frames between FPS refresh. Default is 40.

    See also
    --------
    Message
    """

    def __init__(self, pos, text="", font=params.BODY_FONT, refresh_every=40):
        Message.__init__(self, pos, text, font)
        self.refresh_every = refresh_every
        self.counter = 0
        self.time = 0

    def update(self, time):
        self.counter += 1
        self.time += time
        if self.counter == self.refresh_every:
            self.time /= self.refresh_every
            self.text = "FPS: {}".format(round(1 / self.time, 1))
            self.counter = 0
            self.time = 0


class Button(Message):
    """A text button sprite that underlines itself under hover.

    It can be associated with an action callback triggered by click.

    Parameters
    ----------
    action : function(), optional
        Action callback, must take no arguments. Will be triggered when
        the button is clicked.

    See also
    --------
    Message
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
    """A button sprite which has a series of labels that gets updated on click.

    Each click changes the label in a circular manner.

    Parameters
    ----------
    labels : list of str
    init_label : str

    See also
    --------
    Button
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
