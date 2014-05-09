# -*- coding: utf-8 -*-

"""
    fatafat
    ~~~~~~~

    A static blog generator with simple and quick publishing options.

    :copyright: (c) 2014 by Subhajit Ghosh.
    :license: Apache2, see LICENSE for more details.
"""

from jinja2 import Environment, PackageLoader
from fatafat.blog import DevBlog, GithubBlog
from fatafat.util import makedir

import argparse
import imp
import os
import textwrap

cwd = os.path.dirname(os.path.realpath(__file__))
THEMES_DIR = os.path.join(cwd, 'themes')
TEMPLATES_DIR = os.path.join(cwd, 'templates')


class Configuration(object):
    """Currently empty but can be used in future to supply default values to
    configuration options.
    """

    def __init__(self):
        pass


def publish(args):
    # Update the file paths to be relative paths under the contents directory.
    paths = [os.path.relpath(f, 'contents') for f in args.files]

    if args.prod:
        config = imp.load_source('config', os.path.join('prod', 'config.py'))
        blog = GithubBlog(config)
        blog.publish(paths)
        if args.sync:
            blog.sync()
    else:
        config = imp.load_source('config', os.path.join('dev', 'config.py'))
        blog = DevBlog(config)
        blog.publish(paths)


def start(args):
    """Creates the fatafat powered blog.

    TODOS (isubuz):
        - validate input URLs
    """
    print textwrap.dedent('''\
    Welcome to fatafat!
    Answer the following questions to create your fatafat powered blog:
    ''')

    conf = Configuration()
    conf.SITE_NAME = raw_input('> Enter blog title: ')
    prod_url = raw_input('> Enter production URL of blog: ')
    dev_url = raw_input('> Enter development URL of blog: ')
    conf.GITHUB_USERNAME = raw_input('> Enter Github username: ')
    conf.DISQUS_SITENAME = raw_input('> Enter Disqus sitename: ')
    conf.THEME = 'simi'

    # Create the top-level blog directory structure
    makedir('prod')
    makedir('dev')
    makedir('contents')

    # Create the config.py file under the production and development dirs.
    template_env = Environment(loader=PackageLoader('fatafat', 'templates'))
    template = template_env.get_template('config.jinja2')
    with open(os.path.join('prod', 'config.py'), 'w') as p, \
            open(os.path.join('dev', 'config.py'), 'w') as d:
        conf.SITE_URL = prod_url
        p.write(template.render(config=conf))

        conf.SITE_URL = dev_url
        d.write(template.render(config=conf))

    # Setup the development version of the blog
    conf.SITE_URL = dev_url
    dev_blog = DevBlog(conf)
    dev_blog.setup()

    # Setup the production version of the blog
    conf.SITE_URL = prod_url
    github_blog = GithubBlog(conf)
    github_blog.setup()

    print '\nBlog created.'


def main():
    """Parser the command line arguments."""
    parser = argparse.ArgumentParser(
        description=textwrap.dedent('''\
        A program to generate a static blog in the current directory using
        articles under the contents directory.
        '''),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(
        title='How to use the fatafat command',
        description=textwrap.dedent('''\
        The fatafat command must be run at the root of the directory which
        stores the blog. Several actions can be performed with the fatafat
        command. To get detailed help on individual actions, run:

            fatafat <action> --help     # or
            fatafat <action> -h
        '''),
        help='List of supported actions',
    )

    # Parser for the ``start`` command
    parser_qs = subparsers.add_parser('start', help='Create a new blog.')
    parser_qs.set_defaults(func=start)

    # Parser for the ``publish`` command
    parser_publish = subparsers.add_parser('publish',
                                           help='Publish one or more articles')
    parser_publish.add_argument('-f', '--files',
                                help='Relative paths to the articles',
                                nargs='+',
                                default=[])
    parser_publish.add_argument('--sync',
                                help='Push the blog changes to the Github '
                                     'repository. This option is in effect only'
                                     ' if --prod option is passed.',
                                action='store_true')
    parser_publish.add_argument('--prod',
                                help='Publish to the production blog.',
                                action='store_true')
    parser_publish.set_defaults(func=publish)
    args = parser.parse_args()
    args.func(args)