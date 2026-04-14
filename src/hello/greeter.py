"""Hello World module."""


class Greeter:
    """Simple greeter that returns hello world messages."""

    def __init__(self, name: str = "World") -> None:
        self.name = name

    def greet(self) -> str:
        return f"Hello, {self.name}!"
