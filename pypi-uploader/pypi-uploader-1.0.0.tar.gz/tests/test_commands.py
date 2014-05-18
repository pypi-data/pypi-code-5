"""Tests for :mod:`pypiuploader.commands`."""

import argparse
import io
import sys
if sys.version_info[0] == 2:
    StdOutIO = io.BytesIO
else:
    StdOutIO = io.StringIO

try:
    from unittest import mock
except ImportError:
    import mock
import pytest

from pypiuploader import commands
from pypiuploader import download
from pypiuploader import exceptions
from pypiuploader import pypirc
from pypiuploader import upload


class TestParseArgs(object):

    """Tests for :func:`pypiuploader.commands.parse_args`."""

    def test_no_arguments(self):
        argv = []
        with pytest.raises(SystemExit):
            commands.parse_args(argv)

    def test_no_index_url(self):
        argv = ['files', 'mock']
        with pytest.raises(SystemExit):
            commands.parse_args(argv)

    def test_index_url(self):
        argv = ['files', 'mock', '--index-url', 'internal']
        options = commands.parse_args(argv)
        assert options.index == 'internal'

    def test_index_url_shortcut(self):
        argv = ['files', 'mock', '-i', 'internal']
        options = commands.parse_args(argv)
        assert options.index == 'internal'

    def test_files(self):
        argv = ['files', 'requests==1.0.1', 'mock', '-i', 'internal']
        options = commands.parse_args(argv)
        assert options.command == 'files'
        assert options.files == ['requests==1.0.1', 'mock']

    def test_files_no_use_wheel(self):
        argv = [
            'files', 'requests==1.0.1', 'mock',
            '-i', 'internal',
            '--no-use-wheel',
        ]
        with pytest.raises(SystemExit):
            commands.parse_args(argv)

    def test_packages(self):
        argv = ['packages', 'requests==1.0.1', 'mock', '-i', 'internal']
        options = commands.parse_args(argv)
        assert options.command == 'packages'
        assert options.packages == ['requests==1.0.1', 'mock']
        assert not options.no_use_wheel

    def test_packages_download_dir(self):
        argv = [
            'packages', 'mock', '-i', 'internal',
            '--download-dir', '~/.packages'
        ]
        options = commands.parse_args(argv)
        assert options.download_dir == '~/.packages'
        assert options.command == 'packages'
        assert options.packages == ['mock']

    def test_packages_download_dir_shortcut(self):
        argv = ['packages', 'mock', '-i', 'internal', '-d', '~/.packages']
        options = commands.parse_args(argv)
        assert options.download_dir == '~/.packages'
        assert options.command == 'packages'
        assert options.packages == ['mock']

    def test_packages_no_use_wheel(self):
        argv = ['packages', 'mock', '-i', 'internal', '--no-use-wheel']
        options = commands.parse_args(argv)
        assert options.no_use_wheel
        assert options.command == 'packages'

    def test_requirements(self):
        argv = ['requirements', 'requirements.txt', '-i', 'internal']
        options = commands.parse_args(argv)
        assert options.command == 'requirements'
        assert options.requirements_file == 'requirements.txt'
        assert not options.no_use_wheel

    def test_requirements_download_dir(self):
        argv = [
            'requirements', 'requirements.txt', '-i', 'internal',
            '--download-dir', '~/.packages'
        ]
        options = commands.parse_args(argv)
        assert options.download_dir == '~/.packages'
        assert options.command == 'requirements'
        assert options.requirements_file == 'requirements.txt'

    def test_requirements_download_dir_shortcut(self):
        argv = [
            'requirements', 'requirements.txt', '-i', 'internal',
            '-d', '~/.packages'
        ]
        options = commands.parse_args(argv)
        assert options.download_dir == '~/.packages'
        assert options.command == 'requirements'
        assert options.requirements_file == 'requirements.txt'

    def test_requirements_no_use_wheel(self):
        argv = [
            'requirements', 'requirements.txt',
            '-i', 'internal',
            '--no-use-wheel',
        ]
        options = commands.parse_args(argv)
        assert options.no_use_wheel
        assert options.command == 'requirements'

    def test_username(self):
        argv = ['files', 'mock', '-i', 'internal', '--username', 'foo']
        options = commands.parse_args(argv)
        assert options.username == 'foo'
        assert options.command == 'files'
        assert options.files == ['mock']

    def test_username_shortcut(self):
        argv = ['files', 'mock', '-i', 'internal', '-u', 'foo']
        options = commands.parse_args(argv)
        assert options.username == 'foo'
        assert options.command == 'files'
        assert options.files == ['mock']

    def test_password(self):
        argv = ['files', 'mock', '-i', 'internal', '--password', 'bar']
        options = commands.parse_args(argv)
        assert options.password == 'bar'
        assert options.command == 'files'
        assert options.files == ['mock']

    def test_password_shortcut(self):
        argv = ['files', 'mock', '-i', 'internal', '-p', 'bar']
        options = commands.parse_args(argv)
        assert options.password == 'bar'
        assert options.command == 'files'
        assert options.files == ['mock']


class TestCommand(object):

    """Tests for :func:`pypiuploader.commands.Command`."""

    def test_init(self):
        options = argparse.Namespace(
            command='requirements',
            index='internal',
            requirements_file='requirements.txt')
        stdout = StdOutIO()

        command = commands.Command(options, stdout=stdout)

        assert command.options == options
        assert command.stdout == stdout

    def test_init_default_stdout(self):
        options = argparse.Namespace()

        command = commands.Command(options)

        assert command.options == options
        assert command.stdout == sys.stdout

    @mock.patch.object(pypirc.RCParser, 'from_file')
    def test_make_uploader(self, from_file_mock):
        from_file_mock.side_effect = exceptions.ConfigFileError
        options = argparse.Namespace(
            index='http://localhost:8000',
            username='foo',
            password='bar')
        command = commands.Command(options)

        uploader = command._make_uploader()

        assert uploader.host == 'http://localhost:8000'
        assert uploader.username == 'foo'
        assert uploader.password == 'bar'

    @mock.patch.object(download.PackageDownloader, 'download', autospec=True)
    def test_download_packages(self, download_mock):
        download_return_value = [
            'packages/coverage-3.7.1.tar.gz',
            'packages/mock-1.0.1.tar.gz',
        ]
        download_mock.return_value = download_return_value
        options = argparse.Namespace(
            download_dir='~/packages',
            packages=['coverage==3.7.1', 'mock'],
            no_use_wheel=False)
        command = commands.Command(options)

        filenames = command._download()

        assert filenames == download_return_value
        assert len(download_mock.call_args_list) == 1
        downloader = download_mock.call_args[0][0]
        assert downloader.download_path == '~/packages'
        expected_call = mock.call(
            downloader,
            requirements=['coverage==3.7.1', 'mock'],
            requirements_file=None,
            no_use_wheel=False)
        assert download_mock.call_args == expected_call

    @mock.patch.object(download.PackageDownloader, 'download', autospec=True)
    def test_download_requirements_file(self, download_mock):
        download_return_value = [
            'packages/coverage-3.7.1.tar.gz',
            'packages/mock-1.0.1.tar.gz',
        ]
        download_mock.return_value = download_return_value
        options = argparse.Namespace(
            download_dir='~/packages',
            requirements_file='requirements.txt',
            no_use_wheel=False)
        command = commands.Command(options)

        filenames = command._download()

        assert filenames == download_return_value
        assert len(download_mock.call_args_list) == 1
        downloader = download_mock.call_args[0][0]
        assert downloader.download_path == '~/packages'
        expected_call = mock.call(
            downloader,
            requirements=None,
            requirements_file='requirements.txt',
            no_use_wheel=False)
        assert download_mock.call_args == expected_call

    @mock.patch.object(download.PackageDownloader, 'download', autospec=True)
    def test_download_requirements_file_no_use_wheel(self, download_mock):
        options = argparse.Namespace(
            requirements_file='requirements.txt',
            download_dir=None,
            no_use_wheel=True)
        command = commands.Command(options)

        command._download()

        assert len(download_mock.call_args_list) == 1
        downloader = download_mock.call_args[0][0]
        expected_call = mock.call(
            downloader,
            requirements=None,
            requirements_file='requirements.txt',
            no_use_wheel=True)
        assert download_mock.call_args == expected_call

    def test_print(self):
        options = argparse.Namespace()
        stdout = StdOutIO()
        command = commands.Command(options, stdout=stdout)

        command._print('Foo bar\n')
        command._print('baz\n')

        stdout.seek(0)
        assert stdout.read() == 'Foo bar\nbaz\n'

    def test_upload_file(self):
        options = argparse.Namespace()
        stdout = StdOutIO()
        command = commands.Command(options, stdout=stdout)
        uploader = mock.create_autospec(upload.PackageUploader)

        command._upload_file(uploader, 'mock-1.0.1.tar.gz')

        stdout.seek(0)
        assert uploader.upload.call_args == mock.call('mock-1.0.1.tar.gz')
        assert stdout.read() == 'Uploading mock-1.0.1.tar.gz... success.\n'

    def test_upload_file_conflict(self):
        options = argparse.Namespace()
        stdout = StdOutIO()
        command = commands.Command(options, stdout=stdout)
        uploader = mock.create_autospec(upload.PackageUploader)
        uploader.upload.side_effect = exceptions.PackageConflictError('foo')

        command._upload_file(uploader, 'mock-1.0.1.tar.gz')

        stdout.seek(0)
        assert uploader.upload.call_args == mock.call('mock-1.0.1.tar.gz')
        assert stdout.read() == (
            'Uploading mock-1.0.1.tar.gz... already uploaded.\n'
        )

    def test_upload_files(self):
        options = argparse.Namespace()
        stdout = StdOutIO()
        command = commands.Command(options, stdout=stdout)
        uploader = mock.create_autospec(
            upload.PackageUploader,
            host='http://localhost:8000')
        upload_results = [None, exceptions.PackageConflictError('foo')]

        def upload_side_effect(*args):
            result = upload_results.pop()
            if isinstance(result, Exception):
                raise result
            return result
        uploader.upload.side_effect = upload_side_effect

        command._upload_files(
            uploader,
            ['packages/mock-1.0.1.tar.gz', 'packages/coverage-3.7.1.tar.gz'])

        stdout.seek(0)
        assert uploader.upload.call_args_list == [
            mock.call('packages/mock-1.0.1.tar.gz'),
            mock.call('packages/coverage-3.7.1.tar.gz'),
        ]
        assert stdout.read() == (
            'Uploading packages to http://localhost:8000\n'
            'Uploading packages/mock-1.0.1.tar.gz... already uploaded.\n'
            'Uploading packages/coverage-3.7.1.tar.gz... success.\n'
        )

    @mock.patch.object(commands.Command, '_download', autospec=True)
    def test_get_filenames_for_packages_command(self, download_mock):
        download_return_value = [
            'packages/coverage-3.7.1.tar.gz',
            'packages/mock-1.0.1.tar.gz',
        ]
        download_mock.return_value = download_return_value
        options = argparse.Namespace(command='packages')
        command = commands.Command(options)

        filenames = command._get_filenames()

        assert filenames == download_return_value

    @mock.patch.object(commands.Command, '_download', autospec=True)
    def test_get_filenames_for_requirements_command(self, download_mock):
        download_return_value = [
            'packages/coverage-3.7.1.tar.gz',
            'packages/mock-1.0.1.tar.gz',
        ]
        download_mock.return_value = download_return_value
        options = argparse.Namespace(command='requirements')
        command = commands.Command(options)

        filenames = command._get_filenames()

        assert filenames == download_return_value

    @mock.patch.object(commands.Command, '_download', autospec=True)
    def test_get_filenames_for_files_command(self, download_mock):
        files = [
            'packages/coverage-3.7.1.tar.gz',
            'packages/mock-1.0.1.tar.gz',
        ]
        options = argparse.Namespace(command='files', files=files)
        command = commands.Command(options)

        filenames = command._get_filenames()

        assert not download_mock.called
        assert filenames == files

    @mock.patch.object(commands.Command, '_upload_files', autospec=True)
    @mock.patch.object(commands.Command, '_get_filenames', autospec=True)
    @mock.patch.object(commands.Command, '_make_uploader', autospec=True)
    def test_run(
            self, make_uploader_mock, get_filenames_mock, upload_files_mock):
        uploader = mock.create_autospec(upload.PackageUploader)
        filenames = [
            'packages/coverage-3.7.1.tar.gz',
            'packages/mock-1.0.1.tar.gz',
        ]
        make_uploader_mock.return_value = uploader
        get_filenames_mock.return_value = filenames
        options = argparse.Namespace()
        command = commands.Command(options)

        command.run()

        expected_call = mock.call(command, uploader, filenames)
        assert make_uploader_mock.called
        assert get_filenames_mock.called
        assert upload_files_mock.call_args == expected_call


class TestMain(object):

    """Tests for :func:`pypiuploader.commands.main`."""

    @mock.patch.object(upload.PackageUploader, 'upload', autospec=True)
    def test_files(self, upload_mock):
        upload_results = [None, exceptions.PackageConflictError('foo')]

        def upload_side_effect(*args):
            result = upload_results.pop()
            if isinstance(result, Exception):
                raise result
            return result

        upload_mock.side_effect = upload_side_effect
        argv = [
            'files',
            'packages/coverage-3.7.1.tar.gz',
            'packages/mock-1.0.1.tar.gz',
            '-i', 'http://localhost:8000',
            '-u', 'foo',
            '-p', 'bar',
        ]
        stdout = StdOutIO()

        commands.main(argv=argv, stdout=stdout)

        stdout.seek(0)
        content = stdout.read()
        assert content == (
            'Uploading packages to http://localhost:8000\n'
            'Uploading packages/coverage-3.7.1.tar.gz... already uploaded.\n'
            'Uploading packages/mock-1.0.1.tar.gz... success.\n'
        )
        assert len(upload_mock.call_args_list) == 2
        uploader = upload_mock.call_args[0][0]
        assert uploader.host == 'http://localhost:8000'
        assert uploader.username == 'foo'
        assert uploader.password == 'bar'
        expected_calls = [
            mock.call(uploader, 'packages/coverage-3.7.1.tar.gz'),
            mock.call(uploader, 'packages/mock-1.0.1.tar.gz'),
        ]
        assert upload_mock.call_args_list == expected_calls

    @mock.patch.object(download.PackageDownloader, 'download', autospec=True)
    @mock.patch.object(upload.PackageUploader, 'upload', autospec=True)
    def test_packages(self, upload_mock, download_mock):
        upload_results = [None, exceptions.PackageConflictError('foo')]

        def upload_side_effect(*args):
            result = upload_results.pop()
            if isinstance(result, Exception):
                raise result
            return result

        upload_mock.side_effect = upload_side_effect
        download_mock.return_value = [
            'packages/coverage-3.7.1.tar.gz',
            'packages/mock-1.0.1.tar.gz'
        ]
        argv = [
            'packages',
            'coverage==3.7.1',
            'mock',
            '-i', 'http://localhost:8000',
            '-u', 'foo',
            '-p', 'bar',
            '-d', 'packages',
        ]
        stdout = StdOutIO()

        commands.main(argv=argv, stdout=stdout)

        stdout.seek(0)
        content = stdout.read()
        assert content == (
            'Uploading packages to http://localhost:8000\n'
            'Uploading packages/coverage-3.7.1.tar.gz... already uploaded.\n'
            'Uploading packages/mock-1.0.1.tar.gz... success.\n'
        )

        assert len(download_mock.call_args_list) == 1
        downloader = download_mock.call_args[0][0]
        assert downloader.download_path == 'packages'
        expected_call = mock.call(
            downloader,
            requirements=['coverage==3.7.1', 'mock'],
            requirements_file=None,
            no_use_wheel=False)
        assert download_mock.call_args == expected_call

        assert len(upload_mock.call_args_list) == 2
        uploader = upload_mock.call_args[0][0]
        assert uploader.host == 'http://localhost:8000'
        assert uploader.username == 'foo'
        assert uploader.password == 'bar'
        expected_calls = [
            mock.call(uploader, 'packages/coverage-3.7.1.tar.gz'),
            mock.call(uploader, 'packages/mock-1.0.1.tar.gz'),
        ]
        assert upload_mock.call_args_list == expected_calls

    @mock.patch.object(download.PackageDownloader, 'download', autospec=True)
    @mock.patch.object(upload.PackageUploader, 'upload', autospec=True)
    def test_requirements_no_download_dir(self, upload_mock, download_mock):
        upload_results = [None, exceptions.PackageConflictError('foo')]

        def upload_side_effect(*args):
            result = upload_results.pop()
            if isinstance(result, Exception):
                raise result
            return result

        upload_mock.side_effect = upload_side_effect
        download_mock.return_value = [
            '/tmp/f4Uf/coverage-3.7.1.tar.gz',
            '/tmp/f4Uf/mock-1.0.1.tar.gz'
        ]
        argv = [
            'requirements',
            'requirements.txt',
            '-i', 'http://localhost:8000',
            '-u', 'foo',
            '-p', 'bar',
        ]
        stdout = StdOutIO()

        commands.main(argv=argv, stdout=stdout)

        stdout.seek(0)
        content = stdout.read()
        assert content == (
            'Uploading packages to http://localhost:8000\n'
            'Uploading /tmp/f4Uf/coverage-3.7.1.tar.gz... already uploaded.\n'
            'Uploading /tmp/f4Uf/mock-1.0.1.tar.gz... success.\n'
        )

        assert len(download_mock.call_args_list) == 1
        downloader = download_mock.call_args[0][0]
        assert downloader.download_path is None
        expected_call = mock.call(
            downloader,
            requirements=None,
            requirements_file='requirements.txt',
            no_use_wheel=False)
        assert download_mock.call_args == expected_call

        assert len(upload_mock.call_args_list) == 2
        uploader = upload_mock.call_args[0][0]
        assert uploader.host == 'http://localhost:8000'
        assert uploader.username == 'foo'
        assert uploader.password == 'bar'
        expected_calls = [
            mock.call(uploader, '/tmp/f4Uf/coverage-3.7.1.tar.gz'),
            mock.call(uploader, '/tmp/f4Uf/mock-1.0.1.tar.gz'),
        ]
        assert upload_mock.call_args_list == expected_calls
