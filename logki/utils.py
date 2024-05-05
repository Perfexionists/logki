"""Utilities for logki"""
from __future__ import annotations

# Standard Imports
import io
from typing import Optional, TextIO

# Third-Party Imports

# Logki Imports


class BufferedLog:
    """Buffered Log reads file on the fly keeping it open and returning lines on demand.

    :ivar file_path: path to the file
    :ivar block_size: size of one read block
    :ivar current_position: current position in the log
    :ivar end_position: last position in the file
    :ivar file: opened file
    """

    def __init__(self, file_path: str, block_size: int = 1024):
        """Initializes the buffered log

        :param file_path: path to the file
        :param block_size: size of the read block
        """
        self.file_path: str = file_path
        self.block_size: int = block_size
        self.current_position: int = 0
        self.end_position: int = 0
        self.file: Optional[TextIO] = None

    def __enter__(self) -> BufferedLog:
        """Entering the context

        File is opened, and we infer the start and ending position
        """
        self.file = open(self.file_path, "r", encoding="utf-8")
        self.file.seek(0, io.SEEK_END)
        self.end_position = self.file.tell()
        self.file.seek(0)
        return self

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: BaseException) -> None:
        """Closes the file"""
        assert self.file is not None
        self.file.close()

    def read_next_line(self) -> str:
        """Reads the next line in the log

        :return: next line in the buffer
        """
        assert self.file is not None
        if self.current_position >= self.end_position:
            return ""
        self.file.seek(self.current_position)
        line = self.file.readline()
        self.current_position = self.file.tell()
        return line

    def read_previous_line(self) -> str:
        """Reads the previous line in log

        :return: previous line in the buffer
        """
        assert self.file is not None

        block = ""
        while self.current_position > 0:
            to_read = min(self.block_size, self.current_position)
            self.file.seek(self.current_position - to_read)
            block += self.file.read(to_read)
            self.current_position -= to_read
            if "\n" in block:
                lines = block.split("\n")
                if len(lines) < 3:
                    continue
                last_full_line = lines[-2]
                self.current_position += (
                    sum(len(line) + 1 for line in lines[:-2])
                )
                self.file.seek(self.current_position)
                return last_full_line
        self.file.seek(self.current_position)
        return block

    def is_at_end(self) -> bool:
        """Returns whether the buffer is at the end of the file"""
        assert self.file is not None
        return self.current_position == self.end_position

    def get_current_position(self) -> int:
        """Returns the current position in the log"""
        assert self.file is not None
        return self.file.tell()

    def move_current_position(self, position: int) -> None:
        """Moves position in the log

        :param position: new position in the log
        """
        assert self.file is not None
        self.current_position = position
        self.file.seek(position)

    def close(self):
        """Closes the buffered log"""
        assert self.file is not None
        self.file.close()


def singleton_class(cls):
    """Helper class for creating singleton objects"""
    instances = {}

    def getinstance() -> object:
        """Singleton instance"""
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance
