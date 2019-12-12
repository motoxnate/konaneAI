import os
import random
from scipy.stats import truncnorm


class Heuristic:

    __CONST_FOLDER = "../const"

    __UNIFORM_LOWER = 0
    __UNIFORM_UPPER = 1

    __NORM_MEAN = 0.5
    __NORM_SD = 0.2
    __NORM_LOWER = 0
    __NORM_UPPER = 1

    def __init__(self, randomized_constraints=[], randomness=False):
        """
        Constructor to initialize a new heuristic
        :param randomized_constraints: a list of keys to use as heuristic state values
        :param randomness: False by default and to use constraints loaded from file, NORMAL to randomize constraints
        using a normal distribution. UNIFORM to use uniformly random constraints
        """
        self._constraints = {}
        if os.path.isfile(self.get_file_name()):
            self.load_constants_from_file()

        if randomness == "NORMAL":
            for key in randomized_constraints:
                """Normal distribution centered on mu, with sigma std deviation
                mu = current parameter, so we focus more on heuristics we know are better."""
                self[key] = Heuristic.get_truncated_normal()
        elif randomness == "UNIFORM":
            rand = random.Random()
            for key in randomized_constraints:
                self[key] = rand.uniform(Heuristic.__UNIFORM_LOWER, Heuristic.__UNIFORM_UPPER)

    def heuristic(self, board, player):
        return 0

    @staticmethod
    def get_truncated_normal(mean=None, sd=None, low=None, upp=None):
        mean = Heuristic.__NORM_MEAN if mean is None else mean
        sd = Heuristic.__NORM_SD if sd is None else sd
        low = Heuristic.__NORM_LOWER if low is None else low
        upp = Heuristic.__NORM_UPPER if upp is None else upp
        return truncnorm(
            (low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)

    def get_file_name(self):
        return os.path.join(Heuristic.__CONST_FOLDER, self.__class__.__name__ + ".const")

    def load_constants_from_file(self, static=False):
        if static:
            with open(static, "r") as file:
                lines = file.readlines()
        else:
            with open(self.get_file_name(), "r") as file:
                lines = file.readlines()
        for line in lines:
            no_space_line = "".join(line.split(" "))
            values = no_space_line.split("=")
            self._constraints[values[0]] = float(values[1])

    def save_constants_to_file(self):
        lines = ["%s=%f\n" % (key, self._constraints[key]) for key in self._constraints.keys()]
        with open(self.get_file_name(), "w+") as file:
            file.writelines(lines)
            file.close()

    def save_data_point(self):
        with open(self.get_file_name() + ".csv", "a+") as file:
            for key in self:
                file.write(str(self[key]) + ",")
            file.write("\n")
            file.close()

    def __setitem__(self, key, value):
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
        move_nums = [n, -n, n, -n]
        h = sum([move_nums[i] * constants[i] * heuristics[i] for i in range(len(heuristics))])
        return h

    # def __str__(self):
    #     return " ".join(["%s=%f" % (key, self[key]) for key in self._constraints.keys()])
