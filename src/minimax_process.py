from multiprocessing import Process, Value, Pool

from minimax import alpha_beta_helper, alpha_beta_helper_pool


class MinimaxProcess(Process):
    """
    Class used in the parallel minimax function. Runs an alpha beta search in a single multiprocessing process.
    """

    MAX_PROCESSES = 32

    def __init__(self, board, player, heuristic, depth, m):
        super(MinimaxProcess, self).__init__()
        self._board = board
        self._player = player
        self._heuristic = heuristic
        self._depth = depth
        self._m = m
        self._return = Value('f', -1)
        self._status = "NOT_STARTED"

    def run(self):
        try:
            self._status = "RUNNING"
            self._return.value = alpha_beta_helper(self._board, self._player, self._heuristic, self._depth, self._m)
        except KeyboardInterrupt:
            pass

        self._status = "FINISHED"

    def get_status(self):
        return self._status

    def get_return_value(self):
        return self._return.value


def parallel_minimax(board, player, heuristic_obj, depth, m=1):
    """
    Divides the first layer of the children of the board state into multiple alpha beta calls and separates them
    between all cores on the machine. Slightly broken because of file limit.
    :param board: the root state
    :param player: the player whose turn it is at the root state
    :param heuristic_obj: the heuristic to use in alpha beta
    :param depth: the depth of the search tree
    :param m: 1 to start max, -1 to start min
    :return: (alpha beta of the best move, best move)
    """
    moves = board.get_possible_moves(player)
    if len(moves) == 0:
        return heuristic_obj.heuristic(board, player), None
    states = board.get_possible_resultant_states(player, moves)

    # Checking for knockout moves:
    for i in range(len(states)):
        if len(states[i].get_possible_moves(player * -1)) == 0:
            return float("inf"), moves[i]

    processes = [MinimaxProcess(state, player, heuristic_obj, depth - 1, m * -1) for state in
                 states]

    # Dividing into groups so we don't have too many processes running at once!
    m = MinimaxProcess.MAX_PROCESSES
    process_groups = [processes[i * m: (i+1) * m] for i in range(int(len(processes) / m) + 1)]
    for group in process_groups:
        [p.start() for p in group]
        [p.join() for p in group]

    weighted_moves = [(processes[i].get_return_value(), moves[i]) for i in range(len(moves))]

    # Finding the min or max weight
    func = max if m == 1 else min
    h_lim = weighted_moves[0][0]
    move = weighted_moves[0][1]
    for h, m in weighted_moves:
        if func(h, h_lim) == h:
            h_lim = h
            move = m
    # print(weighted_moves, h_lim, move)
    return h_lim, move


def parallel_minimax_pool(board, player, heuristic_obj, depth, m=1, pool=None):
    """
    Divides the first layer of the children of the board state into multiple alpha beta calls and separates them
    between all cores on the machine. Uses process pools because they are more stable.
    :param board: the root state
    :param player: the player whose turn it is at the root state
    :param heuristic_obj: the heuristic to use in alpha beta
    :param depth: the depth of the search tree
    :param m: 1 to start max, -1 to start min
    :param pool: optional parameter to specify a process pool to use. If not specificed, one will be created with all
    cores in use.
    :return: (alpha beta of the best move, best move)
    """
    moves = board.get_possible_moves(player)
    if len(moves) == 0:
        return heuristic_obj.heuristic(board, player), None
    states = board.get_possible_resultant_states(player, moves)

    # Checking for knockout moves:
    for i in range(len(states)):
        if len(states[i].get_possible_moves(player * -1)) == 0:
            return float("inf"), moves[i]

    if pool is None:
        with Pool() as pool:
            heuristics = pool.map(alpha_beta_helper_pool, [(state, player, heuristic_obj, depth - 1, m * -1) for state in states])
    else:
        heuristics = pool.map(alpha_beta_helper_pool,
                              [(state, player, heuristic_obj, depth - 1, m * -1) for state in states])
    weighted_moves = [(heuristics[i], moves[i]) for i in range(len(moves))]

    # Finding the min or max weight
    func = max if m == 1 else min
    h_lim = weighted_moves[0][0]
    move = weighted_moves[0][1]
    for h, m in weighted_moves:
        if func(h, h_lim) == h:
            h_lim = h
            move = m
    # print(weighted_moves, h_lim, move)
    return h_lim, move
