"""Backtracking solver for polyomino puzzles.

This module implements a generator-based solver that yields state snapshots
for real-time visualization. Uses QTimer-driven consumption pattern for
clean separation from GUI code.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from src.models.board import GameBoard
from src.models.piece import PuzzlePiece


def solve_backtracking(
    pieces: dict[PuzzlePiece, int],
    board: GameBoard,
) -> Generator[dict[str, Any], None, None]:
    """Generator function that solves polyomino puzzles using backtracking.

    Yields state dictionaries for visualization at each step of the algorithm.
    The generator pattern allows for stepped execution via QTimer without
    thread synchronization complexity.

    Args:
        pieces: Dictionary mapping unique puzzle pieces to their counts
                (e.g., {L_tromino: 3, I_tromino: 2})
        board: The game board to solve

    Yields:
        Dictionary containing:
        - type: 'place' | 'remove' | 'solved' | 'no_solution'
        - board_snapshot: Direct reference to current board state (READ-ONLY)
        - placed_pieces: Direct reference to list of (shape, position) tuples (READ-ONLY)
        - remaining_pieces: Direct reference to dict of piece -> count (READ-ONLY)
        - step_count: Number of operations performed

    Important:
        The yielded objects are direct references to internal solver state.
        Consumers MUST treat them as read-only and must not modify them.
        The generator yields control to the caller, and expects to resume
        with unchanged state when next() is called.
    """
    # Single mutable state
    step_count = 0
    remaining: dict[PuzzlePiece, int] = pieces.copy()
    placed: list[tuple[frozenset[tuple[int, int]], tuple[int, int], PuzzlePiece]] = []

    # Get all unique piece types sorted by area (largest first)
    piece_types = sorted(remaining.keys(), key=lambda p: p.area, reverse=True)

    # Check if already solved (no pieces to place)
    if not remaining:
        yield {
            "type": "solved",
            "board_snapshot": board,
            "placed_pieces": placed,
            "remaining_pieces": remaining,
            "step_count": step_count,
        }
        return

    def find_next_empty() -> tuple[int, int] | None:
        """Find first empty cell in L→R, T→B order."""
        for row in range(board.height):
            for col in range(board.width):
                if board.get_piece_at((row, col)) is None:
                    return (row, col)
        return None

    def backtrack() -> Generator[dict[str, Any], None, bool]:
        """Recursive backtracking generator.

        Yields state dictionaries and returns True if solution found.
        """
        nonlocal step_count

        # Find next empty cell
        cell = find_next_empty()
        if cell is None:
            # Board is full - check if solved
            if not remaining:
                step_count += 1
                yield {
                    "type": "solved",
                    "board_snapshot": board,
                    "placed_pieces": placed,
                    "remaining_pieces": remaining,
                    "step_count": step_count,
                }
                return True
            # No empty cells but pieces remain
            return False

        # Try each piece type
        for piece in piece_types:
            count = remaining.get(piece, 0)
            if count <= 0:
                continue

            # Try each orientation
            for orientation in piece.orientations:
                top_left_cell = min(orientation, key=lambda c: (c[0], c[1]))
                origin = (cell[0] - top_left_cell[0], cell[1] - top_left_cell[1])

                if board.can_place_shape(orientation, origin):
                    board.place_shape(orientation, origin)
                    placed.append((orientation, origin, piece))
                    remaining[piece] = count - 1
                    if remaining[piece] == 0:
                        del remaining[piece]

                    step_count += 1
                    yield {
                        "type": "place",
                        "board_snapshot": board,
                        "placed_pieces": placed,
                        "remaining_pieces": remaining,
                        "step_count": step_count,
                    }

                    # Recurse
                    if (yield from backtrack()):
                        return True

                    # Backtrack
                    shape, pos, p = placed.pop()
                    board.remove_shape(shape, pos)
                    remaining[p] = remaining.get(p, 0) + 1
                    step_count += 1
                    yield {
                        "type": "remove",
                        "board_snapshot": board,
                        "placed_pieces": placed,
                        "remaining_pieces": remaining,
                        "step_count": step_count,
                    }

        # No piece fits at this cell
        return False

    # Start backtracking
    if not (yield from backtrack()):
        # No solution found
        yield {
            "type": "no_solution",
            "board_snapshot": board,
            "placed_pieces": placed,
            "remaining_pieces": remaining,
            "step_count": step_count,
        }
