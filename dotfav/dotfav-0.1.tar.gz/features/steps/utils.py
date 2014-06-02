# -*- coding: utf-8 -*_

import sys
import shutil
import json
from subprocess import *
from pathlib import Path

from hamcrest import *


test_temp = Path(__file__).parent / 'temp'
home = test_temp / 'home'
dotfiles = test_temp / 'dotfiles'
dotfiles_home = dotfiles / 'home'
dotfiles_config = dotfiles / 'dotfav.config'


def cleanup_temp_directory():
    if test_temp.is_dir():
        shutil.rmtree(str(test_temp))
    elif test_temp.is_file():
        test_temp.unlink()


def create_test_temp_directories():
    test_temp.mkdir()
    home.mkdir()
    dotfiles.mkdir()
    dotfiles_home.mkdir()


def create_config_file(config):
    config = json.loads(config)
    with dotfiles_config.open(mode='w') as f:
        json.dump(config, f)


def run_dotfav(command, platform=None, *args):
    cmd = [sys.executable, '-m', 'dotfav', command]
    cmd.extend(['--home', str(home)])
    if platform is not None:
        cmd.extend(['--platform', platform])
    cmd.extend(args)

    with Popen(cmd, stdout=PIPE, stderr=PIPE) as process:
        try:
            output, error = process.communicate()
        except:
            process.kill()
            process.wait()
            raise
        retcode = process.poll()
        assert_that(
            retcode, equal_to(0),
            'Process Failed:\nOutput: {}\nError: {}'.format(
                output.decode('utf-8'), error.decode('utf-8')))
