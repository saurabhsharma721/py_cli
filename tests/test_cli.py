"""Tests for the CLI."""

import pytest

from cli import app


def test_default_hello(capsys) -> None:
    with pytest.raises(SystemExit, match="0"):
        app([], exit_on_error=False)
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello, World!"


def test_hello_with_name(capsys) -> None:
    with pytest.raises(SystemExit, match="0"):
        app(["--name", "Python"], exit_on_error=False)
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello, Python!"
