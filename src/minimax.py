
def minimax(board, player, heuristic, depth, m=1):
    func = max if m == 1 else min
    states = board.get_possible_resultant_states(player)
    if depth == 0:
        func_state, funced = states[0], heuristic(states[0])
    else:
        return func([minimax(state, player * -1, heuristic, depth - 1, m * -1) for state in states])
