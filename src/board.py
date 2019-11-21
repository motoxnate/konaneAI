
class Board:

    def __init__(self, size=18, board=None):
        if board is None:
            if not size % 2 == 0:
                raise ValueError("Board size must be even")
            self._size = size
            self._move_number = 1
            self._board = [[1 if (i + n) % 2 == 0 else -1 for i in range(size)] for n in range(size)]
        else:
            # Copy constructor
            self._board = board.get_array()
            self._size = len(self._board)
            self._move_number = board.get_move_number()

    def get_array(self):
        return self._board

    def get_move_number(self):
        return self._move_number

    """
    Moves are represented with tuples of row column pairs.
    ((r1, c1), (r2, c2)) ==> means piece at (r1, c1) is moving to (r2, c2)
    In the beginning of the game, the second point (r2, c2) will be None. This means these pieces are just removed from
    the board.
    
    This function computes which pieces are captured automatically.
    
    :return The success of the move (True or False)
    """
    def do_move(self, move):
        self._move_number += 1

        if move[1] is None:
            self._board[move[0][0]][move[0][1]] = 0
            return True

        ((r1, c1), (r2, c2)) = move
        if not (r1 == r2 or c1 == c2):
            return False

        # Saving the attacking player
        player = self._board[r1][c1]
        self._board[r1][c1] = 0

        # Logic for computing which pieces have been captured
        if r1 == r2:
            # Columns are different:
            min_col = min(c1, c2)
            max_col = max(c1, c2)
            for c in range(min_col, max_col):
                self._board[r1][c] = 0
        else:
            # Rows are different:
            min_row = min(r1, r2)
            max_row = max(r1, r2)
            for r in range(min_row, max_row):
                self._board[r][c1] = 0

        # Placing the piece that did the capturing in its final position
        self._board[r2][c2] = player
        return True

    """
    :return the number of pieces that would be captured by this move
    """
    def captured_pieces_for_move(self, move, player):
        if move[1] is None:
            # Initial move
            return 0

        if not self.is_valid_move(move, player=player):
            # Invalid move:
            return -1

        # Valid move
        ((r1, c1), (r2, c2)) = move
        return int((max(r1, r2) - min(r1, r2) + max(c1, c2) - min(c1, c2)) / 2)

    """
    Contains all the constraints for determining a valid move
    :return True or False
    """
    def is_valid_move(self, move, player=None):
        if player != 1 and player != -1:
            raise ValueError("Player must be 1 or -1!")

        # Making sure the length is equal to 2:
        if len(move) != 2:
            return False

        # First or second move:
        if move[1] is None:
            return move in self.get_first_moves() or move in self.get_second_moves()

        # Enumerating
        ((r1, c1), (r2, c2)) = move

        # Making sure start is not empty and player is correct if given
        if (player and self._board[r1][c1] != player) or self._board[r1][c1] == 0:
            return False

        # Making sure either rows or cols are different
        if (r1 == r2 and c1 == c2) or (r1 != r2 and c1 != c2):
            return False

        # Making sure the start and end are an even number of spaces apart
        if (max(r1, r2) - min(r1, r2) + max(c1, c2) + min(c1, c2)) % 2 != 0:
            return False

        # Finally making sure every other tile is of the opposite player
        if player is None:
            player = self._board[r1][c1]
        if r1 != r2:
            for r in range(r1 + 1, r2, 2):
                if self._board[r][c1] != -player:
                    return False
            for r in range(r1 + 2, r2 + 1, 2):
                if self._board[r][c1] != 0:
                    return False
        else:
            for c in range(c1 + 1, c2, 2):
                if self._board[r1][c] != -player:
                    return False
            for c in range(c1 + 2, c2 + 1, 2):
                if self._board[r1][c] != 0:
                    return False

        # Finally we return true if the move is correct!
        return True

    def get_first_moves(self):
        e = self._size - 1
        h = int(e / 2)
        return [
            ((0, 0), None),
            ((0, e), None),
            ((e, 0), None),
            ((e, e), None),
            ((h, h), None),
            ((h, h + 1), None),
            ((h + 1, h), None),
            ((h + 1, h + 1), None)
        ]

    def get_second_moves(self):
        for r in range(len(self._board)):
            for c in range(len(self._board[r])):
                if self._board[r][c] == 0:
                    moves = []
                    if r > 0:
                        moves.append(((r - 1, c), None))
                    if r < self._size - 1:
                        moves.append(((r + 1, c), None))
                    if c > 0:
                        moves.append(((r, c - 1), None))
                    if c < self._size - 1:
                        moves.append(((r, c + 1), None))
                    return moves

    def _get_moves_for_blank_space(self, r, c, player):
        moves = []
        # print(r, c)

        # Up
        for i in range(r - 2, -1, -2):
            if self._board[i + 1][c] == -player:
                if self._board[i][c] == player:
                    moves.append(((i, c), (r, c)))
                    break
                elif self._board[i][c] == -player:
                    break
            else:
                break

        # Down
        for i in range(r + 2, self._size, 2):
            if self._board[i - 1][c] == -player:
                if self._board[i][c] == player:
                    moves.append(((i, c), (r, c)))
                    break
                elif self._board[i][c] == -player:
                    break
            else:
                break

        # Left
        for i in range(c - 2, -1, -2):
            if self._board[r][i + 1] == -player:
                if self._board[r][i] == player:
                    moves.append(((r, i), (r, c)))
                    break
                elif self._board[r][i] == -player:
                    break
            else:
                break

        # Right
        for i in range(c + 2, self._size, 2):
            if self._board[r][i - 1] == -player:
                if self._board[r][i] == player:
                    moves.append(((r, i), (r, c)))
                    break
                elif self._board[r][i] == -player:
                    break
            else:
                break

        return moves

    """
    :return a list of moves that can be performed
    """
    def get_possible_moves(self, player=None):
        if self._move_number == 1:
            return self.get_first_moves()
        if self._move_number == 2:
            return self.get_second_moves()

        moves = []
        for r in range(self._size):
            for c in range(self._size):
                if self._board[r][c] == 0:
                    moves.extend(self._get_moves_for_blank_space(r, c, player))

        return moves

    """
    Creates a list of resultant states based on all the possible moves in this state
    """
    def get_possible_resultant_states(self, player):
        moves = self.get_possible_moves(player)
        states = [Board(board=self) for _b in range(len(moves))]
        [states[i].do_move(moves[i]) for i in range(len(moves))]
        return states

    def print(self):
        for row in self._board:
            print(row)
