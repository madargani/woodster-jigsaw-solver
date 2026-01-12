from typing import Dict, FrozenSet

import customtkinter as ctk

from polyomino_jigsaw_solver.gui.board_tab import PuzzleBoardTab
from polyomino_jigsaw_solver.gui.piece_tab import PuzzlePieceTab
from polyomino_jigsaw_solver.models.puzzle_piece import PuzzlePiece


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Woodster Jigsaw Solver")
        self.geometry("1200x900")

        # Set dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize state
        self.pieces: Dict[PuzzlePiece, int] = {}
        self.board_cells: FrozenSet[tuple[int, int]] = frozenset()

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Title
        title = ctk.CTkLabel(
            self,
            text="Woodster Jigsaw Puzzle Solver",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title.pack(padx=20, pady=(20, 10))

        # Tabview
        self.tabview = ctk.CTkTabview(self, width=900, height=500)
        self.tabview.pack(padx=20, pady=10)

        # Add custom tabs
        self.tabview.add("Puzzle Pieces")
        self.tabview.add("Puzzle Board")

        # Add tabs
        self.pieces_tab = PuzzlePieceTab(
            self.tabview.tab("Puzzle Pieces"),
            pieces=self.pieces,
            on_pieces_change=self._on_pieces_change,
        )
        self.pieces_tab.pack(fill="both", expand=True)

        self.board_tab = PuzzleBoardTab(
            self.tabview.tab("Puzzle Board"),
            board_cells=self.board_cells,
            on_board_change=self._on_board_change,
        )
        self.board_tab.pack(fill="both", expand=True)

        # Button frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(padx=20, pady=20)

        # Solve button (placeholder)
        solve_button = ctk.CTkButton(
            button_frame,
            text="Solve Puzzle",
            width=200,
            fg_color="#27ae60",
            hover_color="#2ecc71",
            command=self._on_solve,
        )
        solve_button.pack()

    def _on_pieces_change(self, pieces: Dict[PuzzlePiece, int]) -> None:
        self.pieces = pieces

    def _on_board_change(self, board_cells: FrozenSet[tuple[int, int]]) -> None:
        self.board_cells = board_cells

    def _on_solve(self) -> None:
        # Placeholder for solve functionality
        label = ctk.CTkLabel(
            self, text="Solve functionality not yet implemented!", text_color="#e74c3c"
        )
        label.pack(pady=5)
        self.after(3000, label.destroy)
