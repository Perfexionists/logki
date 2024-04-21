"""Basic tests for logki"""

# Standard Imports
import os

# Third-Party Imports
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

# Logki imports
from logki import app
from logki.utils import BufferedLog


def test_app():
    with create_pipe_input() as pipe_input:
        pipe_input.send_text("q\n")
        with BufferedLog(
            os.path.join(os.path.dirname(__file__), "workloads", "example.log")
        ) as buffered_log:
            application = app.create_app(buffered_log)
            application.input = pipe_input
            application.output = DummyOutput()

            # Run the application
            application.run()
