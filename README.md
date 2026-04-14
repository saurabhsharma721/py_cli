# py-cli

Simple Hello World CLI built with [cyclopts](https://github.com/BrianPugh/cyclopts).

## Setup

```bash
# Install dependencies (using uv)
uv sync

# Or with pip
pip install -e ".[dev]"
```

## Usage

### CLI

```bash
# Default greeting
uv run py-cli
# Output: Hello, World!

# Custom name
uv run py-cli --name Python
# Output: Hello, Python!

# Help
uv run py-cli --help
```

### As a Python module

```bash
python app.py
# Output: Hello, World!
```

## Run Tests

```bash
uv run pytest tests/ -v
```

## Project Structure

```
py_cli/
├── app.py              # Main application entry point
├── cli.py              # CLI entry point (cyclopts)
├── src/hello/          # Hello world package
│   ├── __init__.py
│   └── greeter.py      # Greeter class
├── tests/
│   ├── test_greeter.py # Greeter unit tests
│   └── test_cli.py     # CLI tests
├── pyproject.toml
└── README.md
```
