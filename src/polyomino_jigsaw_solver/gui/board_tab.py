import json
from typing import Callable, FrozenSet

import customtkinter as ctk
from tkinter import filedialog

from polyomino_jigsaw_solver.gui.grid_widget import GridWidget

DEFAULT_BOARD_ROWS = 44
DEFAULT_BOARD_COLS = 44


class PuzzleBoardTab(ctk.CTkFrame):
    def __init__(
        self,
        master,
        board_cells: FrozenSet[tuple[int, int]],
        on_board_change: Callable[[FrozenSet[tuple[int, int]]], None],
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self.board_cells = board_cells
        self.on_board_change = on_board_change
        self.rows = DEFAULT_BOARD_ROWS
        self.cols = DEFAULT_BOARD_COLS

        self._setup_ui()

    def _setup_ui(self) -> None:
        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Puzzle Board", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(padx=20, pady=(20, 10))

        # Description
        description = ctk.CTkLabel(
            self,
            text="Click cells to toggle them. Blue cells represent occupied spaces on the board.",
            wraplength=760,
            anchor="w",
        )
        description.pack(padx=20, pady=(0, 10))

        # Board size controls
        size_frame = ctk.CTkFrame(self, fg_color="transparent")
        size_frame.pack(padx=20, pady=(0, 10))

        # Rows input
        ctk.CTkLabel(size_frame, text="Rows:").pack(side="left", padx=(0, 5))
        self.rows_entry = ctk.CTkEntry(size_frame, width=80)
        self.rows_entry.insert(0, str(DEFAULT_BOARD_ROWS))
        self.rows_entry.pack(side="left", padx=(0, 10))

        # Columns input
        ctk.CTkLabel(size_frame, text="Columns:").pack(side="left", padx=(0, 5))
        self.cols_entry = ctk.CTkEntry(size_frame, width=80)
        self.cols_entry.insert(0, str(DEFAULT_BOARD_COLS))
        self.cols_entry.pack(side="left", padx=(0, 10))

        # Resize button
        resize_button = ctk.CTkButton(
            size_frame, text="Resize Board", command=self._on_resize, width=120
        )
        resize_button.pack(side="left", padx=(0, 10))

        # Clear button
        reset_button = ctk.CTkButton(
            size_frame,
            text="Clear Board",
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self._on_clear,
            width=120,
        )
        reset_button.pack(side="left")

        # Grid widget
        self.grid_widget = GridWidget(
            self,
            rows=self.rows,
            cols=self.cols,
            cell_size=15,
            initial_state=self.board_cells,
            on_change=self._on_grid_change,
        )
        self.grid_widget.pack(padx=20, pady=10)

        # Button frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(padx=20, pady=(10, 20))

        # Import button
        import_button = ctk.CTkButton(
            button_frame,
            text="Import",
            fg_color="#9b59b6",
            hover_color="#8e44ad",
            command=self._on_import,
            width=200,
        )
        import_button.pack(side="left", padx=(0, 10))

        # Export button
        export_button = ctk.CTkButton(
            button_frame,
            text="Export",
            command=self._on_export,
            width=200,
        )
        export_button.pack(side="left")

    def _on_resize(self) -> None:
        try:
            new_rows = int(self.rows_entry.get())
            new_cols = int(self.cols_entry.get())

            if new_rows <= 0 or new_cols <= 0:
                error_label = ctk.CTkLabel(
                    self,
                    text="Board dimensions must be positive!",
                    text_color="#e74c3c",
                )
                error_label.pack(pady=5)
                self.after(3000, error_label.destroy)
                return

            self.rows = new_rows
            self.cols = new_cols

            # Filter cells that are within new bounds
            filtered_cells = frozenset(
                (x, y) for x, y in self.board_cells if x < self.cols and y < self.rows
            )
            self.board_cells = filtered_cells

            # Remove old grid widget
            self.grid_widget.destroy()

            # Create new grid widget
            self.grid_widget = GridWidget(
                self,
                rows=self.rows,
                cols=self.cols,
                cell_size=15,
                initial_state=self.board_cells,
                on_change=self._on_grid_change,
            )
            self.grid_widget.pack(padx=20, pady=10)

            self.on_board_change(self.board_cells)

        except ValueError:
            error_label = ctk.CTkLabel(
                self,
                text="Invalid dimensions! Please enter numbers.",
                text_color="#e74c3c",
            )
            error_label.pack(pady=5)
            self.after(3000, error_label.destroy)

    def _on_clear(self) -> None:
        self.grid_widget.clear()
        self.board_cells = frozenset()
        self.on_board_change(self.board_cells)

    def _on_grid_change(self, state: FrozenSet[tuple[int, int]]) -> None:
        self.board_cells = state
        self.on_board_change(state)

    def get_board_cells(self) -> FrozenSet[tuple[int, int]]:
        return self.board_cells

    def set_board_cells(self, cells: FrozenSet[tuple[int, int]]) -> None:
        self.board_cells = cells
        self.grid_widget.set_state(cells)

    def get_board_size(self) -> tuple[int, int]:
        return (self.rows, self.cols)

    def _on_import(self) -> None:
        # Create file dialog
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import Board",
        )

        if file_path:
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)

                board_data = data.get("board", {})
                rows = board_data.get("rows", 44)
                cols = board_data.get("cols", 44)
                cells = frozenset(tuple(cell) for cell in board_data.get("cells", []))

                # Update entry fields
                self.rows_entry.delete(0, "end")
                self.rows_entry.insert(0, str(rows))
                self.cols_entry.delete(0, "end")
                self.cols_entry.insert(0, str(cols))

                # Update board
                self.rows = rows
                self.cols = cols
                self.title_label.configure(text=f"Puzzle Board ({rows}x{cols})")
                self.board_cells = cells

                # Remove old grid and create new one
                self.grid_widget.destroy()
                self.grid_widget = GridWidget(
                    self,
                    rows=rows,
                    cols=cols,
                    cell_size=15,
                    initial_state=cells,
                    on_change=self._on_grid_change,
                )
                self.grid_widget.pack(padx=20, pady=10)

                self.on_board_change(cells)

                # Show success message
                success_label = ctk.CTkLabel(
                    self, text=f"Imported {rows}x{cols} board", text_color="#27ae60"
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
        # Export board to JSON
        export_data = {
            "board": {
                "rows": self.rows,
                "cols": self.cols,
                "cells": list(self.board_cells),
            },
        }

        # Create file dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Board",
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
