"""Main logic of the logki"""
from __future__ import annotations


# Standard Imports
from dataclasses import dataclass
from typing import Optional

# Third-Party Imports

# Logki Imports
from logki.utils import singleton_class, BufferedLog


@dataclass
class Event:
    """Event represents a single line in the log

    :ivar timestamp: timestamp of the event
    :ivar event: type of the event (either call or return)
    :ivar tid: thread id
    :ivar pid: process id
    :ivar uid: uid of the event (function)
    """

    timestamp: int
    event: str
    tid: int
    pid: int
    uid: str

    @classmethod
    def from_line(cls, line: str) -> "Event":
        """Parses the event from single line

        :param line: line from the log
        :return: parsed event
        """
        parts = line.split(":")
        ts, evt = parts[0], parts[-1]
        middle_parts = parts[2].split(")(")
        tid, pid, uid = middle_parts[0], parts[1][1:], middle_parts[1][:-1]
        return Event(int(ts), evt, int(tid), int(pid), uid)


@singleton_class
class State:
    """Represents single state of the run

    :ivar current_line: currently highlighted line in the log
    :ivar real_line: real number in the log
    :ivar buffered_log: instance of buffered log
    :ivar last_command: last executed command
    :ivar current_timestamp: current timestamp in the log
    :ivar first_timestamp: first timestamp in the log
    :ivar stack: stack of the calls
    """

    def __init__(self) -> None:
        self.current_line: int = 0  # Tracks the currently highlighted line
        self.real_line: int = 0
        self.buffered_log: Optional[BufferedLog] = None
        self.last_command: str = ""
        self.current_timestamp: int = 0
        self.first_timestamp: int = 0
        self.stack: list[str] = []

        self._log_content: list[str] = []
        self._buffer_positions: list[int] = []
        self._buffer_size: int = 22
        self._buffer_log_start: int = 0
        self._buffer_log_end: int = 0

    def get_beginning_of_log(self, size: int = 80) -> str:
        """Returns beginning line for stream"""
        assert self.buffered_log is not None
        return self.buffered_log.file_path.center(size, "_")

    def get_end_of_log(self, size: int = 80) -> str:
        """Returns beginning line for stream"""
        return "EOF".center(size, "▔")

    def get_content(self) -> list[str]:
        """Returns current content of the log"""
        return self._log_content

    def init_buffer(self, buffered_log: BufferedLog) -> None:
        """Initializes the buffer from buffered log.

        :param buffered_log: buffered log
        """
        self.buffered_log = buffered_log
        self._buffer_log_start = 0
        self._log_content.append(self.get_beginning_of_log())
        self._buffer_positions.append(0)
        for _ in range(0, self._buffer_size - 1):
            self._log_content.append(self.buffered_log.read_next_line().strip())
            self._buffer_positions.append(self.buffered_log.get_current_position())
        self.first_timestamp = int(self._log_content[1].split(":")[0])
        self.current_timestamp = self.first_timestamp
        self._buffer_log_end = self.buffered_log.get_current_position()

    def move_window_forward(self) -> None:
        """Moves window forward by one line"""
        assert self.buffered_log is not None
        self.real_line += 1
        if self.current_line <= (self._buffer_size - 6) or self.get_end_of_log() in self._log_content:
            self.current_line = min(self.current_line + 1, self._buffer_size)
            return

        self._log_content = self._log_content[1:]
        self.buffered_log.move_current_position(self._buffer_log_end)
        if self.buffered_log.is_at_end():
            line = self.get_end_of_log()
        else:
            line = self.buffered_log.read_next_line()
        self._log_content.append(line.strip())

        self._buffer_log_start = self._buffer_positions[0]
        self._buffer_log_end = self.buffered_log.get_current_position()
        self._buffer_positions = self._buffer_positions[1:] + [self._buffer_log_end]

    def move_window_backward(self) -> None:
        """Moves window back by one line"""
        assert self.buffered_log is not None
        self.real_line = max(self.real_line - 1, 0)
        if self.current_line > 5 or self.get_beginning_of_log() in self._log_content:
            self.current_line = max(self.current_line - 1, 0)
            return

        self._log_content = self._log_content[:-1]
        self.buffered_log.move_current_position(self._buffer_log_start)

        if self.buffered_log.get_current_position() == 0:
            line = self.get_beginning_of_log()
        else:
            line = self.buffered_log.read_previous_line()
        self._log_content = [line.strip()] + self._log_content

        self._buffer_log_start = self.buffered_log.get_current_position()
        self._buffer_log_end = self._buffer_positions[-1]
        self._buffer_positions = [self._buffer_log_start] + self._buffer_positions[:-1]

    def process_event(self) -> None:
        """Processes next event"""
        event = Event.from_line(self._log_content[self.current_line])
        self.current_timestamp = int(event.timestamp)
        if event.event == "call":
            self.stack.append(event.uid)
        else:
            self.stack.pop()

    def undo_event(self) -> None:
        """Undo current event"""
        event = Event.from_line(self._log_content[self.current_line])
        self.current_timestamp = int(event.timestamp)
        if event.event == "call":
            self.stack.pop()
        else:
            self.stack.append(event.uid)
