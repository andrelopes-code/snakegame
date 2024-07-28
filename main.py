import curses
import random
from time import sleep

from board import Board
from config import (
    BG_CHAR,
    DOWN,
    FOOD,
    FOOD_CHAR,
    LEFT,
    NULL,
    NULL_CHAR,
    RIGHT,
    SEGMENT,
    SEGMENT_CHAR,
    SLEEP_TIME,
    UP,
)
from exceptions import SnakeCollisionException
from snake import Snake

# The key codes mapped to the direction constants
KEY_MAP = {
    curses.KEY_UP: UP,
    curses.KEY_DOWN: DOWN,
    curses.KEY_LEFT: LEFT,
    curses.KEY_RIGHT: RIGHT,
    ord('W'): UP,
    ord('w'): UP,
    ord('A'): LEFT,
    ord('a'): LEFT,
    ord('S'): DOWN,
    ord('s'): DOWN,
    ord('D'): RIGHT,
    ord('d'): RIGHT,
}


class Game:
    def __init__(self, rows, columns) -> None:
        self.board = Board(rows, columns)
        self.snake = Snake(self.board)
        self.score = 0

    def run(self, window: curses.window):
        # Save the last key pressed
        last_key = None

        # Read the top score
        with open('highestscore', 'r') as f:
            highest_score = int(f.read())

        try:
            while True:
                key = window.getch()
                window.clear()

                if key == last_key:
                    continue
                elif key in KEY_MAP:
                    last_key = key
                    self.change_snake_direction(KEY_MAP[key])

                # Move the snake
                self.move_snake()

                # Draw game board, iterating through all cells in the board
                # and drawing them with the appropriate character and color
                # acording to the cell type
                for y, row in enumerate(self.board):
                    for x, cell in enumerate(row):
                        if cell == FOOD:
                            # Draw food with food character and color
                            window.addstr(y, x * 2, FOOD_CHAR, curses.color_pair(FOOD))
                        elif cell == SEGMENT:
                            # Draw snake segment with segment character and color
                            window.addstr(
                                y, x * 2, SEGMENT_CHAR, curses.color_pair(SEGMENT)
                            )
                        else:
                            # Draw empty space with null character
                            window.addstr(y, x * 2, NULL_CHAR)

                # Draw footer with score
                window.addstr(' ')
                window.border('|', '|', '-', '-', '+', '+', '+', '+')
                window.addstr(
                    f'  Score: {self.score}  Highest Score: {highest_score}  '
                )
                window.refresh()
                sleep(SLEEP_TIME)

        except Exception:
            with open('highestscore', 'r+') as f:
                file_score = int(f.read())
                if self.score > file_score:
                    f.seek(0)
                    f.truncate()
                    f.write(str(self.score))
            raise

    def move_snake(self):
        head = self.snake.body[-1]
        tail = self.snake.body[0]

        # Update the head based on the direction
        if self.snake.direction == UP:
            head = (head[0] - 1, head[1])
        elif self.snake.direction == DOWN:
            head = (head[0] + 1, head[1])
        elif self.snake.direction == LEFT:
            head = (head[0], head[1] - 1)
        elif self.snake.direction == RIGHT:
            head = (head[0], head[1] + 1)

        if self._is_collision(head):
            raise SnakeCollisionException

        # Check if the next head position is food
        # if it is, grow the snake and spawn a new food
        if self.board[head[0]][head[1]] == FOOD:
            self._catch_the_food_and_grow()

        self._update_position(head, tail)

    def change_snake_direction(self, dir):
        # Change the direction of the snake if the new
        # direction is not the opposite of the current direction
        if dir == UP and self.snake.direction != DOWN:
            self.snake.direction = UP
        elif dir == DOWN and self.snake.direction != UP:
            self.snake.direction = DOWN
        elif dir == LEFT and self.snake.direction != RIGHT:
            self.snake.direction = LEFT
        elif dir == RIGHT and self.snake.direction != LEFT:
            self.snake.direction = RIGHT

    def spawn_random_food(self):
        valid_positions_to_spawn_food = [
            p for p in self.board.positions if self._validate_food_position(p)
        ]

        if not valid_positions_to_spawn_food:
            raise NotImplementedError('No valid positions available to spawn food')

        food_position = random.choice(valid_positions_to_spawn_food)
        self.board[food_position[0]][food_position[1]] = FOOD

    def _validate_food_position(self, p):
        # Check if the food is out of bounds
        # or if it collides with the snake
        # or if it is on the edge of the board
        if (
            p in self.snake.body
            or p[0] == 0
            or p[0] == self.board.rows
            or p[1] == 0
            or p[1] == self.board.columns - 1
            or self.board[p[0]][p[1]] == FOOD
        ):
            return False
        return True

    def _update_position(self, head, tail):
        # Update the position of the snake based
        # on the head and tail given
        self.snake.body.append(head)
        self._fill(head, SEGMENT)
        self._fill(tail, NULL)
        self.snake.body.popleft()

    def _is_collision(self, head: tuple[int, int]):
        # Check if head is out of bounds
        # or if it collides with itself
        if (
            head[0] < 1
            or head[1] < 1
            or head[0] >= self.board.rows
            or head[1] >= self.board.columns
            or self.board[head[0]][head[1]] == SEGMENT
        ):
            return True
        return False

    def _catch_the_food_and_grow(self):
        # The tail row and column
        row, col = self.snake.body[0]

        up = (row - 1, col)
        down = (row + 1, col)
        left = (row, col - 1)
        right = (row, col + 1)

        # Look for a empty space around the snake tail
        # to grow the snake in that direction
        if not self._is_collision(up):
            self.snake.body.appendleft(up)
        elif not self._is_collision(down):
            self.snake.body.appendleft(down)
        elif not self._is_collision(left):
            self.snake.body.appendleft(left)
        elif not self._is_collision(right):
            self.snake.body.appendleft(right)

        # Increment score
        self.score += 1
        # Spawn a new food
        self.spawn_random_food()

    def _fill(self, position, value):
        self.board[position[0]][position[1]] = value


def main(window: curses.window):
    # Set up curses settings
    curses.curs_set(0)
    curses.start_color()
    window.timeout(0)
    window.nodelay(True)
    window.keypad(True)

    # Initialize curses colors for snake, food, and background
    curses.init_pair(NULL, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(SEGMENT, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(FOOD, curses.COLOR_RED, curses.COLOR_BLACK)
    window.bkgd(BG_CHAR, curses.color_pair(NULL))

    # Get rows and colums from current terminal size
    # Divide columns by 2 to get half the screen
    rows, columns = window.getmaxyx()
    columns = int(columns / 2)
    rows = rows - 1

    # Initialize game and spawn first food
    game = Game(rows, columns)
    game.spawn_random_food()
    game.run(window)


if __name__ == '__main__':
    try:
        # Start the curses game
        curses.wrapper(main)
    except Exception as e:
        print(e)
