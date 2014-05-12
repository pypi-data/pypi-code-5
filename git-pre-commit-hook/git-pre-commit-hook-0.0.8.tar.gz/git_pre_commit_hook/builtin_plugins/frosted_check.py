"""Check Python-code with frosted."""
import frosted.api
import re


PYTHON_SHEBANG_REGEX = re.compile(r'''^#!.*python''')


def check(file_staged_for_commit, options):
    if file_staged_for_commit.path.endswith('.py') or \
            PYTHON_SHEBANG_REGEX.search(file_staged_for_commit.contents):
        status = frosted.api.check(
            file_staged_for_commit.contents,
            file_staged_for_commit.path,
        )
        return status == 0
    else:
        return True
