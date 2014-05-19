
import os
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import pytest

from kez.models import sqlite_proxy
from kez.manager import Manager
from kez.ui.application import UI

from .data import STORAGE_ROOT

_proxy = None

@pytest.fixture
def storage_root():
    return STORAGE_ROOT

@pytest.fixture
def vcs_cache(storage_root):
    return os.path.join(storage_root, '__VCS__')

@pytest.fixture
def db():
    global _proxy
    if _proxy is None:
        db_path = os.path.join(STORAGE_ROOT, 'example.db')
        if os.path.exists(db_path):
            os.remove(db_path)
        _proxy = sqlite_proxy(db_path)
    return _proxy

@pytest.fixture
def manager(db, storage_root):
    return Manager(db, storage_root)

@pytest.fixture
def File():
    def FileOpener(relpath, mode="rb"):
        return open(os.path.join(STORAGE_ROOT, relpath.lstrip('/')))
    return FileOpener

@pytest.fixture
def ui():
    return UI(stdout=StringIO(), stderr=StringIO())

