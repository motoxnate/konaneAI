from graphics import *
import numpy as np


class GUI:
    def __init__(self, xres, yres, board_size, verbose=False):
        self.xres = xres
        self.yres = yres
        self.board_size = board_size
        self.board = self.setup_game_window()
        self.verbose = verbose

    def setup_game_window(self):
        """Setup for graphics window"""
        self.game_window = GraphWin("AI Settings", self.xres, self.yres)
        self.game_window.setBackground(color_rgb(210, 210, 210))
        """Create Grid"""
        lines = []
        for i in range(1, self.board_size):
            lines.append(Line(Point(i * self.xres / self.board_size, 0),
                              Point(i * self.xres / self.board_size, self.yres)))
            lines.append(Line(Point(0, i * self.xres / self.board_size),
                              Point(self.xres, i * self.yres / self.board_size)))
        for line in lines:
            line.draw(self.game_window)

        """Create Pieces"""
        pieces = np.ndarray((self.board_size, self.board_size), dtype=Circle)
        half = self.xres / self.board_size / 2
        rad = half - 5
        for i in range(0, self.board_size, 2):  # Column
            for j in range(1, self.board_size, 2):  # Row
                # Whites
                pieces[i][j] = Circle(Point(
                    (i * self.xres / self.board_size) + half,
                    (j * self.yres / self.board_size) + half), rad)
                pieces[i][j].setFill("white")
                pieces[i][j].draw(self.game_window)
                # Blacks
                pieces[i][j - 1] = Circle(Point(
                    (i * self.xres / self.board_size) + half,
                    ((j - 1) * self.yres / self.board_size) + half), rad)
                pieces[i][j - 1].setFill("black")
                pieces[i][j - 1].draw(self.game_window)

        for i in range(1, self.board_size, 2):
            for j in range(0, self.board_size, 2):
                # Whites
                pieces[i][j] = Circle(Point(
                    (i * self.xres / self.board_size) + half,
                    (j * self.yres / self.board_size) + half), rad)
                pieces[i][j].setFill("white")
                pieces[i][j].draw(self.game_window)
                # Blacks
                pieces[i][j + 1] = Circle(Point(
                    (i * self.xres / self.board_size) + half,
                    ((j + 1) * self.yres / self.board_size) + half), rad)
                pieces[i][j + 1].setFill("black")
                pieces[i][j + 1].draw(self.game_window)
        return pieces

    def graphics_move(self, move):
        """Execute a move on the graphics screen
        :param move: The move to execute. Note the pieces array is in (row, col) form
                     whereas the rest of the board and incoming move is in (col, row).
        :return True when successful, otherwise false"""
        print("Graphics:", move)
        # If removal
        if move[1] is None:
            (c, r) = move[0]
            self.board[r][c].undraw()
            return True

        """ For a standard move:
        (c1, r1) Are the coordinates of the origin piece
        (c2, r2) Are the coordinates of the destination spot"""
        ((c1, r1), (c2, r2)) = move
        if not (r1 == r2 or c1 == c2):
            raise ValueError
        piece1 = self.board[r1][c1]
        piece2 = self.board[r2][c2]
        movement = self.calculate_movement(piece1.getCenter(), piece2.getCenter())

        if r1 == r2:
            # Columns are different:
            min_col = min(c1, c2)
            max_col = max(c1, c2)
            for c in range(min_col, max_col):
                self.board[r1][c].undraw()
        else:
            # Rows are different:
            min_row = min(r1, r2)
            max_row = max(r1, r2)
            for r in range(min_row, max_row):
                self.board[r][c1].undraw()
        # May have to redraw the piece, if it was cleared in the removal process
        try:
            self.board[r1][c1].draw(self.game_window)
        except Exception as e:
            pass
        piece1.move(movement[0], movement[1])
        self.board[c2][r2] = piece1

    def calculate_movement(self, pos1, pos2):
        start = (pos1.getX(), pos2.getY())
        end = (pos2.getX(), pos2.getY())
        if self.verbose:
            print("Start:", start)
            print("End:", end)
        return end[0] - start[0], end[1] - start[1]

    def options_window(self):
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