import unittest

from ioc.extra.tornado.router import Router, TornadoMultiDict
from tornado.httpserver import HTTPRequest
import wtforms

def view():
    return "hello"

class RouterTest(unittest.TestCase):
    def setUp(self):

        self.router = Router()

    def test_add_and_match_routes(self):
        self.router.add("homepage", "/", view)

        self.assertEquals(('homepage', {}, view), self.router.match("/"))

        self.router.add("blog_post", "/blog/<string:slug>", view, methods=['GET'])

        self.assertEquals(('blog_post', {'slug': 'hello'}, view), self.router.match("/blog/hello"))

    def test_add_and_generate_routes(self):

        self.router.add("homepage", "/", view)
        self.router.add("blog_post", "/blog/<string:slug>", view)

        self.assertEquals("/", self.router.generate("homepage"))
        self.assertEquals("/blog/hello", self.router.generate("blog_post", slug="hello"))

        self.assertEquals("http://localhost/blog/hello", self.router.generate("blog_post", slug="hello", force_external=True))


    # def test_multidict_one_level(self):
    #     request = HTTPRequest('GET', '/')
    #     request.arguments = {u'media.name': ['pekinon.png'], u'media.content_type': ['image/png'], u'name': ['asd'], u'message': [''], u'email': ['sad'], u'media.path': ['/var/uploads/0047585288']}
    #
    #     mdict = TornadoMultiDict(request)
    #
    #     self.assertEquals(mdict.data, {
    #         'media': {
    #             'name': ['pekinon.png'],
    #             'content_type': ['image/png'],
    #             'path': ['/var/uploads/0047585288']
    #         },
    #         'name': ['asd'],
    #         'message': [''],
    #         'email': ['sad']
    #     })
    #
    # def test_wtform(self):
    #
    #     class DriveElement(object):
    #         def __init__(self, name=None, email=None, message=None, media=None):
    #             self.name = name
    #             self.email = email
    #             self.message = message
    #             self.media = media
    #
    #     class UploadForm(wtforms.Form):
    #         name = wtforms.TextField('name', validators=[wtforms.validators.DataRequired()])
    #         email = wtforms.TextField('email', validators=[wtforms.validators.Email(), wtforms.validators.DataRequired()])
    #         message = wtforms.TextAreaField('message', validators=[wtforms.validators.DataRequired()])
    #         media = wtforms.FileField(u'Video')
    #
    #     request = HTTPRequest('GET', '/')
    #     request.arguments = {u'media.name': ['pekinon.png'], u'media.content_type': ['image/png'], u'name': ['asd'], u'message': [''], u'email': ['sad'], u'media.path': ['/var/uploads/0047585288']}
    #
    #
    #     element = DriveElement()
    #     form = UploadForm(TornadoMultiDict(request), element)


