"""PuzzleConfiguration class for managing puzzle configurations."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.logic.validator import validate_piece_shape
from src.models.board import GameBoard
from src.models.piece import PuzzlePiece


class PuzzleConfiguration:
    """Represents a complete puzzle definition.

    Attributes:
        name: User-defined puzzle name
        board_width: Board width in cells
        board_height: Board height in cells
        blocked_cells: Initially filled (blocked) cell positions
        pieces: Dictionary of piece to count
        created_at: Timestamp when configuration was created
        modified_at: Timestamp of last modification
    """

    def __init__(
        self,
        name: str,
        board_width: int,
        board_height: int,
        pieces: dict[PuzzlePiece, int] | None = None,
        blocked_cells: set[tuple[int, int]] | None = None,
    ) -> None:
        """Initialize a puzzle configuration.

        Args:
            name: User-defined puzzle name
            board_width: Board width in cells (1-50)
            board_height: Board height in cells (1-50)
            pieces: Dictionary mapping piece to count (how many of that piece)
            blocked_cells: Set of initially filled (blocked) cell positions

        Raises:
            ValueError: If constraints are violated
        """
        if not name or not name.strip():
            raise ValueError("Puzzle name cannot be empty")
        if not (1 <= board_width <= 50):
            raise ValueError("Board width must be between 1 and 50")
        if not (1 <= board_height <= 50):
            raise ValueError("Board height must be between 1 and 50")

        # Validate blocked cells are within bounds
        if blocked_cells:
            for cell in blocked_cells:
                row, col = cell
                if not (0 <= row < board_height and 0 <= col < board_width):
                    raise ValueError(
                        f"Blocked cell {cell} is out of board bounds "
                        f"({board_width}x{board_height})"
                    )

        self._name = name.strip()
        self._board_width = board_width
        self._board_height = board_height
        self._blocked_cells = blocked_cells.copy() if blocked_cells else set()
        self._pieces = pieces.copy() if pieces else {}
        self._created_at = datetime.utcnow()
        self._modified_at = datetime.utcnow()

    @property
    def name(self) -> str:
        """Get the puzzle name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the puzzle name."""
        if not value or not value.strip():
            raise ValueError("Puzzle name cannot be empty")
        self._name = value.strip()
        self._modified_at = datetime.utcnow()

    @property
    def board_width(self) -> int:
        """Get the board width."""
        return self._board_width

    @property
    def board_height(self) -> int:
        """Get the board height."""
        return self._board_height

    @property
    def blocked_cells(self) -> set[tuple[int, int]]:
        """Get the set of blocked cell positions."""
        return self._blocked_cells.copy()

    @property
    def pieces(self) -> dict[PuzzlePiece, int]:
        """Get the dictionary of pieces with counts."""
        return self._pieces.copy()

    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at

    @property
    def modified_at(self) -> datetime:
        """Get last modification timestamp."""
        return self._modified_at

    @property
    def available_area(self) -> int:
        """Get number of cells available for piece placement (excluding blocked cells)."""
        return self._board_width * self._board_height - len(self._blocked_cells)

    @property
    def is_empty(self) -> bool:
        """Check if configuration has no pieces."""
        return len(self._pieces) == 0

    def get_available_area(self) -> int:
        """Get number of cells available for piece placement (excluding blocked cells)."""
        return self._board_width * self._board_height - len(self._blocked_cells)

    def get_total_piece_area(self) -> int:
        """Get total area of all pieces accounting for counts.

        Returns:
            Sum of all piece areas multiplied by their counts
        """
        total = 0
        for piece, count in self._pieces.items():
            total += piece.area * count
        return total

    def get_all_pieces(self) -> list[PuzzlePiece]:
        """Get list of all pieces (expanding counts).

        Returns:
            List of pieces with each piece repeated according to its count
        """
        all_pieces = []
        for piece, count in self._pieces.items():
            all_pieces.extend([piece] * count)
        return all_pieces

    def get_piece_counts(self) -> dict[str, int]:
        """Get mapping of piece shape representations to their counts.

        Returns:
            Dictionary of piece shape string -> count
        """
        return {
            str(piece.canonical_shape): count for piece, count in self._pieces.items()
        }

    def update_piece(self, piece: PuzzlePiece, count: int = 1) -> None:
        """Update an existing piece in the configuration.

        Args:
            piece: Updated PuzzlePiece with same shape
            count: Number of copies of this piece

        Raises:
            ValueError: If piece not found or shape is invalid
        """
        # Validate new shape
        shape_errors = validate_piece_shape(set(piece.canonical_shape))
        if shape_errors:
            raise ValueError(f"Piece: {shape_errors[0].message}")

        if piece not in self._pieces:
            raise ValueError("Piece not found")

        self._pieces[piece] = count
        self._modified_at = datetime.utcnow()

    def clear_pieces(self) -> None:
        """Remove all pieces from the configuration."""
        self._pieces.clear()
        self._modified_at = datetime.utcnow()

    def validate(self) -> list[str]:
        """Validate the configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors: list[str] = []

        # Check piece counts are positive
        for piece, count in self._pieces.items():
            if count <= 0:
                errors.append(f"Piece has invalid count {count}")

        # Check piece contiguity using centralized validator
        for piece in self._pieces:
            shape_errors = validate_piece_shape(set(piece.canonical_shape))
            for error in shape_errors:
                errors.append(f"Piece: {error.message}")

        # Check total piece area vs available board area
        piece_area = self.get_total_piece_area()
        board_area = self.get_board_area()

        if piece_area > board_area:
            errors.append(
                f"Total piece area ({piece_area}) exceeds board area ({board_area})"
            )
        elif piece_area != self.available_area:
            errors.append(
                f"Total piece area ({piece_area}) does not equal available board area "
                f"({self.available_area}) - blocked cells: {len(self._blocked_cells)}"
            )

        return errors

    def add_piece(self, piece: PuzzlePiece, count: int = 1) -> None:
        """Add a piece to the configuration.

        Args:
            piece: Puzzle piece to add
            count: Number of copies to add (default: 1)

        Raises:
            ValueError: If piece is invalid
        """
        # Use centralized validation
        shape_errors = validate_piece_shape(set(piece.canonical_shape))
        if shape_errors:
            raise ValueError(f"Piece: {shape_errors[0].message}")

        # Check for duplicate shape
        if piece in self._pieces:
            self._pieces[piece] += count
        else:
            self._pieces[piece] = count

        self._modified_at = datetime.utcnow()

    def remove_piece(self, piece: PuzzlePiece, count: int = 1) -> None:
        """Remove a piece from the configuration.

        Args:
            piece: Piece to remove
            count: Number of copies to remove (default: 1)

        Raises:
            ValueError: If piece not found or count exceeds available
        """
        if piece not in self._pieces:
            raise ValueError("Piece not found")

        if self._pieces[piece] < count:
            raise ValueError(
                f"Cannot remove {count} of this piece, only {self._pieces[piece]} available"
            )

        self._pieces[piece] -= count
        if self._pieces[piece] == 0:
            del self._pieces[piece]

        self._modified_at = datetime.utcnow()

    def get_board(self) -> GameBoard:
        """Create a GameBoard from configuration.

        Returns:
            New GameBoard instance with blocked_cells configured
        """
        return GameBoard(
            self._board_width,
            self._board_height,
            self._blocked_cells.copy(),
        )

    def get_piece_area(self) -> int:
        """Get total area of all pieces accounting for counts.

        Returns:
            Sum of all piece areas multiplied by their counts
        """
        return self.get_total_piece_area()

    def get_board_area(self) -> int:
        """Get total board area.

        Returns:
            board_width × board_height
        """
        return self._board_width * self._board_height

    def is_solvable_area(self) -> bool:
        """Check if piece area matches available board area.

        Returns:
            True if total piece area equals available board area (total_area - blocked_cells)
        """
        return self.get_total_piece_area() == self.available_area

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary for serialization.

        Returns:
            Dictionary representation including blocked_cells and piece counts
        """
        return {
            "name": self._name,
            "board_width": self._board_width,
            "board_height": self._board_height,
            "blocked_cells": [[row, col] for row, col in self._blocked_cells],
            "pieces": [
                {"shape": list(piece.canonical_shape), "count": count}
                for piece, count in self._pieces.items()
            ],
            "created_at": self._created_at.isoformat(),
            "modified_at": self._modified_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PuzzleConfiguration:
        """Create configuration from dictionary.

        Args:
            data: Dictionary representation including piece counts

        Returns:
            New PuzzleConfiguration instance

        Raises:
            ValueError: If data is invalid
        """
        required_fields = ["name", "board_width", "board_height", "pieces"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Handle blocked_cells (handle missing field for backward compatibility)
        blocked_cells: set[tuple[int, int]] = set()
        if "blocked_cells" in data:
            blocked_cells = set((row, col) for row, col in data["blocked_cells"])

        config = cls(
            name=data["name"],
            board_width=data["board_width"],
            board_height=data["board_height"],
            pieces=None,
            blocked_cells=blocked_cells,
        )

        for piece_data in data["pieces"]:
            if "shape" not in piece_data:
                raise ValueError("Invalid piece data: missing shape")

            shape = set((row, col) for row, col in piece_data["shape"])
            piece = PuzzlePiece(shape=shape)
            count = piece_data.get(
                "count", 1
            )  # Default to 1 for backward compatibility
            config.add_piece(piece, count)

        # Handle timestamps if present
        if "created_at" in data:
            try:
                config._created_at = datetime.fromisoformat(data["created_at"])
            except (ValueError, TypeError):
                pass

        if "modified_at" in data:
            try:
                config._modified_at = datetime.fromisoformat(data["modified_at"])
            except (ValueError, TypeError):
                pass

        return config

    def copy(self) -> PuzzleConfiguration:
        """Create a deep copy of the configuration.

        Returns:
            New PuzzleConfiguration with identical state (including blocked cells)
        """
        pieces_copy = {
            PuzzlePiece(shape=set(p.canonical_shape)): count
            for p, count in self._pieces.items()
        }
        new_config = PuzzleConfiguration(
            name=self._name,
            board_width=self._board_width,
            board_height=self._board_height,
            pieces=pieces_copy,
            blocked_cells=self._blocked_cells.copy(),
        )
        # Preserve timestamps
        new_config._created_at = self._created_at
        new_config._modified_at = self._modified_at
        return new_config

    def __eq__(self, other: object) -> bool:
        """Check equality with another configuration."""
        if not isinstance(other, PuzzleConfiguration):
            return NotImplemented
        return (
            self._name == other._name
            and self._board_width == other._board_width
            and self._board_height == other._board_height
            and self._blocked_cells == other._blocked_cells
            and len(self._pieces) == len(other._pieces)
            and all(
                p1.canonical_shape == p2.canonical_shape and c1 == c2
                for (p1, c1), (p2, c2) in zip(
                    sorted(
                        self._pieces.items(), key=lambda x: str(x[0].canonical_shape)
                    ),
                    sorted(
                        other._pieces.items(), key=lambda x: str(x[0].canonical_shape)
                    ),
                )
            )
        )

    def __repr__(self) -> str:
        """Get string representation."""
        return (
            f"PuzzleConfiguration(name='{self._name}', "
            f"board={self._board_width}x{self._board_height}, "
            f"pieces={len(self._pieces)})"
        )
