#-*- coding: utf-8 -*-

from mechanize import Browser, ParseResponse, HTMLForm, urlopen
from BeautifulSoup import BeautifulSoup


class WebBrowser(Browser):
    def __init__(self, factory=None, history=None, request_class=None):

        self.current_page = None
        Browser.__init__(self, factory, history, request_class)

        self.set_handle_equiv(True)
        self.set_handle_gzip(True)
        self.set_handle_redirect(True)
        self.set_handle_referer(True)
        self.set_handle_robots(False)
        self.addheaders = [('User-agent', 'Mozilla/5.0')]


    def urlopen(self, url, data=None,timeout=10):
        if (isinstance(url, str) or isinstance(url, unicode))\
                and not '://' in url:
            url = 'http://' + url
 
        self.response = self.open(url, data, timeout)
        self.current_page = WebDocument(self.response)

    def follow_link(self, link=None, **kwds):
        self.response = Browser.follow_link(self, link, **kwds)
        self.current_page = WebDocument(self.response)

    def submit_form(self, form, timeout=10):
        if isinstance(form, str) or isinstance(form, unicode):
            request = self.current_page.forms[form].click()
        else:
            request = form.click()
        self.urlopen(request, timeout=timeout)
        

class WebDocument(object):
    """ A document comming from the web.
    """

    def __init__(self, response):
        self._web_doc = response.get_data()       
        self.soup = BeautifulSoup(self._web_doc)

        try:
            self.title = self.soup.html.head.title

            body_tag = self.soup.html.body
            self.body = body_tag
        except AttributeError:
            pass

        self._contents = ParseResponse(response, backwards_compat=False)
        
        forms = [[i.name, i] for i in self._contents if isinstance(i, HTMLForm)]
        for f in enumerate(forms):
            if f[1][0] is None: 
                f[1][0] = 'unnamed-%s' %f[0]
        self.forms = dict(forms)

        
    def __iter__(self):
        for thing in self._contents:
            yield thing
        

    def findAll(self, element_type, attrs):
        return self.soup.findAll(element_type, **attrs)

        # element_key = kwargs.keys()[0]
        # element_value = kwargs[element_key]
        # element_key = element_key.strip('_')
        # for element in parent:
        #     try:
        #         if element[element_key] == element_value:
        #             return element
        #     except TypeError:
        #         pass
        #     except KeyError:
        #         pass
            
    def find(self, element_type, attrs):
        return self.soup.find(element_type, **attrs)
