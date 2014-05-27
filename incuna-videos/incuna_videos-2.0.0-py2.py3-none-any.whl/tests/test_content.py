from django.test import TestCase
from incuna_test_utils.compat import Python2CountEqualMixin

from . import factories
from .models import DummyPage
from ..content import VideoContent
from videos.module.chapters.tests.factories import ChapterFactory
from videos.module.speakers.tests.factories import SpeakerFactory


class VideoContentTest(Python2CountEqualMixin, TestCase):
    model = DummyPage.content_type_for(VideoContent)

    def test_get_context_data(self):
        content = self.model(region='main')
        video = factories.VideoFactory.create()
        source = factories.SourceFactory.create(video=video)
        chapter = ChapterFactory.create(video=video)
        speaker = SpeakerFactory.create()
        video.speakers.add(speaker)
        content.video = video
        request = 'dummy'
        context = content.get_context_data(request=request)

        expected = {
            'type': 'block',  # Default set in 'models.py' when registered
            'video': content.video,
            'request': request,
            'sources': [source],

            # Extras included by standard extensions
            'chapters': [chapter],
            'speakers': [speaker],
        }
        self.assertCountEqual(context, expected)

    def test_get_template_names(self):
        content = self.model(region='main')
        expected = [
            'videos/content/main_block.html',  # Region && type
            'videos/content/main.html',  # Region default
            'videos/content/block.html',  # Just type
            'videos/content/default.html',  # Default/Last resort
        ]
        self.assertCountEqual(content.get_template_names(), expected)

    def test_render(self):
        content = self.model(region='main')
        source = factories.SourceFactory.create()
        content.video = source.video
        with self.assertNumQueries(3):
            # Three queries:
            # - Get Speakers
            # - Get Sources
            # - Get Chapters
            result = content.render()
        self.assertIn(source.get_absolute_url(), result)
