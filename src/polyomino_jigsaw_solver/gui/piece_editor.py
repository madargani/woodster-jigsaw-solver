from typing import Callable, FrozenSet, Optional

import customtkinter as ctk
from polyomino_jigsaw_solver.gui.grid_widget import GridWidget
from polyomino_jigsaw_solver.models.puzzle_piece import PuzzlePiece


class PieceEditorDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        initial_coords: Optional[FrozenSet[tuple[int, int]]] = None,
        on_save: Optional[Callable[[PuzzlePiece], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self.title("Piece Editor")
        self.geometry("400x500")
        self.on_save = on_save
        self.on_cancel = on_cancel

        # Initial state
        initial_state = initial_coords if initial_coords else frozenset()

        # Instructions label
        instructions = ctk.CTkLabel(
            self,
            text="Click cells to toggle them. Define your piece shape below.",
            wraplength=380,
            anchor="w",
        )
        instructions.pack(padx=20, pady=(20, 10))

        # Grid widget (10x10 as specified)
        self.grid_widget = GridWidget(
            self, rows=10, cols=10, cell_size=30, initial_state=initial_state
        )
        self.grid_widget.pack(padx=20, pady=10)

        # Button frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(padx=20, pady=20)

        # Clear button
        clear_button = ctk.CTkButton(
            button_frame,
            text="Clear",
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=100,
            command=self._on_clear,
        )
        clear_button.pack(side="left", padx=(0, 10))

        # Cancel button
        cancel_button = ctk.CTkButton(
            button_frame, text="Cancel", width=100, command=self._on_cancel
        )
        cancel_button.pack(side="left", padx=(0, 10))

        # Save button
        save_button = ctk.CTkButton(
            button_frame,
            text="Done",
            fg_color="#27ae60",
            hover_color="#2ecc71",
            width=100,
            command=self._on_save,
        )
        save_button.pack(side="left")

    def _on_clear(self) -> None:
        self.grid_widget.clear()

    def _on_cancel(self) -> None:
        if self.on_cancel is not None:
            self.on_cancel()
        self.destroy()

    def _on_save(self) -> None:
        state = self.grid_widget.get_state()

        if not state:
            # Show error message
            error_label = ctk.CTkLabel(
                self, text="Please select at least one cell!", text_color="#e74c3c"
            )
            error_label.pack(pady=(0, 10))
            self.after(3000, error_label.destroy)
            return

        piece = PuzzlePiece(state)

        if self.on_save is not None:
            self.on_save(piece)

        self.destroy()
