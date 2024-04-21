from colorama import Style

from .messages import info, warn, error


class Logger:
    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color

    def info(self, message: str) -> None:
        info(f"{self.color}{self.name}{Style.RESET_ALL} ", message)

    def warn(self, message: str) -> None:
        warn(f"{self.color}{self.name}{Style.RESET_ALL} ", message)

    def error(self, message: str) -> None:
        error(f"{self.color}{self.name}{Style.RESET_ALL} ", message)
