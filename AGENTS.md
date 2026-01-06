# Agent Guide for woodster-jigsaw-solver

This guide provides essential information for AI agents working on this codebase.

## Project Overview

Python 3.13+ project for solving the Aztec Labrynth puzzle using computer vision. Uses a backtracking algorithm to find solutions from piece images.

## Project Structure

```
src/woodster_jigsaw_solver/
├── __main__.py           # CLI entry point (accessible via `solve` command)
├── models/
│   └── puzzle_piece.py   # Core PuzzlePiece dataclass
├── solver/               # Solver logic (WIP)
├── vision/               # Image processing (WIP)
└── visualization/        # Visualization utilities (WIP)
tests/                    # pytest test suite
pyproject.toml            # Project config & dependencies
uv.lock                   # Locked dependencies (managed by uv)
```

## Commands

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_puzzle_piece.py

# Run specific test class
pytest tests/test_puzzle_piece.py::TestPuzzlePieceEquality

# Run specific test method
pytest tests/test_puzzle_piece.py::TestPuzzlePieceEquality::test_same_piece_is_equal

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=woodster_jigsaw_solver
```

### Running the Application
```bash
# Via CLI command
solve --board <board_image> --puzzle <pieces_image>

# Via Python module
python -m woodster_jigsaw_solver --board <board_image> --puzzle <pieces_image>
```

### Dependencies
```bash
# Install/Update dependencies (uses uv)
uv sync

# Add new dependency
uv add <package_name>
```

## Code Style Guidelines

### Type Hints
- **Always** use type hints for function parameters and return types
- Import from `typing` module: `from typing import FrozenSet, Iterable, List, Tuple`
- Use complex nested types where appropriate (e.g., `FrozenSet[FrozenSet[Tuple[int, int]]]`)
- Add type annotations for local variables in complex logic for clarity

### Naming Conventions
- **Functions/Methods**: `snake_case` (e.g., `_generate_transformations`, `_rotate`)
- **Classes**: `PascalCase` (e.g., `PuzzlePiece`, `TestPuzzlePieceEquality`)
- **Private methods**: Prefix with single underscore (e.g., `_flip`, `_normalize`)
- **Constants**: `UPPER_SNAKE_CASE` (if needed)

### Data Structures
- Use `@dataclass(frozen=True)` for immutable data models
- Prefer `FrozenSet` over `Set` for immutable collections
- Use `frozenset` and `tuple` for hashable structures
- Use `object.__setattr__(self, "attr", value)` to set attributes in frozen dataclasses during `__init__`

### Import Organization
```python
# 1. Standard library imports
from dataclasses import dataclass

# 2. Third-party imports
import pytest

# 3. Local imports
from woodster_jigsaw_solver.models.puzzle_piece import PuzzlePiece
```

Separate groups with blank lines.

### Formatting
- **Indentation**: 4 spaces (no tabs)
- **Line length**: Keep under 100 characters
- **Blank lines**: One blank line between functions, two between classes
- No trailing whitespace

### Error Handling
- Minimal explicit error handling in main codebase
- Rely on type hints and built-in validation (e.g., `list(coordinates)` will raise if not iterable)
- Use `pytest.raises` in tests to verify exception behavior

### Testing Conventions
- Use pytest framework
- Group related tests in classes (e.g., `TestPuzzlePieceEquality`)
- Test names should be descriptive: `test_<what>_<expected_result>`
- Use descriptive assertions: `assert p1 == p2` (not `assert result`)
- Test classes should be named `Test<ClassName>`

### Code Patterns
- Use list comprehensions and generator expressions for transformations
- Normalize coordinates by subtracting min_x/min_y and sorting
- Handle empty input gracefully (e.g., `if not coords: return ()`)
- Create frozen dataclasses for objects that need to be hashable/set members

## Existing Patterns to Follow

The `PuzzlePiece` class in `models/puzzle_piece.py` demonstrates the project's conventions:
- Frozen dataclass with transformation logic
- Private helper methods (`_generate_transformations`, `_rotate`, `_flip`, `_normalize`)
- Type hints throughout
- Immutable data structures (frozenset, tuple)
- No explicit error handling, relies on type system

## Linting/Formatting Tools

No explicit linting config found. The project uses `.ruff_cache/` suggesting ruff may be used but no `.ruff.toml` or config in `pyproject.toml` is present. Follow PEP 8 conventions.

## Notes

- Project is in early development (many empty module `__init__.py` files)
- No docstrings currently in the codebase (this may change)
- Uses `uv` for dependency management (lockfile present in git)
- Python 3.13+ is required
