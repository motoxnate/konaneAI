"""
File for AI algorithm definitions
"""
from minimax_process import minimax


"""
Basic minimax algorithm for Konane

:param board: the board object to use
:param heuristic: static evaluation function(board, player)
:return heuristic, move
"""
def minimax(board, player, heuristic, depth, m=1):
    if depth == 0:
        return heuristic(board, player), None

    # Deriving new states
    moves = board.get_possible_moves(player)
    if len(moves) == 0:
        return heuristic(board, player), None
    states = board.get_possible_resultant_states(player, moves)

    weighted_moves = []
    for i in range(len(moves)):
        weight = minimax_helper(states[i], player * -1, heuristic, depth - 1, m * -1)
        weighted_moves.append((weight, moves[i]))

    # Finding the min or max weight
    func = max if m == 1 else min
    h_lim = weighted_moves[0][0]
    move = weighted_moves[0][1]
    for h, m in weighted_moves:
        if func(h, h_lim) == h:
            h_lim = h
            move = m
    return h_lim, move


def minimax_helper(board, player, heuristic, depth, m=1):
    if depth == 0:
        return heuristic(board, player)

    # Deriving new states
    moves = board.get_possible_moves(player)
    if len(moves) == 0:
        return heuristic(board, player)
    states = board.get_possible_resultant_states(player, moves)

    weighted_moves = []
    for i in range(len(moves)):
        weight = minimax_helper(states[i], player * -1, heuristic, depth - 1, m * -1)
        weighted_moves.append((weight, moves[i]))

    # Finding the min or max weight
    func = max if m == 1 else min
    h_lim = weighted_moves[0][0]
    for h, m in weighted_moves:
        if func(h, h_lim) == h:
            h_lim = h
    return h_lim
