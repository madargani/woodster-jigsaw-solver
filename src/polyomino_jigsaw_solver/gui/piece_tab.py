import json
from typing import Dict, Callable

import customtkinter as ctk
from tkinter import filedialog
from polyomino_jigsaw_solver.gui.piece_list import PieceListWidget
from polyomino_jigsaw_solver.gui.piece_editor import PieceEditorDialog
from polyomino_jigsaw_solver.models.puzzle_piece import PuzzlePiece


class PuzzlePieceTab(ctk.CTkFrame):
    def __init__(
        self,
        master,
        pieces: Dict[PuzzlePiece, int],
        on_pieces_change: Callable[[Dict[PuzzlePiece, int]], None],
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self.pieces = pieces
        self.on_pieces_change = on_pieces_change

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Title
        title = ctk.CTkLabel(
            self, text="Puzzle Pieces", font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(padx=20, pady=(20, 10))

        # Description
        description = ctk.CTkLabel(
            self,
            text="Add and manage your puzzle pieces. Click 'Add New Piece' to create pieces.",
            wraplength=760,
            anchor="w",
        )
        description.pack(padx=20, pady=(0, 10))

        # Piece list
        self.piece_list = PieceListWidget(
            self,
            pieces=self.pieces,
            on_pieces_change=self._on_pieces_change,
            on_add_piece=self._on_add_piece,
        )
        self.piece_list.pack(fill="both", expand=True, padx=10, pady=10)

        # Button frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(padx=20, pady=(10, 20))

        # Import button
        import_button = ctk.CTkButton(
            button_frame,
            text="Import",
            fg_color="#9b59b6",
            hover_color="#8e44ad",
            width=200,
            command=self._on_import,
        )
        import_button.pack(side="left", padx=(0, 10))

        # Export button
        export_button = ctk.CTkButton(
            button_frame,
            text="Export",
            width=200,
            command=self._on_export,
        )
        export_button.pack(side="left")

    def _on_pieces_change(self, pieces: Dict[PuzzlePiece, int]) -> None:
        self.pieces = pieces
        self.on_pieces_change(pieces)

    def _on_add_piece(self) -> None:
        dialog = PieceEditorDialog(self, on_save=self._on_piece_saved)

    def _on_piece_saved(self, piece: PuzzlePiece) -> None:
        # Check if piece already exists
        for existing_piece in self.pieces.keys():
            if existing_piece.transformations == piece.transformations:
                # Piece already exists, increment count
                self.pieces[existing_piece] += 1
                break
        else:
            # No existing pieces or new piece, add it
            self.pieces[piece] = 1

        self.piece_list.update_pieces(self.pieces)
        self.on_pieces_change(self.pieces)

    def get_pieces(self) -> Dict[PuzzlePiece, int]:
        return self.pieces

    def set_pieces(self, pieces: Dict[PuzzlePiece, int]) -> None:
        self.pieces = pieces
        self.piece_list.update_pieces(pieces)

    def _on_import(self) -> None:
        # Create file dialog
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import Pieces",
        )

        if file_path:
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)

                # Clear current pieces
                self.pieces.clear()

                # Load pieces from file
                for piece_data in data.get("pieces", []):
                    piece = PuzzlePiece(piece_data["coordinates"])
                    self.pieces[piece] = piece_data.get("count", 1)

                # Update UI
                self.piece_list.update_pieces(self.pieces)
                self.on_pieces_change(self.pieces)

                # Show success message
                success_label = ctk.CTkLabel(
                    self,
                    text=f"Imported {len(self.pieces)} pieces",
                    text_color="#27ae60",
                )
                success_label.pack(pady=5)
                self.after(3000, success_label.destroy)

            except (json.JSONDecodeError, KeyError, IOError) as e:
                error_label = ctk.CTkLabel(
                    self, text=f"Failed to import: {str(e)}", text_color="#e74c3c"
                )
                error_label.pack(pady=5)
                self.after(3000, error_label.destroy)

    def _on_export(self) -> None:
        # Export pieces to JSON
        export_data = {
            "pieces": [
                {"coordinates": list(next(iter(piece.transformations))), "count": count}
                for piece, count in self.pieces.items()
            ],
        }

        # Create file dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Pieces",
        )

        if file_path:
            with open(file_path, "w") as f:
                json.dump(export_data, f, indent=2)

            # Show success message
            success_label = ctk.CTkLabel(
                self, text=f"Exported to {file_path}", text_color="#27ae60"
            )
            success_label.pack(pady=5)
            self.after(3000, success_label.destroy)
