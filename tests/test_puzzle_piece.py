import pytest

from polyomino_jigsaw_solver.models.puzzle_piece import PuzzlePiece


class TestPuzzlePieceEquality:
    def test_same_piece_is_equal(self):
        p1 = PuzzlePiece([(0, 0), (1, 0), (0, 1)])
        p2 = PuzzlePiece([(0, 0), (1, 0), (0, 1)])
        assert p1 == p2

    def test_rotated_pieces_are_equal(self):
        p1 = PuzzlePiece([(0, 0), (1, 0), (0, 1)])
        p2 = PuzzlePiece([(0, 0), (0, 1), (1, 1)])
        assert p1 == p2

    def test_flipped_pieces_are_equal(self):
        p1 = PuzzlePiece([(0, 0), (1, 0), (0, 1)])
        p2 = PuzzlePiece([(0, 0), (1, 0), (1, 1)])
        assert p1 == p2

    def test_rotated_and_flipped_pieces_are_equal(self):
        p1 = PuzzlePiece([(0, 0), (1, 0), (0, 1)])
        p2 = PuzzlePiece([(0, 0), (-1, 0), (0, -1)])
        assert p1 == p2

    def test_different_pieces_are_not_equal(self):
        p1 = PuzzlePiece([(0, 0), (1, 0), (0, 1)])
        p2 = PuzzlePiece([(0, 0), (1, 0), (2, 0)])
        assert p1 != p2

    def test_different_shapes_are_not_equal(self):
        p1 = PuzzlePiece([(0, 0), (1, 0), (0, 1)])
        p2 = PuzzlePiece([(0, 0), (1, 0), (2, 0)])
        assert p1 != p2


class TestPuzzlePieceHashing:
    def test_can_be_added_to_set(self):
        p1 = PuzzlePiece([(0, 0), (1, 0), (0, 1)])
        p2 = PuzzlePiece([(0, 0), (0, 1), (1, 1)])
        piece_set = {p1, p2}
        assert len(piece_set) == 1

    def test_equal_pieces_deduplicate_in_set(self):
        p1 = PuzzlePiece([(0, 0), (1, 0), (0, 1)])
        p2 = PuzzlePiece([(0, 0), (0, 1), (1, 1)])
        p3 = PuzzlePiece([(0, 0), (1, 0), (1, 1)])
        piece_set = {p1, p2, p3}
        assert len(piece_set) == 1

    def test_different_pieces_remain_in_set(self):
        p1 = PuzzlePiece([(0, 0), (1, 0), (0, 1)])
        p2 = PuzzlePiece([(0, 0), (1, 0), (2, 0)])
        piece_set = {p1, p2}
        assert len(piece_set) == 2

    def test_can_be_used_as_dict_key(self):
        p1 = PuzzlePiece([(0, 0), (1, 0), (0, 1)])
        p2 = PuzzlePiece([(0, 0), (1, 0), (2, 0)])
        piece_dict = {p1: "first", p2: "second"}
        assert len(piece_dict) == 2

    def test_equal_pieces_map_to_same_dict_entry(self):
        p1 = PuzzlePiece([(0, 0), (1, 0), (0, 1)])
        p2 = PuzzlePiece([(0, 0), (0, 1), (1, 1)])
        piece_dict = {p1: "value"}
        assert piece_dict[p2] == "value"


class TestPuzzlePieceIteration:
    def test_can_iterate_transformations(self):
        p = PuzzlePiece([(0, 0), (1, 0), (0, 1)])
        count = 0
        for transform in p.transformations:
            assert isinstance(transform, frozenset)
            count += 1
        assert count > 0

    def test_all_transformations_are_frozensets(self):
        p = PuzzlePiece([(0, 0), (1, 0), (0, 1)])
        for transform in p.transformations:
            assert isinstance(transform, frozenset)

    def test_each_transformation_has_correct_cell_count(self):
        p = PuzzlePiece([(0, 0), (1, 0), (0, 1)])
        for transform in p.transformations:
            assert len(transform) == 3


class TestPuzzlePieceTransformationUniqueness:
    def test_l_shape_has_four_transformations(self):
        p = PuzzlePiece([(0, 0), (1, 0), (0, 1)])
        assert len(p.transformations) == 4

    def test_square_has_one_transformation(self):
        p = PuzzlePiece([(0, 0), (1, 0), (0, 1), (1, 1)])
        assert len(p.transformations) == 1

    def test_line_piece_has_two_transformations(self):
        p = PuzzlePiece([(0, 0), (1, 0), (2, 0)])
        assert len(p.transformations) == 2

    def test_asymmetric_piece_has_four_transformations(self):
        p = PuzzlePiece([(0, 0), (1, 0), (2, 0), (1, 1)])
        assert len(p.transformations) == 4

    def test_transformation_uniqueness_handles_all_symmetries(self):
        p1 = PuzzlePiece([(0, 0), (1, 0), (2, 0), (3, 0)])
        p2 = PuzzlePiece([(0, 0), (0, 1), (0, 2), (0, 3)])
        assert len(p1.transformations) == 2
        assert len(p2.transformations) == 2
        assert p1 == p2


class TestPuzzlePieceImmutability:
    def test_frozen_dataclass_prevents_attribute_modification(self):
        p = PuzzlePiece([(0, 0), (1, 0), (0, 1)])
        with pytest.raises(Exception):
            p.transformations = set()
