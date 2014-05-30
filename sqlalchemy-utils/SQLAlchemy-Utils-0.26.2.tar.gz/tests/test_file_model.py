import magic
import sqlalchemy as sa
from sqlalchemy_utils import generic_relationship

from siilo.storages.filesystem import FileSystemStorage

from tests import TestCase


storage = FileSystemStorage(
    base_directory='tests/',
)


class TestFileModel(TestCase):
    def create_models(self):
        class File(self.Base):
            __tablename__ = 'file'

            id = sa.Column(sa.Integer, primary_key=True)

            name = sa.Column(sa.String, index=True)

            size = sa.Column(sa.Integer, index=True)

            type = sa.Column(sa.String)

            mime_type = sa.Column(sa.String)

            object_id = sa.Column(sa.Integer)

            object_type = sa.Column(sa.String)

            object = generic_relationship(object_type, object_id)

            def __init__(self, name):
                self.name = name
                contents = storage.open(self.name).read()
                self.type = magic.from_buffer(contents)
                self.mime_type = magic.from_buffer(contents)
                self.size = storage.size(self.name)

            @property
            def url(self):
                return storage.url(self.name)

        class Article(self.Base):
            __tablename__ = 'article'
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.Unicode(255))

            picture_id = sa.Column(sa.Integer, sa.ForeignKey(File.id))

            # picture = sa.orm.relationship()

            attachments = sa.orm.relationship(File)

        self.Article = Article
        self.File = File

    def test_something(self):
        file = self.File('test.txt')
        assert 0
        # article = self.Article(name=u'Some article')
        # self.session.add(article)
