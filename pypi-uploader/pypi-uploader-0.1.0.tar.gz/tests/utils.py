import tempfile


PYPIRC = b"""
[distutils]
index-servers =
  pypi

  internal
  external

[pypi]
username: foo
password: bar

[internal]
repository: http://127.0.0.1:8000
username: bar
password: foo

[external]
repository: https://foo.bar.com/
username: baz
"""


def _make_tmp_pypirc_file(content=None):
    if content is None:
        content = PYPIRC
    tmpfile = tempfile.NamedTemporaryFile()
    tmpfile.write(content)
    tmpfile.seek(0)
    return tmpfile
