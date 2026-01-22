"""Piece tab component for the puzzle editor.

This module contains the PieceTab class which provides the UI for creating
and editing polyomino pieces through a grid-based drawing interface.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QPen, QResizeEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from src.models.piece import PuzzlePiece


class PieceGridWidget(QWidget):
    """Grid widget for drawing and editing piece shapes.

    This widget provides a grid-based drawing interface where users can
    create polyomino pieces by clicking and dragging to add cells.

    Attributes:
        grid_width: Width of the drawing grid
        grid_height: Height of the drawing grid
        filled_cells: Set of filled cell positions (row, col)
    """

    # Constants
    MIN_CELL_SIZE = 15
    MAX_CELL_SIZE = 50
    DEFAULT_CELL_SIZE = 30
    FILL_COLOR = QColor(0, 123, 255)  # Blue for filled cells
    GRID_COLOR = QColor(180, 180, 180)  # Medium gray for grid lines

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the piece grid widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self._grid_width = 10
        self._grid_height = 10
        self._filled_cells: set[tuple[int, int]] = set()
        self._cell_size = self.DEFAULT_CELL_SIZE
        self._is_filling = True  # True = add cells, False = remove cells

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

    @property
    def grid_width(self) -> int:
        """Get the grid width."""
        return self._grid_width

    @grid_width.setter
    def grid_width(self, value: int) -> None:
        """Set the grid width.

        Args:
            value: New width (1-50)
        """
        self._grid_width = max(1, min(50, value))
        self._trim_filled_cells()
        self.updateGeometry()
        self.update()

    @property
    def grid_height(self) -> int:
        """Get the grid height."""
        return self._grid_height

    @grid_height.setter
    def grid_height(self, value: int) -> None:
        """Set the grid height.

        Args:
            value: New height (1-50)
        """
        self._grid_height = max(1, min(50, value))
        self._trim_filled_cells()
        self.updateGeometry()
        self.update()

    @property
    def filled_cells(self) -> set[tuple[int, int]]:
        """Get the set of filled cell positions."""
        return self._filled_cells.copy()

    @filled_cells.setter
    def filled_cells(self, cells: set[tuple[int, int]]) -> None:
        """Set the filled cells and update display.

        Args:
            cells: Set of (row, col) positions to mark as filled
        """
        self._filled_cells = cells.copy()
        self._trim_filled_cells()
        self.update()

    def _trim_filled_cells(self) -> None:
        """Remove filled cells that are outside the grid bounds."""
        self._filled_cells = {
            (r, c)
            for r, c in self._filled_cells
            if 0 <= r < self._grid_height and 0 <= c < self._grid_width
        }

    def set_dimensions(self, width: int, height: int) -> None:
        """Set grid dimensions.

        Args:
            width: New width (1-50)
            height: New height (1-50)
        """
        self._grid_width = max(1, min(50, width))
        self._grid_height = max(1, min(50, height))
        self._trim_filled_cells()
        self._calculate_cell_size()
        self.updateGeometry()
        self.update()

    def clear(self) -> None:
        """Clear all filled cells."""
        self._filled_cells.clear()
        self.update()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handle widget resize to auto-fit cell size."""
        self._calculate_cell_size()
        super().resizeEvent(event)

    def _calculate_cell_size(self) -> None:
        """Calculate optimal cell size based on available space."""
        # Extra padding for labels (20px on each side)
        padding = 25
        available_width = self.width() - padding * 2
        available_height = self.height() - padding * 2

        if self._grid_width > 0 and self._grid_height > 0:
            cell_width = available_width // self._grid_width
            cell_height = available_height // self._grid_height
            self._cell_size = max(
                self.MIN_CELL_SIZE, min(cell_width, cell_height, self.MAX_CELL_SIZE)
            )

    def sizeHint(self) -> QSize:
        """Return the preferred size hint."""
        width = self._grid_width * self._cell_size + 10
        height = self._grid_height * self._cell_size + 10
        return QSize(width, height)

    def minimumSizeHint(self) -> QSize:
        """Return the minimum size hint."""
        width = self._grid_width * self.MIN_CELL_SIZE + 10
        height = self._grid_height * self.MIN_CELL_SIZE + 10
        return QSize(width, height)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the grid."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Extra padding for labels
        label_padding = 25
        grid_width = self._grid_width * self._cell_size
        grid_height = self._grid_height * self._cell_size
        offset_x = (self.width() - grid_width) // 2
        offset_y = (self.height() - grid_height) // 2

        # Ensure labels have enough space
        offset_x = max(offset_x, label_padding)
        offset_y = max(offset_y, label_padding)

        # Draw cells
        for row in range(self._grid_height):
            for col in range(self._grid_width):
                x = offset_x + col * self._cell_size
                y = offset_y + row * self._cell_size

                # Determine cell color
                if (row, col) in self._filled_cells:
                    color = self.FILL_COLOR
                else:
                    color = QColor(255, 255, 255)

                painter.fillRect(x, y, self._cell_size, self._cell_size, color)

                # Draw grid lines
                pen = QPen(self.GRID_COLOR)
                pen.setWidth(1)
                painter.setPen(pen)
                painter.drawRect(x, y, self._cell_size, self._cell_size)

        # Draw row/column labels if cells are large enough
        if self._cell_size >= 20:
            font = painter.font()
            font.setPointSize(max(7, min(10, self._cell_size // 3)))
            painter.setFont(font)
            painter.setPen(QColor(100, 100, 100))

            # Column labels (top)
            for col in range(self._grid_width):
                x = offset_x + col * self._cell_size + self._cell_size // 2
                y = offset_y - 8
                label = str(col)
                metrics = painter.fontMetrics()
                text_width = metrics.horizontalAdvance(label)
                painter.drawText(int(x - text_width // 2), int(y), label)

            # Row labels (left)
            for row in range(self._grid_height):
                x = offset_x - 8
                y = offset_y + row * self._cell_size + self._cell_size // 2
                label = str(row)
                metrics = painter.fontMetrics()
                text_height = metrics.height()
                painter.drawText(
                    int(x - metrics.horizontalAdvance(label)),
                    int(y + text_height // 3),
                    label,
                )

    def _get_cell_at_position(self, pos_x: int, pos_y: int) -> tuple[int, int] | None:
        """Get the cell coordinates at the given position.

        Args:
            pos_x: X coordinate in widget space
            pos_y: Y coordinate in widget space

        Returns:
            (row, col) tuple or None if position is outside the grid
        """
        grid_width = self._grid_width * self._cell_size
        grid_height = self._grid_height * self._cell_size
        offset_x = (self.width() - grid_width) // 2
        offset_y = (self.height() - grid_height) // 2

        # Check if position is within grid bounds
        if pos_x < offset_x or pos_x >= offset_x + grid_width:
            return None
        if pos_y < offset_y or pos_y >= offset_y + grid_height:
            return None

        col = (pos_x - offset_x) // self._cell_size
        row = (pos_y - offset_y) // self._cell_size

        if 0 <= row < self._grid_height and 0 <= col < self._grid_width:
            return (row, col)
        return None

    def mousePressEvent(self, event) -> None:
        """Handle mouse press for toggling cells."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_filling = True
            self._toggle_cell_at_position(event.pos())
        elif event.button() == Qt.MouseButton.RightButton:
            self._is_filling = False
            self._toggle_cell_at_position(event.pos())

    def mouseMoveEvent(self, event) -> None:
        """Handle mouse drag for painting cells."""
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._is_filling = True
            self._toggle_cell_at_position(event.pos())
        elif event.buttons() & Qt.MouseButton.RightButton:
            self._is_filling = False
            self._toggle_cell_at_position(event.pos())

    def _toggle_cell_at_position(self, pos) -> None:
        """Toggle cell state at the given position.

        Args:
            pos: QPoint position
        """
        cell = self._get_cell_at_position(pos.x(), pos.y())
        if cell is not None:
            if self._is_filling:
                self._filled_cells.add(cell)
            else:
                self._filled_cells.discard(cell)
            self.update()


class PieceListItemWidget(QWidget):
    """Custom widget for piece list items with count controls.

    Displays piece dimensions and cell count with +/- buttons for
    adjusting the quantity of each piece type.
    """

    # Signals emitted when count buttons are clicked
    increment_requested = Signal(PuzzlePiece)
    decrement_requested = Signal(PuzzlePiece)

    def __init__(
        self, piece: PuzzlePiece, count: int, parent: QWidget | None = None
    ) -> None:
        """Initialize the piece list item widget.

        Args:
            piece: The puzzle piece this item represents
            count: Current count of this piece type
            parent: Parent widget
        """
        super().__init__(parent)
        self._piece = piece
        self._count = count
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the widget layout and components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Label: "(3×4) (7 cells)"
        self._label = QLabel(self._get_label_text())
        self._label.setMinimumWidth(100)
        self._label.setStyleSheet("font-weight: bold;")

        # Minus button
        self._minus_btn = QToolButton()
        self._minus_btn.setText("-")
        self._minus_btn.setFixedSize(28, 28)
        self._minus_btn.setToolTip("Remove one")
        self._minus_btn.clicked.connect(self._on_minus_clicked)

        # Count label: "x3"
        self._count_label = QLabel(self._get_count_text())
        self._count_label.setFixedWidth(30)
        self._count_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        # Plus button
        self._plus_btn = QToolButton()
        self._plus_btn.setText("+")
        self._plus_btn.setFixedSize(28, 28)
        self._plus_btn.setToolTip("Add one")
        self._plus_btn.clicked.connect(self._on_plus_clicked)

        layout.addWidget(self._label)
        layout.addWidget(self._minus_btn)
        layout.addWidget(self._count_label)
        layout.addWidget(self._plus_btn)
        layout.addStretch()

    def _get_label_text(self) -> str:
        """Generate label like '(3×4) (7 cells)'."""
        return f"({self._piece.width}×{self._piece.height}) ({len(self._piece.canonical_shape)} cells)"

    def _get_count_text(self) -> str:
        """Generate count text like 'x3'."""
        return f"x{self._count}"

    def _on_plus_clicked(self) -> None:
        """Handle plus button click."""
        self.increment_requested.emit(self._piece)

    def _on_minus_clicked(self) -> None:
        """Handle minus button click."""
        self.decrement_requested.emit(self._piece)

    def update_count(self, count: int) -> None:
        """Update the displayed count.

        Args:
            count: New count value
        """
        self._count = count
        self._count_label.setText(self._get_count_text())


class PieceTab(QWidget):
    """Tab widget for piece creation and editing.

    This tab provides a piece list for managing multiple pieces and a grid
    editor for drawing piece shapes.

    Signals:
        piece_selected: Emitted when a piece is selected from the list
        piece_added: Emitted when a new piece is added
        piece_deleted: Emitted when a piece is deleted
        piece_modified: Emitted when a piece shape is modified
    """

    # Signals
    piece_selected = Signal(PuzzlePiece)
    piece_added = Signal(PuzzlePiece)
    piece_deleted = Signal(PuzzlePiece)
    piece_modified = Signal(PuzzlePiece)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        on_piece_selected: Callable[[PuzzlePiece | None], None] | None = None,
        on_piece_added: Callable[[PuzzlePiece], None] | None = None,
        on_piece_deleted: Callable[[PuzzlePiece], None] | None = None,
        on_piece_modified: Callable[[PuzzlePiece], None] | None = None,
    ) -> None:
        """Initialize the piece tab.

        Args:
            parent: Parent widget
            on_piece_selected: Callback when a piece is selected (or None if deselected)
            on_piece_added: Callback when a new piece is added
            on_piece_deleted: Callback when a piece is deleted
            on_piece_modified: Callback when a piece shape is modified
        """
        super().__init__(parent)

        self._pieces: dict[PuzzlePiece, int] = {}
        self._selected_piece: PuzzlePiece | None = None
        self._piece_counter = 0  # Only for generating unique labels

        self._piece_selected_callback = on_piece_selected
        self._piece_added_callback = on_piece_added
        self._piece_deleted_callback = on_piece_deleted
        self._piece_modified_callback = on_piece_modified

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        # Main layout with pieces list on left and editor on right
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Left side: Piece list
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        pieces_label = QLabel("Pieces:")
        pieces_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        left_panel.addWidget(pieces_label)

        # Piece list widget
        self._piece_list = QListWidget()
        self._piece_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._piece_list.setFixedWidth(200)
        self._piece_list.setUniformItemSizes(True)
        self._piece_list.setStyleSheet("QListWidget::item { min-height: 40px; }")
        self._piece_list.itemSelectionChanged.connect(self._on_piece_selection_changed)
        self._piece_list.itemClicked.connect(self._on_piece_item_clicked)
        left_panel.addWidget(self._piece_list)

        # Piece count label
        self._piece_count_label = QLabel("Pieces: 0")
        left_panel.addWidget(self._piece_count_label)

        # Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(5)

        self._add_button = QPushButton("Add Piece")
        self._add_button.clicked.connect(self._on_add_piece)
        button_layout.addWidget(self._add_button)

        self._delete_button = QPushButton("Delete Piece")
        self._delete_button.clicked.connect(self._on_delete_piece)
        button_layout.addWidget(self._delete_button)

        self._clear_button = QPushButton("Clear Shape")
        self._clear_button.clicked.connect(self._on_clear_shape)
        button_layout.addWidget(self._clear_button)

        left_panel.addLayout(button_layout)

        # Add spacer
        left_panel.addStretch()

        main_layout.addLayout(left_panel)

        # Right side: Grid editor
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)

        # Instructions
        instructions = QLabel(
            "Click and drag to draw piece shape.\nRight-click to erase cells."
        )
        instructions.setStyleSheet("color: #666; font-style: italic;")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(instructions)

        # Grid dimensions controls
        grid_size_layout = QHBoxLayout()
        grid_size_layout.setSpacing(10)

        width_label = QLabel("Grid Width:")
        self._width_spinner = QSpinBox()
        self._width_spinner.setRange(1, 20)
        self._width_spinner.setValue(10)
        self._width_spinner.setFixedWidth(80)
        self._width_spinner.valueChanged.connect(self._on_grid_size_changed)

        height_label = QLabel("Height:")
        self._height_spinner = QSpinBox()
        self._height_spinner.setRange(1, 20)
        self._height_spinner.setValue(10)
        self._height_spinner.setFixedWidth(80)
        self._height_spinner.valueChanged.connect(self._on_grid_size_changed)

        grid_size_layout.addWidget(width_label)
        grid_size_layout.addWidget(self._width_spinner)
        grid_size_layout.addWidget(height_label)
        grid_size_layout.addWidget(self._height_spinner)
        grid_size_layout.addStretch()

        right_panel.addLayout(grid_size_layout)

        # Piece grid
        self._grid_widget = PieceGridWidget()
        right_panel.addWidget(self._grid_widget)

        # Shape info
        self._shape_info_label = QLabel("Cells: 0")
        self._shape_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(self._shape_info_label)

        # Set row stretch for the grid area to expand
        right_panel.setStretch(2, 1)

        main_layout.addLayout(right_panel)

        # Set stretch ratio
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 3)

    def _on_piece_selection_changed(self) -> None:
        """Handle piece selection changes."""
        selected_items = self._piece_list.selectedItems()
        if selected_items:
            index = self._piece_list.row(selected_items[0])
            # Sort pieces the same way as _refresh_piece_list
            sorted_pieces = sorted(
                self._pieces.keys(),
                key=lambda p: len(p.canonical_shape),
            )
            if 0 <= index < len(sorted_pieces):
                self._selected_piece = sorted_pieces[index]
                # Load the piece shape into the grid
                shape = self._selected_piece.canonical_shape
                self._grid_widget.filled_cells = set(shape)
                self._update_shape_info()
        else:
            self._selected_piece = None
            self._grid_widget.clear()
            self._update_shape_info()

        self.piece_selected.emit(self._selected_piece)
        if self._piece_selected_callback:
            self._piece_selected_callback(self._selected_piece)

    def _on_piece_item_clicked(self, item: QListWidgetItem) -> None:
        """Handle clicking on a piece list item.

        This ensures selection is properly handled when clicking on
        the custom widget area.
        """
        # Just trigger the selection changed handler to ensure consistency
        self._on_piece_selection_changed()

    def _on_add_piece(self) -> None:
        """Handle adding a new piece."""
        # Create new piece from current grid
        shape = self._grid_widget.filled_cells
        if not shape:
            # Create empty piece - user will draw it
            shape = {(0, 0)}

        new_piece = PuzzlePiece(shape=shape)

        # Check if this shape already exists (uses canonical shape comparison)
        if new_piece in self._pieces:
            # Increment count for existing piece
            self._pieces[new_piece] += 1
        else:
            # Add new piece with count 1
            self._pieces[new_piece] = 1

        # Refresh list with custom widgets
        self._refresh_piece_list()
        self._select_piece_in_list(new_piece)
        self._piece_count_label.setText(f"Pieces: {len(self._get_all_pieces())}")
        self.piece_added.emit(new_piece)
        if self._piece_added_callback:
            self._piece_added_callback(new_piece)

    def _get_piece_label(self, piece: PuzzlePiece) -> str:
        """Generate a descriptive label for a piece.

        Args:
            piece: The piece to label

        Returns:
            A descriptive label showing shape info and count
        """
        cell_count = len(piece.canonical_shape)
        count = self._pieces.get(piece, 1)

        # Try to identify the shape type
        shape_type = self._identify_shape_type(piece)

        if count > 1:
            return f"{shape_type} ({cell_count} cells) ×{count}"
        return f"{shape_type} ({cell_count} cells)"

    def _identify_shape_type(self, piece: PuzzlePiece) -> str:
        """Identify the type of polyomino shape.

        Args:
            piece: The piece to identify

        Returns:
            A string describing the shape type
        """
        shape = piece.canonical_shape
        area = len(shape)

        # Get bounding box dimensions
        min_row = min(r for r, c in shape)
        max_row = max(r for r, c in shape)
        min_col = min(c for r, c in shape)
        max_col = max(c for r, c in shape)
        width = max_col - min_col + 1
        height = max_row - min_row + 1

        # Special shape patterns
        if area == 1:
            return "Mono"
        elif area == 2:
            return "Domino"
        elif area == 3:
            # L-shape or straight
            if width == 1 or height == 1:
                return "Triomino (straight)"
            else:
                return "Triomino (L)"
        elif area == 4:
            # Check for common tetromino types
            # Straight (I)
            if width == 4 or height == 4:
                return "Tetromino (I)"
            # Square (O)
            elif width == 2 and height == 2:
                return "Tetromino (O)"
            # L-shape
            elif (width == 3 and height == 2) or (width == 2 and height == 3):
                return "Tetromino (L)"
            # T-shape
            elif width == 3 and height == 2:
                # Check if it's a T
                return "Tetromino (T)"
            # S or Z shape
            elif width == 3 and height == 2:
                return "Tetromino (S)"
            else:
                return "Tetromino"
        else:
            # For larger pieces, use dimensions
            if width == 1 or height == 1:
                return f"Bar ({area})"
            elif width == height:
                return f"Square ({area})"
            else:
                return f"Polyomino ({width}×{height})"

    def _get_piece_index(self, piece: PuzzlePiece) -> int:
        """Get the index of a piece in the internal list.

        Args:
            piece: The piece to find

        Returns:
            The index in the sorted pieces list, or -1 if not found
        """
        sorted_pieces = sorted(
            self._pieces.keys(),
            key=lambda p: len(p.canonical_shape),
        )
        try:
            return sorted_pieces.index(piece)
        except ValueError:
            return -1

    def _get_all_pieces(self) -> list[PuzzlePiece]:
        """Get a flat list of all pieces with counts expanded.

        Returns:
            List of pieces with each piece repeated according to its count
        """
        all_pieces = []
        for piece, count in self._pieces.items():
            all_pieces.extend([piece] * count)
        return all_pieces

    def _refresh_piece_list(self) -> None:
        """Refresh all list items with custom widgets showing counts.

        Pieces are automatically sorted by number of cells (ascending).
        """
        self._piece_list.clear()

        # Sort pieces by number of cells (ascending order)
        sorted_pieces = sorted(
            self._pieces.items(),
            key=lambda item: len(item[0].canonical_shape),
        )

        for piece, count in sorted_pieces:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, piece)

            widget = PieceListItemWidget(piece, count)
            widget.increment_requested.connect(self._on_piece_increment)
            widget.decrement_requested.connect(self._on_piece_decrement)

            self._piece_list.addItem(item)
            self._piece_list.setItemWidget(item, widget)

    def _on_piece_increment(self, piece: PuzzlePiece) -> None:
        """Handle increment button click for a piece."""
        if piece in self._pieces:
            self._pieces[piece] += 1
            self._refresh_piece_list()
            # Re-select the piece
            self._select_piece_in_list(piece)
            self._piece_count_label.setText(f"Pieces: {len(self._get_all_pieces())}")

    def _on_piece_decrement(self, piece: PuzzlePiece) -> None:
        """Handle decrement button click for a piece."""
        if piece not in self._pieces:
            return

        if self._pieces[piece] > 1:
            self._pieces[piece] -= 1
            self._refresh_piece_list()
            # Re-select the piece
            self._select_piece_in_list(piece)
        else:
            # Remove entirely when count reaches 0
            del self._pieces[piece]
            self._selected_piece = None
            self._grid_widget.clear()
            self._refresh_piece_list()

        self._piece_count_label.setText(f"Pieces: {len(self._get_all_pieces())}")

    def _select_piece_in_list(self, piece: PuzzlePiece) -> None:
        """Select a piece in the list widget."""
        sorted_pieces = sorted(
            self._pieces.keys(),
            key=lambda p: len(p.canonical_shape),
        )
        try:
            index = sorted_pieces.index(piece)
            self._piece_list.setCurrentRow(index)
        except ValueError:
            pass

    def _on_delete_piece(self) -> None:
        """Handle deleting the selected piece."""
        if self._selected_piece is None:
            return

        piece_to_delete = self._selected_piece

        # Decrement count or remove if only 1
        if piece_to_delete in self._pieces:
            if self._pieces[piece_to_delete] > 1:
                self._pieces[piece_to_delete] -= 1
            else:
                # Remove entirely
                del self._pieces[piece_to_delete]

        # Clear selection and grid
        self._selected_piece = None
        self._grid_widget.clear()

        # Refresh list and update count
        self._refresh_piece_list()
        self._piece_count_label.setText(f"Pieces: {len(self._get_all_pieces())}")

        self.piece_deleted.emit(piece_to_delete)
        if self._piece_deleted_callback:
            self._piece_deleted_callback(piece_to_delete)

    def _on_clear_shape(self) -> None:
        """Handle clearing the current shape."""
        self._grid_widget.clear()
        self._update_shape_info()

        # Update selected piece if any - just clear its cells
        if self._selected_piece:
            # Update the shape in place (since PuzzlePiece is immutable, we need to replace)
            # Get current count
            count = self._pieces.get(self._selected_piece, 1)
            # Create new piece with empty shape (will be validated elsewhere)
            new_piece = PuzzlePiece(shape={(0, 0)})
            # Replace in dict - remove old, add new
            del self._pieces[self._selected_piece]
            self._pieces[new_piece] = count
            self._selected_piece = new_piece
            self._refresh_piece_list()
            self.piece_modified.emit(new_piece)
            if self._piece_modified_callback:
                self._piece_modified_callback(new_piece)

    def _on_grid_size_changed(self) -> None:
        """Handle grid size changes."""
        width = self._width_spinner.value()
        height = self._height_spinner.value()
        self._grid_widget.set_dimensions(width, height)

    def _update_shape_info(self) -> None:
        """Update the shape information label."""
        cell_count = len(self._grid_widget.filled_cells)
        self._shape_info_label.setText(f"Cells: {cell_count}")

    @property
    def pieces(self) -> list[PuzzlePiece]:
        """Get the list of all pieces with counts expanded."""
        return self._get_all_pieces()

    @property
    def selected_piece(self) -> PuzzlePiece | None:
        """Get the currently selected piece."""
        return self._selected_piece

    def get_current_shape(self) -> set[tuple[int, int]]:
        """Get the current shape from the grid.

        Returns:
            Set of (row, col) coordinates representing the current shape
        """
        return self._grid_widget.filled_cells

    def save_current_shape_to_piece(self) -> None:
        """Save the current grid shape to the selected piece."""
        if self._selected_piece is not None:
            shape = self._grid_widget.filled_cells
            # Get current count
            count = self._pieces.get(self._selected_piece, 1)
            new_piece = PuzzlePiece(shape=shape)
            # Replace in dict
            del self._pieces[self._selected_piece]
            self._pieces[new_piece] = count
            self._selected_piece = new_piece
            self._refresh_piece_list()
            self.piece_modified.emit(new_piece)
            if self._piece_modified_callback:
                self._piece_modified_callback(new_piece)

    def add_piece(self, piece: PuzzlePiece) -> None:
        """Add a piece to the list.

        Args:
            piece: The piece to add
        """
        # Check if this shape already exists
        if piece in self._pieces:
            self._pieces[piece] += 1
        else:
            self._pieces[piece] = 1

        # Add to list with shape info
        piece_label = self._get_piece_label(piece)
        item = QListWidgetItem(piece_label)
        item.setData(Qt.ItemDataRole.UserRole, piece)
        self._piece_list.addItem(item)
        self._piece_count_label.setText(f"Pieces: {len(self._get_all_pieces())}")

    def clear_all(self) -> None:
        """Clear all pieces and reset the UI."""
        self._pieces.clear()
        self._selected_piece = None
        self._piece_list.clear()
        self._grid_widget.clear()
        self._piece_count_label.setText("Pieces: 0")
        self._update_shape_info()
