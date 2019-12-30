import argparse
import numpy as np
from multiprocessing import Pool
try:
    from src.board import Board
    from src.heuristic import *
    from src.artemis_client import ArtemisClient
    from src.game import do_game, do_games
    from src.GUI import *
except ModuleNotFoundError:
    from board import Board
    from heuristic import *
    from artemis_client import ArtemisClient
    from game import do_game, do_games
    from GUI import *

"""
Operational Modes

TRAINING:
Generate a list of random weights 

HEURISTIC_COMPETITION:
Runs a competition between two different heuristics to see which performs better

HUMAN_PLAYER:
Graphics window pops up and the human user can play against the AI

SERVER_ONE_AI_PLAY:
Code that uses the artemis client class to communicate with the final exam server. Probably won't be a useful mode 
outside of the final exam date.
"""

DEPTH = 5
SIZE = 18
_X = _Y = 600
TRAINING_SIZE = 18
TRAINING_DEPTH = 5
GRAPHICS = True
USER = "5555"
OPPONENT = "4444"


def main(tester=None, test_board=False, test_moves=False):
    __MODE = "SERVER_ONE_AI_PLAY"
    """Begin Main"""
    if __MODE == "TRAINING":
        learning_heuristic1 = MCPDLearningHeuristic()
        session_number = 0

        try:
            while True:
                """
                Playing training games indefinitely.

                Player 1 always has the more favorable heuristic settings
                If player -1 wins, then player 1 gets player -1's settings and a new set of settings are generated for
                player -1.
                """
                learning_heuristic2 = MCPDLearningHeuristic(randomness="UNIFORM")
                print("Player 1: %s\nPlayer -1: %s" % (str(learning_heuristic1), str(learning_heuristic2)))
                starting_player = -1 if session_number % 2 == 0 else 1
                cur = time.time()

                winner, move_count = do_game(learning_heuristic1, learning_heuristic2, depth1=1, depth2=2, size=18,
                                             player=starting_player, verbose=False)
                print("\nPlayer %d won in %d turns in %d seconds" % (winner, move_count, time.time() - cur))

                # Checking to see who won, setting the winning value to the first slot, and saving it.
                if winner == -1:
                    print("=========> New settings: %s <=========" % str(learning_heuristic2))
                    learning_heuristic1 = learning_heuristic2
                    learning_heuristic1.save_constants_to_file()
                else:
                    learning_heuristic1.save_data_point()
                session_number += 1
                print("Session %d complete\n" % session_number)

        except KeyboardInterrupt:
            print("\nNormal Exit, %d training sessions run." % session_number)
    elif __MODE == "HEURISTIC_COMPETITION":

        # Change these to compare different heuristics
        h1 = MoveCountHeuristic()
        h2 = PieceDifferenceHeuristic()
        total_games = 5

        wins1, wins2, total_turns = do_games(total_games, h1, h2, depth1=5, depth2=5, size=18)

        message = """
        
        Heuristic Competition Finished!
        %d Games played, %d turns played, about %f turns on average per game
        %d Player 1 wins, about %d%% of the time
        %d Player -1 wins, about %d%% of the time
        """ % (total_games, total_turns, total_turns / total_games, wins1, int(wins1 / total_games * 100), wins2,
               int(wins2 / total_games * 100))
        print(message)

    elif __MODE == "HUMAN_PLAYER":
        """
        Creates a graphical interface for the user to play against an AI with.
        """
        pass

    elif __MODE == "SERVER_ONE_AI_PLAY":
        pieces = None
        if GRAPHICS:
            gui_object = GUI(_X, _Y, SIZE)
        client = ArtemisClient(gui=gui_object)
        p, w, b, t = client.do_server_connection(MCPDLearningHeuristic(), 0, verbose=True, username=USER,
                                                 opponent=OPPONENT,
                                                 depth=25)
        print("\n\nGame finished, played as %d, player %d won, remaining time: %f" % (p, w, t))
        b.print()

    else:
        print("Invalid mode: %s" % __MODE)


def get_mode(path="../const/MODE.txt"):
    with open(path, "r") as file:
        lines = file.readlines()
    return lines[0]


def set_mode(mode, path="../const/MODE.txt"):
    with open(path, "w") as file:
        file.write(mode)
    return True


def button_click(mouse, rectangle):
    """Check if a point is inside a rectangle"""
    ul = rectangle.getP1()
    lr = rectangle.getP2()
    return (ul.getX() < mouse.getX() < lr.getX()) and (ul.getY() < mouse.getY() < lr.getY())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-username", "-u", type=str, help="Username")
    parser.add_argument("-opponent", "-o", type=str, help="Opponent")
    parser.add_argument("-graphics", "-g", type=bool, help="Graphics")
    args = parser.parse_args()
    if args.username:
        # print("Username:", args.username)
        USER = PASS = args.username
    if args.opponent:
        # print("Opponent:", args.opponent)
        OPPONENT = args.opponent
    GRAPHICS = (True if args.graphics else False)
    main()
