from config import NULL


class Board(list):
    def __init__(self, rows, columns) -> None:
        self.rows = rows
        self.columns = columns
        self.positions = [(r, c) for r in range(rows) for c in range(columns)]
        super().__init__([[NULL for _ in range(columns)] for _ in range(rows)])
