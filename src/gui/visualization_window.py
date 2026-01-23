"""VisualizationWindow class for solver visualization with QTimer pacing.

This module provides a dedicated window for solver visualization with
QTimer-driven execution, UI controls, and board rendering.
"""

from __future__ import annotations

from typing import Any, Generator, Optional

from PySide6.QtCore import QSize, Qt, QTimer, Slot
from PySide6.QtGui import QCloseEvent, QResizeEvent
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QMainWindow,
                               QPushButton, QSizePolicy, QSlider, QSpacerItem,
                               QVBoxLayout, QWidget)

from src.gui.board_widget import BoardWidget


class VisualizationWindow(QMainWindow):
    """Dedicated window for solver visualization with QTimer pacing."""

    def __init__(
        self,
        puzzle_config: "PuzzleConfiguration",
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize visualization window.

        Args:
            puzzle_config: The puzzle configuration to solve
            parent: Parent widget
        """
        super().__init__(parent)
        self._config = puzzle_config
        self._generator: Optional[Generator[dict[str, Any], None, None]] = None
        self._timer = QTimer(self)
        self._delay_ms = 100
        self._is_playing = False  # Track playing state explicitly

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Create and arrange UI elements."""
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Board visualization frame
        board_frame = QFrame()
        board_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        board_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        board_layout = QVBoxLayout(board_frame)

        # Create board widget
        board = self._config.get_board()
        self._board_widget = BoardWidget(
            width=board.width,
            height=board.height,
            cell_size=30,
        )
        board_layout.addWidget(self._board_widget, 0, Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(board_frame, stretch=1)

        # Control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(0, 10, 0, 0)

        # Speed label and slider
        speed_label = QLabel("Speed:")
        control_layout.addWidget(speed_label)

        self._speed_slider = QSlider(Qt.Orientation.Horizontal)
        self._speed_slider.setMinimum(0)
        self._speed_slider.setMaximum(1000)
        self._speed_slider.setValue(100)
        self._speed_slider.valueChanged.connect(self._on_speed_changed)
        control_layout.addWidget(self._speed_slider)

        # Speed preset buttons
        for label, value in [("Slow", 500), ("Medium", 100), ("Fast", 10)]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, v=value: self._speed_slider.setValue(v))
            control_layout.addWidget(btn)

        control_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed))

        # Play/Pause button
        self._play_pause_btn = QPushButton("Play")
        self._play_pause_btn.clicked.connect(self._on_play_pause_clicked)
        control_layout.addWidget(self._play_pause_btn)

        # Step button
        self._step_btn = QPushButton("Step")
        self._step_btn.clicked.connect(self._on_step_clicked)
        control_layout.addWidget(self._step_btn)

        # Stop button
        self._stop_btn = QPushButton("Stop")
        self._stop_btn.clicked.connect(self._on_stop_clicked)
        control_layout.addWidget(self._stop_btn)

        main_layout.addWidget(control_panel)

        # Status label
        self._status_label = QLabel("Press Play to start solving...")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self._status_label)

        # Set window properties
        self.setWindowTitle("Solver Visualization")
        self.resize(QSize(800, 600))

    def _connect_signals(self) -> None:
        """Connect timer to advance method."""
        self._timer.timeout.connect(self._advance)

    def _create_solver(self) -> None:
        """Create the solver generator from configuration."""
        from src.logic.solver import solve_backtracking

        board = self._config.get_board()
        self._generator = solve_backtracking(self._config.pieces, board)

    @Slot()
    def _advance(self) -> None:
        """Called by timer to advance generator one step."""
        generator = self._generator
        if generator is None:
            return
        try:
            event = next(generator)
            self._board_widget.handle_event(event)
            event_type = event["type"]
            if event_type == "solved":
                self._status_label.setText(
                    f"SOLUTION FOUND! Completed in {event.get('step_count', 0)} steps."
                )
                self._on_stop_clicked()
            elif event_type == "no_solution":
                self._status_label.setText("No solution exists for this puzzle.")
                self._on_stop_clicked()
            else:
                step = event.get("step_count", 0)
                status = {
                    "attempt": "Attempting placement...",
                    "place": "Piece placed",
                    "remove": "Backtracking...",
                }.get(event_type, "Unknown")
                self._status_label.setText(f"Step {step}: {status}")
        except StopIteration:
            self._on_stop_clicked()

    @Slot()
    def _on_play_pause_clicked(self) -> None:
        """Handle play/pause button click."""
        if self._is_playing:
            # Currently playing, so pause
            self._is_playing = False
            self._play_pause_btn.setText("Play")
            self._timer.stop()
            self._status_label.setText("Paused")
        else:
            # Currently paused, so play
            if self._generator is None:
                self._create_solver()
            self._is_playing = True
            self._play_pause_btn.setText("Pause")
            self._timer.setInterval(self._speed_slider.value())
            self._timer.start()
            if self._generator is not None:
                self._advance()
            self._status_label.setText("Solving...")

    @Slot()
    def _on_step_clicked(self) -> None:
        """Execute one solver step."""
        if self._generator is None:
            self._create_solver()
        try:
            event = next(self._generator)
            self._board_widget.handle_event(event)
        except StopIteration:
            self._status_label.setText("Solver finished")
            self._play_pause_btn.setText("Play")

    @Slot()
    def _on_stop_clicked(self) -> None:
        """Stop the solver and reset."""
        self._timer.stop()
        self._is_playing = False
        if self._generator is not None:
            self._generator.close()
            self._generator = None
        self._play_pause_btn.setText("Play")

    @Slot(int)
    def _on_speed_changed(self, value: int) -> None:
        """Handle speed slider change."""
        self._delay_ms = max(10, min(1000, value))
        self._timer.setInterval(self._delay_ms)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handle window resize to adapt board cell size."""
        board = self._config.get_board()

        # Account for margins (10px each side) and control panel (~60px) and status label (~25px)
        margin = 20
        controls_height = 85  # ~60 for controls, ~25 for status label
        available_width = event.size().width() - margin
        available_height = event.size().height() - margin - controls_height

        # Calculate max cell size that fits
        max_cell_width = available_width // board.width
        max_cell_height = available_height // board.height
        cell_size = min(max_cell_width, max_cell_height)

        # Ensure minimum size
        cell_size = max(10, cell_size)

        self._board_widget.set_cell_size(cell_size)
        super().resizeEvent(event)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close."""
        self._on_stop_clicked()
        super().closeEvent(event)


# Import for type hints (avoid circular import)
from src.models.puzzle_config import PuzzleConfiguration
