import sys
import socket
from multiprocessing import Pool

from board import Board


class ArtemisClient:
    """
    This class handles all of the server communication that was needed for the final exam in my AI class.

    It probably won't be useful to anyone but I'm going to leave it in here because I can't justify throwing it out.
    """

    HOST = "artemis.engr.uconn.edu"
    PORT = 4705

    ENCODING = "ASCII"

    USER = "10"
    PASS = "10"
    OPPONENT = "7"

    def __init__(self):
        self.s = None

    def do_server_connection(self, ai, connection_index, verbose=False, size=18, username=1, opponent=2, depth=5):
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
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as err:
            print("Socket error: %s" % str(err))
            return None

        try:
            host_ip = socket.gethostbyname(ArtemisClient.HOST)
        except socket.gaierror:
            print("There was an error resolving the host")
            return None

        # connecting to the server
        self.s.connect((host_ip, ArtemisClient.PORT))
        version_message = self.get_message_from_socket()
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
            message = self.get_message_from_socket()
            # time.sleep(1)
            messages = message.split('\n')
            log("message: " + str(messages))

            try:
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
                            response = ArtemisClient.my_move_to_server_move(move, size)
                        else:
                            print("Unknown request: " + str(request))
                            continue

                        log("Response:" + response)
                        self.send_response_to_socket(response)
                        last_response = response
                    else:
                        if message.startswith("Move"):
                            server_move = message[4:]
                            my_move = ArtemisClient.server_move_to_my_move(server_move, size)
                            log("Doing Move: " + str(my_move))
                            board.do_move(my_move)
                            if verbose:
                                board.print()
                            elif board.get_move_number() % 5 == 0:
                                print(board.get_move_number(), "\t", remaining_time, sep="")

                        elif message.startswith("Removed"):
                            server_move = str(message[8:])
                            my_move = ArtemisClient.server_move_to_my_move(server_move, size)
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
            except Exception as e:
                print("Other messages: " + str(messages) + " " + str(e))
        self.s.close()
        pool.close()
        return my_player, winner, board, remaining_time

    def get_message_from_socket(self):
        m = str(self.s.recv(1024).decode(ArtemisClient.ENCODING))
        return m[0:-1]

    def send_response_to_socket(self, message):
        try:
            self.s.send((message + "\r\n").encode(ArtemisClient.ENCODING))
        except BrokenPipeError as e:
            print("Server closed connection")
            raise e

    @staticmethod
    def server_move_to_my_move(server_move, size):
        point_strs = server_move.replace("[", "").replace("]", "").split(":")
        point_vals = [int(s) for s in point_strs]
        if len(point_vals) == 2:
            return (size - point_vals[0] - 1, point_vals[1]), None
        return (size - point_vals[0] - 1, point_vals[1]), (size - point_vals[2] - 1, point_vals[3])

    @staticmethod
    def my_move_to_server_move(my_move, size):
        if my_move[1] is None:
            return "[%d:%d]" % (size - my_move[0][0] - 1, my_move[0][1])
        return "[%d:%d]:[%d:%d]" % (size - my_move[0][0] - 1, my_move[0][1], size - my_move[1][0] - 1, my_move[1][1])
