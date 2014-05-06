import os
import fnmatch
import restructuredtext_lint


DEFAULTS = {
    'files': '*.rst',
}


def make_message(error):
    return '%s %s:%s %s\n' % (
        error.type, error.source, error.line, error.message,
    )


def check(file_staged_for_commit, options):
    basename = os.path.basename(file_staged_for_commit.path)
    if not fnmatch.fnmatch(basename, options.rst_files):
        return True
    errors = restructuredtext_lint.lint(
        file_staged_for_commit.contents,
        file_staged_for_commit.path,
    )
    if errors:
        print('\n'.join(make_message(e) for e in errors))
        return False
    else:
        return True
