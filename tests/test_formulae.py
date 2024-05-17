"""Testing of formulae defined in logki"""

# Standard Imports
import os

# Third-Party Imports

# Logki imports
from logki.formulae import FormulaParser
from logki.utils import Command


def test_basic_commands():
    parser = FormulaParser()
    assert parser.eval("next") == Command.Next
    assert parser.eval("prev") == Command.Prev
    assert parser.eval("exit") == Command.Quit
    assert parser.eval("track v += 1") == Command.Track
    assert parser.eval("verify v == 0") == Command.Verify
    assert parser.eval("disprove v == 0") == Command.Disprove
    assert parser.eval("list v") == Command.Print
    assert parser.eval("help") == Command.Help
