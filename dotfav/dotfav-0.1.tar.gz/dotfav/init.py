# -*- coding: utf-8 -*-

from dotfav.path import Path
import dotfav.config


class Iinitialize(object):
    def __init__(self, default_dotfiles, config):
        self._default_dotfiles = Path(default_dotfiles)
        self._config = config

    def run(self):
        self._config.dotfiles = self._default_dotfiles.resolve()


def main(default_dotfiles, home=None):
    home = Path('~' if home is None else home)
    config_path = home / '.dotfav' / 'config'
    config = dotfav.config.create_json_config(config_path)

    command = Iinitialize(default_dotfiles, config)
    command.run()
