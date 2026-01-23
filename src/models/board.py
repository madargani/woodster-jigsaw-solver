"""GameBoard class for representing the puzzle board."""

from __future__ import annotations


class GameBoard:
    """Represents the rectangular grid area where pieces must be placed.

    Attributes:
        width: Number of columns in the board
        height: Number of rows in the board
        cells: 2D array (list of lists) where cells[row][col] = piece_id, None, or -1
        blocked_cells: Set of initially filled (blocked) cell positions
    """

    def __init__(
        self,
        width: int,
        height: int,
        blocked_cells: set[tuple[int, int]] | None = None,
    ) -> None:
        """Initialize a game board with specified dimensions.

        Args:
            width: Number of columns (1-50)
            height: Number of rows (1-50)
            blocked_cells: Set of initially filled (blocked) cell positions

        Raises:
            ValueError: If dimensions are out of valid range
            ValueError: If blocked_cells contain out-of-bounds positions
        """
        if not (1 <= width <= 50):
            raise ValueError("Width must be between 1 and 50")
        if not (1 <= height <= 50):
            raise ValueError("Height must be between 1 and 50")

        self._width = width
        self._height = height
        self._cells: list[list[int | None]] = [
            [None for _ in range(width)] for _ in range(height)
        ]

        # Validate and set blocked cells
        self._blocked_cells: set[tuple[int, int]] = set()
        if blocked_cells:
            for cell in blocked_cells:
                row, col = cell
                if not (0 <= row < height and 0 <= col < width):
                    raise ValueError(
                        f"Blocked cell {cell} is out of board bounds ({width}x{height})"
                    )
                self._blocked_cells.add(cell)
                # Mark blocked cells as occupied (use -1 as special marker)
                self._cells[row][col] = -1

    @property
    def width(self) -> int:
        """Get the board width."""
        return self._width

    @property
    def height(self) -> int:
        """Get the board height."""
        return self._height

    @property
    def total_area(self) -> int:
        """Get total number of cells."""
        return self._width * self._height

    @property
    def available_area(self) -> int:
        """Get number of cells available for piece placement (excluding blocked cells)."""
        return self._width * self._height - len(self._blocked_cells)

    @property
    def blocked_cells(self) -> set[tuple[int, int]]:
        """Get the set of blocked cell positions."""
        return self._blocked_cells.copy()

    @property
    def filled_area(self) -> int:
        """Get number of occupied cells."""
        return sum(1 for row in self._cells for cell in row if cell is not None)

    @property
    def empty_area(self) -> int:
        """Get number of empty cells."""
        return sum(1 for row in self._cells for cell in row if cell is None)

    def can_place_shape(
        self, shape: frozenset[tuple[int, int]], position: tuple[int, int]
    ) -> bool:
        """Check if a shape can be placed at the specified position.

        Args:
            shape: The shape cells as a frozenset of (row_offset, col_offset) tuples
            position: (row, col) position to place shape origin

        Returns:
            True if shape fits without overlapping, going out of bounds, or hitting blocked cells
        """
        for row_offset, col_offset in shape:
            row = position[0] + row_offset
            col = position[1] + col_offset

            # Check bounds
            if not (0 <= row < self._height and 0 <= col < self._width):
                return False

            # Check if cell is blocked (initially filled)
            if (row, col) in self._blocked_cells:
                return False

            # Check if cell is already occupied by a piece
            cell_content = self._cells[row][col]
            if cell_content is not None and cell_content != -1:
                return False

        return True

    def place_shape(
        self, shape: frozenset[tuple[int, int]], position: tuple[int, int]
    ) -> None:
        """Place a shape at the specified position.

        Args:
            shape: The shape cells as a frozenset of (row_offset, col_offset) tuples
            position: (row, col) position to place shape origin

        Raises:
            ValueError: If shape cannot be placed at position
        """
        if not self.can_place_shape(shape, position):
            raise ValueError(f"Cannot place shape at position {position}")

        shape_hash = hash(shape)
        for row_offset, col_offset in shape:
            row = position[0] + row_offset
            col = position[1] + col_offset
            self._cells[row][col] = shape_hash

    def remove_shape(
        self, shape: frozenset[tuple[int, int]], position: tuple[int, int]
    ) -> None:
        """Remove a shape from the board.

        Args:
            shape: The shape cells as a frozenset of (row_offset, col_offset) tuples
            position: (row, col) position where shape is placed

        Raises:
            ValueError: If shape is not found at position
        """
        shape_hash = hash(shape)
        for row_offset, col_offset in shape:
            row = position[0] + row_offset
            col = position[1] + col_offset
            if self._cells[row][col] != shape_hash:
                raise ValueError(f"Shape not found at position {position}")

        # Remove the shape
        for row_offset, col_offset in shape:
            row = position[0] + row_offset
            col = position[1] + col_offset
            self._cells[row][col] = None

    def get_occupied_cells(self) -> set[tuple[int, int]]:
        """Get set of all occupied cell positions.

        Returns:
            Set of (row, col) tuples with pieces placed
        """
        return {
            (row, col)
            for row in range(self._height)
            for col in range(self._width)
            if self._cells[row][col] is not None
        }

    def get_empty_cells(self) -> set[tuple[int, int]]:
        """Get set of all empty cell positions.

        Returns:
            Set of (row, col) tuples without pieces
        """
        return {
            (row, col)
            for row in range(self._height)
            for col in range(self._width)
            if self._cells[row][col] is None
        }

    def is_full(self) -> bool:
        """Check if board is completely filled.

        Returns:
            True if all cells are occupied
        """
        return all(
            self._cells[row][col] is not None
            for row in range(self._height)
            for col in range(self._width)
        )

    def is_empty(self) -> bool:
        """Check if the board is completely empty.

        Returns:
            True if no pieces are placed (blocked cells are ignored)
        """
        # Check if any non-blocked cells are occupied
        return all(cell is None or cell == -1 for row in self._cells for cell in row)

    def is_blocked(self, position: tuple[int, int]) -> bool:
        """Check if a cell is blocked (initially filled).

        Args:
            position: (row, col) position to query

        Returns:
            True if cell is blocked
        """
        return position in self._blocked_cells

    def get_blocked_cells(self) -> set[tuple[int, int]]:
        """Get set of all blocked cell positions.

        Returns:
            Set of (row, col) tuples that are blocked
        """
        return self._blocked_cells.copy()

    def get_piece_at(self, position: tuple[int, int]) -> int | None:
        """Get the piece ID at the specified position.

        Args:
            position: (row, col) position to query

        Returns:
            Piece ID (hash) if cell is occupied, None otherwise
        """
        row, col = position
        return self._cells[row][col]

    def clear(self) -> None:
        """Clear all pieces from the board."""
        for row in range(self._height):
            for col in range(self._width):
                if self._cells[row][col] != -1:
                    self._cells[row][col] = None

    def copy(self) -> GameBoard:
        """Create a deep copy of the board.

        Returns:
            New GameBoard with identical state (including blocked cells)
        """
        new_board = GameBoard(self._width, self._height, self._blocked_cells.copy())
        new_board._cells = [row[:] for row in self._cells]
        return new_board

    def __eq__(self, other: object) -> bool:
        """Check equality with another board."""
        if not isinstance(other, GameBoard):
            return NotImplemented
        return (
            self._width == other._width
            and self._height == other._height
            and all(
                self._cells[row][col] == other._cells[row][col]
                for row in range(self._height)
                for col in range(self._width)
            )
            and self._blocked_cells == other._blocked_cells
        )

    def __repr__(self) -> str:
        """Get string representation."""
        return f"GameBoard(width={self._width}, height={self._height})"
