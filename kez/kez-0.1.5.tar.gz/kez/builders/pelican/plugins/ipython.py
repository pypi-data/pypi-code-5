
import os
import re
from os.path import exists as pathexists, join as pathjoin
import hashlib

from docutils import nodes
from docutils.parsers.rst import directives, Directive
from docutils.parsers.rst.directives.body import MathBlock
from docutils.utils import relative_path
from pelican import log, signals
from django.conf import settings as django_settings

MEDIA_ROOT = django_settings.MEDIA_ROOT
MEDIA_URL = django_settings.MEDIA_URL

from bigmouth.tools.nbconvert import ipynb2html

src_attribute_pattern = re.compile(r'\ssrc="(.+?)"[\s>]')

class IPythonNotebookDirective(Directive):
    """Convert a ipython notebook to html"""
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = False

    def _get_source_path(self):
        # Taken from `docutils.parsers.rst.directives.misc.Include`
        source = self.state_machine.input_lines.source(
            self.lineno - self.state_machine.input_offset - 1)
        source_dir = os.path.dirname(os.path.abspath(source))
        path = directives.path(self.arguments[0])
        path = os.path.normpath(os.path.join(source_dir, path))
        path = relative_path(None, path)
        return nodes.reprunicode(path)

    def run(self):
        infile = self._get_source_path()
        self.state.document.settings.record_dependencies.add(infile)
        html = ipynb2html(infile)
        source_root = os.path.dirname(infile)
        def on_match(m):
            url = m.group(1)
            if url:
                src = pathjoin(source_root, url.lstrip('/'))
                if pathexists(src):
                    _, ext = os.path.splitext(src)
                    hash = hashlib.md5(src).hexdigest()
                    relpath = pathjoin(os.path.basename(source_root), hash) + ext
                    dst = pathjoin(MEDIA_ROOT, relpath)
                    if not pathexists(os.path.dirname(dst)):
                        os.makedirs(os.path.dirname(dst))
                    shutil.copyfile(src, dst)
                    url = pathjoin(MEDIA_URL, relpath)
            return url
        html = src_attribute_pattern.sub(on_match, html)
        node = nodes.raw('', html, format='html')
        return [node]

class PanelMathBlock(MathBlock):

    def run(self):
        node = nodes.container('')
        return 

def ensure_latex(gen, metadata):
    if 'latex' in metadata and metadata['latex'].lower() != "no":
        metadata['latex'] = True
    else:
        metadata['latex'] = False

def register():
    directives.register_directive('ipynb', IPythonNotebookDirective)
    signals.article_generator_context.connect(ensure_latex)

