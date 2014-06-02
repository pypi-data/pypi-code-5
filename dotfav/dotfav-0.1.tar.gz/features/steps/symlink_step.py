# -*- coding: utf-8 -*-

from hamcrest import *

from utils import *



@given('dotfiles home directory contains a file named "{filename}"')
def step_impl(context, filename):
    (dotfiles_home / filename).touch()


@given('dotfiles home directory contains a directory named "{dirname}"')
def step_impl(context, dirname):
    (dotfiles_home / dirname).mkdir()


@given('dotfiles contains config file')
def step_impl(context):
    create_config_file(context.text)


@then('no files are symlinked')
def step_impl(context):
    symlink_path = [p.resolve() for p in home.iterdir() if p.is_symlink()]
    dotfiles = dotfiles_home.rglob('*')
    assert_that(symlink_path,
                any_of(is_(empty()), is_not(contains(is_in(dotfiles)))))


@then('"{name}" in home symlinks to "{target}" in dotfiles home')
def step_impl(context, name, target):
    path = home / name
    target_path = dotfiles_home / target
    assert_that(path.is_symlink(), 'path must be symlink file')
    assert_that(path.resolve(), equal_to(target_path))


@then('"{filename}" in home is file')
def step_impl(context, filename):
    path = home / filename
    assert_that(path.is_file(), 'path must be file')


@then('"{dirname}" in home is directory')
def step_impl(context, dirname):
    path = home / dirname
    assert_that(path.is_dir(), 'path must be directory')
