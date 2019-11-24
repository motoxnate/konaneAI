import unittest
import main
from board import Board


class TestCases(unittest.TestCase):
    def test_main(self):
        main.main(tester=self, test_board=True, test_moves=False)

    def valid_board_helper(self, board):
        self.assertTrue(board.is_valid_board())

    def valid_move_helper(self):
        pass


if __name__ == '__main__':
    unittest.main()
