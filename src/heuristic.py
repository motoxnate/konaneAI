import os
import random


class Heuristic:
    """
    Heuristic Class

    Meant to be overriden to add new heuristics to use with minimax or alphabeta. Also contains methods for loading and
    saving static values from and to files. By default this file will be named: <Class-name>.const
    """

    __CONST_FOLDER = "../const"

    __UNIFORM_LOWER = 0
    __UNIFORM_UPPER = 1

    def __init__(self, randomized_constraints=[], randomness=False):
        """
        Constructor to initialize a new heuristic
        :param randomized_constraints: a list of keys to use as heuristic state values. Don't specify if you want to
        use the ones loaded from the file
        :param randomness: False by default and to use constraints loaded from file, NORMAL to randomize constraints
        using a normal distribution. UNIFORM to use uniformly random constraints
        """
        self._constraints = {}
        if os.path.isfile(self.get_file_name()):
            self.load_constants_from_file()

        if randomness:
            rand = random.Random()
            for key in randomized_constraints:
                self[key] = rand.uniform(Heuristic.__UNIFORM_LOWER, Heuristic.__UNIFORM_UPPER)

    def heuristic(self, board, player):
        """
        The function to override for defining a new heuristic
        :param board: the board state to evaluate
        :param player: the player to evaluate the board state for
        :return: the heuristic value based on the board state and the player to evaluate for. The higher this value, the
        better the evaluated board state for the given player.
        """
        return 0

    def get_file_name(self):
        return os.path.join(Heuristic.__CONST_FOLDER, self.__class__.__name__ + ".const")

    def load_constants_from_file(self, file_name=None):
        """
        Loads static values from a file
        :param file_name: optional argument for specifing the file name
        """
        if file_name is not None:
            with open(file_name, "r") as file:
                lines = file.readlines()
        else:
            with open(self.get_file_name(), "r") as file:
                lines = file.readlines()
        for line in lines:
            no_space_line = "".join(line.split(" "))
            values = no_space_line.split("=")
            self._constraints[values[0]] = float(values[1])

    def save_constants_to_file(self, file_name=None):
        """
        Saves the current static values to a file
        """
        lines = ["%s=%f\n" % (key, self._constraints[key]) for key in self._constraints.keys()]
        with open(file_name if file_name else self.get_file_name(), "w+") as file:
            file.writelines(lines)
            file.close()

    def save_data_point(self):
        with open(self.get_file_name() + ".csv", "a+") as file:
            for key in self:
                file.write(str(self[key]) + ",")
            file.write("\n")
            file.close()

    def __setitem__(self, key, value):
        """
        Used for setting state values.
        :param key: the name of the static value
        :param value: the value to set to
        :return:
        """
        self._constraints[key] = value

    def __getitem__(self, item):
        """
        Should be used for getting constraints over self._constraints[key]
        :param item:
        :return:
        """
        if item not in self._constraints:
            return 0
        else:
            return self._constraints[item]

    def __iter__(self):
        return iter(self._constraints.keys())

    def __str__(self):
        return "%s with constraints %s" % (self.__class__.__name__, str(self._constraints))


class MoveCountHeuristic(Heuristic):

    def heuristic(self, board, player):
        return len(board.get_possible_moves(player))


class PieceDifferenceHeuristic(Heuristic):

    def heuristic(self, board, player):
        return board.get_player_piece_count(player) - board.get_player_piece_count(-player)


class MCPDLearningHeuristic(Heuristic):
    """
    Combination of the move count and piece difference heuristics.

    The heuristic is the dot product of the static values and two two of each heuristic.
    Testing was also done to factor in the move numbers, but this idea was scrapped because it didn't work as
    consistently.
    """

    def __init__(self, randomness=False):
        super(MCPDLearningHeuristic, self).__init__(randomized_constraints=["mc1", "mc2", "pd1", "pd2"], randomness=randomness)
        self.move_count_h = MoveCountHeuristic()
        self.piece_diff_h = PieceDifferenceHeuristic()

    def heuristic(self, board, player):
        n = board.get_move_number()
        move_count = self.move_count_h.heuristic(board, player)
        piece_diff = self.piece_diff_h.heuristic(board, player)

        heuristics = [move_count, move_count, piece_diff, piece_diff]
        constants = [self["mc1"], self["mc2"], self["pd1"], self["pd2"]]
        move_nums = [1, 1, 1, 1 ] # [n, -n, n, -n]
        h = sum([move_nums[i] * constants[i] * heuristics[i] for i in range(len(heuristics))])
        return h
