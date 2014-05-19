
import pytest

from kez.utils import parse_vcs_url
from kez.utils import ConfigParser
from kez.utils import evaluate_config_options

from .data import URL1

def test_parse_git_ssh_url():
    assert URL1 == "git@github.com:averagehuman/maths.averagehuman.org.git"
    kw = parse_vcs_url(URL1)
    assert kw["url"] == URL1
    assert kw["vcs"] == "git"
    assert kw["host"] == "github"
    assert kw["owner"] == "averagehuman"
    assert kw["repo"] == "maths.averagehuman.org"
    assert kw["slug"] == "github-com-averagehuman-maths-averagehuman-org-git"

def test_config_parser(File):
    cfg = ConfigParser()
    with File("example.cfg") as fp:
        cfg.readfp(fp)
    strkey = cfg.get("section", "__strkey__")
    intkey = cfg.get("section", "__intkey__")
    listkey = cfg.get("section", "__listkey__")
    assert strkey == "pelican"
    assert intkey == 42
    assert listkey == [2, 4, 6, 8]
    options, settings = evaluate_config_options(cfg, "section")
    # double-underscores are stripped
    assert options == {'strkey': 'pelican', 'intkey': 42, 'listkey': [2, 4, 6, 8]}
    assert settings == {'SITENAME': 'My Site', 'THEME': 'indigo'}

