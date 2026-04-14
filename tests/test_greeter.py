"""Tests for the Greeter class."""

from src.hello.greeter import Greeter


class TestGreeter:
    def test_default_greeting(self) -> None:
        greeter = Greeter()
        assert greeter.greet() == "Hello, World!"

    def test_custom_name(self) -> None:
        greeter = Greeter("Python")
        assert greeter.greet() == "Hello, Python!"

    def test_empty_name(self) -> None:
        greeter = Greeter("")
        assert greeter.greet() == "Hello, !"
