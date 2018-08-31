from __future__ import print_function
import clingo
import threading
import sys
import signal
import copy
from . import clingo_stats

# defines
INTERRUPT  = """*** Info : ({}): INTERRUPTED by signal!
UNKNOWN

INTERRUPTED  : 1"""

SUMMARY_STR = """Calls        : 1
Time         : 0.000s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
CPU Time     : 0.000s"""

STATS_STR = """
Choices      : 0
Conflicts    : 0        (Analyzed: 0)
Restarts     : 0
Problems     : 0        (Average Length: 0.00 Splits: 0)
Lemmas       : 0        (Deleted: 0)
  Binary     : 0        (Ratio:   0.00%)
  Ternary    : 0        (Ratio:   0.00%)
  Conflict   : 0        (Average Length:    0.0 Ratio:   0.00%)
  Loop       : 0        (Average Length:    0.0 Ratio:   0.00%)
  Other      : 0        (Average Length:    0.0 Ratio:   0.00%)
Backjumps    : 0        (Average:  0.00 Max:   0 Sum:      0)
  Executed   : 0        (Average:  0.00 Max:   0 Sum:      0 Ratio:   0.00%)
  Bounded    : 0        (Average:  0.00 Max:   0 Sum:      0 Ratio: 100.00%)

Variables    : 0        (Eliminated:    0 Frozen:    0)
Constraints  : 0        (Binary:   0.0% Ternary:   0.0% Other:   0.0%)i
"""

class ClingoSignalHandler:

    def __init__(self, control,
                 name="",
                 print_after_solving=False,
                 function_after_solving=None,
                 function_on_solving=None,
                 function_on_not_solving=None,
                 function_on_not_solved=None
                ):
        # public
        self.statistics = None
        self.function_after_solving = function_after_solving
        self.function_on_solving = function_on_solving
        self.function_on_not_solving = function_on_not_solving
        self.function_on_not_solved = function_on_not_solved
        # private
        self.interrupted = False
        self.control = control
        self.solved = False
        self.name = name
        self.print_after_solving = print_after_solving
        if self.function_after_solving is None:
            self.function_after_solving = self.after_solving
        if self.function_on_solving is None:
            self.function_on_solving = self.on_solving
        if self.function_on_not_solving is None:
            self.function_on_not_solving = self.on_not_solving
        if self.function_on_not_solved is None:
            self.function_on_not_solved = self.on_not_solved
        self.condition = threading.Condition()
        self.solving = False
        self.result = None
        # signal handling
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

    #
    # private: printing funtions
    #

    def do_print_stats(self, statistics):
        print(clingo_stats.Stats().summary(statistics))
        print(clingo_stats.Stats().statistics(statistics))

    def after_solving(self):
        self.do_print_stats(self.control.statistics)

    def on_solving(self):
        print(INTERRUPT.format(self.name))
        self.do_print_stats(self.control.statistics)
        sys.exit(1)

    def on_not_solving(self):
        print(INTERRUPT.format(self.name))
        statistics = self.control.statistics
        if self.statistics is not None:
            statistics = self.statistics
        self.do_print_stats(statistics)
        sys.exit(1)

    def on_not_solved(self):
        print(INTERRUPT.format(self.name))
        print(SUMMARY_STR)
        print(STATS_STR)
        sys.exit(1)

    #
    # signal handling
    #

    # private
    def signal_handler(self, signum, frame):
        if self.solving:
            self.control.interrupt()
            self.interrupted = True
        elif self.solved:
            self.function_on_not_solving()
        else:
            self.function_on_not_solved()

    # private
    def stop(self, result):
        self.result = result
        # notify
        with self.condition:
            self.condition.notify()

    # private
    def do_solve(self, control, *args, **kwargs):
        with self.condition:
            with control.solve(
                async=True, on_finish=self.stop, *args, **kwargs
            ) as handle:
                # In Python 2, Condition.wait() isn't interruptible when called without a timeout.
                # In Python 3, infinite timeouts lead to overflow errors.
                # To accomodate for both Python versions, a switch on the timeout is necessary.
                # More information available at: https://bugs.python.org/issue8844
                self.condition.wait(timeout = float("inf") if sys.version_info[0] < 3 else None)
                handle.wait()

    # public
    def solve(self, *args, **kwargs):
        self.solving = True
        # self.control.solve(*args, **kwargs)
        self.do_solve(self.control, *args, **kwargs)
        self.solved = True
        self.solving = False
        if self.interrupted:
            self.function_on_solving()
        elif self.print_after_solving:
            self.function_after_solving()
        return self.result

    # public
    # asyncronous solve that can be interrupted (control object is a parameter)
    def single_solve(self, control, *args, **kwargs):
        self.do_solve(control, *args, **kwargs)
        return self.result

    # public
    def ground(self, *args):
        if self.solved:
            self.statistics = copy.deepcopy(
                self.control.statistics
            )
        self.control.ground(*args)
        self.statistics = None


class Test:

    def __init__(self, name=""):
        self.name = name # used only for printing the INTERRUPT string

    #
    # select where to stop
    #   stop = 0 normally
    #   stop = 1 on_solving     (solves for long)
    #   stop = 2 on_not_solved  (infinite loop)
    #   stop = 3 on_not_solving (grounds for long, signals do not work)
    #   stop = 4 on_not_solving (infinite loop)
    #
    def run(self, stop=0):

        # start
        options = ["--stats"]
        control = clingo.Control(options)
        clingo_proxy = ClingoSignalHandler(
            control,
            self.name,
            print_after_solving=True
            #print_after_solving=False
        )

        # base program
        const = "#const n=8."
        if stop == 1:
            const = "#const n=10."
        control.add("base", [], const)
        control.add("base", [], """
pigeon(1..n+1). box(1..n).
1 { in(X,Y) : box(Y) } 1 :- pigeon(X).
:- 2 { in(X,Y) : pigeon(X) },  box(Y), not x.
#external x.
""")

        # infinite loop?
        while True:
            if stop == 2:
                pass
            else:
                break

        # ground and solve
        clingo_proxy.ground([("base", [])])
        print(clingo_proxy.solve(
            on_model=lambda x: print(x.symbols(shown=True))
        ))

        if stop == 3:
            control.add("big", [], "#const m=300. a(1..m,1..m,1..m).")
            clingo_proxy.ground([("big", [])])

        # infinite loop?
        while True:
            if stop == 4:
                pass
            else:
                break

if __name__ == "__main__":
    stop = 0
    #stop = 1
    #stop = 2
    #stop = 3
    #stop = 4
    Test("test").run(stop)

