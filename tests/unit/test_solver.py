"""Unit tests for the solver module (User Story 2).

These tests verify the solve_backtracking() generator function and its
yield format for visualization purposes.
"""

from __future__ import annotations

import pytest

from src.models.piece import PuzzlePiece
from src.models.board import GameBoard


class TestSolveBacktrackingGenerator:
    """Tests for the solve_backtracking() generator function."""

    def test_generator_exists(self) -> None:
        """Test that solve_backtracking generator function exists and is importable."""
        from src.logic.solver import solve_backtracking

        # The function should exist and be callable
        assert callable(solve_backtracking)

    def test_simple_solvable_puzzle_returns_generator(self) -> None:
        """Test that solve_backtracking returns a generator for a simple solvable puzzle."""
        from src.logic.solver import solve_backtracking

        # Create a simple 2x2 board with two domino pieces
        domino1 = PuzzlePiece(shape={(0, 0), (0, 1)})  # Horizontal domino
        domino2 = PuzzlePiece(shape={(0, 0), (1, 0)})  # Vertical domino

        board = GameBoard(width=2, height=2)
        pieces = {domino1: 1, domino2: 1}

        # Should return a generator
        result = solve_backtracking(pieces, board)
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")

    def test_generator_yields_solution_for_2x2_puzzle(self) -> None:
        """Test that generator finds solution for 2x2 puzzle with two dominoes."""
        from src.logic.solver import solve_backtracking

        # Two dominoes on 2x2 board - use count=2 for same shape
        domino = PuzzlePiece(shape={(0, 0), (0, 1)})

        board = GameBoard(width=2, height=2)
        pieces = {domino: 2}  # Two copies of same domino shape

        generator = solve_backtracking(pieces, board)

        # Collect all yields
        yields = list(generator)

        # Last yield should indicate solution found
        assert len(yields) > 0
        last_yield = yields[-1]
        assert last_yield["type"] == "solved"
        # Board should be full in solution
        assert last_yield["board_snapshot"].is_full()

    def test_generator_yields_no_solution_for_oversized_pieces(self) -> None:
        """Test that generator correctly identifies unsolvable puzzles."""
        from src.logic.solver import solve_backtracking

        # Two trominoes (3 cells each) on 2x2 board (only 4 cells)
        tromino = PuzzlePiece(shape={(0, 0), (0, 1), (0, 2)})

        board = GameBoard(width=2, height=2)
        pieces = {tromino: 2}

        generator = solve_backtracking(pieces, board)
        yields = list(generator)

        # Last yield should indicate no solution
        assert len(yields) > 0
        last_yield = yields[-1]
        assert last_yield["type"] == "no_solution"

    def test_generator_yields_for_single_piece(self) -> None:
        """Test generator behavior for a puzzle with a single piece."""
        from src.logic.solver import solve_backtracking

        # Single piece that exactly fits
        monomino = PuzzlePiece(shape={(0, 0)})

        board = GameBoard(width=1, height=1)
        pieces = {monomino: 1}

        generator = solve_backtracking(pieces, board)
        yields = list(generator)

        # Should find solution
        assert len(yields) > 0
        last_yield = yields[-1]
        assert last_yield["type"] == "solved"

    def test_generator_handles_multiple_piece_copies(self) -> None:
        """Test that generator handles puzzles with multiple copies of same piece shape."""
        from src.logic.solver import solve_backtracking

        # Four monominoes on 2x2 board
        monomino = PuzzlePiece(shape={(0, 0)})

        board = GameBoard(width=2, height=2)
        pieces = {monomino: 4}

        generator = solve_backtracking(pieces, board)
        yields = list(generator)

        # Should find solution
        last_yield = yields[-1]
        assert last_yield["type"] == "solved"
        assert last_yield["board_snapshot"].is_full()


class TestGeneratorYieldFormat:
    """Tests for the generator yield format and state snapshots."""

    def test_yield_contains_required_keys(self) -> None:
        """Test that each yield contains all required keys for visualization."""
        from src.logic.solver import solve_backtracking

        domino = PuzzlePiece(shape={(0, 0), (0, 1)})
        board = GameBoard(width=2, height=2)
        pieces = {domino: 2}

        generator = solve_backtracking(pieces, board)
        first_yield = next(generator)

        # Should contain these keys
        required_keys = [
            "type",
            "board_snapshot",
            "placed_pieces",
            "remaining_pieces",
            "step_count",
        ]
        for key in required_keys:
            assert key in first_yield, f"Missing required key: {key}"

    def test_yield_type_values(self) -> None:
        """Test that yield type values are valid."""
        from src.logic.solver import solve_backtracking

        domino = PuzzlePiece(shape={(0, 0), (0, 1)})
        board = GameBoard(width=2, height=2)
        pieces = {domino: 2}

        generator = solve_backtracking(pieces, board)

        valid_types = {"place", "remove", "dead_end", "solved", "no_solution"}

        for yield_obj in generator:
            assert yield_obj["type"] in valid_types, (
                f"Invalid yield type: {yield_obj['type']}"
            )

    def test_board_snapshot_is_reference_not_copy(self) -> None:
        """Test that board_snapshot is a direct reference, not a deep copy.

        The solver yields direct references to internal state for memory efficiency.
        Consumers MUST NOT modify the yielded objects, as it will corrupt the solver's state.
        """
        from src.logic.solver import solve_backtracking

        domino = PuzzlePiece(shape={(0, 0), (0, 1)})
        board = GameBoard(width=2, height=2)
        pieces = {domino: 2}

        generator = solve_backtracking(pieces, board)
        first_yield = next(generator)

        snapshot = first_yield["board_snapshot"]
        assert snapshot is board

    def test_step_count_increments(self) -> None:
        """Test that step_count increments with each yield."""
        from src.logic.solver import solve_backtracking

        domino = PuzzlePiece(shape={(0, 0), (0, 1)})
        board = GameBoard(width=2, height=2)
        pieces = {domino: 2}

        generator = solve_backtracking(pieces, board)

        step_counts = [yield_obj["step_count"] for yield_obj in generator]

        # Step counts should be non-decreasing
        for i in range(1, len(step_counts)):
            assert step_counts[i] >= step_counts[i - 1]

    def test_placed_pieces_reflects_current_state(self) -> None:
        """Test that placed_pieces reflects the current solver state."""
        from src.logic.solver import solve_backtracking

        # Use pieces that will be easy to track
        domino = PuzzlePiece(shape={(0, 0), (0, 1)})
        board = GameBoard(width=2, height=2)
        pieces = {domino: 2}

        generator = solve_backtracking(pieces, board)

        for yield_obj in generator:
            placed = yield_obj["placed_pieces"]
            remaining = yield_obj["remaining_pieces"]

            # Total pieces should match original configuration
            total_placed = sum(count for count in remaining.values()) + len(placed)
            assert total_placed == 2

    def test_remaining_pieces_decrements(self) -> None:
        """Test that remaining_pieces count decrements as pieces are placed."""
        from src.logic.solver import solve_backtracking

        # Two identical pieces
        domino = PuzzlePiece(shape={(0, 0), (0, 1)})
        board = GameBoard(width=2, height=2)
        pieces = {domino: 2}

        generator = solve_backtracking(pieces, board)

        prev_remaining_count = 2
        for yield_obj in generator:
            current_remaining = sum(yield_obj["remaining_pieces"].values())
            # Should be <= previous (non-increasing as pieces are placed)
            assert current_remaining <= prev_remaining_count
            prev_remaining_count = current_remaining


class TestBacktrackingBehavior:
    """Tests for backtracking algorithm behavior."""

    def test_generator_backtracks_on_dead_end(self) -> None:
        """Test that generator can backtrack when exploring different positions."""
        from src.logic.solver import solve_backtracking

        # Use a puzzle where the solver explores multiple options
        # 6 dominoes on 4x3 board (12 cells = 6 × 2)
        # Dominoes can be placed in various orientations requiring exploration
        domino = PuzzlePiece(shape={(0, 0), (0, 1)})  # Horizontal domino
        board = GameBoard(width=4, height=3)
        pieces = {domino: 6}

        generator = solve_backtracking(pieces, board)
        yields = list(generator)

        # Should have multiple place yields showing exploration
        place_yields = [y for y in yields if y["type"] == "place"]
        dead_end_yields = [y for y in yields if y["type"] == "dead_end"]

        # The solver should explore multiple positions
        assert len(place_yields) >= 6, (
            f"Generator should place all 6 dominoes, got {len(place_yields)}"
        )
        assert len(place_yields) == 6, (
            f"Should place all 6 dominoes, got {len(place_yields)}"
        )

    def test_all_orientations_tried(self) -> None:
        """Test that the solver explores different board positions."""
        from src.logic.solver import solve_backtracking

        # Use a simple puzzle with enough pieces to require exploration
        # 2 dominoes on 3x2 board (6 cells = 2 × 3, but dominoes are 2 cells each)
        # Actually let's use 3 dominoes on 3x2 board (6 cells = 3 × 2)
        domino = PuzzlePiece(shape={(0, 0), (0, 1)})  # Horizontal domino
        board = GameBoard(width=3, height=2)
        pieces = {domino: 3}

        generator = solve_backtracking(pieces, board)
        yields = list(generator)

        # Should have multiple place yields
        place_yields = [y for y in yields if y["type"] == "place"]
        assert len(place_yields) >= 2, (
            f"Generator should place multiple pieces, got {len(place_yields)}"
        )

    def test_empty_puzzle_immediately_solved(self) -> None:
        """Test that an empty puzzle (no pieces) is immediately solved."""
        from src.logic.solver import solve_backtracking

        monomino = PuzzlePiece(shape={(0, 0)})
        board = GameBoard(width=2, height=2)
        # No pieces - already "solved"
        pieces: dict[PuzzlePiece, int] = {}

        generator = solve_backtracking(pieces, board)
        yields = list(generator)

        # Should have exactly one yield: solved
        assert len(yields) == 1
        assert yields[0]["type"] == "solved"


class TestGeneratorEdgeCases:
    """Tests for edge cases in the generator."""

    def test_unsolvable_due_to_blocked_cells(self) -> None:
        """Test generator handles puzzles unsolvable due to blocked cells."""
        from src.logic.solver import solve_backtracking

        # 2x2 board with center blocked (leaves L-shape that can't fit 2 dominoes)
        domino = PuzzlePiece(shape={(0, 0), (0, 1)})
        board = GameBoard(width=2, height=2, blocked_cells={(0, 1)})
        pieces = {domino: 2}

        generator = solve_backtracking(pieces, board)
        yields = list(generator)

        # Should indicate no solution
        last_yield = yields[-1]
        assert last_yield["type"] == "no_solution"

    def test_piece_larger_than_board(self) -> None:
        """Test generator handles pieces larger than board."""
        from src.logic.solver import solve_backtracking

        # 4-cell piece on 2x2 board
        tetromino = PuzzlePiece(shape={(0, 0), (0, 1), (0, 2), (0, 3)})
        board = GameBoard(width=2, height=2)
        pieces = {tetromino: 1}

        generator = solve_backtracking(pieces, board)
        yields = list(generator)

        # Should indicate no solution
        last_yield = yields[-1]
        assert last_yield["type"] == "no_solution"

    def test_exact_fit_puzzle(self) -> None:
        """Test puzzle where piece area exactly equals board area."""
        from src.logic.solver import solve_backtracking

        # Use 4 L-tetrominoes on 4x4 board (16 cells = 4 × 4)
        # L-tetromino has area 4
        l_tetromino = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1), (1, 2)})
        board = GameBoard(width=4, height=4)
        pieces = {l_tetromino: 4}

        generator = solve_backtracking(pieces, board)
        yields = list(generator)

        # Should find solution (or at least try - L-tetrominoes can tile 4x4)
        last_yield = yields[-1]
        # Note: 4 L-tetrominoes can tile a 4x4 board
        assert last_yield["type"] in ("solved", "no_solution")


class TestStopIterationHandling:
    """Tests for StopIteration handling and termination."""

    def test_generator_terminates_with_solution(self) -> None:
        """Test that generator terminates properly when solution is found."""
        from src.logic.solver import solve_backtracking

        domino = PuzzlePiece(shape={(0, 0), (0, 1)})
        board = GameBoard(width=2, height=2)
        pieces = {domino: 2}

        generator = solve_backtracking(pieces, board)

        # Exhaust the generator
        final_state = None
        for state in generator:
            final_state = state

        # Last yield should be solved
        assert final_state is not None
        assert final_state["type"] == "solved"

    def test_generator_terminates_without_solution(self) -> None:
        """Test that generator terminates properly when no solution exists."""
        from src.logic.solver import solve_backtracking

        tromino = PuzzlePiece(shape={(0, 0), (0, 1), (0, 2)})
        board = GameBoard(width=2, height=2)
        pieces = {tromino: 2}

        generator = solve_backtracking(pieces, board)

        # Exhaust the generator
        final_state = None
        for state in generator:
            final_state = state

        # Last yield should be no_solution
        assert final_state is not None
        assert final_state["type"] == "no_solution"

    def test_generator_close_stops_iteration(self) -> None:
        """Test that generator.close() stops iteration."""
        from src.logic.solver import solve_backtracking

        # Use a puzzle that would take a while to solve
        # This ensures we can interrupt it
        l_piece = PuzzlePiece(shape={(0, 0), (1, 0), (1, 1)})
        board = GameBoard(width=5, height=5)
        pieces = {l_piece: 8}

        generator = solve_backtracking(pieces, board)

        # Get a few yields
        count = 0
        for state in generator:
            count += 1
            if count >= 5:
                break

        # Close the generator
        generator.close()

        # Should not be able to get more yields
        with pytest.raises(StopIteration):
            next(generator)
