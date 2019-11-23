from src.board import Board
from minimax import minimax
from src.minimax_process import parallel_minimax


def move_count_heuristic(board, player):
    return len(board.get_possible_moves(player))


def piece_difference_heuristic(board, player):
    return board.get_player_piece_count(player) - board.get_player_piece_count(-player)


def main():
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
                h, move = parallel_minimax(board, player, piece_difference_heuristic, 3, player)
            print("Selected move: " + str(move))

            # input("")
            if not board.do_move(move):
                raise ValueError("Invalid move: " + str(move))
            player *= -1
    except KeyboardInterrupt:
        pass
    print("Player", -1 * player, "Wins!")


if __name__ == "__main__":
    main()
