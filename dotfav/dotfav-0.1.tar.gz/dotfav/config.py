# -*- coding: utf-8 -*-

import json
import abc

from dotfav.path import Path


class ConfigFileNotFound(Exception):
    def __init__(self, e):
        self.exception = e


class Config(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def dotfiles(self):
        '''dotfiles path. dotfav.path.Path object'''
        pass

    @dotfiles.setter
    @abc.abstractmethod
    def dotfiles(self, value):
        pass

    @property
    def doftiles_home(self):
        return dotfiles / 'home'


class JsonConfig(Config):
    def __init__(self, obj, filepath):
        self._obj = obj
        self._filepath = filepath

    @property
    def dotfiles(self):
        return Path(self._obj['dotfiles'])

    @dotfiles.setter
    def dotfiles(self, value):
        self._obj['dotfiles'] = str(value)
        self._update_file()

    def _update_file(self):
        if not self._filepath.exists():
            if not self._filepath.parent.exists():
                self._filepath.parent.mkdir(parents=True)
            self._filepath.touch()
        with self._filepath.open(encoding='utf-8', mode='w') as f:
            json.dump(self._obj, f)


def create_json_config(filepath):
    return JsonConfig({}, filepath)


def fromJsonFile(filepath):
    try:
        with filepath.open(encoding='utf-8') as f:
            obj = json.load(f)
            return JsonConfig(obj, filepath)
    except FileNotFoundError as e:
        raise ConfigFileNotFound(e)