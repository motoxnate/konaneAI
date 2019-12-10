import os
import random
from scipy.stats import truncnorm


class Heuristic:

    __CONST_FOLDER = "../const"

    def __init__(self, randomized_constraints=[], randomness=False):
        self._constraints = {}
        if os.path.isfile(self.get_file_name()) and not randomness:
            self.load_constants_from_file()
        elif randomness == "NORMAL":
            self.load_constants_from_file(static=True)
            for key in randomized_constraints:
                """Normal distribution centered on mu, with sigma std deviation
                mu = current parameter, so we focus more on heuristics we know are better."""
                gen = self.get_truncated_normal(self, mean=self._constraints[key], sd=0.2, low=0, upp=1)
                self._constraints[key] = gen.rvs()
        elif randomness == "2":
            if not self.load_previous_constants(2):
                raise ValueError
        elif randomness == "3":
            if not self.load_previous_constants(3):
                raise ValueError
        elif randomness == "UNIFORM":
            rand = random.Random()
            for key in randomized_constraints:
                self._constraints[key] = rand.uniform(0, 1)
        else:
            pass

    def heuristic(self, board, player):
        return 0

    @staticmethod
    def get_truncated_normal(self, mean=0, sd=1, low=0, upp=10):
        return truncnorm(
            (low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)

    def get_file_name(self):
        return os.path.join(Heuristic.__CONST_FOLDER, self.__class__.__name__ + ".const")

    def load_constants_from_file(self, static=False):
        if static:
            with open("../const/MCPDLearningHeuristic.const", "r") as file:
                lines = file.readlines()
        else:
            with open(self.get_file_name(), "r") as file:
                lines = file.readlines()
        for line in lines:
            no_space_line = "".join(line.split(" "))
            values = no_space_line.split("=")
            self._constraints[values[0]] = float(values[1])

    def load_previous_constants(self, i):
        with open("../const/MCPDLearningHeuristic.const.csv", "r") as file:
            lines = file.readlines()
        x = -1
        """Starting at lines[-1], check if the last two are the same. 
        If i = 3, then must look for the previous again."""
        try:
            for y in range(i-1):
                while lines[x] == lines[x - 1]:
                    print("loop", y)
                    x -= 1
                x -= 1

            line = lines[x]
            line = line.split(',')
            self._constraints["mc1"] = float(line[0])
            self._constraints["mc2"] = float(line[1])
            self._constraints["pd1"] = float(line[2])
            self._constraints["pd2"] = float(line[3])
            return True

        except IndexError:
            return False

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


class MoveCountHeuristic(Heuristic):

    def heuristic(self, board, player):
        return len(board.get_possible_moves(player))


class PieceDifferenceHeuristic(Heuristic):

    def heuristic(self, board, player):
        return board.get_player_piece_count(player) - board.get_player_piece_count(-player)


class MCPDLearningHeuristic(Heuristic):

    def __init__(self, randomness=False):
        super(MCPDLearningHeuristic, self).__init__(randomized_constraints=["mc1", "mc2", "pd1", "pd2"], randomness=randomness)
        print("Test:", randomness)
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

    def __str__(self):
        return " ".join(["%s=%f" % (key, self[key]) for key in self._constraints.keys()])
