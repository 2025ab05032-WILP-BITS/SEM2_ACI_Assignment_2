import unittest
import sys
import os

# Ensure project root is on path so tests can import `solutionPS1`
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from solutionPS1 import find_best_move, board_to_tuple, minimax, get_valid_values

class TestSolution(unittest.TestCase):
    def test_sample_case(self):
        board = [
            [5,3,4,6,7,8,9,1,0],
            [6,7,2,1,9,5,3,4,8],
            [1,9,8,3,4,2,5,6,7],
            [8,5,9,7,6,1,4,2,3],
            [4,2,6,8,5,3,7,9,1],
            [7,1,3,9,2,4,8,5,6],
            [9,6,1,5,3,7,2,8,4],
            [2,8,7,4,1,9,6,3,5],
            [3,4,5,2,8,6,1,7,9],
        ]
        r, c, v, p1, p2 = find_best_move(board, 'P2')
        self.assertEqual((r, c, v, p2), (0, 8, 2, 2))

    def test_full_board_raises(self):
        full_board = [
            [5,3,4,6,7,8,9,1,2],
            [6,7,2,1,9,5,3,4,8],
            [1,9,8,3,4,2,5,6,7],
            [8,5,9,7,6,1,4,2,3],
            [4,2,6,8,5,3,7,9,1],
            [7,1,3,9,2,4,8,5,6],
            [9,6,1,5,3,7,2,8,4],
            [2,8,7,4,1,9,6,3,5],
            [3,4,5,2,8,6,1,7,9],
        ]
        with self.assertRaises(RuntimeError):
            find_best_move(full_board, 'P1')

    def test_no_valid_values_for_cell(self):
        # Construct a small scenario where cell (0,0) has no valid numbers
        board = [[0]*9 for _ in range(9)]
        # Fill row 0 with 1..8 except position 0
        for i, val in enumerate(range(1, 9), start=1):
            board[0][i] = val
        # Fill column 0 with 9 (already used in row), and subgrid fill ensures no 9 available
        board[1][0] = 9

        # Now (0,0) cannot take 1-9 because 1-8 are in the row and 9 is in the column
        vals = get_valid_values(board, 0, 0)
        self.assertEqual(vals, [])

    def test_minimax_terminal(self):
        # Full board terminal state should evaluate to 0 net change
        full_board = [
            [5,3,4,6,7,8,9,1,2],
            [6,7,2,1,9,5,3,4,8],
            [1,9,8,3,4,2,5,6,7],
            [8,5,9,7,6,1,4,2,3],
            [4,2,6,8,5,3,7,9,1],
            [7,1,3,9,2,4,8,5,6],
            [9,6,1,5,3,7,2,8,4],
            [2,8,7,4,1,9,6,3,5],
            [3,4,5,2,8,6,1,7,9],
        ]
        result = minimax(board_to_tuple(full_board), 'P1', {})
        self.assertEqual(result, 0)

    def test_minimax_small_board(self):
        # Small contrived board with single empty to keep minimax fast
        board = [
            [1,2,3,4,5,6,7,8,9],
            [4,5,6,7,8,9,1,2,3],
            [7,8,9,1,2,3,4,5,6],
            [2,3,4,5,6,7,8,9,1],
            [5,6,7,8,9,1,2,3,4],
            [8,9,1,2,3,4,5,6,7],
            [3,4,5,6,7,8,9,1,2],
            [6,7,8,9,1,2,3,4,5],
            [9,1,2,3,4,5,6,7,0],
        ]
        # Only one move left; minimax should be fast and deterministic
        res = minimax(board_to_tuple(board), 'P1', {})
        self.assertIsInstance(res, int)

if __name__ == '__main__':
    unittest.main()
