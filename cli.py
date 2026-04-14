"""CLI entry point using cyclopts."""

from __future__ import annotations

import cyclopts

from src.hello.greeter import Greeter

app = cyclopts.App(
    name="py-cli",
    help="Simple Hello World CLI.",
)


@app.default
def hello(name: str = "World") -> None:
    """Greet someone with a hello message.

    Args:
        name: Name to greet. Defaults to "World".
    """
    greeter = Greeter(name)
    print(greeter.greet())


def main() -> None:
    app()


if __name__ == "__main__":
    main()
