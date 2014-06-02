from tengs_cli import cli
import sys

def test_parse_args(monkeypatch):
    monkeypatch.setattr("sys.exit", lambda x: x)
    parser = cli.parse_args(['-h', '--verbose'])
    assert parser.verbose
