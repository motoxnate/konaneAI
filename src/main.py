import time

from src.board import Board
from src.heuristic import *
from minimax import minimax
from src.minimax_process import parallel_minimax


"""
Operational Modes

TRAINING:
Generate a list of random weights 

FINAL_EXAM:
Perform first and second moves
Alternate getting moves and sending next move
"""
__MODE = "TRAINING"


def main(tester=None, test_board=False, test_moves=False):

    if __MODE == "TRAINING":
        learning_heuristic1 = MCPDLearningHeuristic()
        session_number = 0

        try:
            while True:
                """
                Playing one game

                Player 1 always has the more favorable heuristic settings
                If player -1 wins, then player 1 gets player -1's settings and a new set of settings are generated for
                player -1.
                """
                learning_heuristic2 = MCPDLearningHeuristic(always_random=True)
                print("Player 1: %s\nPlayer -1: %s" % (str(learning_heuristic1), str(learning_heuristic2)))
                board = Board(size=10)
                player = -1 if session_number % 2 == 0 else 1
                cur = time.time()
                while True:
                    if board.get_move_number() % 5 == 0:
                        print(board.get_move_number(), end=" ")

                    moves = board.get_possible_moves(player=player)
                    if len(moves) == 0:
                        break
                    move = ((0, 0), None)
                    h = 0
                    if board.get_move_number() < 2:
                        move = moves[0]
                    else:
                        if player == 1:
                            h, move = parallel_minimax(board, player, learning_heuristic1, 5)
                        else:
                            h, move = parallel_minimax(board, player, learning_heuristic2, 5)

                    # print("\n")
                    # board.print()
                    # print(h, move)

                    if not board.do_move(move):
                        raise ValueError("Invalid move: " + str(move))
                    player *= -1
                print("\nPlayer %d lost in %d turns in %d seconds" % (player, board.get_move_number(), time.time() - cur))

                # Checking to see who won, setting the winning value to the first slot, and saving it.
                if player == 1:
                    print("=========> New settings: %s <=========" % str(learning_heuristic2))
                    learning_heuristic1 = learning_heuristic2
                    learning_heuristic1.save_constants_to_file()
                else:
                    learning_heuristic1.save_data_point()
                session_number += 1
                print("Session %d complete\n" % session_number)
                # input("")
        except KeyboardInterrupt:
            print("\nNormal Exit, %d training sessions run." % session_number)
        exit(0)
    elif __MODE == "FINAL_EXAM":
        pass

    board = Board(size=18)
    move_count_heuristic = MoveCountHeuristic()
    piece_difference_heuristic = PieceDifferenceHeuristic()
    learning_heuristic1 = MCPDLearningHeuristic()
    learning_heuristic2 = MCPDLearningHeuristic()
    player = 1
    try:
        while True:
            board.print()
            print(board.get_move_number(), "Turn:", player)
            moves = board.get_possible_moves(player=player)
            if len(moves) == 0:
                break
            print("\n".join([str((move, board.is_valid_move(move, player=player), board.captured_pieces_for_move(move, player), board.get_num_pieces(player))) for move in moves]))

            move = ((0, 0), None)
            if board.get_move_number() < 2:
                move = moves[0]
            else:
                if player == 1:
                    h, move = parallel_minimax(board, player, learning_heuristic1, 5, player)
                else:
                    h, move = parallel_minimax(board, player, learning_heuristic2, 5, player)
            print("Selected move: " + str(move))

            if test_moves is True:
                board_a = board.get_array()
            # input("")
            if not board.do_move(move):
                raise ValueError("Invalid move: " + str(move))
            # A few unit tests
            if test_board is True:
                tester.valid_board_helper(board)
            if test_moves is True:
                pass
            player *= -1
    except KeyboardInterrupt:
        print("NO CONTEST!!!")
        exit()
    print("Player", -1 * player, "Wins!")


if __name__ == "__main__":
    main()
