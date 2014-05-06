"""Check files with flake8."""
import flake8.main
import re


PYTHON_SHEBANG_REGEX = re.compile(r'''^#!.*python''')


def check(file_staged_for_commit, options):
    if file_staged_for_commit.path.endswith('.py') or \
            PYTHON_SHEBANG_REGEX.search(file_staged_for_commit.contents):
        status = flake8.main.check_code(file_staged_for_commit.contents)
        return status == 0
    else:
        return True
