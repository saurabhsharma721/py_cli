"""Main application entry point."""

from src.hello.greeter import Greeter


def main() -> None:
    greeter = Greeter()
    print(greeter.greet())


if __name__ == "__main__":
    main()
