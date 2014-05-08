"""Give credit for the current git project or all projects down from cwd."""


import os
import sys
import subprocess


def get_credit_for_repo(filepath):
    """Get a dict of {user: lines in HEAD} for the filepath git repo."""

    _prev_dir = os.getcwd()
    os.chdir(filepath)
    proc = subprocess.Popen(
        "git log --pretty=format:%an", shell=True, stdout=subprocess.PIPE
    )
    proc.wait()
    os.chdir(_prev_dir)

    return parse_git_log(proc.stdout)


def parse_git_log(output):
    """Parses the string output of the git log command into a dict."""

    committers = {}
    for line in output or []:
        line = line.strip()
        if isinstance(line, bytes):
            line = line.decode("latin-1")
        if line in committers:
            committers[line] += 1
        else:
            committers[line] = 1
    return committers


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
            print("  {0}: {1} ({2:.1f}%)".format(
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
            print("  {0}: {1} ({2:.1f}%)".format(
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
            all_credit[repo] = get_credit_for_repo(repo)

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
