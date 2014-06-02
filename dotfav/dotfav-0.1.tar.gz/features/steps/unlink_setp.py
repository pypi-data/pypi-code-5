# -*- coding: utf-8 -*-

from hamcrest import *

from utils import *


@then('home directory does not changed')
def step_impl(context):
    actual = list(home.iterdir())
    assert_that(actual, is_(equal_to(context.home_files)))