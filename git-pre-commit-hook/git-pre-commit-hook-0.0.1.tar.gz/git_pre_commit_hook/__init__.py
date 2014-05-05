import argparse
import os
import sys
import stat
import git_pre_commit_hook_utils


plugins = {}


def load_plugins():
    try:
        from pkg_resources import iter_entry_points
    except ImportError:
        return None
    for entry_point in iter_entry_points('git_pre_commit_hook.extensions'):
        plugins[entry_point.name] = entry_point.load()


def list_plugins(args):
    for plugin_name, plugin_module in plugins.items():
        print plugin_name, '-', plugin_module.__doc__
    return 0


def show_plugin_info(args):
    if args.name not in plugins:
        raise RuntimeError("Plugin '%s' doesn't exists" % (args.name))
    print args.name, '-', plugins[args.name].__doc__
    print 'Defaults:'
    print getattr(plugins[args.name], 'DEFAULTS', None)
    return 0


def run(args):
    if not args.plugins:
        raise RuntimeError('run requires at least one --plugin argument')
    for commited_file in git_pre_commit_hook_utils.files_staged_for_commit():
        for plugin_name in set(args.plugins):
            check_result = plugins[plugin_name].check(commited_file, args)
            if not check_result:
                raise RuntimeError(
                    "plugin {0} return False for {1}".format(
                        plugin_name, commited_file.path,
                    )
                )
    return 0


def gen_hook(args):
    return r'''
#!/usr/bin/env python
import sys
import git_pre_commit_hook


if __name__ == '__main__':
    sys.exit(git_pre_commit_hook.main({0}))
'''.format(['run'] + [arg for arg in args if arg != '--force']).lstrip('\n')


def install(args):
    path_to_hook = git_pre_commit_hook_utils.path_to_hook()
    if not args.force:
        if os.path.exists(path_to_hook):
            raise RuntimeError(
                'pre-commit hook already exists at %s' % (path_to_hook,)
            )
    with open(path_to_hook, 'w') as fd:
        fd.write(gen_hook(sys.argv[2:]))
    os.chmod(path_to_hook, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)


def add_plugins_arguments(parser, plugins):
    parser.add_argument(
        '--plugins',
        choices=plugins.keys(),
        action='append'
    )
    for plugin_name, plugin_module in plugins.items():
        for option, value in getattr(plugin_module, 'DEFAULTS', {}).items():
            parser.add_argument(
                '--%s_%s' % (plugin_name, option,),
                default=value,
            )
    parser.set_defaults(func=run)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    load_plugins()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    list_plugins_parser = subparsers.add_parser('list-plugins')
    list_plugins_parser.set_defaults(func=list_plugins)

    show_plugin_info_parser = subparsers.add_parser('show-plugin-info')
    show_plugin_info_parser.add_argument('name')
    show_plugin_info_parser.set_defaults(func=show_plugin_info)

    install_parser = subparsers.add_parser('install')
    install_parser.add_argument('--force', action='store_true', default=False)
    add_plugins_arguments(install_parser, plugins)
    install_parser.set_defaults(func=install)

    run_parser = subparsers.add_parser('run')
    add_plugins_arguments(run_parser, plugins)
    run_parser.set_defaults(func=run)

    args = parser.parse_args(args)
    try:
        return args.func(args)
    except RuntimeError as e:
        print e
        return 1
    else:
        return 0
