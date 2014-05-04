import subprocess
import collections
import re


ExecutionResult = collections.namedtuple(
    'ExecutionResult',
    'status, stdout, stderr',
)


def _execute(args):
    process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    status = process.poll()
    return ExecutionResult(status, stdout, stderr)


def _current_commitish():
    if _execute('git rev-parse --verify HEAD'.split()).status:
        return '4b825dc642cb6eb9a060e54bf8d69288fbee4904'
    else:
        return 'HEAD'


def _diff_index():
    return subprocess.check_output(
        [
            'git',
            'diff-index',
            '--cached',
            '-z',
            '--diff-filter=AM',
            _current_commitish(),
        ]
    )


def _contents(sha):
    return subprocess.check_output(
        [
            'git',
            'show',
            sha,
        ]
    )


def _size(sha):
    cmd_out = subprocess.check_output(
        [
            'git',
            'cat-file',
            '-s',
            sha,
        ]
    )
    return int(cmd_out)


FileAtIndex = collections.namedtuple(
    'FileAtIndex',
    'contents, size, mode, sha1, status, path'
)


def files_staged_for_commit():
    # see: git help diff-index
    # "RAW OUTPUT FORMAT" section
    diff_index_row_regex = re.compile(
        r'''
        :
        (?P<old_mode>[^ ]+)
        [ ]
        (?P<new_mode>[^ ]+)
        [ ]
        (?P<old_sha1>[^ ]+)
        [ ]
        (?P<new_sha1>[^ ]+)
        [ ]
        (?P<status>[^\0]+)
        \0
        (?P<path>[^\0]+)
        \0
        ''',
        re.X
    )
    for match in diff_index_row_regex.finditer(_diff_index()):
        mode, sha, status, path = match.group(
            'new_mode', 'new_sha1', 'status', 'path'
        )
        yield FileAtIndex(
            _contents(sha),
            _size(sha),
            mode,
            sha,
            status,
            path
        )
