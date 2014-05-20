# -*- coding: utf-8 -*-
# (c) 2014 Mind Candy Ltd. All Rights Reserved.  
# Licensed under the MIT License; you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at http://opensource.org/licenses/MIT.

from fattoush import step, Driver
from nose import tools
from time import sleep

@step(u'I open "([^"]*)" in my web browser')
def i_open_url_in_my_web_browser(step, url):
    wd = Driver.instance(step)
    wd.get(url)

@step(u'I expect the url to start with "([^"]*)"')
def i_expect_the_url_to_become_url(step, url):
    wd = Driver.instance(step)
    tools.assert_equal(wd.current_url[:len(url)], url)


@step(u'I type "([^"]*)" into the search box')
def i_type_search_term_into_the_search_box(step, search_term):
    wd = Driver.instance(step)
    search_box = wd.find_element_by_id('gbqfq')
    search_box.send_keys(search_term)

@step(u'I submit the search')
def i_submit_the_search(step):
    wd = Driver.instance(step)
    search_box = wd.find_element_by_id('gbqfq')
    search_box.send_keys('\n')

@step(u'I expect the top result to contain the string "([^"]*)"')
def i_expect_the_top_result_to_contain_the_string_search_term(step,
                                                              search_term):
    wd = Driver.instance(step)
    assert isinstance(wd, Driver)
    for i in range(5):
        try:
            results = wd.find_elements_by_class_name('rc')
            top_result = results[0]
            break
        except IndexError:
            sleep(1)
            continue
    else:
        raise
    tools.assert_true(search_term in top_result.text,
                      u'could not find {0} in {1}'.format(
                          search_term, top_result.text))
