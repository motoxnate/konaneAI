from graphics import *
import numpy as np


def setup_game_window(x, y, size):
    """Setup for graphics window
    :param x: x resolution
    :param y: y resolution
    :param size: size of the board"""
    game_window = GraphWin("AI Settings", x, y)
    game_window.setBackground(color_rgb(210, 210, 210))
    """Grid"""
    lines = []
    for i in range(1, size):
        lines.append(Line(Point(i * x / size, 0), Point(i * x / size, y)))
        lines.append(Line(Point(0, i * x / size), Point(x, i * y / size)))
    for line in lines:
        line.draw(game_window)

    """Game Pieces
       White: 1, Black: -1"""
    pieces = np.ndarray((size, size), dtype=Circle)
    half = x / size / 2
    rad = half - 5
    for i in range(0, size, 2):  # Column
        for j in range(1, size, 2):  # Row
            # Whites
            pieces[i][j] = Circle(Point(
                (i * x / size) + half,
                (j * y / size) + half), rad)
            pieces[i][j].setFill("white")
            pieces[i][j].draw(game_window)
            # Blacks
            pieces[i][j - 1] = Circle(Point(
                (i * x / size) + half,
                ((j - 1) * y / size) + half), rad)
            pieces[i][j - 1].setFill("black")
            pieces[i][j - 1].draw(game_window)

    for i in range(1, size, 2):
        for j in range(0, size, 2):
            # Whites
            pieces[i][j] = Circle(Point(
                (i * x / size) + half,
                (j * y / size) + half), rad)
            pieces[i][j].setFill("white")
            pieces[i][j].draw(game_window)
            # Blacks
            pieces[i][j + 1] = Circle(Point(
                (i * x / size) + half,
                ((j + 1) * y / size) + half), rad)
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