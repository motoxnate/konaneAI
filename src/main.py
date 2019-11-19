
from src.board import Board


def main():
    board = Board(size=10)
    player = 1
    try:
        while True:
            board.print()
            print("Turn:", player)
            moves = board.get_possible_moves(player=player)
            if len(moves) == 0:
                break
            print("\n".join([str((move, board.is_valid_move(move, player=player), board.captured_pieces_for_move(move))) for move in moves]))
            input("")
            if not board.do_move(moves[0]):
                raise ValueError("Invalid move: " + str(moves[0]))
            player *= -1
    except KeyboardInterrupt:
        pass
    print("Player", -1 * player, "Wins!")


if __name__ == "__main__":
    main()
