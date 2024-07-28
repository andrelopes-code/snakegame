from collections import deque

from config import RIGHT, SEGMENT


class Snake:
    def __init__(self, board) -> None:
        self.board = board
        self.direction = RIGHT
        self.body = deque()
        self.draw_snake()

    def draw_snake(self):
        # Set the initial state of the snake in the board
        self.body.extend([(2, 2), (2, 3), (2, 4), (2, 5)])
        for segment in self.body:
            self.board[segment[0]][segment[1]] = SEGMENT
