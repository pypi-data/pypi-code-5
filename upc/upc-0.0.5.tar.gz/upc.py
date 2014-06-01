#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""A simple command-line tool for managing upyun files.

It acts just like GNU tools, and also support command completion
which can be triggered by double enter 'Tab'.

For local files operation, you have lls, lcd and others which acts like
lftp.

"""

import os
import sys
import cmd
import stat
import getopt
import fnmatch
import functools
from datetime import datetime
from upyun import UpYun, UpYunClientException, UpYunServiceException


# fix auto completion on macintosh
import readline
if 'libedit' in readline.__doc__:
    import rlcompleter
    readline.parse_and_bind("bind ^I rl_complete")

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser


__author__ = 'Kang Li<i@likang.me>'
__version__ = '0.0.5'


conf_path = os.path.expanduser('~/.upcrc')


def neat(**neat_args):
    """Command function wrapper, capture error and show them neatly"""
    def neat_wrapper(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except UpYunServiceException as ex:
                if not neat_args.get('silence', False):
                    self.output('ServiceError(%s): %s' % (ex.status, ex.msg))
            except UpYunClientException as ex:
                if not neat_args.get('silence', False):
                    self.output('ClientError: %s' % ex.msg)
            except Exception as ex:
                if not neat_args.get('silence', False):
                    msg = getattr(ex, 'msg', '')
                    message = getattr(ex, 'message', '')
                    self.output('UnexpectedError: %s' % msg or message or ex)

            if 'default' in neat_args:
                return neat_args['default']
        return wrapper
    return neat_wrapper


class Terminal(cmd.Cmd):
    """A simple command-line tool for managing upyun files.

    It acts just like GNU tools, and also support command completion
    which can be triggered by double enter 'Tab'.

    For local files operation, you have lls, lcd and others which acts like
    lftp.

    """
    def __init__(self, options, completekey='tab', stdin=None, stdout=None):
        self.options = options
        self.pwd = '/'
        self.prompt = 'upyun > '
        self.up = None
        self.vocab = ['ls', 'pwd', 'cd', 'rm', 'put', 'get',
                      'mkdir', 'rmdir', 'use', 'open', 'usage',
                      'quit', 'help']

        cmd.Cmd.__init__(self, completekey, stdin, stdout)

    @neat()
    def do_usage(self, line):
        """Show the usage of current bucket

        usage [-h]

            -h  Show human-readable output
        """
        usage_size = self.up.usage().strip()
        if '-h' in line:
            self.output(human_size(usage_size))
        else:
            self.output(usage_size + ' bytes')

    @neat()
    def do_ls(self, line):
        """List directory contents

        usage [-hsStTnN]

            -h  Show human-readable output
            -s  Sort by file size
            -S  Sort by file size desc
            -t  Sort by created time
            -T  Sort by created time desc
            -n  Sort by file name
            -N  Sort by file name desc
        """
        opts, dirs = getopt.getopt(line.split(), 'hsStTnN')
        opts = [o[0] for o in opts]
        dirs = dirs or ['']

        path = os.path.join(self.pwd, dirs[0])
        files = self.up.getlist(path)

        # do the sort
        if '-s' in opts or '-S' in opts:
            files.sort(key=lambda v: int(v['size']), reverse='-S' in opts)

        if '-t' in opts or '-T' in opts:
            files.sort(key=lambda v: v['time'], reverse='-T' in opts)

        if '-n' in opts or '-N' in opts:
            files.sort(key=lambda v: v['name'], reverse='-N' in opts)

        show_size = human_size if '-h' in opts else int
        for f in files:
            self.output('%s\t%s\t%s\t%s' % (
                {'F': 'd', 'N': '-'}[f['type']],
                datetime.fromtimestamp(int(f['time'])),
                show_size(f['size']) if f['type'] == 'N' else '-',
                f['name'])
            )

    def complete_ls(self, *args):
        return file_complete(args, self.pwd,
                             self.remote_list_dir_func, type_filter='dir')

    @neat()
    def do_put(self, line):
        """Upload local files/directories to current work directory.

        put [-r] file ...

            -r  Recursively upload entire directories.

        """
        opts, fds = getopt.getopt(line.split(), 'r')
        opts = [o[0] for o in opts]
        if not fds:
            self.do_help('put')
            return

        files = []
        dirs = []
        # support shell wildcards
        for f in os.listdir(os.getcwd()):
            for fd in fds:
                fd = fd.rstrip(os.sep)
                if fnmatch.fnmatch(f, fd):
                    path = os.path.join(os.getcwd(), f)
                    if os.path.isdir(path):
                        dirs.append(f)
                    else:
                        files.append(f)
        files = list(set(files))
        dirs = list(set(dirs))

        # find files recursively
        if '-r' in opts:
            for d in dirs:
                for dirpath, dirnames, filenames in os.walk(d):
                    files.extend([os.path.join(dirpath, f) for f in filenames])

        for f in files:
            with open(os.path.join(os.getcwd(), f), 'rb') as fd:
                to_path = os.path.join(self.pwd, f)
                self.up.put(to_path, fd, checksum=False)
                self.output('%s\t OK' % f)

    def complete_put(self, *args):
        return file_complete(args, os.getcwd(), local_list_dir_func)

    @neat()
    def do_get(self, line, first_call=True):
        """Download files entries

        get [-r] file ...

            -r  Download folder.

        """
        opts, fds = getopt.getopt(line.split(), 'r')
        opts = [o[0] for o in opts]
        if not fds:
            self.do_help('get')
            return

        to_be_dld = []
        # support shell wildcards
        cwd_files = self.up.getlist(self.pwd)
        if first_call:
            for cf in cwd_files:
                for fd in fds:
                    fd = fd.rstrip(os.sep)
                    if fnmatch.fnmatch(cf['name'], fd):
                        to_be_dld.append(cf['name'])
        else:
            to_be_dld = fds

        # rm file, recursively if needed
        for fd in to_be_dld:
            path = os.path.join(self.pwd, fd)
            info = self.up.getinfo(path)
            if info['file-type'] == 'folder':
                if '-r' in opts:
                    fs = self.up.getlist(path)
                    for f in fs:
                        new_path = os.path.join(path, f['name'])
                        self.do_get('-r %s' % new_path, False)
            else:
                relative_path = path[len(self.pwd):]
                try:
                    os.makedirs(os.path.join(os.getcwd(),
                                             os.path.dirname(relative_path)))
                except OSError:
                    pass
                with open(os.path.join(os.getcwd(), relative_path), 'wb') as f:
                    self.up.get(path, f)

    def complete_file(self, *args):
        return file_complete(args, self.pwd, self.remote_list_dir_func)

    @neat()
    def do_mkdir(self, line):
        """Make directories

        mkdir [-p] directory_name ...

            -p  Create intermediate directories as required.

        """
        opts, dirs = getopt.getopt(line.split(), 'p')
        opts = [o[0] for o in opts]
        if not dirs:
            self.do_help('mkdir')
            return

        for d in dirs:
            headers = {'Folder': 'true'}
            if '-p' in opts:
                headers['Mkdir'] = 'true'
            # Okay, I don't like this too, but ... :(
            self.up._UpYun__do_http_request('POST', os.path.join(self.pwd, d),
                                            headers=headers)

    @neat()
    def do_rm(self, line, first_call=True):
        """Remove directory entries

        rm [-r] file ...

            -r  Remove the file hierarchy rooted in each file argument.

        """
        opts, fds = getopt.getopt(line.split(), 'r')
        opts = [o[0] for o in opts]
        if not fds:
            self.do_help('rm')
            return

        to_be_rmd = []
        # support shell wildcards
        cwd_files = self.up.getlist(self.pwd)
        if first_call:
            for cf in cwd_files:
                for fd in fds:
                    fd = fd.rstrip(os.sep)
                    if fnmatch.fnmatch(cf['name'], fd):
                        to_be_rmd.append(cf['name'])
        else:
            to_be_rmd = fds

        # rm file, recursively if needed
        for fd in to_be_rmd:
            path = os.path.join(self.pwd, fd)
            info = self.up.getinfo(path)
            if info['file-type'] == 'folder':
                if '-r' in opts:
                    fs = self.up.getlist(path)
                    for f in fs:
                        new_path = os.path.join(path, f['name'])
                        self.do_rm('-r %s' % new_path, False)
            self.up.delete(path)

    def complete_rm(self, *args):
        return file_complete(args, self.pwd, self.remote_list_dir_func)

    def do_rmdir(self, d):
        """Remove directories, same with rm"""
        self.do_rm(d)

    complete_rmdir = complete_rm

    @neat()
    def do_cd(self, line):
        """Change working directory

        cd [directory]
        """
        dir_name = (line.strip().split()+[''])[0]
        if not dir_name:
            self.pwd = '/'
            return

        path = os.path.abspath(os.path.join(self.pwd, dir_name))
        if path != '/':
            path = path.rstrip(os.sep)

        self.up.getinfo(path)
        self.pwd = path

    complete_cd = complete_ls

    def do_pwd(self, line):
        """Print working directory name"""
        self.output(self.pwd)

    @neat()
    def do_file(self, line):
        """Show file/directory info

        file file ...

            -h  Show human-readable output
        """
        opts, files = getopt.getopt(line.strip().split(), 'h')
        if not files:
            self.do_help('file')
            return
        opts = [o[0] for o in opts]

        show_size = human_size if '-h' in opts else int
        for f in files:

            info = self.up.getinfo(os.path.join(self.pwd, f))

            if info['file-type'] == 'folder':
                size = '-'
            else:
                size = show_size(info['file-size'])
            self.output('%s\t%s\t%s\t%s' % (
                {'folder': 'd', 'file': '-'}[info['file-type']],
                datetime.fromtimestamp(int(info['file-date'], )),
                size,
                f))

    complete_file = complete_rm

    @neat()
    def do_lls(self, line):
        """List local directory contents

        usage [-hsStT]

            -h  Show human-readable output
            -s  Sort by file size
            -S  Sort by file size desc
            -t  Sort by created time
            -T  Sort by created time desc
            -n  Sort by file name
            -N  Sort by file name desc
        """
        opts, dirs = getopt.getopt(line.strip().split(), 'hsStTnN')
        opts = [o[0] for o in opts]
        dirs = dirs or ['']

        path = os.path.join(os.getcwd(), dirs[0])
        files = []

        for f in os.listdir(path):
            fi = os.stat(os.path.join(path, f))
            files.append({
                'size': fi.st_size,
                'time': fi.st_mtime,
                'name': f,
                'type': 'F' if stat.S_ISDIR(fi.st_mode) else 'N',

            })

        # do the sort
        if '-s' in opts or '-S' in opts:
            files.sort(key=lambda v: int(v['size']), reverse='-S' in opts)

        if '-t' in opts or '-T' in opts:
            files.sort(key=lambda v: v['time'], reverse='-T' in opts)

        if '-n' in opts or '-N' in opts:
            files.sort(key=lambda v: v['name'], reverse='-N' in opts)

        show_size = human_size if '-h' in opts else int
        for f in files:
            self.output('%s\t%s\t%s\t%s' % (
                {'F': 'd', 'N': '-'}[f['type']],
                datetime.fromtimestamp(int(f['time'])),
                show_size(f['size']) if f['type'] == 'N' else '-',
                f['name'])
            )

    def complete_lls(self, *args):
        return file_complete(args, os.getcwd(),
                             local_list_dir_func, type_filter='dir')

    def do_lpwd(self, line):
        """Print local working directory name"""
        self.output(os.getcwd())

    @neat()
    def do_lcd(self, d):
        """Change local working directory"""
        d = (d.strip().split() + [''])[0]
        if not d:
            d = '~'
        path = os.path.expanduser(os.path.join(os.getcwd(), d))
        if not os.path.isdir(path):
            self.output('no such directory: %s' % path)
            return
        os.chdir(path)

    def complete_lcd(self, *args):
        return file_complete(args, os.getcwd(),
                             local_list_dir_func, type_filter='dir')

    @neat()
    def do_lmkdir(self, line):
        opts, dirs = getopt.getopt(line.strip().split(), 'p')
        opts = [o[0] for o in opts]

        for d in dirs:
            path = os.path.join(os.getcwd(), d)
            path = os.path.abspath(os.path.expanduser(path))

            if '-p' in opts:
                os.makedirs(path)
            else:
                os.mkdir(path)

    complete_lmkdir = complete_lcd


    def do_use(self, line):
        """Switch bucket.

        use bucket_name
        """
        bucket = (line.strip().split() + [''])[0]
        if not bucket:
            self.do_help('use')
            return

        self.switch_bucket(bucket)

    def complete_use(self, *args):
        bucket = (args[0].strip().split()+[''])[0]

        return [b for b in self.options.sections() if b.startswith(bucket)]

    def do_quit(self, line):
        """
        Quit/Exit the upyun client shell.
        You can also use the Ctrol-D shortcut.
        """
        self.output('')
        sys.exit(0)

    do_EOF = do_exit = do_quit

    def do_welcome(self, line):
        self.output(r"""
 __  __     ______   __  __     __  __     __   __
/\ \/\ \   /\  == \ /\ \_\ \   /\ \/\ \   /\ "-.\ \
\ \ \_\ \  \ \  _-/ \ \____ \  \ \ \_\ \  \ \ \-.  \
 \ \_____\  \ \_\    \/\_____\  \ \_____\  \ \_\\"\_\
  \/_____/   \/_/     \/_____/   \/_____/   \/_/ \/_/
  """)

    @neat(default=list(), silence=True)
    def remote_list_dir_func(self, wd):
        """Get directory contents on the remote."""
        files = self.up.getlist(wd)
        result = []
        for f in files:
            result.append({
                'name': f['name'],
                'is_dir': f['type'] == 'F'
            })
        return result

    @neat()
    def switch_bucket(self, bucket):
        """Switch to buckets defined in conf_file, and check if it's valid."""
        if self.options.has_section(bucket):
            params = {k: v.strip() for k, v in self.options.items(bucket)}
            params['bucket'] = bucket
            up = UpYun(**params)
            up.usage()
            self.pwd = '/'
            self.up = up
            self.update_prompt()
        else:
            self.output("bucket '%s' doesn't exist in the config file(%s)." % (
                bucket, conf_path))

    def update_prompt(self):
        """Update cmd prompt"""
        if self.up:
            prompt = '/' if self.pwd == '/' else os.path.basename(self.pwd)
            self.prompt = '(%s) %s > ' % (self.up.bucket, prompt)

    def postcmd(self, stop, line):
        self.update_prompt()

    def output(self, stuff):
        self.stdout.write(stuff + '\n')

    def do_help(self, arg):
        """List available commands with "help"
        or detailed help with "help cmd"."""
        if arg:
            try:
                func = getattr(self, 'help_' + arg)
            except AttributeError:
                try:
                    doc = trim_doc(getattr(self, 'do_' + arg).__doc__)
                    if doc:
                        self.stdout.write('%s\n' % str(doc))
                        return
                except AttributeError:
                    pass
                self.stdout.write('%s\n' % str(self.nohelp % (arg,)))
                return
            func()
        else:
            names = self.get_names()
            cmds_doc = []
            cmds_undoc = []
            help = {}
            for name in names:
                if name[:5] == 'help_':
                    help[name[5:]] = 1
            names.sort()
            # There can be duplicates if routines overridden
            prevname = ''
            for name in names:
                if name[:3] == 'do_':
                    if name == prevname:
                        continue
                    prevname = name
                    cmd=name[3:]
                    if cmd in help:
                        cmds_doc.append(cmd)
                        del help[cmd]
                    elif getattr(self, name).__doc__:
                        cmds_doc.append(cmd)
                    else:
                        cmds_undoc.append(cmd)
            self.stdout.write("%s\n" % str(self.doc_leader))
            self.print_topics(self.doc_header,   cmds_doc,    15, 80)
            self.print_topics(self.misc_header,  help.keys(), 15, 80)
            self.print_topics(self.undoc_header, cmds_undoc,  15, 80)


def mix_unicode(s, encoding='utf-8'):
    if sys.version < '3':
        return s.decode(encoding)
    return s


def mix_str(s, encoding='utf-8'):
    if sys.version < '3':
        return s.encode(encoding)
    return s


def local_list_dir_func(wd):
    files = os.listdir(wd)
    result = []
    for f in files:
        result.append({
            'name': mix_unicode(f),
            'is_dir': os.path.isdir(os.path.join(wd, f))
        })
    return result


def human_size(num):
    num = int(num)
    if num == 0:
        return '0 byte'
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return '%3.2f %s' % (num, x)
        num /= 1024.0
    return '%3.2f %s' % (num, 'TB')


def file_complete(args, pwd, list_dir_func, type_filter=None):
    """Get list of files based on the typed path.

    :param path: typed path
    :param pwd: current word directory
    :param list_dir_func: call back function which
    return contents in certain directory
    :param type_filter:
    :return: list of possible contents you might want to type
    """
    path = args[0]
    new_mod = False
    # fix python3 on macintosh
    if path != args[1].split()[-1]:
        new_mod = True
        path = args[1].split()[-1]

    path = mix_unicode(path)
    pwd = mix_unicode(pwd)
    input_path = (path.strip().split() + [''])[0]
    dist_path = os.path.join(pwd, input_path)

    abs_dist_path = os.path.abspath(dist_path)
    if dist_path.endswith(os.sep):
        abs_dist_path += os.sep

    origin_dir_name = os.path.dirname(input_path)
    dir_name = os.path.dirname(abs_dist_path)
    base_name = os.path.basename(abs_dist_path)

    files = []

    # filter the files
    for f in list_dir_func(dir_name):
        if f['is_dir']:
            if type_filter == 'file':
                continue
            files.append(f['name'] + os.sep)
        else:
            if type_filter == 'dir':
                continue
            files.append(f['name'])

    completes = [f for f in files if f.startswith(base_name)]

    # find the longest common substring from the very start
    if len(completes) > 1:
        common = base_name
        max_common_length = min([len(c) for c in completes])
        for i in range(len(base_name), max_common_length):
            if len(set([c[i] for c in completes])) == 1:
                common += completes[0][i]
            else:
                break
        if common != base_name:
            if not new_mod:
                return [mix_str(common)]
            else:
                return [mix_str(os.path.join(origin_dir_name, common))]

    if new_mod:
        return [mix_str(c) for c in completes]
    else:
        return [mix_str(os.path.join(origin_dir_name, c)) for c in completes]


def trim_doc(docstring):
    """Remove indention of python docstring properly

    for more detail, see http://legacy.python.org/dev/peps/pep-0257/
    """
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)


def load_options():
    if not os.path.exists(conf_path):
        print("Sorry but I can't find the config file. Please fill the "
              "following template and save it to %s" % conf_path)
        print("""
; Sample upc config file

; The below sample bucket section shows all possible config values,
; create one or more 'real' bucket sections to be able to control them under
; upc.

;[bucket_name]
;username=foo
;password=bar
;endpoint=
;timeout=
;chunksize=

;[more_buckets] ; your bucket name
;..""")
        sys.exit(2)
    options = ConfigParser()
    with open(conf_path, 'r') as f:
        options.readfp(f)
    return options


def main():
    options = load_options()
    up_cmd = Terminal(options)

    if len(sys.argv) == 1:
        print ('usage: upc bucket-name')
        print ('usage: upc bucket-name command [option ...]')
        sys.exit(2)

    up_cmd.switch_bucket(sys.argv[1])
    if up_cmd.up is None:
        sys.exit(2)

    if len(sys.argv) >= 3:
        up_cmd.onecmd(' '.join(sys.argv[2:]))
    else:
        try:
            up_cmd.cmdqueue.append('welcome')
            up_cmd.cmdloop()
        except KeyboardInterrupt:
            up_cmd.output('')


if __name__ == '__main__':
    main()
