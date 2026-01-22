"""Board tab component for the puzzle editor.

This module contains the BoardTab class which provides the UI for configuring
the puzzle board dimensions and marking blocked cells.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QPen, QResizeEvent
from PySide6.QtWidgets import (QGridLayout, QLabel, QSizePolicy, QSpinBox,
                               QWidget)


class BoardGridWidget(QWidget):
    """Grid widget for editing board cells.

    This widget displays a grid where users can toggle blocked cells.
    The grid automatically resizes to fit within the available screen area.

    Attributes:
        width: Number of columns in the board
        height: Number of rows in the board
        blocked_cells: Set of blocked cell positions (row, col)
    """

    # Signals
    blocked_cells_changed = Signal(set)

    # Constants
    MIN_CELL_SIZE = 5
    MAX_CELL_SIZE = 50
    DEFAULT_CELL_SIZE = 25
    BLOCKED_COLOR = QColor(80, 80, 80)  # Dark gray for blocked cells
    EMPTY_COLOR = QColor(245, 245, 245)  # Light gray for empty cells
    GRID_COLOR = QColor(180, 180, 180)  # Medium gray for grid lines

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the board grid widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self._width = 5
        self._height = 5
        self._blocked_cells: set[tuple[int, int]] = set()
        self._cell_size = self.DEFAULT_CELL_SIZE
        self._is_blocking = True  # True = add blocked, False = remove blocked

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

    @property
    def board_width(self) -> int:
        """Get the board width."""
        return self._width

    @board_width.setter
    def board_width(self, value: int) -> None:
        """Set the board width and update display.

        Args:
            value: New width (1-50)
        """
        self._width = max(1, min(50, value))
        self.updateGeometry()
        self.update()

    @property
    def board_height(self) -> int:
        """Get the board height."""
        return self._height

    @board_height.setter
    def board_height(self, value: int) -> None:
        """Set the board height and update display.

        Args:
            value: New height (1-50)
        """
        self._height = max(1, min(50, value))
        self.updateGeometry()
        self.update()

    @property
    def blocked_cells(self) -> set[tuple[int, int]]:
        """Get the set of blocked cell positions."""
        return self._blocked_cells.copy()

    @blocked_cells.setter
    def blocked_cells(self, cells: set[tuple[int, int]]) -> None:
        """Set the blocked cells and update display.

        Args:
            cells: Set of (row, col) positions to mark as blocked
        """
        self._blocked_cells = cells.copy()
        self.update()

    def set_dimensions(self, width: int, height: int) -> None:
        """Set board dimensions and clear blocked cells that are out of bounds.

        Args:
            width: New width (1-50)
            height: New height (1-50)
        """
        self._width = max(1, min(50, width))
        self._height = max(1, min(50, height))

        # Remove out-of-bounds blocked cells
        self._blocked_cells = {
            (r, c)
            for r, c in self._blocked_cells
            if 0 <= r < self._height and 0 <= c < self._width
        }

        self._calculate_cell_size()
        self.updateGeometry()
        self.update()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handle widget resize to auto-fit cell size."""
        self._calculate_cell_size()
        super().resizeEvent(event)

    def _calculate_cell_size(self) -> None:
        """Calculate optimal cell size based on available space."""
        # Extra padding for labels (25px on each side)
        padding = 25
        available_width = self.width() - padding * 2
        available_height = self.height() - padding * 2

        if self._width > 0 and self._height > 0:
            cell_width = available_width // self._width
            cell_height = available_height // self._height
            self._cell_size = max(
                self.MIN_CELL_SIZE, min(cell_width, cell_height, self.MAX_CELL_SIZE)
            )

    def sizeHint(self) -> QSize:
        """Return the preferred size hint."""
        width = self._width * self._cell_size + 10
        height = self._height * self._cell_size + 10
        return QSize(width, height)

    def minimumSizeHint(self) -> QSize:
        """Return the minimum size hint."""
        width = self._width * self.MIN_CELL_SIZE + 10
        height = self._height * self.MIN_CELL_SIZE + 10
        return QSize(width, height)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the board grid."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Extra padding for labels
        label_padding = 25
        grid_width = self._width * self._cell_size
        grid_height = self._height * self._cell_size
        offset_x = (self.width() - grid_width) // 2
        offset_y = (self.height() - grid_height) // 2

        # Ensure labels have enough space
        offset_x = max(offset_x, label_padding)
        offset_y = max(offset_y, label_padding)

        # Draw cells
        for row in range(self._height):
            for col in range(self._width):
                x = offset_x + col * self._cell_size
                y = offset_y + row * self._cell_size

                # Determine cell color
                if (row, col) in self._blocked_cells:
                    color = self.BLOCKED_COLOR
                else:
                    color = self.EMPTY_COLOR

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
            for col in range(self._width):
                x = offset_x + col * self._cell_size + self._cell_size // 2
                y = offset_y - 8
                label = str(col)
                metrics = painter.fontMetrics()
                text_width = metrics.horizontalAdvance(label)
                painter.drawText(int(x - text_width // 2), int(y), label)

            # Row labels (left)
            for row in range(self._height):
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
        grid_width = self._width * self._cell_size
        grid_height = self._height * self._cell_size
        offset_x = (self.width() - grid_width) // 2
        offset_y = (self.height() - grid_height) // 2

        # Check if position is within grid bounds
        if pos_x < offset_x or pos_x >= offset_x + grid_width:
            return None
        if pos_y < offset_y or pos_y >= offset_y + grid_height:
            return None

        col = (pos_x - offset_x) // self._cell_size
        row = (pos_y - offset_y) // self._cell_size

        if 0 <= row < self._height and 0 <= col < self._width:
            return (row, col)
        return None

    def mousePressEvent(self, event) -> None:
        """Handle mouse press for toggling blocked cells."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_blocking = True
            self._toggle_cell_at_position(event.pos())
        elif event.button() == Qt.MouseButton.RightButton:
            self._is_blocking = False
            self._toggle_cell_at_position(event.pos())

    def mouseMoveEvent(self, event) -> None:
        """Handle mouse drag for painting blocked cells."""
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._is_blocking = True
            self._toggle_cell_at_position(event.pos())
        elif event.buttons() & Qt.MouseButton.RightButton:
            self._is_blocking = False
            self._toggle_cell_at_position(event.pos())

    def _toggle_cell_at_position(self, pos) -> None:
        """Toggle blocked state at the given position.

        Args:
            pos: QPoint position
        """
        cell = self._get_cell_at_position(pos.x(), pos.y())
        if cell is not None:
            if self._is_blocking:
                self._blocked_cells.add(cell)
            else:
                self._blocked_cells.discard(cell)
            self.blocked_cells_changed.emit(self._blocked_cells)
            self.update()


class BoardTab(QWidget):
    """Tab widget for board configuration.

    This tab provides controls for setting board dimensions and a grid
    editor for marking blocked cells.

    Signals:
        dimensions_changed: Emitted when board dimensions change (width, height)
        blocked_cells_changed: Emitted when blocked cells change
    """

    # Signals
    dimensions_changed = Signal(int, int)
    blocked_cells_changed = Signal(set)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        on_dimensions_changed: Callable[[int, int], None] | None = None,
        on_blocked_cells_changed: Callable[[set[tuple[int, int]]], None] | None = None,
    ) -> None:
        """Initialize the board tab.

        Args:
            parent: Parent widget
            on_dimensions_changed: Callback for dimension changes (width, height)
            on_blocked_cells_changed: Callback for blocked cells changes
        """
        super().__init__(parent)

        self._dimensions_callback = on_dimensions_changed
        self._blocked_cells_callback = on_blocked_cells_changed

        self._init_ui()

        # Connect internal signals to callbacks
        self._width_spinner.valueChanged.connect(self._on_dimension_changed)
        self._height_spinner.valueChanged.connect(self._on_dimension_changed)
        self._grid_widget.blocked_cells_changed.connect(self._on_blocked_cells_changed)

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QGridLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Dimension controls section
        dimensions_label = QLabel("Board Dimensions:")
        dimensions_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(dimensions_label, 0, 0, 1, 2)

        # Width control
        width_label = QLabel("Width:")
        self._width_spinner = QSpinBox()
        self._width_spinner.setRange(1, 50)
        self._width_spinner.setValue(5)
        self._width_spinner.setFixedWidth(80)
        layout.addWidget(width_label, 1, 0)
        layout.addWidget(self._width_spinner, 1, 1)

        # Height control
        height_label = QLabel("Height:")
        self._height_spinner = QSpinBox()
        self._height_spinner.setRange(1, 50)
        self._height_spinner.setValue(5)
        self._height_spinner.setFixedWidth(80)
        layout.addWidget(height_label, 2, 0)
        layout.addWidget(self._height_spinner, 2, 1)

        # Instructions
        instructions = QLabel(
            "Click and drag to mark blocked cells.\nRight-click to remove."
        )
        instructions.setStyleSheet("color: #666; font-style: italic;")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions, 3, 0, 1, 2)

        # Board grid
        self._grid_widget = BoardGridWidget()
        layout.addWidget(self._grid_widget, 4, 0, 1, 2)

        # Status info
        self._status_label = QLabel("Blocked cells: 0")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status_label, 5, 0, 1, 2)

        # Set row stretch for the grid area to expand
        layout.setRowStretch(4, 1)

    def _on_dimension_changed(self) -> None:
        """Handle dimension spinner changes."""
        width = self._width_spinner.value()
        height = self._height_spinner.value()
        self._grid_widget.set_dimensions(width, height)
        self.dimensions_changed.emit(width, height)
        if self._dimensions_callback:
            self._dimensions_callback(width, height)

    def _on_blocked_cells_changed(self, cells: set[tuple[int, int]]) -> None:
        """Handle blocked cells changes.

        Args:
            cells: Set of blocked cell positions
        """
        self._status_label.setText(f"Blocked cells: {len(cells)}")
        self.blocked_cells_changed.emit(cells)
        if self._blocked_cells_callback:
            self._blocked_cells_callback(cells)

    @property
    def board_width(self) -> int:
        """Get the current board width."""
        return self._width_spinner.value()

    @property
    def board_height(self) -> int:
        """Get the current board height."""
        return self._height_spinner.value()

    @property
    def blocked_cells(self) -> set[tuple[int, int]]:
        """Get the current blocked cells."""
        return self._grid_widget.blocked_cells

    def set_dimensions(self, width: int, height: int) -> None:
        """Set board dimensions.

        Args:
            width: Board width (1-50)
            height: Board height (1-50)
        """
        self._width_spinner.setValue(width)
        self._height_spinner.setValue(height)

    def set_blocked_cells(self, cells: set[tuple[int, int]]) -> None:
        """Set blocked cells.

        Args:
            cells: Set of (row, col) positions to mark as blocked
        """
        self._grid_widget.blocked_cells = cells
        self._status_label.setText(f"Blocked cells: {len(cells)}")
