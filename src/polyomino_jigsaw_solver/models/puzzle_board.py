from dataclasses import dataclass, field
from typing import List, Set, Tuple


class PiecePlacementError(Exception):
    """Raised when a piece cannot be placed on the board."""


class PieceRemovalError(Exception):
    """Raised when a piece cannot be removed from the board."""


@dataclass
class PuzzleBoard:
    """A board for polyomino puzzle pieces.

    The board tracks filled cells using (x, y) coordinates where:
    - x = column (horizontal position)
    - y = row (vertical position)
    - (0, 0) is the top-left corner
    """

    width: int
    height: int
    filled_cells: Set[Tuple[int, int]] = field(default_factory=set)
    placed_pieces: List[Tuple[List[Tuple[int, int]], int, int]] = field(
        default_factory=list
    )

    def check_piece(
        self, transformation: List[Tuple[int, int]], row: int, col: int
    ) -> bool:
        """Check if a piece fits at the specified position.

        The piece is positioned so that the leftmost cell of the first row
        (minimum row, then minimum column in that row) is at the given
        row and column.

        For example, if the piece is shaped like:
          x
          xxx
        The x at row 0 column 1 (leftmost cell of the first row) should be
        positioned at the input row and column.

        Args:
            transformation: The piece transformation as a list of (x, y) coordinates
            row: The row (y-coordinate) where the leftmost cell of the first row should be placed
            col: The column (x-coordinate) where the leftmost cell of the first row should be placed

        Returns:
            True if the piece fits within bounds and doesn't overlap filled cells,
            False otherwise.
        """
        if not transformation:
            return False

        min_y = min(y for _, y in transformation)
        min_x = min(x for x, y in transformation if y == min_y)

        x_offset = col - min_x
        y_offset = row - min_y

        # Check each cell of the piece
        for x, y in transformation:
            # Calculate the actual board position
            board_x = x + x_offset
            board_y = y + y_offset

            # Check bounds
            if not (0 <= board_x < self.width and 0 <= board_y < self.height):
                return False

            # Check overlap with filled cells
            if (board_x, board_y) in self.filled_cells:
                return False

        return True

    def insert_piece(
        self, transformation: List[Tuple[int, int]], row: int, col: int
    ) -> None:
        """Insert a piece at the specified position.

        Raises PiecePlacementError if the piece doesn't fit within bounds
        or overlaps with existing filled cells.

        Args:
            transformation: The piece transformation as a list of (x, y) coordinates
            row: The row (y-coordinate) where the leftmost cell of the first row should be placed
            col: The column (x-coordinate) where the leftmost cell of the first row should be placed

        Raises:
            PiecePlacementError: If the piece doesn't fit or overlaps
        """
        if not transformation:
            raise PiecePlacementError("Transformation cannot be empty")

        if not self.check_piece(transformation, row, col):
            raise PiecePlacementError("Piece does not fit at the specified position")

        min_y = min(y for _, y in transformation)
        min_x = min(x for x, y in transformation if y == min_y)

        x_offset = col - min_x
        y_offset = row - min_y

        for x, y in transformation:
            board_x = x + x_offset
            board_y = y + y_offset
            self.filled_cells.add((board_x, board_y))

        self.placed_pieces.append((transformation, row, col))

    def remove_piece(
        self, transformation: List[Tuple[int, int]], row: int, col: int
    ) -> None:
        """Remove a piece from specified position.

        Raises PieceRemovalError if any cell of piece is not in filled_cells.

        Args:
            transformation: The piece transformation as a list of (x, y) coordinates
            row: The row (y-coordinate) where the leftmost cell of the first row is positioned
            col: The column (x-coordinate) where the leftmost cell of the first row is positioned

        Raises:
            PieceRemovalError: If any cell is not in filled_cells
        """
        if not transformation:
            raise PieceRemovalError("Transformation cannot be empty")

        min_y = min(y for _, y in transformation)
        min_x = min(x for x, y in transformation if y == min_y)

        x_offset = col - min_x
        y_offset = row - min_y

        piece_cells = []
        for x, y in transformation:
            board_x = x + x_offset
            board_y = y + y_offset
            piece_cells.append((board_x, board_y))

        missing_cells = [cell for cell in piece_cells if cell not in self.filled_cells]
        if missing_cells:
            raise PieceRemovalError(
                f"Cannot remove piece - cells not filled: {missing_cells}"
            )

        for cell in piece_cells:
            self.filled_cells.discard(cell)

        self.placed_pieces.remove((transformation, row, col))

    def is_cell_empty(self, row: int, col: int) -> bool:
        """Check if a cell is empty.

        Args:
            row: The row (y-coordinate) of the cell
            col: The column (x-coordinate) of the cell

        Returns:
            True if the cell is empty, False if filled

        Raises:
            ValueError: If the position is out of bounds
        """
        if not (0 <= row < self.height and 0 <= col < self.width):
            raise ValueError("Position out of bounds")
        return (col, row) not in self.filled_cells
