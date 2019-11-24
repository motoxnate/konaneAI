from src.board import Board
from minimax import minimax
from src.minimax_process import parallel_minimax


def move_count_heuristic(board, player):
    return len(board.get_possible_moves(player))


def piece_difference_heuristic(board, player):
    return board.get_player_piece_count(player) - board.get_player_piece_count(-player)


"""
Operational Modes

TRAINING:
Generate a list of random weights 

FINAL_EXAM:
Perform first and second moves
Alternate getting moves and sending next move
"""
__MODE = "TRAINING"


def main():

    if __MODE == "TRAINING":
        pass
    elif __MODE == "FINAL_EXAM":
        pass

    board = Board(size=18)
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
                    h, move = parallel_minimax(board, player, move_count_heuristic, 15, player)
                else:
                    h, move = parallel_minimax(board, player, piece_difference_heuristic, 15, player)
            print("Selected move: " + str(move))

            # input("")
            if not board.do_move(move):
                raise ValueError("Invalid move: " + str(move))
            player *= -1
    except KeyboardInterrupt:
        print("NO CONTEST!!!")
        exit()
    print("Player", -1 * player, "Wins!")


if __name__ == "__main__":
    main()
