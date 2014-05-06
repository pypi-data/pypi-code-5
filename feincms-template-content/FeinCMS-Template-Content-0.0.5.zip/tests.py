from django.conf import settings

settings.configure(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    INSTALLED_APPS=(
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'feincms',
        'feincms.module.page',
        'feincms.module.medialibrary',
        'feincms_template_content',
        'testapp',
    ),
    MEDIA_URL='/media-test-path/',
)


from django.test import TestCase
from django.template.context import Context
from django.template import RequestContext
from feincms_template_content.models import TemplateContent
from testapp.models import (
    CreatedTestContent,
    CreatedCustomContent,
    CreatedImageContent,
    CreatedMediaLibraryImageContent,
)
from mock import Mock
from django.contrib import admin
from django.core.exceptions import ValidationError
from feincms.module.page.models import Page
from feincms.module.medialibrary.models import MediaFile

from django.core.management import call_command
call_command('syncdb', interactive=False)


admin.autodiscover()

#TODO:
# test that **kwargs get passed around the methods properly


class TemplateContentTestCase(TestCase):
    def test_folder_name(self):
        tests = (
            ('class', 'class'),
            ('Class', 'class'),
            ('CLASS', 'class'),
            ('ClassName', 'class_name'),
            ('className', 'class_name'),
            ('CLASSName', 'class_name'),
            ('ClassNAME', 'class_name'),
            ('classNAME', 'class_name'),
            ('ClassNAMEExtra', 'class_name_extra'),
            ('classNAMEExtra', 'class_name_extra'),
            ('TestContent', 'test'),
            ('test_content', 'test'),
        )
        for name, check in tests:
            test_type = type(name, (TemplateContent,), {
                '__module__': TemplateContent.__module__,
                'Meta': type("Meta", (object,), {'abstract': True}),
            })
            result = test_type._generate_template_name()
            self.assertEqual(result, check)

    def test_template_field(self):
        template_field = None
        for field in CreatedTestContent._meta.fields:
            if field.name == 'template':
                template_field = field

        assert template_field is not None, 'template field not found'
        self.assertEqual(template_field.default,
                         CreatedTestContent.template_choices[0][0])

    def test_default_template_choices(self):
        self.assertEqual(TemplateContent.template_choices, None)

    def test_auto_template_choices(self):
        self.assertEqual(CreatedTestContent.template_choices,
                         (('content/test.html', 'Normal'),))

    def test_manual_template_choices(self):
        self.assertEqual(CreatedCustomContent.template_choices,
                         (('content/custom/1.html', 't1'),
                          ('content/custom/2.html', 't2')))

    def test_get_context_object_name(self):
        c = CreatedTestContent()
        self.assertEqual(c.get_context_object_name(), 'content')
        mock_name = Mock()
        c.context_object_name = mock_name
        self.assertIs(c.get_context_object_name(), mock_name)

    def test_get_context_data(self):
        c = CreatedTestContent()
        self.assertEqual(c.get_context_data(), {'content': c})
        mock_name = Mock()
        c.context_object_name = mock_name
        self.assertEqual(c.get_context_data(), {mock_name: c})

    def test_get_context(self):
        c = CreatedTestContent()
        data = Mock(spec_set=[])
        c.get_context_data = Mock(spec_set=[], return_value=data)
        ctx = c.get_context()
        self.assertEqual(type(ctx), Context)
        self.assertEqual(len(ctx.dicts), 2)
        self.assertEqual(ctx.dicts[1], data)

    def test_get_context_request(self):
        c = CreatedTestContent()
        request = Mock(spec_set=[])
        ctx = c.get_context(request=request)
        self.assertEqual(type(ctx), RequestContext)

    def test_render(self):
        c = CreatedTestContent()
        self.assertEqual(c.render().strip(), 'test')

    def test_admin_form_hidden_template_field(self):
        inline_class = CreatedTestContent.feincms_item_editor_inline
        inline = inline_class(Page, admin.site)
        self.assertIn('template', inline.exclude)

    def test_admin_form_template_field(self):
        inline_class = CreatedCustomContent.feincms_item_editor_inline
        inline = inline_class(Page, admin.site)
        self.assertNotIn('template', inline.exclude)


class TestImageContent(TestCase):
    def test_image_str_repr(self):
        c = CreatedImageContent()
        c.image = "test.png"
        self.assertEqual(unicode(c), u"test.png")

    def test_image_template(self):
        c = CreatedImageContent()
        c.image = "test.png"
        self.assertEqual(c.render().strip(),
                         '<img style="display:block" src="/media-test-path/test.png">')


class TestMediaLibraryImageContent(TestCase):
    def setUp(self):
        self.page = Page.objects.create(title="Page")
        self.content = CreatedMediaLibraryImageContent()
        self.content.parent = self.page

    def test_image(self):
        self.content.image = MediaFile.objects.create(file="test.png", type="image")
        self.content.clean()
        self.content.save()

    def test_non_image(self):
        self.content.image = MediaFile.objects.create(file="test.pdf", type="pdf")
        with self.assertRaises(ValidationError):
            self.content.clean()

    def test_str_rep(self):
        self.content.image = MediaFile.objects.create(file="test.png", type="image")
        self.assertEqual(unicode(self.content), u"test.png")

    def test_image_template(self):
        self.content.image = MediaFile.objects.create(file="test.png", type="image")
        self.assertEqual(unicode(self.content), u"test.png")
        self.assertEqual(self.content.render().strip(),
                         '<img style="display:block" src="/media-test-path/test.png">')

    def test_image_template_float_left(self):
        self.content.image = MediaFile.objects.create(file="test.png", type="image")
        self.content.template = "content/image/float_left.html"
        self.assertEqual(unicode(self.content), u"test.png")
        self.assertEqual(self.content.render().strip(),
                         '<img style="display:block; float:left" src="/media-test-path/test.png">')

    def test_image_template_float_right(self):
        self.content.image = MediaFile.objects.create(file="test.png", type="image")
        self.content.template = "content/image/float_right.html"
        self.assertEqual(unicode(self.content), u"test.png")
        self.assertEqual(self.content.render().strip(),
                         '<img style="display:block; float:right" src="/media-test-path/test.png">')
