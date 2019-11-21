
"""
File for AI algorithm definitions
"""


"""
Basic minimax algorithm for Konane

:param board: the board object to use
:param heuristic: static evaluation function(board, player)
:return heuristic, move
"""
def minimax(board, player, heuristic, depth, m=1):
    if depth == 0:
        return heuristic(board, player)

    # Deriving new states
    moves = board.get_possible_moves(player)
    if len(moves) == 0:
        return heuristic(board, player)
    states = board.get_possible_resultant_states(player, moves)

    weighted_moves = []
    for i in range(len(moves)):
        weighted_move = minimax(states[i], player * -1, heuristic, depth - 1, m * -1)
        if type(weighted_move) is tuple:
            weighted_move = (weighted_move[0], moves[i])
        else:
            weighted_move = (weighted_move, moves[i])
        weighted_moves.append(weighted_move)

    # Finding the min or max weight
    func = max if m == 1 else min
    h_lim = weighted_moves[0][0]
    move = weighted_moves[0][1]
    for h, m in weighted_moves:
        if func(h, h_lim) == h:
            h_lim = h
            move = m
    return h_lim, move
