from __future__ import print_function
from src.utils import clingo_stats
from src.utils import utils
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
            raise Exception(TOO_MANY) 

    def __last(self, string):
        if Printer.last == string:
            return True
        Printer.last = string
        return False

    def __print_warning(self, string, **kwargs):
        if not self.__last(string):
            sys.stdout.flush()
            print(string, file=sys.stderr, **kwargs)
            self.__check_messages(1)

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

    def print_spec_error(self,string):
        self.__print_error(string)

    def warning_included_file(self,file,loc=None):
        warning = WARNING_INCLUDED_FILE 
        if loc: 
            warning = warning.replace("<cmd>: ",str(loc))
        self.__print_warning(warning.format(file))

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

    def print_stats(self,control,models,more_models,opt_models,stats=False):
        print("")
        print("Models       : {}{}".format(models,"+" if more_models else ""))
        print("  Optimum    : {}".format("yes" if opt_models>0 else "no"))
        if opt_models > 1:
            print("  Optimal    : {}".format(opt_models))
        print(clingo_stats.Stats().summary(control,False))
        if stats:
            print(clingo_stats.Stats().statistics(control))

