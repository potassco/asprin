from __future__ import print_function
from src.utils import clingo_stats
import re


BASE="base"


class Printer:


    def print_stats(self,control,models,more_models,opt_models,stats=False):
        print("")
        print("Models       : {}{}".format(models,"+" if more_models else ""))
        print("  Optimum    : {}".format("yes" if opt_models>0 else "no"))
        if opt_models > 1:
            print("  Optimal    : {}".format(opt_models))
        print(clingo_stats.Stats().summary(control,False))
        if stats:
            print(clingo_stats.Stats().statistics(control))


    def print_error(self,programs,program,string):
        if program != BASE:
            print(string,end="")
            return
        for i in string.splitlines():
            printed = False
            match = re.match(r'<block>:(\d+):(\d+)-(\d+:)?(\d+)(.*)',i)
            if match:
                error_line = int(match.group(1))
                col_ini    = int(match.group(2))
                extra_line = int(match.group(3)[:-1]) if match.group(3) is not None else None
                col_end    = int(match.group(4))
                rest       =     match.group(5)
                locations = programs[program][""].get_locations()
                for loc in locations:
                    if loc.lines >= error_line:
                        if error_line == 1:
                            col_ini += loc.col - 1
                            if not extra_line:
                                col_end += loc.col - 1
                        print("{}:{}:{}-{}{}{}".format(loc.filename, error_line+loc.line-1,col_ini,
                                                        "{}:".format(extra_line+loc.line-1) if extra_line else "",
                                                        col_end,rest))
                        printed = True
                        break
                    else:
                        error_line = error_line - loc.lines
                        extra_line = extra_line - loc.lines if extra_line else None
            if not printed:
                print(i)
