
from kez.exceptions import *

from .data import *

def output(stream):
    return stream.getvalue().strip()

def test_invalid_command(ui):
    ui.run(["invalid"])
    assert output(ui.stdout) == ""
    assert output(ui.stderr) == "unknown command 'invalid'"

