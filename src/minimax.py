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


def minimax(board, player, heuristic_obj, depth, m=1):
    if depth == 0:
        return heuristic_obj.heuristic(board, player), None

    # Deriving new states
    moves = board.get_possible_moves(player)
    if len(moves) == 0:
        return heuristic_obj.heuristic(board, player), None
    states = board.get_possible_resultant_states(player, moves)

    weighted_moves = []
    for i in range(len(moves)):
        weight = minimax_helper(states[i], player * -1, heuristic_obj, depth - 1, m * -1)
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


def minimax_helper(board, player, heuristic_obj, depth, m=1):
    if depth == 0:
        return heuristic_obj.heuristic(board, player)

    # Deriving new states
    moves = board.get_possible_moves(player)
    if len(moves) == 0:
        return heuristic_obj.heuristic(board, player)
    states = board.get_possible_resultant_states(player, moves)

    weighted_moves = []
    for i in range(len(moves)):
        weight = minimax_helper(states[i], player * -1, heuristic_obj, depth - 1, m * -1)
        weighted_moves.append((weight, moves[i]))

    # Finding the min or max weight
    func = max if m == 1 else min
    h_lim = weighted_moves[0][0]
    for h, m in weighted_moves:
        if func(h, h_lim) == h:
            h_lim = h
    return h_lim


"""
if maximizingPlayer then
        value := −∞
        for each child of node do
            value := max(value, alphabeta(child, depth − 1, α, β, FALSE))
            α := max(α, value)
            if α ≥ β then
                break (* β cut-off *)
        return value
    else
        value := +∞
        for each child of node do
            value := min(value, alphabeta(child, depth − 1, α, β, TRUE))
            β := min(β, value)
            if α ≥ β then
                break (* α cut-off *)
        return value
"""
def alpha_beta_helper(board, player, heuristic_obj, depth, alpha=None, beta=None, m=1):
    if alpha is None:
        alpha = float("inf")
    if beta is None:
        beta = -float("inf")

    if depth == 0:
        return heuristic_obj.heuristic(board, player)

    # Deriving new states
    moves = board.get_possible_moves(player)
    if len(moves) == 0:
        return heuristic_obj.heuristic(board, player)
    states = board.get_possible_resultant_states(player, moves)

    if m == 1:
        # Maximizing player
        value = -float("inf")
        for state in states:
            value = max(value, alpha_beta_helper(state, player * -1, heuristic_obj, depth - 1, alpha, beta, m * -1))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        # Minimizing player
        value = float("inf")
        for state in states:
            value = min(value, alpha_beta_helper(state, player * -1, heuristic_obj, depth - 1, alpha, beta, m * -1))
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value
