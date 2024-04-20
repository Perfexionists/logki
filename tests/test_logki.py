"""Basic tests for logki"""

# Standard Imports
import os

# Third-Party Imports
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

# Logki imports
import logki.logki as logki


def test_app():
    with create_pipe_input() as pipe_input:
        pipe_input.send_text('q\n')
        with logki.BufferedLog(os.path.join(os.path.dirname(__file__), "workloads", "example.log")) as buffered_log:
            app = logki.create_app(buffered_log)
            app.input = pipe_input
            app.output = DummyOutput()

            # Run the application
            app.run()
