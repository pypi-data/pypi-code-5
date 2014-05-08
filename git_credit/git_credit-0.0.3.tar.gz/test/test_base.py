"""Unit tests for git_credit.base."""


from __future__ import division

import os
import sys
import pytest
from mock import Mock, patch

from git_credit import base


@pytest.fixture(params=(
        ["fname"],
        ["fname", "/fake/dir/not/real"],
        ["fname", "/fake/dir/not/real", "/totes/fake/not/even/real"],
        ["fname", "/fake/dir", "/not/real", "/totes/fake/dir", "/cant/even/"],
    ),
    ids=("no dirs", "one dir", "two dirs", "many dirs"),
)
def args(request):
    return request.param


def test_parse_args(args):
    """Check the lazy arg parser is working as intended."""

    with patch.object(base, "walk_git", return_value={"fake": 10}) as mock_git:
        base.parse_args(args)

    for arg in args[1:]:
        mock_git.assert_any_call(arg)

    assert mock_git.called


def test_getting_help(args):
    """Ensure the error message is raised."""

    args = args[1:]
    with pytest.raises(SystemExit) as sys_exit:
        base.get_help(args)

    if not args:
        exp = "{0} is not a git repo".format(os.path.realpath(os.curdir))
    elif len(args) == 1:
        exp = "{0} is not a git repo".format(args[0])
    elif len(args) == 2:
        exp = "Neither {0} nor {1} contain git repos".format(args[0], args[1])
    else:
        exp = "None of {0} or {1} contain git repos".format(
            ", ".join(args[:-1]),
            args[-1],
        )

    assert exp in sys_exit.value.args


def test_main():
    """Mock to ensure program flow."""

    with patch.object(base, "parse_args") as mock_parse:
        with patch.object(base, "display_credit") as mock_display:
            base.main()
    mock_parse.assert_called_once_with(sys.argv)
    assert mock_display.called


@pytest.mark.parametrize("filepath", (".", "..", None, "/fake/dir"))
def test_walk_git(filepath):
    """A whole lot of mocking going on here..."""

    realpath_mock = patch.object(base.os.path, "realpath", return_value="fake")
    walk_mock = patch.object(base.os, "walk", return_value=[("ok", 0, 0)])
    git_dir_mock = patch.object(base, "is_git_dir", return_value=True)
    get_credit_mock = patch.object(base, "get_credit_by_line", return_value=1)

    with realpath_mock as mock_realpath:
        with walk_mock as mock_walk:
            with git_dir_mock as mock_git_dir:
                with get_credit_mock as mock_get_credit:
                    assert base.walk_git(filepath) == {"ok": 1}

    if filepath is None:
        mock_realpath.assert_called_once_with(os.curdir)
    else:
        mock_realpath.assert_called_once_with(filepath)

    mock_walk.assert_called_once_with("fake")
    mock_git_dir.assert_called_once_with("ok")
    mock_get_credit.assert_called_once_with("ok")


@pytest.mark.parametrize("test_input",
    (
        {"fake_repo": {"johann": 30, "julia": 40, "cornelia": 30}},
        {
            "fake_repo": {"vilda": 25, "melvin": 40, "melissa": 35},
            "other_repo": {"jessica": 60, "daniel": 40},
        },
        {
            "fake_repo": {"vilda": 25, "melvin": 40, "melissa": 35},
            "other_repo": {"jessica": 60, "daniel": 40},
            "repo_trio": {"melvin": 90, "fernado": 10},
        }
    ),
    ids=("one", "more than one", "same person different repo"),
)
def test_output_more_than_one(test_input, capfd):
    """Test the output formatting with fake data."""

    base.display_credit(test_input)
    out, _ = capfd.readouterr()
    out = out.splitlines()

    all_committers = {}
    for repo, committers in test_input.items():
        repo_lines = sum(committers.values())
        assert "git credit for repo: {0}".format(repo) in out
        for name, lines in committers.items():
            assert "    {0}: {1} lines ({2:.1f}%)".format(
                name,
                lines,
                ((lines / repo_lines) * 100),
            ) in out
            if name in all_committers:
                all_committers[name] += lines
            else:
                all_committers[name] = lines

    if len(test_input) > 1:
        exp = "total git credit across all {0} repos:".format(len(test_input))
        assert exp in out
        total_lines = sum(all_committers.values())
        for name, lines in all_committers.items():
            assert "    {0}: {1} lines ({2:.1f}%)".format(
                name,
                lines,
                ((lines / total_lines) * 100),
            ) in out


def test_is_git_dir():
    """Mock all calls to test determining if we are in a git dir."""

    realpath_mock = patch.object(base.os.path, "realpath", return_value="ok")
    join_mock = patch.object(base.os.path, "join", return_value="joined")

    with realpath_mock as mock_realpath:
        with join_mock as mock_join:
            with patch.object(base.os.path, "exists") as mock_exists:
                with patch.object(base.os.path, "isdir") as mock_isdir:
                    base.is_git_dir("something")

    mock_realpath.assert_called_once_with("something")
    mock_join.assert_called_once_with("ok", ".git")
    mock_exists.assert_called_once_with("joined")
    mock_isdir.assert_called_once_with("joined")
