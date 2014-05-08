"""Give credit for the current git project or all projects down from cwd."""


from __future__ import division

import os
import sys
import time
import subprocess


def _clean_line(line):
    """Strips and maybe decodes a line of text."""

    line = line.strip()
    if isinstance(line, bytes):
        line = line.decode("latin-1")
    return line


def _run_cmd(cmd):
    """Runs a shell command and captures stdout."""

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    output = []
    while True:
        try:
            stdout, _ = proc.communicate()
        except:
            break
        stdout = _clean_line(stdout)
        if stdout:
            output.append(stdout)
        time.sleep(.1)

    return "".join(output).splitlines()


def get_credit_by_line(filepath):
    """Get a dictionary of git credit for all files in a repo by lines."""

    _prev_dir = os.getcwd()
    os.chdir(filepath)
    all_files = {}
    walk_cmd = "git ls-tree --name-only -r HEAD | grep -E '\\.py$'"
    for py_file in _run_cmd(walk_cmd):
        cmd = "git blame --line-porcelain -L '/[^\\s]/' {0}".format(py_file)
        for line in _run_cmd(cmd):
            if not line.startswith("author "):
                continue
            line = line[7:]

            if line in all_files:
                all_files[line] += 1
            else:
                all_files[line] = 1

    os.chdir(_prev_dir)
    return all_files


def is_git_dir(filepath):
    """Return a boolean of if this filepath has a .git folder."""

    git_dir = os.path.join(os.path.realpath(filepath), ".git")
    return os.path.exists(git_dir) and os.path.isdir(git_dir)


def sorted_by_value(credit):
    """Return the credit dict as a sorted list by value."""

    return sorted(credit.items(), key=lambda user: user[1], reverse=True)


def display_credit(credit):
    """Display the credit dict in a nice fashion."""

    total_per_committer = {}
    for repo, committers in credit.items():
        repo_total = sum(committers.values())
        print("git credit for repo: {0}".format(repo))
        for committer, lines in sorted_by_value(committers):
            print("    {0}: {1} lines ({2:.1f}%)".format(
                committer,
                lines,
                ((lines / repo_total) * 100),
            ))
            if committer in total_per_committer:
                total_per_committer[committer] += lines
            else:
                total_per_committer[committer] = lines

    if len(credit) > 1:
        total_lines = sum(total_per_committer.values())
        print("total git credit across all {0} repos:".format(len(credit)))
        for committer, lines in sorted_by_value(total_per_committer):
            print("    {0}: {1} lines ({2:.1f}%)".format(
                committer,
                lines,
                ((lines / total_lines) * 100),
            ))


def walk_git(filepath=None):
    """Get credit for all repos down from filepath.

    Returns:
        dict of {repo: {committer: lines_in_HEAD}}
    """

    if filepath is None:
        filepath = os.curdir

    all_credit = {}
    for repo, _, _ in os.walk(os.path.realpath(filepath)):
        if is_git_dir(repo):
            all_credit[repo] = get_credit_by_line(repo)

    return all_credit


def get_help(repo=None):
    """Raises SystemExit with a help message for the user."""

    if not repo:
        repo = [os.path.realpath(os.curdir)]

    if len(repo) == 1:
        msg = "{0} is not a git repo".format(repo[0])
    elif len(repo) == 2:
        msg = "Neither {0} nor {1} contain git repos".format(repo[0], repo[1])
    else:
        msg = "None of {0} or {1} contain git repos".format(
            ", ".join(repo[:-1]),
            repo[-1],
        )

    raise SystemExit(msg)


def parse_args(args):
    """Check for arguments as filepaths and build the credit dict with them."""

    if len(args) == 1:
        all_credit = walk_git()
    elif len(args) == 2:
        all_credit = walk_git(args[1])
    else:
        all_credit = {}
        for arg in args[1:]:
            all_credit.update(walk_git(arg))

    return all_credit or get_help(args[1:])


def main():
    """Command line entry point."""

    display_credit(parse_args(sys.argv))


if __name__ == "__main__":
    main()
