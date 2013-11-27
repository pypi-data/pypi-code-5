version = (0, 1, 2)

__version__ = '.'.join(map(str, version))

from .registry import register, autodiscover


__all__ = ['register', 'autodiscover']
