import customtkinter as ctk
from polyomino_jigsaw_solver.models.puzzle_piece import PuzzlePiece


class PieceShapeWidget(ctk.CTkFrame):
    def __init__(self, master, piece: PuzzlePiece, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.piece = piece

        self.label = ctk.CTkLabel(
            self,
            text=piece.ascii_diagram(),
            font=("Courier New", 12),
            justify="left",
            anchor="nw",
        )
        self.label.pack(padx=10, pady=10, fill="both", expand=True)

    def update_piece(self, piece: PuzzlePiece) -> None:
        self.piece = piece
        self.label.configure(text=piece.ascii_diagram())
