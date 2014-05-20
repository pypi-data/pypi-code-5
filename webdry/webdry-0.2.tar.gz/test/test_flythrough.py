from selenium.webdriver import Firefox
from webdry import *


def setup():
    start_browser(Firefox())
    get("http://127.0.0.1:7000")

def teardown():
    stop_browser()


def test_query_and_access():
    find(name="username").send_keys(u"Some Body")
    find(xpath="//input[@type='submit']").click()
    back()

def test_looping():
    for e in find_all(xpath="//ul[@class='aside']/li/a"):
        assert e.is_displayed()

def test_query_on_loop_var():
    for div in find_all(xpath="//div"):
        assert div.find(xpath=".//h2").is_displayed()

def test_chained_queries():
    find(id="sidebar").find(xpath=".//h2/a").click()
    back()

def test_direct_arg():
    for e in find_all("ul.aside > li > a"):
        assert e.is_displayed()

