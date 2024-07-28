class SnakeCollisionException(Exception):
    def __init__(self, message='Game Over') -> None:
        super().__init__(message)
