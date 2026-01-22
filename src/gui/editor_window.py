"""EditorWindow class for the Polyomino Puzzle Solver application.

This module provides the main editor window with a tabbed interface for
defining puzzle pieces and board configurations.
"""

from __future__ import annotations

from pathlib import Path
from typing import override

from PySide6.QtCore import QEvent, QSize
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QMainWindow,
                               QMessageBox, QPushButton, QSizePolicy,
                               QStatusBar, QTabWidget, QVBoxLayout, QWidget)

from src.gui.board_tab import BoardTab
from src.gui.piece_tab import PieceTab
from src.gui.saved_puzzles_tab import SavedPuzzlesTab
from src.gui.visualization_window import VisualizationWindow
from src.models.piece import PuzzlePiece
from src.models.puzzle_config import PuzzleConfiguration
from src.utils.file_io import (export_puzzle, import_puzzle, load_puzzle,
                               save_puzzle)

SAVED_PUZZLES_DIR = Path.home() / ".polyomino-puzzles" / "saved"


class EditorWindow(QMainWindow):
    """Main editor window for the Polyomino Puzzle Solver.

    Attributes:
        config: The current puzzle configuration being edited
        board_tab: Tab for editing board dimensions and blocked cells
        piece_tab: Tab for drawing piece shapes
        piece_list: List widget showing defined pieces
    """

    def __init__(self) -> None:
        """Initialize the editor window."""
        super().__init__()
        self.setWindowTitle("Polyomino Puzzle Solver")
        self.setMinimumSize(QSize(800, 600))
        self._config = PuzzleConfiguration(
            name="New Puzzle",
            board_width=5,
            board_height=5,
            pieces={},
            blocked_cells=set(),
        )
        self._selected_piece_index: int | None = None

        self._setup_ui()
        self._setup_menu()
        self._setup_status_bar()
        self._saved_puzzles_tab.refresh()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Central widget with layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self._tab_widget = QTabWidget()
        self._tab_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        main_layout.addWidget(self._tab_widget)

        # Create tabs
        self._piece_tab = PieceTab(
            on_piece_selected=self._on_piece_selected,
            on_piece_added=self._on_piece_added,
            on_piece_deleted=self._on_piece_deleted,
        )
        self._board_tab = BoardTab(
            on_dimensions_changed=self._on_board_dimensions_changed,
            on_blocked_cells_changed=self._on_blocked_cells_changed,
        )
        self._saved_puzzles_tab = SavedPuzzlesTab(
            on_puzzle_selected=self._on_saved_puzzle_selected,
            on_puzzle_deleted=self._on_saved_puzzle_deleted,
        )

        self._tab_widget.addTab(self._piece_tab, "Pieces")
        self._tab_widget.addTab(self._board_tab, "Board")
        self._tab_widget.addTab(self._saved_puzzles_tab, "Saved Puzzles")

        # Bottom button bar
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 5, 10, 10)

        # Spacer
        button_layout.addStretch()

        # Solve button
        self._solve_btn = QPushButton("Solve")
        self._solve_btn.setMinimumWidth(100)
        self._solve_btn.setStyleSheet("font-weight: bold;")
        self._solve_btn.clicked.connect(self._on_solve)
        button_layout.addWidget(self._solve_btn)

        # Validation status label
        self._validation_label = QLabel("")
        self._validation_label.setStyleSheet("color: orange;")
        button_layout.addWidget(self._validation_label)

        main_layout.addWidget(button_container)

        # Initialize board
        self._update_board()

    def _setup_menu(self) -> None:
        """Set up the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New Puzzle", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._on_new_puzzle)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._on_save)
        file_menu.addAction(save_action)

        load_action = QAction("Load", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self._on_load)
        file_menu.addAction(load_action)

        file_menu.addSeparator()

        export_action = QAction("Export...", self)
        export_action.triggered.connect(self._on_export)
        file_menu.addAction(export_action)

        import_action = QAction("Import...", self)
        import_action.triggered.connect(self._on_import)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        clear_action = QAction("Clear All", self)
        clear_action.triggered.connect(self._on_clear)
        edit_menu.addAction(clear_action)

        # Solve menu
        solve_menu = menubar.addMenu("Solve")

        solve_action = QAction("Solve", self)
        solve_action.setShortcut("Ctrl+Enter")
        solve_action.triggered.connect(self._on_solve)
        solve_menu.addAction(solve_action)

    def _setup_status_bar(self) -> None:
        """Set up the status bar."""
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready")

    def _on_piece_selected(self, piece) -> None:
        """Handle piece selection from piece tab."""
        pass  # Currently no action needed on selection

    def _on_saved_puzzle_selected(self, filepath: Path) -> None:
        """Handle saved puzzle selection."""
        self._load_puzzle_from_file(filepath)

    def _on_saved_puzzle_deleted(self, filepath: Path) -> None:
        """Handle saved puzzle deletion."""
        self._status_bar.showMessage(f"Deleted puzzle: {filepath.stem}")

    @property
    def config(self) -> PuzzleConfiguration:
        """Get the current puzzle configuration."""
        return self._config

    def _update_board(self) -> None:
        """Update the board tab with current configuration."""
        self._board_tab.set_dimensions(
            self._config.board_width, self._config.board_height
        )
        self._board_tab.set_blocked_cells(self._config.blocked_cells)

    def _update_validation(self) -> None:
        """Update validation status display."""
        # Get piece area and board area
        piece_area = self._config.get_piece_area()
        board_area = self._config.get_board_area() - len(self._config.blocked_cells)

        if len(self._config.pieces) == 0:
            self._validation_label.setText("No pieces defined")
            self._validation_label.setStyleSheet("color: orange;")
        elif piece_area > board_area:
            self._validation_label.setText(
                f"Warning: Piece area ({piece_area}) exceeds "
                f"available board area ({board_area})"
            )
            self._validation_label.setStyleSheet("color: red;")
        elif piece_area < board_area:
            self._validation_label.setText(
                f"Note: Piece area ({piece_area}) is less than "
                f"board area ({board_area})"
            )
            self._validation_label.setStyleSheet("color: blue;")
        else:
            self._validation_label.setText("Configuration valid")
            self._validation_label.setStyleSheet("color: green;")

    def _on_board_dimensions_changed(self, width: int, height: int) -> None:
        """Handle board dimension changes."""
        # Create new configuration with updated dimensions
        self._config = PuzzleConfiguration(
            name=self._config.name,
            board_width=width,
            board_height=height,
            pieces=self._config.pieces.copy(),
            blocked_cells=self._board_tab.blocked_cells,
        )

        self._update_validation()
        self._status_bar.showMessage(f"Board size: {width}×{height}")

    def _on_blocked_cells_changed(self, blocked_cells: set[tuple[int, int]]) -> None:
        """Handle blocked cells changes."""
        # Update configuration
        self._config = PuzzleConfiguration(
            name=self._config.name,
            board_width=self._config.board_width,
            board_height=self._config.board_height,
            pieces=self._config.pieces.copy(),
            blocked_cells=blocked_cells,
        )

        self._update_validation()

    def _on_piece_added(self, piece: PuzzlePiece) -> None:
        """Handle piece added from piece tab."""
        # Sync with our configuration
        self._config.add_piece(piece)
        self._update_validation()

    def _on_piece_deleted(self, piece: PuzzlePiece) -> None:
        """Handle piece deleted from piece tab."""
        # Sync with our configuration
        if piece in self._config.pieces:
            self._config.remove_piece(piece)
        self._update_validation()

    def _on_new_puzzle(self) -> None:
        """Handle new puzzle action."""
        reply = QMessageBox.question(
            self,
            "New Puzzle",
            "Create a new puzzle? All unsaved changes will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._config = PuzzleConfiguration(
                name="New Puzzle",
                board_width=5,
                board_height=5,
                pieces={},
                blocked_cells=set(),
            )
            self._update_board()
            self._update_validation()
            self._status_bar.showMessage("New puzzle created")

    def _on_save(self) -> None:
        """Handle save action."""
        SAVED_PUZZLES_DIR.mkdir(parents=True, exist_ok=True)

        puzzle_name, ok = QFileDialog.getSaveFileName(
            self,
            "Save Puzzle",
            str(SAVED_PUZZLES_DIR),
            "JSON Files (*.json)",
        )

        if not ok or not puzzle_name:
            return

        filepath = Path(puzzle_name)
        if filepath.suffix != ".json":
            filepath = filepath.with_suffix(".json")

        try:
            save_puzzle(self._config, filepath)
            self._status_bar.showMessage(f"Puzzle saved: {filepath.name}")
            QMessageBox.information(
                self,
                "Save Successful",
                f"Puzzle saved to:\n{filepath}",
            )
            self._saved_puzzles_tab.refresh()
        except OSError as e:
            QMessageBox.critical(
                self,
                "Save Failed",
                f"Failed to save puzzle:\n{e}",
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Failed",
                f"An unexpected error occurred:\n{e}",
            )

    def _on_load(self) -> None:
        """Handle load action."""
        SAVED_PUZZLES_DIR.mkdir(parents=True, exist_ok=True)

        filepath, ok = QFileDialog.getOpenFileName(
            self,
            "Load Puzzle",
            str(SAVED_PUZZLES_DIR),
            "JSON Files (*.json)",
        )

        if not ok or not filepath:
            return

        self._load_puzzle_from_file(Path(filepath))

    def _on_export(self) -> None:
        """Handle export action."""
        filepath, ok = QFileDialog.getSaveFileName(
            self,
            "Export Puzzle",
            "",
            "JSON Files (*.json)",
        )

        if not ok or not filepath:
            return

        export_path = Path(filepath)
        if export_path.suffix != ".json":
            export_path = export_path.with_suffix(".json")

        try:
            export_puzzle(self._config, export_path)
            self._status_bar.showMessage(f"Puzzle exported: {export_path.name}")
            QMessageBox.information(
                self,
                "Export Successful",
                f"Puzzle exported to:\n{export_path}",
            )
        except OSError as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export puzzle:\n{e}",
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"An unexpected error occurred:\n{e}",
            )

    def _on_import(self) -> None:
        """Handle import action."""
        filepath, ok = QFileDialog.getOpenFileName(
            self,
            "Import Puzzle",
            "",
            "JSON Files (*.json)",
        )

        if not ok or not filepath:
            return

        path = Path(filepath)

        try:
            loaded_config = import_puzzle(path)

            loaded_config.name = loaded_config.name or "Imported Puzzle"
            self._config = loaded_config
            self._update_board()
            self._update_validation()

            # Use the piece tab's internal method to add pieces with proper sorting
            self._piece_tab.clear_all()
            for piece, count in self._config.pieces.items():
                self._piece_tab._pieces[piece] = count
            self._piece_tab._refresh_piece_list()
            self._piece_tab._piece_count_label.setText(
                f"Pieces: {len(self._piece_tab._get_all_pieces())}"
            )

            self._status_bar.showMessage(f"Imported puzzle: {path.name}")

            QMessageBox.information(
                self,
                "Import Successful",
                f"Puzzle imported:\n{path.name}\n\n"
                f"Board: {self._config.board_width}x{self._config.board_height}\n"
                f"Piece types: {len(self._config.pieces)}",
            )
        except FileNotFoundError:
            QMessageBox.critical(
                self,
                "Import Failed",
                f"File not found:\n{path}",
            )
        except ValueError as e:
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Invalid puzzle file:\n{e}",
            )
        except OSError as e:
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Failed to import puzzle:\n{e}",
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Failed",
                f"An unexpected error occurred:\n{e}",
            )

    def _on_clear(self) -> None:
        """Handle clear action."""
        reply = QMessageBox.question(
            self,
            "Clear All",
            "Clear all pieces and reset board?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._config = PuzzleConfiguration(
                name=self._config.name,
                board_width=self._config.board_width,
                board_height=self._config.board_height,
                pieces={},
                blocked_cells=set(),
            )
            self._update_board()
            self._update_validation()
            self._piece_tab.clear_all()
            self._status_bar.showMessage("Cleared all pieces and reset board")

    def _on_solve(self) -> None:
        """Handle solve action."""
        # Validate configuration
        if len(self._config.pieces) == 0:
            QMessageBox.warning(
                self,
                "No Pieces",
                "Please define at least one piece before solving.",
            )
            return

        # Check if configuration is valid
        piece_area = self._config.get_piece_area()
        board_area = self._config.get_board_area() - len(self._config.blocked_cells)

        if piece_area > board_area:
            reply = QMessageBox.question(
                self,
                "Configuration Warning",
                f"Warning: Total piece area ({piece_area}) exceeds available board area ({board_area}).\n\nThe puzzle may not have a solution.\n\nDo you want to try solving anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # Create and show visualization window
        viz_window = VisualizationWindow(self._config)
        viz_window.show()

        self._status_bar.showMessage("Solving...")

    @override
    def closeEvent(self, event: QEvent) -> None:
        """Handle close event."""
        reply = QMessageBox.question(
            self,
            "Exit",
            "Exit the application?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.No:
            event.ignore()
        else:
            event.accept()

    def _load_puzzle_from_file(self, filepath: Path) -> None:
        """Load a puzzle configuration from a file.

        Args:
            filepath: Path to the puzzle file
        """
        try:
            loaded_config = load_puzzle(filepath)

            loaded_config.name = loaded_config.name or "Imported Puzzle"
            self._config = loaded_config
            self._update_board()
            self._update_validation()

            # Use the piece tab's internal method to add pieces with proper sorting
            self._piece_tab.clear_all()
            for piece, count in self._config.pieces.items():
                self._piece_tab._pieces[piece] = count
            self._piece_tab._refresh_piece_list()
            self._piece_tab._piece_count_label.setText(
                f"Pieces: {len(self._piece_tab._get_all_pieces())}"
            )

            self._status_bar.showMessage(f"Loaded puzzle: {filepath.name}")

            QMessageBox.information(
                self,
                "Load Successful",
                f"Puzzle loaded:\n{filepath.name}\n\n"
                f"Board: {self._config.board_width}x{self._config.board_height}\n"
                f"Piece types: {len(self._config.pieces)}",
            )
        except FileNotFoundError:
            QMessageBox.critical(
                self,
                "Load Failed",
                f"File not found:\n{filepath}",
            )
        except ValueError as e:
            QMessageBox.critical(
                self,
                "Load Failed",
                f"Invalid puzzle file:\n{e}",
            )
        except OSError as e:
            QMessageBox.critical(
                self,
                "Load Failed",
                f"Failed to load puzzle:\n{e}",
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Load Failed",
                f"An unexpected error occurred:\n{e}",
            )
