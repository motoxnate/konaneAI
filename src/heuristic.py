import os
import random


class Heuristic:

    __CONST_FOLDER = "../const"

    def __init__(self):
        self._constraints = {}
        if os.path.exists(Heuristic.__CONST_FOLDER):
            self.load_constants_from_file()

    def heuristic(self, board, player):
        return 0

    def load_constants_from_file(self):
        lines = []
        with open(os.path.join(Heuristic.__CONST_FOLDER, self.__class__.__name__)) as file:
            lines = file.readlines()
        for line in lines:
            no_space_line = "".join(line.split(" "))
            values = no_space_line.split("=")
            self._constraints[values[0]] = values[1]

    def save_constants_to_file(self):
        lines = ["%s=%s" % (key, self._constraints[key]) for key in self._constraints.keys()]
        with open(os.path.join(Heuristic.__CONST_FOLDER, self.__class__.__name__)) as file:
            file.writelines(lines)

    def __setitem__(self, key, value):
        self._constraints[key] = value

    def __getitem__(self, item):
        """
        Should be used for getting constraints over self._constraints[key]
        :param item:
        :return:
        """
        if item in self._constraints:
            rand = random.Random()
            self._constraints[item] = rand.randint()
            return self._constraints[item]
        else:
            return self._constraints[item]


class MoveCountHeuristic(Heuristic):

    def heuristic(self, board, player):
        return len(board.get_possible_moves(player))


class PieceDifferenceHeuristic(Heuristic):

    def heuristic(self, board, player):
        return board.get_player_piece_count(player) - board.get_player_piece_count(-player)



