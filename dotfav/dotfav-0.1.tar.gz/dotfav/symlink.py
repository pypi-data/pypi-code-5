# -*- coding: utf-8 -*-

import os
import sys
import json
from itertools import product
from itertools import chain

from dotfav.path import Path
import dotfav.config


class InstallCommandGenerator(object):
    def __init__(self, targets):
        self._targets = targets

    def __iter__(self):
        for command in self._symlink_commands():
            yield command

    def _symlink_commands(self):
        for src, dst in self._targets:
            yield self._create_symlink_command(src, dst)

    def _create_symlink_command(self, src, dst):
        return SymlinkCommand(src, dst)


class CommandError(Exception):
    def __init__(self, msg, real_exception=None):
        self.real_exception = real_exception
        
    def __str__(self):
        return str(self.real_exception)


class SymlinkCommand(object):
    def __init__(self, src, dst):
        self._src = src
        self._dst = dst

    def execute(self):
        msg = 'Create symbolic link from `{}\' to `{}\''
        print(msg.format(self._src, self._dst), file=sys.stderr)
        self.__do_symlink()

    def __do_symlink(self):
        try:
            if self._dst.is_symlink():
                prompt = '`{}\' already exists. replace `{}\'? [yn]: '.format(
                    self._dst, self._dst)
                ans = input(prompt)
                if ans.lower().startswith('y'):
                    self._dst.unlink()
                else:
                    return
            self._dst.symlink_to(self._src)
        except OSError as e:
            print('{}: {}'.format(self._dst, e.strerror), file=sys.stderr)


class HomeFileCollection(object):
    def __init__(self, src, dst, files):
        self._src = src
        self._dst = dst
        self._files = files

    def __iter__(self):
        files = self._files
        directories = (self._src, self._dst)
        return ((src / basename, dst / basename)
                for ((src, dst), basename) in product((directories, ), files))


class HomeFileSymlinkingCommands(object):
    def __init__(self, src, dst, files):
        self._src = src
        self._dst = dst
        self._files = files

    def __iter__(self):
        targets = HomeFileCollection(src=self._src, dst=self._dst, files=self._files)
        return iter(InstallCommandGenerator(targets))


class MappedFileCollection(object):
    def __init__(self, src, dst, mapped_files):
        self.__src = src
        self.__dst = dst
        self.__mapped_files = mapped_files

    def __iter__(self):
        for f, t in self.__mapped_files:
            yield self.__src / f, self.__dst / t


class MappedFileSymlinkingCommands(object):
    def __init__(self, src, dst, maps, platform):
        self._src = src
        self._dst = dst
        self._maps = maps
        self._platform = platform

    def __iter__(self):
        mapped_files = self.__reverse_inner_tuple(
            self.__filter_platform(self._maps, self._platform))
        targets = MappedFileCollection(self._src, self._dst, mapped_files)
        return iter(InstallCommandGenerator(targets))

    @staticmethod
    def __reverse_inner_tuple(iterable):
        return (tuple(reversed(t)) for t in iterable)

    @staticmethod
    def __filter_platform(maps, platform):
        return chain(*(c['target'].items() for c in maps if platform in c['os']))


class Symlink(object):
    def __init__(self, dotfiles, home, platform):
        self._dotfiles = Path(dotfiles)
        self._home = Path(home)
        self._platform = platform

        self._map_file = self._dotfiles / 'dotfav.config'
        self._src = self._dotfiles / 'home'
        self._dst = self._home

    def run(self):
        commands = []

        if not self._src.is_dir():
            print('`{}\': {}'.format(src, files.value.strerror), file=sys.stderr)
            sys.exit(1)

        children = map(lambda p: p.name, self._src.iterdir())
        commands.extend(self._home_file_symlinking_commands(children))

        if self._map_file.is_file():
            commands.extend(self._mapped_file_symlinking_commands())

        for command in commands:
            command.execute()

    def _home_file_symlinking_commands(self, files):
        return HomeFileSymlinkingCommands(self._src, self._dst, files)

    def _mapped_file_symlinking_commands(self):
        with self._map_file.open() as f:
            maps = json.load(f)
            return MappedFileSymlinkingCommands(self._src,
                                                self._dst,
                                                maps,
                                                self._platform)


def main(home=None, platform=None):
    try:
        home = '~' if home is None else home
        config_path = Path(home) / '.dotfav' / 'config'
        config = dotfav.config.fromJsonFile(config_path)
        dotfiles = config.dotfiles

        platform = sys.platform if platform is None else platform

        command = Symlink(dotfiles, home, platform)
        command.run()
    except dotfav.config.ConfigFileNotFound as e:
        print('Not initialized yet.', file=sys.stderr)
        print('Run `dotfav init <path>\' first.', file=sys.stderr)


