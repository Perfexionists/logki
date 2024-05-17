"""Formulae and the parser for the formulae"""

from __future__ import annotations


# Standard Imports
from typing import Callable
from collections import defaultdict

# Third-Party Imports
from lark import Lark, ParseTree, Transformer
from lark.exceptions import LarkError

# Logki Imports
from logki.utils import singleton_class, Command


@singleton_class
class FormulaParser:
    """Parser for formulae"""

    def __init__(self) -> None:
        """Create a parser for a given expression grammar"""
        grammar = """
            command: ("h" | "help") -> cmd_help
                   | ("q" | "quit" | "exit") -> cmd_quit
                   | ("p" | "prev") -> cmd_prev
                   | ("n" | "next") -> cmd_next
                   | ("t" | "track") statement -> cmd_track
                   | ("v" | "verify") guard -> cmd_verify
                   | ("d" | "disprove") guard -> cmd_disprove
                   | ("b" | "break" | "breakon" | "break on") guard -> cmd_breakon
                   | ("l" | "list" | "e" | "echo" | "print") expression -> cmd_list
            statement: "(" guard ")" single_statement -> guarded_statement
                    | single_statement                

            single_statement: lvar lop expression
            expression: value
            lvar: var
            ?var: WORD
            value: NUMBER  -> val_const
                 | var     -> val_var
            !lop: "+="
            !bop: "==" | "!="
            guard: value bop value

            %import common.WORD
            %import common.NUMBER
            %import common.WS
            %ignore WS
        """
        self.parser: Lark = Lark(grammar, start="command", parser="lalr")
        self.command_evaluation: CommandEvaluation = CommandEvaluation()

    def parse(self, expression: str) -> ParseTree:
        """Parses the expression wrt the formula grammar"""
        tree = self.parser.parse(expression)
        return tree

    def eval(self, expression: str) -> Command:
        """Evaluates a boolean expression"""
        try:
            return self.command_evaluation.transform(self.parse(expression))
        except LarkError as exc:
            print(exc)
            return Command.Error


class CommandEvaluation(Transformer):
    """Command evaluation transforms the parsed tree into a command, evaluating as sideeffect expressions."""

    def __init__(self):
        super().__init__()
        self.symbol_table: dict[str, float] = defaultdict(float)
        self.assertions: list[Callable[[]]] = []
        self.statements: list[tuple[Callable[[], bool], Callable[[]]]] = []
        self.print_statement: str = ""

    def cmd_help(self, _) -> Command:
        """Prints help"""
        return Command.Help

    def cmd_prev(self, _) -> Command:
        """Goes one stap back in the log"""
        return Command.Prev

    def cmd_next(self, _) -> Command:
        """Goes one step forward in the log"""
        return Command.Next

    def cmd_quit(self, _) -> Command:
        """Quits the applications"""
        return Command.Quit

    def cmd_track(self, args) -> Command:
        """Adds arguments to list of tracked expressions"""
        (stmt,) = args
        self.statements.append(stmt)
        return Command.Track

    def cmd_verify(self, args) -> Command:
        """Verifies that all lines in log satisfies given expression"""
        (assertion,) = args
        self.assertions.append(assertion)
        return Command.Verify

    def cmd_disprove(self, args) -> Command:
        """Disproves the expression, i.e. finds line in log that does not satisfy the given expression"""
        (assertion,) = args
        self.assertions.append(assertion)
        return Command.Disprove

    def cmd_breakon(self, args) -> Command:
        """Runs the log and breaks until a given expression is satisfied"""
        (assertion,) = args
        self.assertions.append(assertion)
        return Command.BreakOn

    def cmd_list(self, args) -> Command:
        """Prints anything"""
        (expr,) = args
        self.print_statement = str(expr())
        return Command.Print

    def single_statement(self, args):
        (lvar, lop, expr) = args
        if lop == "+=":
            # Temporary
            return lambda: lvar + expr()
        else:
            assert False and f"Unsupported combination {lvar}, {lop}, {expr}"

    def guarded_statement(self, args):
        (guard, stmt) = args
        return guard, stmt

    def expression(self, args):
        if len(args) == 1:
            return lambda: args[0]
        else:
            assert False and "Unsupported"

    def lvar(self, args):
        (var,) = args
        return var

    def var(self, args):
        (var,) = args
        return var

    def guard(self, args):
        (var, op, expr) = args
        if op == "==":
            # Temporary
            return lambda: var == expr()
        else:
            assert False and f"Unsupported combination {var}, {op}, {expr}"

    def val_var(self, args):
        (var,) = args
        return var

    def val_const(self, args):
        (const,) = args
        as_float = float(const)
        if as_float.is_integer():
            return int(as_float)
        else:
            return as_float

    def lop(self, args):
        (lop,) = args
        return lop

    def bop(self, args):
        (bop,) = args
        return bop
