# MIT License
# 
# Copyright (c) 2017 Javier Romero
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -*- coding: utf-8 -*-

from __future__ import print_function
from ..utils import clingo_stats
from ..utils import utils
import sys

BASE = utils.BASE
WARNING_INCLUDED_FILE = "<cmd>: warning: already included file:\n  {}\n"
ERROR_INCLUDED_FILE = "file could not be opened:\n  {}\n"
MESSAGE_LIMIT = 20
TOO_MANY = "too many messages."
SUMMARY_STR="""Calls        : 1
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

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

class Printer:

    messages = 0  # class variables
    last     = "" #

    #
    # errors and warnings
    #
   
    def __check_messages(self, n):
        Printer.messages += n
        if Printer.messages >= MESSAGE_LIMIT:
            pass #raise Exception(TOO_MANY) 

    def __last(self, string):
        if Printer.last == string:
            return True
        Printer.last = string
        return False

    def __print_error(self, string, **kwargs):
        if not self.__last(string):
            sys.stdout.flush()
            print(string, file=sys.stderr, **kwargs)
            self.__check_messages(1)

    def print_error_string(self, string):
        if not self.__last(string):
            sys.stdout.flush()
            print(string, file=sys.stderr, end = "")
            self.__check_messages(int(string.count("\n")/2))

    def print_error_location(self, location, string):
        self.__print_error("{}error: {}".format(location,string))

    def print_error(self, string):
        self.__print_error(string)

    def print_spec_error(self, string):
        self.__print_error(string)

    def print_warning(self, string, **kwargs):
        if not self.__last(string):
            sys.stdout.flush()
            print(string, file=sys.stderr, **kwargs)
            self.__check_messages(1)

    def print_spec_warning(self, string):
        self.print_warning(string)

    def warning_included_file(self, file, loc=None):
        warning = WARNING_INCLUDED_FILE 
        if loc: 
            warning = warning.replace("<cmd>: ", str(loc))
        self.print_warning(warning.format(file))

    def error_included_file(self, file, loc):
        self.print_error_location(loc, ERROR_INCLUDED_FILE.format(file))

    #
    # simply print
    #
    def do_print(self, *args, **kwargs):
        print(*args, **kwargs)

    #
    # stats
    #

    def print_stats(self, ctl, models, more_models,
                    opt_models, non_optimal, 
                    stats, copy_stats, solving):
        # first lines
        out = "\nModels       : {}{}".format(models,"+" if more_models else "")
        if not non_optimal:
            out += "\n  Optimum    : {}".format("yes" if opt_models>0 else "no")
            if opt_models > 0:
                out += "\n  Optimal    : {}".format(opt_models)
        out += "\n"
        # copy stats
        if copy_stats is not None:
            ctl = Bunch(statistics=copy_stats)
        # gather string
        if not solving:
            out += SUMMARY_STR + STATS_STR if stats else SUMMARY_STR
        else:
            out += clingo_stats.Stats().summary(ctl, False)
            if stats:
                out += "\n" + clingo_stats.Stats().statistics(ctl)
        # print
        print(out)
        sys.stdout.flush()

