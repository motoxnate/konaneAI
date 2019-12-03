from minimax_process import minimax


def minimax(board, player, heuristic_obj, depth, m=1):
    """
    Basic minimax algorithm for Konane
    :param board: Board object
    :param player: the player whose turn it is at the top level of the search tree
    :param heuristic_obj: heuristic to use
    :param depth: the max depth of the search tree
    :param m: 1 is starting at max, -1 is starting at min
    :return: (heuristic, move)
    """
    if depth == 0:
        return heuristic_obj.heuristic(board, player), None

    # Deriving new states
    moves = board.get_possible_moves(player)
    if len(moves) == 0:
        return heuristic_obj.heuristic(board, player), None
    states = board.get_possible_resultant_states(player, moves)

    weighted_moves = []
    for i in range(len(moves)):
        weight = minimax_helper(states[i], player, heuristic_obj, depth - 1, m * -1)
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
    """
    Minimax helper function
    :param board: Board object
    :param player: the player whose turn it is at the top level of the search tree
    :param heuristic_obj: heuristic to use
    :param depth: the max depth of the search tree
    :param m: 1 is starting at max, -1 is starting at min
    :return: heuristic
    """
    if depth == 0:
        return heuristic_obj.heuristic(board, player)

    # Deriving new states
    moves = board.get_possible_moves(player)
    if len(moves) == 0:
        return heuristic_obj.heuristic(board, player)
    states = board.get_possible_resultant_states(player, moves)

    weighted_moves = []
    for i in range(len(moves)):
        weight = minimax_helper(states[i], player, heuristic_obj, depth - 1, m * -1)
        weighted_moves.append((weight, moves[i]))

    # Finding the min or max weight
    func = max if m == 1 else min
    h_lim = weighted_moves[0][0]
    for h, m in weighted_moves:
        if func(h, h_lim) == h:
            h_lim = h
    return h_lim


def maximaxpp(board, player, heuristic_obj, depth):
    """
    Maximaxpp function. Instead of alternating min and max, the heuristic function instead evaluates each board state
    from the point of view of alternating players. Hence the name: Maximax-per-player.

    :param board: Board object
    :param player: the player whose turn it is at the top level of the search tree
    :param heuristic_obj: heuristic to use
    :param depth: the max depth of the search tree
    :return: (heuristic, move)
    """
    if depth == 0:
        return heuristic_obj.heuristic(board, player), None

    # Deriving new states
    moves = board.get_possible_moves(player)
    if len(moves) == 0:
        return heuristic_obj.heuristic(board, player), None
    states = board.get_possible_resultant_states(player, moves)

    weighted_moves = []
    for i in range(len(moves)):
        weight = maximaxpp_helper(states[i], player * -1, heuristic_obj, depth - 1)
        weighted_moves.append((weight, moves[i]))

    h_lim = weighted_moves[0][0]
    move = weighted_moves[0][1]
    for h, m in weighted_moves:
        if h > h_lim:
            h_lim = h
            move = m
    return h_lim, move


def maximaxpp_helper(board, player, heuristic_obj, depth):
    """
    Maximaxpp helper function
    :param board: Board object
    :param player: the player whose turn it is at the top level of the search tree
    :param heuristic_obj: heuristic to use
    :param depth: the max depth of the search tree
    :return: heuristic
    """
    if depth == 0:
        return heuristic_obj.heuristic(board, player)

    # Deriving new states
    moves = board.get_possible_moves(player)
    if len(moves) == 0:
        return heuristic_obj.heuristic(board, player)
    states = board.get_possible_resultant_states(player, moves)

    weighted_moves = []
    for i in range(len(moves)):
        weight = minimax_helper(states[i], player * -1, heuristic_obj, depth - 1)
        weighted_moves.append((weight, moves[i]))

    h_lim = weighted_moves[0][0]
    for h, m in weighted_moves:
        if h > h_lim:
            h_lim = h
    return h_lim


def alpha_beta_helper(board, player, heuristic_obj, depth, alpha=None, beta=None, m=1):
    if alpha is None:
        alpha = float("inf")
    if beta is None:
        beta = -float("inf")

    if depth == 0:
        return m * heuristic_obj.heuristic(board, player)

    # Deriving new states
    moves = board.get_possible_moves(player)
    if len(moves) == 0:
        return heuristic_obj.heuristic(board, player)
    states = board.get_possible_resultant_states(player, moves)

    if m == 1:
        # Maximizing player
        value = -float("inf")
        for state in states:
            value = max(value, alpha_beta_helper(state, player, heuristic_obj, depth - 1, alpha, beta, m * -1))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        # Minimizing player
        value = float("inf")
        for state in states:
            value = min(value, alpha_beta_helper(state, player, heuristic_obj, depth - 1, alpha, beta, m * -1))
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value
