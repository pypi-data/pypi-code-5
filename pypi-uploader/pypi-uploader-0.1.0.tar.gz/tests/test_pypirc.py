"""Tests for :mod:`pypiuploader.pypirc`."""

try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import io
import tempfile
import types

import pytest

from pypiuploader import exceptions
from pypiuploader import pypirc
from . import utils


def test_read_config():
    """Test :class:`pypiuploader.pypirc.read_config`."""

    tmpfile = utils._make_tmp_pypirc_file()

    config = pypirc.read_config(tmpfile.name)

    assert isinstance(config, configparser.ConfigParser)
    sections = sorted(config.sections())
    assert sections == ['distutils', 'external', 'internal', 'pypi']


class TestRCParser(object):

    """Tests for :class:`pypiuploader.pypirc.RCParser`."""

    def test_from_file(self):
        tmpfile = utils._make_tmp_pypirc_file()

        parser = pypirc.RCParser.from_file(tmpfile.name)

        assert isinstance(parser.config, configparser.ConfigParser)
        sections = sorted(parser.config.sections())
        assert sections == ['distutils', 'external', 'internal', 'pypi']

    def test_from_file_when_pypirc_does_not_exist(self):
        tmpfile = tempfile.NamedTemporaryFile()
        tmpfile.close()
        with pytest.raises(exceptions.ConfigFileError) as exc:
            pypirc.RCParser.from_file(tmpfile.name)
        assert tmpfile.name in str(exc.value)

    def test_read_index_servers(self):
        parser = self._make_parser()
        servers = parser._read_index_servers()
        assert isinstance(servers, types.GeneratorType)
        assert list(servers) == ['internal', 'external']

    def test_read_index_servers_when_no_distutils_section(self):
        parser = self._make_parser(b'')
        servers = parser._read_index_servers()
        assert isinstance(servers, types.GeneratorType)
        assert list(servers) == []

    def test_read_index_servers_when_no_index_servers(self):
        parser = self._make_parser(b'[distutils]\n')
        with pytest.raises(configparser.NoOptionError):
            list(parser._read_index_servers())

    def test_read_server_auth(self):
        parser = self._make_parser()
        auth = parser._read_server_auth('internal')
        assert auth == ('bar', 'foo')

    def test_read_server_auth_without_password(self):
        parser = self._make_parser()
        auth = parser._read_server_auth('external')
        assert auth == ('baz', None)

    def test_find_repo_config_not_found(self):
        parser = self._make_parser()
        servers = ['internal', 'external']
        repo_config = parser._find_repo_config(servers, 'foo')
        assert repo_config is None

    def test_find_repo_config_by_server_name(self):
        parser = self._make_parser()
        servers = ['internal', 'external']

        repo_config = parser._find_repo_config(servers, 'internal')

        expected_config = {
            'repository': 'http://127.0.0.1:8000',
            'username': 'bar',
            'password': 'foo',
        }
        assert repo_config == expected_config

    def test_find_repo_config_by_repository(self):
        parser = self._make_parser()
        servers = ['internal', 'external']

        repo_config = parser._find_repo_config(servers, 'https://foo.bar.com/')

        expected_config = {
            'repository': 'https://foo.bar.com/',
            'username': 'baz',
            'password': None,
        }
        assert repo_config == expected_config

    def test_get_repository_config(self):
        parser = self._make_parser()

        repo_config = parser.get_repository_config('internal')

        expected_config = {
            'repository': 'http://127.0.0.1:8000',
            'username': 'bar',
            'password': 'foo',
        }
        assert repo_config == expected_config

    def test_get_repository_config_when_no_distutils_section(self):
        parser = self._make_parser(b'')

        repo_config = parser.get_repository_config('internal')

        assert repo_config is None

    def test_get_repository_config_when_no_repository_section(self):
        parser = self._make_parser(
            b'[distutils]\n'
            b'index-servers = internal'
        )
        with pytest.raises(configparser.NoSectionError):
            parser.get_repository_config('internal')

    def _make_parser(self, content=None):
        if content is None:
            content = utils.PYPIRC
        config_buffer = io.StringIO(content.decode())
        config = configparser.ConfigParser()
        config.readfp(config_buffer)
        parser = pypirc.RCParser(config)
        return parser
