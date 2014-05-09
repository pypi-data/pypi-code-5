# -*- coding: utf-8 -*-

"""
    fatafat.blog
    ~~~~~~~~~~~~

    This module implements the various types of fatafat powered blogs.

    :copyright: (c) 2014 by Subhajit Ghosh.
    :license: Apache2, see LICENSE for more details.
"""

from fatafat.util import create_parent_dir, makedir, rel_paths
from jinja2 import Environment, FileSystemLoader
from markdown import Markdown
from os.path import join

import datetime
import fatafat
import os
import pickle
import sh


class Article(object):
    """Represents an article in a blog."""

    # The list of attributes which must be present in an article header.
    REQ_METADATA = ['title', 'date']

    def __init__(self, content, metadata, rel_path):
        # Check if all required metadata are present
        for attr in self.REQ_METADATA:
            if attr not in metadata:
                raise Exception('Missing metadata: {0}'.format(attr))

        self.title = metadata['title'][0]
        self.summary = metadata['summary'][0] if 'summary' in metadata else ''

        try:
            self.date = datetime.datetime.strptime(metadata['date'][0],
                                                   '%d-%m-%Y')
        except ValueError:
            raise ValueError('Article date must be in format: DD-MM-YYYY')

        self.status = metadata['status'][0] if 'status' in metadata \
            else 'published'
        self.content = content
        self.url = 'articles/{0}.html'.format(os.path.splitext(rel_path)[0])

    @staticmethod
    def from_markdown(path, rel_path):
        """Returns an ``Article`` by reading the markdown file at ``path``.

        :param path: Absolute path to the markdown file.
        :param rel_path: Relative path to the markdown file prefixed by
            ``contents``.
        """
        with open(path) as f:
            content = f.read()

        md = Markdown(extensions=['meta'])
        content = md.convert(content)

        if not hasattr(md, 'Meta'):
            raise Exception('Missing article metadata')

        metadata = {k.lower(): v for k, v in md.Meta.iteritems()}
        return Article(content, metadata, rel_path)


class Blog(object):
    """Implements a fatafat powered blog."""

    def __init__(self, config, path):
        # Output directory locations which stores the static output
        self.site_dir = join(path, 'site')
        self.site_articles_dir = join(self.site_dir, 'articles')

        # Contents directory location which stores the blog articles. This
        # location is common for both the prod and dev blog.
        self.contents_dir = join(os.getcwd(), 'contents')

        # Data directory location which stores the blog data files
        self.data_dir = join(path, 'data')

        # Theme directory locations
        self.theme = config.THEME
        self.themes_dir = join(path, 'themes')
        self.theme_dir = join(self.themes_dir, self.theme)

        # Jinja2 templates environment
        self.template_env = Environment(
            loader=FileSystemLoader(join(self.theme_dir, 'templates')))

        # Template variables which are available across all templates
        self.global_template_vars = {
            'SITENAME': config.SITE_NAME,
            'SITEURL': config.SITE_URL,
            'DISQUS_SITENAME': config.DISQUS_SITENAME
        }

    def setup(self):
        """Creates the skeleton for the blog."""
        self._create_blog_layout()

        # Create the blank readme file
        sh.touch(join(self.site_dir, 'README.md'))

        # Copy the theme files
        sh.cp('-r', join(fatafat.THEMES_DIR, self.theme), self.themes_dir)
        sh.cp('-r', os.path.join(self.theme_dir, 'assets'), self.site_dir)

        # Create the index file
        with open(os.path.join(self.data_dir, 'index.db'), 'wb') as f:
            pickle.dump({}, f)

    def publish(self, paths):
        """Publishes one or more articles."""
        # If paths is empty, grab all the articles in the contents directory.
        if not paths:
            paths = rel_paths(self.contents_dir)

        articles = {}
        for path in paths:
            article = Article.from_markdown(
                os.path.join(self.contents_dir, path), path)

            # Ignore drafts
            if article.status == 'draft':
                continue

            self.write_article(article)
            articles[article.url] = article

        self.write_index(articles)

    def write_article(self, article):
        """Writes the HTML file for the article."""
        output_path = join(self.site_dir, article.url)
        create_parent_dir(output_path)

        template = self.template_env.get_template('article.jinja2')
        with open(output_path, 'w') as f:
            f.write(template.render(article=article,
                                    **self.global_template_vars))

    def write_index(self, articles):
        """Writes the index.html file and creates the blog index."""
        # TODO (isubuz)
        # For now ignore the input list of articles and (re)generate the index
        # by reading all the article. This will change when a mechanism to
        # identify and removing stale articles from the index is devised.
        articles_index = {}
        for path in rel_paths(self.contents_dir):
            article = Article.from_markdown(
                os.path.join(self.contents_dir, path), path)
            # Ignore drafts
            if article.status == 'draft':
                continue
            articles_index[article.url] = article

        db_path = join(self.data_dir, 'index.db')

        # TODO (isubuz):
        # Uncomment when above issue is addressed.
        # Load and update the current index
        # with open(db_path, 'rb') as f:
        #     articles_index = pickle.load(f)
        # for url in articles:
        #     articles_index[url] = articles[url]

        # Sort all articles by date
        all_articles = articles_index.values()
        all_articles.sort(key=lambda item: item.date, reverse=True)

        # Generate index.html
        template = self.template_env.get_template('index.jinja2')
        with open(join(self.site_dir, 'index.html'), 'w') as f:
            f.write(template.render(articles=all_articles,
                                    **self.global_template_vars))

        # Save the current index to file
        with open(db_path, 'wb') as f:
            pickle.dump(articles_index, f)

    def _create_blog_layout(self):
        """Creates the directory structure for the blog."""

        # Layout for ``site`` directory
        makedir(self.site_dir)
        makedir(self.site_articles_dir)

        # Layout for ``contents`` directory
        makedir(self.contents_dir)

        # Layout for ``themes`` directory
        makedir(self.themes_dir)

        # Layout for ``data`` directory
        makedir(self.data_dir)


class DevBlog(Blog):
    """Implements a local fatafat blog for development."""

    def __init__(self, config):
        super(DevBlog, self).__init__(config, 'dev')


class GithubBlog(Blog):
    """Implements a fatafat blog hosted in Github."""

    def __init__(self, config):
        super(GithubBlog, self).__init__(config, 'prod')

        self.git = sh.git.bake(_cwd=self.site_dir)
        self.git_repo_url = 'git@github.com:{0}/{0}.github.io.git'.format(
            config.GITHUB_USERNAME)

    def setup(self):
        super(GithubBlog, self).setup()

        # Initialize and make the first commit
        self.git.init()
        self.git.add('*')
        self.git.remote('add', 'origin', self.git_repo_url)
        self.git.commit(m='First commit to the create a fatafat powered blog')

    def publish(self, paths):
        super(GithubBlog, self).publish(paths)

        self.git.add('*')
        if not paths:
            message = 'Regenerated blog.'
        else:
            message = 'Published articles: {0}'.format(', '.join(paths))

        # Include exit code 1 to ignore 'nothing to commit' error.
        self.git.commit(m=message, _ok_code=[0, 1])

    def sync(self):
        """Pushes the local blog changes to the Github repository."""
        self.git.push('-u', 'origin', 'master')