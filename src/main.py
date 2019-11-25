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


def do_game(heuristic_obj_1, heuristic_obj_2, depth=5, size=18, player=1, verbose=False):
    """
    Completes a game with the given inputs
    :param heuristic_obj_1: player 1's heuristic
    :param heuristic_obj_2: player -1's heuristic
    :param depth:
    :param size:
    :param player: the starting player
    :param verbose:
    :return: the winning player of the game tupled with the turn count
    """
    board = Board(size=size)
    while True:
        moves = board.get_possible_moves(player=player)
        if len(moves) == 0:
            break
        h = 0
        if board.get_move_number() < 2:
            move = moves[0]
        else:
            if player == 1:
                h, move = parallel_minimax(board, player, heuristic_obj_1, depth)
            else:
                h, move = parallel_minimax(board, player, heuristic_obj_2, depth)

        if verbose:
            print("\n")
            board.print()
            print(h, move)
        else:
            if board.get_move_number() % 5 == 0:
                print(board.get_move_number(), end=" ")

        if not board.do_move(move):
            raise ValueError("Invalid move: " + str(move))
        player *= -1
    return -player, board.get_move_number()


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
                starting_player = -1 if session_number % 2 == 0 else 1
                cur = time.time()

                winner, move_count = do_game(learning_heuristic1, learning_heuristic2, size=6, player=starting_player, verbose=False)
                print("\nPlayer %d won in %d turns in %d seconds" % (winner, move_count, time.time() - cur))

                # Checking to see who won, setting the winning value to the first slot, and saving it.
                if winner == -1:
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
