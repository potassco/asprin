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
            self.__check_messages(int(string.count("\n")//2))

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
                    opt_models, non_optimal, stats, file=sys.stdout):
        out = "\nModels       : {}{}\n".format(
                models,"+" if more_models else ""
            )
        if not non_optimal:
            out += "  Optimum    : {}\n".format("yes" if opt_models>0 else "no")
            if opt_models > 0:
                out += "  Optimal    : {}\n".format(opt_models)
        out += clingo_stats.Stats().summary(ctl, False) + "\n"
        if stats:
            accu = clingo_stats.Stats().statistics(ctl)
            if accu:
                out += accu + "\n"
        print(out, end="", file=file)

