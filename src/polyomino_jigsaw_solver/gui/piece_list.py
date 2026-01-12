from typing import Callable, Dict

import customtkinter as ctk
from polyomino_jigsaw_solver.models.puzzle_piece import PuzzlePiece


class PieceListItem(ctk.CTkFrame):
    def __init__(
        self,
        master,
        piece: PuzzlePiece,
        count: int,
        on_increment: Callable[[PuzzlePiece], None],
        on_decrement: Callable[[PuzzlePiece], None],
        on_delete: Callable[[PuzzlePiece], None],
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self.piece = piece
        self.count = count
        self.on_increment = on_increment
        self.on_decrement = on_decrement
        self.on_delete = on_delete

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Get the first transformation for display
        coords = next(iter(self.piece.transformations))
        size = len(coords)

        # Left frame: shape info
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(side="left", padx=10, pady=5)

        size_label = ctk.CTkLabel(
            info_frame,
            text=f"Size: {size}",
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w",
        )
        size_label.pack(fill="x", pady=(0, 2))

        ascii_label = ctk.CTkLabel(
            info_frame,
            text=self.piece.ascii_diagram(),
            font=("Courier New", 10),
            justify="left",
            anchor="nw",
        )
        ascii_label.pack(fill="both")

        # Right frame: count and buttons
        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.pack(side="right", padx=10, pady=5)

        # Count display and controls
        count_frame = ctk.CTkFrame(control_frame)
        count_frame.pack(pady=(0, 5))

        dec_button = ctk.CTkButton(
            count_frame, text="-", width=30, command=self._on_decrement
        )
        dec_button.pack(side="left", padx=2)

        self.count_label = ctk.CTkLabel(count_frame, text=str(self.count), width=40)
        self.count_label.pack(side="left", padx=2)

        inc_button = ctk.CTkButton(
            count_frame, text="+", width=30, command=self._on_increment
        )
        inc_button.pack(side="left", padx=2)

        # Delete button
        delete_button = ctk.CTkButton(
            control_frame,
            text="Delete",
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=lambda: self.on_delete(self.piece),
        )
        delete_button.pack(fill="x", pady=(5, 0))

    def _on_increment(self) -> None:
        self.on_increment(self.piece)

    def _on_decrement(self) -> None:
        self.on_decrement(self.piece)

    def update_count(self, count: int) -> None:
        self.count = count
        self.count_label.configure(text=str(self.count))


class PieceListWidget(ctk.CTkScrollableFrame):
    def __init__(
        self,
        master,
        pieces: Dict[PuzzlePiece, int],
        on_pieces_change: Callable[[Dict[PuzzlePiece, int]], None],
        on_add_piece: Callable[[], None],
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self.pieces = pieces
        self.on_pieces_change = on_pieces_change
        self.on_add_piece = on_add_piece
        self.add_button = None
        self.separator = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Add piece button
        self.add_button = ctk.CTkButton(
            self, text="Add New Piece", command=self._on_add_piece, height=40
        )
        self.add_button.pack(fill="x", padx=10, pady=5)

        # Separator
        self.separator = ctk.CTkFrame(self, height=2)
        self.separator.pack(fill="x", padx=10, pady=10)

        self._refresh_list()

    def _refresh_list(self) -> None:
        # Clear only PieceListItem widgets, not button or separator
        for widget in list(self.winfo_children()):
            if isinstance(widget, PieceListItem):
                widget.destroy()

        # Sort pieces by size
        sorted_pieces = sorted(
            self.pieces.items(),
            key=lambda item: len(next(iter(item[0].transformations))),
        )

        # Add piece items
        for piece, count in sorted_pieces:
            item = PieceListItem(
                self,
                piece=piece,
                count=count,
                on_increment=self._on_increment,
                on_decrement=self._on_decrement,
                on_delete=self._on_delete,
            )
            item.pack(fill="x", padx=5, pady=5)

    def _on_add_piece(self) -> None:
        self.on_add_piece()

    def _on_increment(self, piece: PuzzlePiece) -> None:
        self.pieces[piece] += 1
        self._refresh_list()
        self.on_pieces_change(self.pieces)

    def _on_decrement(self, piece: PuzzlePiece) -> None:
        if self.pieces[piece] > 1:
            self.pieces[piece] -= 1
            self._refresh_list()
            self.on_pieces_change(self.pieces)

    def _on_delete(self, piece: PuzzlePiece) -> None:
        del self.pieces[piece]
        self._refresh_list()
        self.on_pieces_change(self.pieces)

    def update_pieces(self, pieces: Dict[PuzzlePiece, int]) -> None:
        self.pieces = pieces
        self._refresh_list()
