import argparse
from graphics import *
import numpy as np
from multiprocessing import Pool

try:
    from src.board import Board
    from src.heuristic import *
    from src.artemis_client import ArtemisClient
    from src.game import do_game, do_games
except ModuleNotFoundError:
    from board import Board
    from heuristic import *
    from artemis_client import ArtemisClient
    from game import do_game, do_games

"""
Operational Modes

TRAINING:
Generate a list of random weights 

HEURISTIC_COMPETITION:
Runs a competition between two different heuristics to see which performs better

FINAL_EXAM:
Perform first and second moves
Alternate getting moves and sending next move
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
        client = ArtemisClient()
        if GRAPHICS:
            pieces = setup_game_window(_X, _Y)
        else:
            pieces = np.zeros((SIZE, SIZE))
        p, w, b, t = client.do_server_connection(MCPDLearningHeuristic(), 0, verbose=True, username=USER,
                                                 opponent=OPPONENT,
                                                 depth=25)
        print("\n\nGame finished, played as %d, player %d won, remaining time: %f" % (p, w, t))
        b.print()

    else:
        print("Invalid mode: %s" % __MODE)


def setup_game_window(x, y):
    """Setup for graphics window
    :param x: x resolution
    :param y: y resolution"""
    game_window = GraphWin("AI Settings", x, y)
    game_window.setBackground(color_rgb(210, 210, 210))
    """Grid"""
    lines = []
    for i in range(1, SIZE):
        lines.append(Line(Point(i * x / SIZE, 0), Point(i * x / SIZE, y)))
        lines.append(Line(Point(0, i * x / SIZE), Point(x, i * y / SIZE)))
    for line in lines:
        line.draw(game_window)

    """Game Pieces
       White: 1, Black: -1"""
    pieces = np.ndarray((SIZE, SIZE), dtype=Circle)
    half = x / SIZE / 2
    rad = half - 5
    for i in range(0, SIZE, 2):  # Column
        for j in range(1, SIZE, 2):  # Row
            # Whites
            pieces[i][j] = Circle(Point(
                (i * x / SIZE) + half,
                (j * y / SIZE) + half), rad)
            pieces[i][j].setFill("white")
            pieces[i][j].draw(game_window)
            # Blacks
            pieces[i][j - 1] = Circle(Point(
                (i * x / SIZE) + half,
                ((j - 1) * y / SIZE) + half), rad)
            pieces[i][j - 1].setFill("black")
            pieces[i][j - 1].draw(game_window)

    for i in range(1, SIZE, 2):
        for j in range(0, SIZE, 2):
            # Whites
            pieces[i][j] = Circle(Point(
                (i * x / SIZE) + half,
                (j * y / SIZE) + half), rad)
            pieces[i][j].setFill("white")
            pieces[i][j].draw(game_window)
            # Blacks
            pieces[i][j + 1] = Circle(Point(
                (i * x / SIZE) + half,
                ((j + 1) * y / SIZE) + half), rad)
            pieces[i][j + 1].setFill("black")
            pieces[i][j + 1].draw(game_window)
    return pieces


def graphics_move(pieces, move):
    print("Graphics:", move)
    # If removal
    if move[1] is None:
        (c, r) = move[0]
        pieces[r][c].undraw()
        return True

    # If normal move
    ((c1, r1), (c2, r2)) = move
    piece1 = pieces[r1][c1]
    piece2 = pieces[r2][c2]
    start_coords = (piece1.getCenter().getX(), piece1.getCenter().getY())
    end_coords = (piece2.getCenter().getX(), piece2.getCenter().getY())
    print("Start:", start_coords)
    print("End:", end_coords)
    movement = (end_coords[0]-start_coords[0], end_coords[1]-start_coords[1])
    if not (r1 == r2 or c1 == c2):
        raise ValueError

    if r1 == r2:
        # Columns are different:
        min_col = min(c1, c2)
        max_col = max(c1, c2)
        for c in range(min_col, max_col):
            pieces[r1][c].undraw()

    else:
        # Rows are different:
        min_row = min(r1, r2)
        max_row = max(r1, r2)
        for r in range(min_row, max_row):
            pieces[r][c1].undraw()

    piece1.move(movement[0], movement[1])
    pieces[c2][r2] = piece1


def options_window():
    pass
    # """Setup for graphics window"""
    # main_window = GraphWin("AI Settings", 500, 400)
    # main_window.setBackground(color_rgb(210, 210, 210))
    #
    # headline = Text(Point(250, 20), "AI Settings")
    # headline.setFace("arial")
    # headline.setSize(18)
    # headline.draw(main_window)
    #
    # run_button = Rectangle(Point(400, 350), Point(480, 380))
    # run_button.setFill(color_rgb(161, 255, 165))
    # run_button.draw(main_window)
    # run_text = Text(Point(440, 365), "Run")
    # run_text.draw(main_window)
    #
    # heuristic_label = Text(Point(60, 50), "Heuristic Mode: ")
    # heuristic_label.setSize(14)
    # heuristic_label.draw(main_window)
    # heuristic_outline = Rectangle(Point(120, 35), Point(320, 65))
    # heuristic_outline.setFill(color_rgb(255, 233, 161))
    # heuristic_outline.draw(main_window)
    # heuristic_stat = Text(Point(220, 50), __MODE)
    # heuristic_stat.setSize(14)
    # heuristic_stat.draw(main_window)
    #
    # blue = color_rgb(161, 211, 255)
    # training_button = Rectangle(Point(20, 70), Point(150, 100))
    # training_button.setFill(blue)
    # training_button.draw(main_window)
    # training_text = Text(Point(85, 85), "Training")
    # training_text.setSize(14)
    # training_text.draw(main_window)
    #
    # competition_button = Rectangle(Point(20, 150), Point(150, 180))
    # competition_button.setFill(blue)
    # competition_button.draw(main_window)
    # competition_text = Text(Point(85, 165), "Heuristic Competition")
    # competition_text.draw(main_window)
    #
    # exam_button = Rectangle(Point(20, 230), Point(150, 260))
    # exam_button.setFill(blue)
    # exam_button.draw(main_window)
    # exam_text = Text(Point(85, 245), "Exam Mode")
    # exam_text.setSize(14)
    # exam_text.draw(main_window)
    #
    # """Get mouse location and check buttons"""
    # while True:
    #     mouse = main_window.getMouse()
    #     print("click")
    #
    #     if button_click(mouse, run_button):
    #         main_window.close()
    #         break
    #     elif button_click(mouse, training_button):
    #         __MODE = "TRAINING"
    #         set_mode(__MODE)
    #         heuristic_stat.setText(__MODE)
    #     elif button_click(mouse, competition_button):
    #         __MODE = "HEURISTIC_COMPETITION"
    #         set_mode(__MODE)
    #         heuristic_stat.setText(__MODE)
    #     elif button_click(mouse, exam_button):
    #         __MODE = "FINAL_EXAM"
    #         set_mode(__MODE)
    #         heuristic_stat.setText(__MODE)


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
    args = parser.parse_args()
    if args.username:
        # print("Username:", args.username)
        USER = PASS = args.username
    if args.opponent:
        # print("Opponent:", args.opponent)
        OPPONENT = args.opponent
    main()
