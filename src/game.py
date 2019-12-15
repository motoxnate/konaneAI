from multiprocessing import Pool

from board import Board
from minimax_process import parallel_minimax_pool


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
    pool = Pool()
    while True:
        moves = board.get_possible_moves(player=player)
        if len(moves) == 0:
            break
        h = 0
        if board.get_move_number() < 2:
            move = moves[0]
        else:
            if player == 1:
                h, move = parallel_minimax_pool(board, player, heuristic_obj_1, depth, pool=pool)
            else:
                h, move = parallel_minimax_pool(board, player, heuristic_obj_2, depth, pool=pool)

        if verbose:
            print("\n")
            board.print()
            print(h, move)
        else:
            if board.get_move_number() % 5 == 0:
                print(board.get_move_number(), end=" ", flush=True)

        if not board.do_move(move):
            raise ValueError("Invalid move: " + str(move))
        player *= -1
    pool.close()
    return -player, board.get_move_number()


def do_games(game_number, heuristic_obj_1, heuristic_obj_2, depth=5, size=18, verbose=False):
    wins1 = 0
    wins2 = 0
    total_move_numbers = 0
    player = 1
    for i in range(game_number):
        winner, move_number = do_game(heuristic_obj_1, heuristic_obj_2, depth, size, player, verbose)
        if winner == 1:
            wins1 += 1
        else:
            wins2 += 1
        total_move_numbers += move_number
        player *= -1
        print()
    return wins1, wins2, total_move_numbers
