from __future__ import print_function
from src.utils import clingo_stats
import re
import sys

BASE="base"
ERROR_LEXER="{}:{}:{}-{}: error: lexer error, unexpected {}\n"
ERROR_PARSER="{}:{}:{}-{}: error: syntax error, {}\n"
WARNING_INCLUDED_FILE="<cmd>: warning: already included file:\n  {}\n"

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


    def print_captured_error(self,programs,program,string):
        if program != BASE:
            print(string,end="")
            return
        for i in string.splitlines():
            printed = False
            match = re.match(r'<block>:(\d+):(\d+)-(\d+:)?(\d+)(.*)',i)
            if match:
                error_line = int(match.group(1))
                col_ini    = int(match.group(2))
                line_extra = int(match.group(3)[:-1]) if match.group(3) is not None else None
                col_end    = int(match.group(4))
                rest       =     match.group(5)
                positions = programs[program][""].get_positions()
                for loc in positions:
                    if loc.lines >= error_line:
                        if error_line == 1:
                            col_ini += loc.col - 1
                            if not line_extra:
                                col_end += loc.col - 1
                        print("{}:{}:{}-{}{}{}".format(loc.filename, error_line+loc.line-1,col_ini,
                                                        "{}:".format(line_extra+loc.line-1) if line_extra else "",
                                                        col_end,rest))
                        printed = True
                        break
                    else:
                        error_line = error_line - loc.lines
                        line_extra = line_extra - loc.lines if line_extra else None
            if not printed:
                print(i)


    def __print_warning(sef,string):
        print(string,file=sys.stderr)


    def warning_included_file(self,file):
        self.__print_warning(WARNING_INCLUDED_FILE.format(file))


    def __print_message_location(self,loc):
        return "{}:{}:{}-{}{}:".format(loc.filename,loc.line,loc.col_ini,
                                  "{}:".format(loc.line_extra) if loc.line_extra else "",
                                  loc.col_end)


    def warning_included_file(self,file,loc=None):
        warning = WARNING_INCLUDED_FILE 
        if loc: 
            warning = warning.replace("<cmd>:",self.__print_message_location(loc))
        self.__print_warning(warning.format(file))

    def print_error_lexer(self,filename,lineno,col_ini,col_end,string):
        print(ERROR_LEXER.format(filename,lineno,col_ini,col_end,string))

    def print_error_parser(self,filename,lineno,col_ini,col_end,string):
        print(ERROR_PARSER.format(filename,lineno,col_ini,col_end,string))


    def print_error(self, location, string):
        print("{}{}".format(location,string))


