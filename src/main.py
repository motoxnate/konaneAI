import socket
import argparse
from graphics import *
from multiprocessing import Pool
from threading import Thread

try:
    from src.board import Board
    from src.heuristic import *
    from src.minimax_process import parallel_minimax, parallel_minimax_pool
except ModuleNotFoundError:
    from board import Board
    from heuristic import *
    from minimax_process import parallel_minimax, parallel_minimax_pool


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

HOST = "artemis.engr.uconn.edu"
PORT = 4705
ENCODING = "ASCII"

USER = "69420"
PASS = "69420"
OPPONENT = "42069"
DEPTH = 5
SIZE = 18

TRAINING_SIZE = 18
TRAINING_DEPTH = 5


def main(tester=None, test_board=False, test_moves=False):
    __MODE = "TRAINING"
    """Begin Main"""
    if __MODE == "TRAINING":
        learning_heuristic1 = MCPDLearningHeuristic()
        session_number = 0

        try:
            while True:
                """
                Playing training games

                Player 1 always has the more favorable heuristic settings
                If player -1 wins, then player 1 gets player -1's settings and a new set of settings are generated for
                player -1.

                Randomness setting in learning heuristic may be:
                False: Not random
                UNIFORM: Uses a uniform distribution
                NORMAL: Uses a normal distribution
                """
                learning_heuristic2 = MCPDLearningHeuristic(randomness="UNIFORM")
                print("Player 1: %s\nPlayer -1: %s" % (str(learning_heuristic1), str(learning_heuristic2)))
                starting_player = -1 if session_number % 2 == 0 else 1
                cur = time.time()

                winner, move_count = do_game(learning_heuristic1, learning_heuristic2, depth=15, size=18,
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

        wins1, wins2, total_turns = do_games(total_games, h1, h2, depth=5, size=18)

        message = """
        
        Heuristic Competition Finished!
        %d Games played, %d turns played, about %f turns on average per game
        %d Player 1 wins, about %d%% of the time
        %d Player -1 wins, about %d%% of the time
        """ % (total_games, total_turns, total_turns / total_games, wins1, int(wins1 / total_games * 100), wins2, int(wins2 / total_games * 100))
        print(message)

    elif __MODE == "HUMAN_PLAYER":
        # Should create an AI connected to the server and a graphics windows connected to the server that will play
        # against the AI
        pass

    elif __MODE == "SERVER_TRAINING":
        # Same as regular training except works with the server to catch any errors we may be having with the server
        h1 = MCPDLearningHeuristic()
        t1 = Thread(target=do_server_connection, args=(h1, 0, False, 18, USER, OPPONENT, 1))
        h2 = MCPDLearningHeuristic()
        t2 = Thread(target=do_server_connection, args=(h2, 1, False, 18, OPPONENT, USER, 5))

        t1.start()
        t2.start()

        t1.join()
        t2.join()

    elif __MODE == "SERVER_ONE_AI_PLAY":

        p, w, b, t = do_server_connection(MCPDLearningHeuristic(), 0, verbose=True, username=USER, opponent=OPPONENT)
        print("Game finished, played as %d, player %d won, remaining time: %f" % (p, w, t))
        b.print()

    elif __MODE == "FINAL_EXAM":

        p, w, b, t = do_server_connection(MCPDLearningHeuristic(), 0, verbose=False, username=USER, opponent=OPPONENT, depth=15)
        print("Game finished, played as %d, player %d won, remaining time: %f" % (p, w, t))
        b.print()

    else:
        print("Invalid mode: %s" % __MODE)


def do_server_connection(ai, connection_index, verbose=False, size=SIZE, username=1, opponent=2, depth=5):
    """
    Connects to the server and plays a game from the point of one player
    :param ai: the heuristic to use
    :param connection_index: unique identifier used in logging output (all connections should have different indices)
    :param verbose: true for loud, false for silent
    :param size: size of the board to use
    :param username: username and password
    :param opponent: opponent name
    :param depth: the depth of the minimax search
    :return: (player number of this connection i.e. 1 or -1, winning player, final board state, remaining time)
    """
    log = (lambda x: print("Connection %d: [%s]" % (connection_index, x))) if verbose else (lambda x: x)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as err:
        print("Socket error: %s" % str(err))
        sys.exit(1)

    try:
        host_ip = socket.gethostbyname(HOST)
    except socket.gaierror:
        print("There was an error resolving the host")
        sys.exit(1)

    # connecting to the server
    s.connect((host_ip, PORT))
    version_message = get_message_from_socket(s)
    log("Connected to server version %s" % version_message.split("v")[-1])

    board = Board(size=size)
    my_player = 0
    game_num = -1
    winner = 0
    remaining_time = 180
    log("Using AI: " + str(ai))
    pool = Pool()

    if not verbose:
        print("Turn\tTime")

    last_response = None
    while winner == 0:
        message = get_message_from_socket(s)
        # time.sleep(1)
        messages = message.split('\n')
        log("message: " + str(messages))

        for message in messages:
            if "?" in message:
                # It is a request:
                request = message[message.index("?") + 1:]

                if request.startswith("Username"):
                    response = username

                elif request.startswith("Password"):
                    response = username

                elif request.startswith("Opponent"):
                    response = opponent

                elif request.startswith("Move") or request.startswith("Remove"):
                    if "(" in message:
                        remaining_time = message[message.index("(") + 1: message.index(")")]
                        remaining_time = int(remaining_time) / 1000
                        log("Time Left: " + str(remaining_time))

                    h, move = parallel_minimax_pool(board, my_player, ai, depth, pool=pool)
                    response = my_move_to_server_move(move, size)
                else:
                    print("Unknown request: " + str(request))
                    continue

                log("Response:" + response)
                send_response_to_socket(s, response)
                last_response = response
            else:
                if message.startswith("Move"):
                    server_move = message[4:]
                    my_move = server_move_to_my_move(server_move, size)
                    log("Doing Move: " + str(my_move))
                    board.do_move(my_move)
                    if verbose:
                        board.print()
                    elif board.get_move_number() % 5 == 0:
                        print(board.get_move_number(), "\t", remaining_time, sep="")

                elif message.startswith("Removed"):
                    server_move = str(message[8:])
                    my_move = server_move_to_my_move(server_move, size)
                    log("Doing Initial Move: " + str(my_move))
                    board.do_move(my_move)

                elif message.startswith("Player:"):
                    log("I won the coin toss" if message[7:] == "1" else "I lost the coin toss")

                elif message.startswith("Color:"):
                    my_player = 1 if message[6:] == "BLACK" else -1
                    log("My player is " + str(my_player))

                elif message.startswith("Game:"):
                    game_num = message[5:]
                    log("Game Number: " + str(game_num))

                elif message.startswith("Opponent wins!") or message.startswith("You win!"):
                    log(message)
                    winner = my_player if message.startswith("You") else -my_player
                    break
                elif message.startswith("Error"):
                    raise ValueError(message + " | Last response: " + last_response)
                else:
                    print("Unknown message: " + str(message))
    s.close()
    pool.close()
    return my_player, winner, board, remaining_time


def do_game(heuristic_obj_1, heuristic_obj_2, depth=5, size=18, player=1, verbose=False):
    """
    Completes a game with the given inputs
    :param heuristic_obj_1: player 1's heuristic
    :param heuristic_obj_2: player -1's heuristic
    :param depth:
    :param size:
    :param player: the starting player
    :param verbose:
    :return: the winning player of the game tupled with the turn count
    """
    board = Board(size=size)
    pool = Pool()
    while True:
        moves = board.get_possible_moves(player=player)
        if len(moves) == 0:
            break
        h = 0
        if board.get_move_number() < 2:
            move = moves[0]
        else:
            if player == 1:
                h, move = parallel_minimax_pool(board, player, heuristic_obj_1, depth, pool=pool)
            else:
                h, move = parallel_minimax_pool(board, player, heuristic_obj_2, depth, pool=pool)

        if verbose:
            print("\n")
            board.print()
            print(h, move)
        else:
            if board.get_move_number() % 5 == 0:
                print(board.get_move_number(), end=" ", flush=True)

        if not board.do_move(move):
            raise ValueError("Invalid move: " + str(move))
        player *= -1
    pool.close()
    return -player, board.get_move_number()


def do_games(game_number, heuristic_obj_1, heuristic_obj_2, depth=5, size=18, verbose=False):
    wins1 = 0
    wins2 = 0
    total_move_numbers = 0
    player = 1
    for i in range(game_number):
        winner, move_number = do_game(heuristic_obj_1, heuristic_obj_2, depth, size, player, verbose)
        if winner == 1:
            wins1 += 1
        else:
            wins2 += 1
        total_move_numbers += move_number
        player *= -1
        print()
    return wins1, wins2, total_move_numbers


def get_message_from_socket(s):
    m = str(s.recv(1024).decode(ENCODING))
    return m[0:-1]


def send_response_to_socket(s, message):
    try:
        s.send((message + "\r\n").encode(ENCODING))
    except BrokenPipeError as e:
        print("Server closed connection")
        raise e


def server_move_to_my_move(server_move, size):
    point_strs = server_move.replace("[", "").replace("]", "").split(":")
    point_vals = [int(s) for s in point_strs]
    if len(point_vals) == 2:
        return (size - point_vals[0] - 1, point_vals[1]), None
    return (size - point_vals[0] - 1, point_vals[1]), (size - point_vals[2] - 1, point_vals[3])


def my_move_to_server_move(my_move, size):
    if my_move[1] is None:
        return "[%d:%d]" % (size - my_move[0][0] - 1, my_move[0][1])
    return "[%d:%d]:[%d:%d]" % (size - my_move[0][0] - 1, my_move[0][1], size - my_move[1][0] - 1, my_move[1][1])


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
