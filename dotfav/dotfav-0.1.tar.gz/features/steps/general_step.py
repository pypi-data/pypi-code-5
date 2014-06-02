# -*- coding: utf-8 -*-

from hamcrest import *

from utils import *


@given('there are dotfiles home directory in dotfiles')
def step_impl(context):
    cleanup_temp_directory()
    create_test_temp_directories()
    assert_that(dotfiles_home.is_dir(), 'dotfiles_home must be directory')


@given('dotfiles home directory contains no files')
def step_impl(context):
    pass


@given('home directory contains some files')
def step_impl(context):
    context.home_files = list(home.iterdir())

@given('dotfav is initialized')
def step_impl(context):
    run_dotfav('init', None, str(dotfiles))

@when('we run dotfav symlink')
def step_impl(context):
    run_dotfav(command='symlink')


@when('we run dotfav symlink at platform "{platform}"')
def step_impl(context, platform):
    run_dotfav(command='symlink', platform=platform)


@when('we run dotfav unlink')
def step_impl(context):
    run_dotfav(command='unlink')
