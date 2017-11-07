"""Generic asset management utilities for Pygame."""

import os
import pygame

from . import settings


class AssetLoader:
    """Base asset loader.

    Exposes a load(filename, *args, **kwargs) that shall be implemented in
    inherited assets.

    Class attributes
    ----------------
    asset_type : str
        The type of asset this loader supports. For debug purposes only.
    search_dirs : list of str
        The directories where this loader searches assets, relative
        to the base_dir.
    base_dir : str
        The base directory for asset search.
        Default is settings.BASE_DIR.
    """

    asset_type = 'asset'
    search_dirs = []
    base_dir = settings.BASE_DIR

    @classmethod
    def get_asset(cls, file_path):
        """Get the asset given a file path.

        Abstract class method, shall be implemented in subclasses using
        pygame's assets.

        Parameters
        ----------
        file_path : str
            Full path to the asset.
        """
        raise NotImplementedError

    @classmethod
    def get_file_path(cls, search_dir, filename):
        return os.path.join(cls.base_dir, search_dir, filename)

    @classmethod
    def load(cls, filename, *args, **kwargs):
        """Load an asset.

        Parameters
        ----------
        filename : str
            The asset's filename, e.g. 'asset.png'.
        """
        for search_dir in cls.search_dirs:
            file_path = cls.get_file_path(search_dir, filename)
            try:
                asset = cls.get_asset(file_path, *args, **kwargs)
                return asset
            except Exception as e:
                pass
        raise AssetLoader.AssetNotFoundError(cls, filename)

    class AssetNotFoundError(FileNotFoundError):
        """Error for assets not found."""

        def __init__(self, loader, filename, *args, **kwargs):
            message = (
                '{} "{}" does not exist (search paths: {}).'
                .format(loader.asset_type.lower(),
                        filename,
                        ', '.join(loader.search_dirs)))
            super().__init__(message, *args, **kwargs)


class SoundAssetLoader(AssetLoader):
    """Sound asset loader."""

    asset_type = 'sound'
    search_dirs = settings.SOUND_DIRS

    @classmethod
    def get_asset(cls, file_path, *, volume=1):
        sound = pygame.mixer.Sound(file_path)
        sound.set_volume(volume)
        return sound


def sound(filename, *, volume=1):
    """Load a sound.

    Searches for the sound in the SOUND_DIRS from the settings.py file.
    If sound is not found, raises a FileNotFound exception.

    Parameters
    ----------
    filename : str
        The sound's file name, e.g. 'click_sound.wav'.
    volume : float, optional
        The sound's volume, between 0 and 1.
        Default is 1.
    """
    return SoundAssetLoader.load(filename, volume=volume)


class ImageAssetLoader(AssetLoader):
    """Image asset loader."""

    asset_type = 'image'
    search_dirs = settings.IMG_DIRS

    @classmethod
    def get_asset(cls, file_path, *, alpha=None):
        image = pygame.image.load(file_path)
        if alpha is None:
            alpha = image.get_alpha() is not None
        if alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()
        return image


def image(filename, *, alpha=None):
    """Load an image.

    Searches for the image in the IMG_DIRS from the settings.py file.
    If image is not found, raises a FileNotFound exception.

    image('img.png') -> pygame.Surface

    Parameters
    ----------
    filename : str
        The image's file name, e.g. 'mysprite.png'.
    alpha : bool, optional
        Pass True or False to explicitly define if the image has alpha channel.
        Default is to derive it from the surface's get_alpha() value.
    """
    return ImageAssetLoader.load(filename)


def image_with_rect(filename, *, alpha=None):
    """Load an image and return it and its rect.

    Searches for the image in the IMG_DIRS from the settings.py file.
    If image is not found, raises a FileNotFound exception.

    image_with_rect('img.png') -> (pygame.Surface, pygame.Rect)

    Parameters
    ----------
    filename : str
        The image's file name, e.g. 'mysprite.png'.
    alpha : bool, optional
        Pass True or False to explicitly define if the image has alpha channel.
        Default is to derive it from the surface's get_alpha() value.
    """
    _image = image(filename, alpha=alpha)
    return _image, _image.get_rect()


class MusicAssetLoader(AssetLoader):
    """Music loader."""

    asset_type = 'music'
    search_dirs = settings.MUSIC_DIRS

    @classmethod
    def get_asset(cls, file_path, *, volume=1, **kwargs):
        if not pygame.mixer.get_init():
            pygame.mixer.pre_init(**kwargs)
            pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.set_volume(volume)


def music(filename, *, volume=1):
    """Load a music in the pygame mixer.

    Parameters
    ----------
    filename : str
        The music's file name, e.g. 'main_theme.wav'.
    volume : float, optional
        Set the playback volume to this value
    """
    return MusicAssetLoader.load(filename, volume=volume)


class FontAssetLoader(AssetLoader):
    """Font loader."""

    asset_type = 'font'
    search_dirs = settings.FONT_DIRS

    class Font(pygame.font.Font):
        """Subclass of pygame.font.Font.

        Redefines the render() function with sensible defaults.
        """

        def render(self, text, color=None, background=None, antialias=True):
            """Render the font.

            Redefinition of Pygame's font.Font.render function, only with
            sensible defaults and keyword arguments.

            Parameters
            ----------
            text : str
                The text to render.
            color : RGB tuple, optional
                Default is black (0, 0, 0).
            background : RGB tuple
                Default is None.
            antialias : bool, optional
                Default is True.
            """
            if color is None:
                color = (0, 0, 0)
            return super().render(text, antialias, color, background)

    @classmethod
    def get_asset(cls, file_path, *, size=20):
        return FontAssetLoader.Font(file_path, size)


def font(filename='', *, size=20):
    """Load a font.

    Return a pygame.font.Font object.

    Parameters
    ----------
    filename : str, optional
        The font's file name, e.g. 'myfont.otf'.
        Default is settings.DEFAULT_FONT
    size : int, optional
        The font size, in pixels.
        Default is 20.
    """
    if not filename:
        filename = settings.DEFAULT_FONT
    return FontAssetLoader.load(filename, size=size)


class FreetypeFontAssetLoader(AssetLoader):
    """Font loader using pygame.freetype."""

    asset_type = 'font'
    search_dirs = settings.FONT_DIRS

    @classmethod
    def get_asset(cls, file_path, *, size=20):
        if not pygame.freetype.was_init():
            pygame.freetype.init()
        return pygame.freetype.Font(file_path, size)


def freetype(filename='', *, size=20):
    """Load a font.

    Return a pygame.freetype.Font object.

    Parameters
    ----------
    filename : str, optional
        The font's file name, e.g. 'myfont.otf'.
        Default is settings.DEFAULT_FONT
    size : int, optional
        The font size, in pixels.
        Default is 20.
    """
    if not filename:
        filename = settings.DEFAULT_FONT
    return FreetypeFontAssetLoader.load(filename, size=size)
