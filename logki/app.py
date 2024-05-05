"""logki is prompt script for going through the logs, for example of perun ktrace """
from __future__ import annotations

# Standard Imports
from typing import Any
import sys

# Third-Party Imports
import tabulate
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyPressEvent
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea, Frame

# Logki imports
import logki
from logki.logic import Event, State
from logki.utils import BufferedLog

NS_TO_MS = 1000000


# Custom syntax highlighting
def get_colored_log() -> list[tuple[str, str]]:
    """Returns coloured contents"""
    current_state: State = State()
    styled_lines = []
    lineno_width = len(
        str(current_state.real_line - current_state.current_line + current_state._buffer_size)
    )
    for i, line in enumerate(current_state.get_content()):
        lineno = current_state.real_line - current_state.current_line + i
        if i == current_state.current_line:
            # Apply a different background for the current line
            if current_state.real_line == 0:
                styled_lines.extend([("class:current_line", f"{' '*lineno_width} {line}" + "\n")])
            else:
                styled_lines.extend(
                    [("class:current_line", f"{lineno: >{lineno_width}}| {line}" + "\n")]
                )
        elif i == 0 and (current_state.real_line - current_state.current_line) == 0:
            styled_lines.extend([("class:text", f"{' '*lineno_width} {line}" + "\n")])
        else:
            styled_lines.extend(
                [("class:text", f"{lineno: >{lineno_width}}| ")]
                + get_colored_log_line(line)
                + [("", "\n")]
            )
    return styled_lines


def get_colored_log_line(line: str) -> list[tuple[str, str]]:
    """Returns colored line

    :param line: current line
    """
    try:
        event = Event.from_line(line)
        return [
            ("class:timestamp", str(event.timestamp)),
            ("class:text", ":("),
            ("class:pid", str(event.pid)),
            ("class:text", ":"),
            ("class:tid", str(event.tid)),
            ("class:text", ")("),
            ("class:function", event.uid),
            ("class:text", "):"),
            (f"class:{event.event}", event.event),
        ]
    except IndexError:
        return [("class:skip", line)]


# Key bindings for the application
bindings = KeyBindings()


@bindings.add("c-c")
@bindings.add("c-q")
def _(event: KeyPressEvent) -> None:
    """Quit application."""
    event.app.exit()


def format_time(time: int) -> str:
    """Formats time

    :param time: formatted time
    """
    if time < NS_TO_MS:
        return f"{time / NS_TO_MS:.2f}ms"
    else:
        minutes, milliseconds = divmod(int(time / NS_TO_MS), 60)
        seconds, milliseconds = divmod(milliseconds, 1000)
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:d}"


def get_stats() -> str:
    """Returns statistics for current state"""
    current_state: State = State()
    data = [
        ["current event", f"{current_state.real_line}"],
        [
            "current time",
            f"{format_time(current_state.current_timestamp - current_state.first_timestamp)}",
        ],
    ]
    return tabulate.tabulate(data, headers=[], tablefmt="presto")


def get_stack() -> list[tuple[str, str]]:
    """Returns formatted stack"""
    current_state: State = State()
    lines = []
    for f in current_state.stack[::-1]:
        lines.extend([("class:function", f), ("", "\n")])
    return lines


def create_app(buffered_log: BufferedLog) -> Application[Any]:
    """Creates apllication for given buffered log

    :param buffered_log: buffered log
    """
    current_state: State = State()
    current_state.init_buffer(buffered_log)

    def process_command(buff):
        try:
            current_state: State = State()
            set_status("")
            cmd = buff.text.strip().lower()

            if cmd == "":
                cmd = current_state.last_command

            if cmd == "help":
                terminal.text = "Commands: help, next, prev"
            elif cmd in ("next", "n", "j"):
                if (
                    current_state.buffered_log.is_at_end()
                    and current_state.current_line == current_state._buffer_size
                ):
                    set_status("On the end of the file")
                else:
                    if current_state.real_line != 0:
                        current_state.process_event()
                    current_state.move_window_forward()
            elif cmd in ("prev", "p", "k"):
                if current_state.real_line == 0:
                    set_status("On the start of the file")
                else:
                    current_state.move_window_backward()
                    if (
                        not current_state.buffered_log.is_at_end()
                        or current_state.current_line != current_state._buffer_size
                    ):
                        current_state.undo_event()
            elif cmd in ("quit", "exit", "q"):
                app.exit()
            else:
                terminal.text = f"Unknown command: {cmd}"
            current_state.last_command = cmd
            # Refresh log view to reflect changes
            log_view.content = FormattedTextControl(get_colored_log)
            buff.document = Document()  # Clear the terminal input after command execution
            return True
        except Exception as exc:
            set_status(f"error: {exc}")

    # Define the layout
    stack_view = Frame(title="Stack", body=Window(content=FormattedTextControl(get_stack)))
    counter_view = Frame(title="Stats", body=Window(content=FormattedTextControl(get_stats)))
    log_view = Frame(title="Log", body=Window(content=FormattedTextControl(get_colored_log)))
    state_view = Frame(
        title="State",
        body=HSplit([stack_view, counter_view]),
    )
    status_text = TextArea(text="", height=1, multiline=False)
    status_view = Frame(title="Status", body=status_text)

    def set_status(status: str) -> None:
        """Returns statistics for current state"""
        status_text.buffer.document = Document(text=status)

    terminal = TextArea(
        prompt="> ", multiline=False, wrap_lines=False, accept_handler=process_command
    )
    root_container = HSplit(
        [
            VSplit([log_view, state_view]),
            status_view,
            terminal,
        ]
    )

    # Define styles
    style = Style(
        [
            ("skip", "#b4b4b8"),
            ("timestamp", "#ff595e"),
            ("tid", "#ff924c"),
            ("pid", "#ffca3a"),
            ("function", "#8ac926"),
            ("call", "#1982c4"),
            ("return", "#6a4c93"),
            ("current_line", "bg:#0044ff #ffffff"),
            ("text", ""),
        ]
    )

    # Create the application
    app: Application[Any] = Application(
        layout=Layout(root_container, focused_element=terminal),
        key_bindings=bindings,
        style=style,
        full_screen=True,
    )
    return app


def launch():
    """Launches logki"""
    if len(sys.argv) == 2 and sys.argv[1] == "--version":
        print(f"logki {logki.__version__}")
        sys.exit(0)
    elif len(sys.argv) == 2:
        with BufferedLog(sys.argv[1]) as buffered_log:
            application = create_app(buffered_log)
            application.run()
    else:
        print("usage: ./logki.py <LOG>.log")
        sys.exit(1)


if __name__ == "__main__":
    launch()
