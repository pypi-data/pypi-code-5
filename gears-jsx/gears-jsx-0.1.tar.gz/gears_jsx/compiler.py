import os

from gears.compilers import ExecCompiler


class JSXCompiler(ExecCompiler):
    result_mimetype = 'application/javascript'
    executable = 'node'
    params = [os.path.join(os.path.dirname(__file__), 'compiler.js')]
