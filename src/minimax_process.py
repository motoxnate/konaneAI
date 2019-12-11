from multiprocessing import Process, Value

import minimax


class MinimaxProcess(Process):

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
            self._return.value = minimax.alpha_beta_helper(self._board, self._player, self._heuristic, self._depth, self._m)
        except KeyboardInterrupt:
            pass

        self._status = "FINISHED"

    def get_status(self):
        return self._status

    def get_return_value(self):
        return self._return.value


def parallel_minimax(board, player, heuristic_obj, depth, m=1):
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
    [p.start() for p in processes]
    [p.join() for p in processes]
    [p.close() for p in processes]
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
