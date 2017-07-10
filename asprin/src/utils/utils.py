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

import os
import tempfile
import re
import clingo

#
# defines
#

# programs
EMPTY     = ""
BASE      = "base"
SPEC      = "specification"
GENERATE  = "generate"
PREFP     = "preference"
PBASE     = "preference_base"
HEURISTIC = "heuristic"
APPROX    = "approximation"
WARNINGS  = "warnings"

# predicate names
DOM        = "dom" 
GEN_DOM    = "gen_dom"
VOLATILE   = "volatile"
MODEL      = "m"
HOLDS      = "holds" 
HOLDSP     = "holds'"
PREFERENCE = "preference"
OPTIMIZE   = "optimize"
UNSAT      = "unsat"
ERROR      = "error"
SHOW       = "show"

# translation tokens
HASH_SEM = "#sem"

# ast
try:
    NO_SIGN = clingo.ast.Sign.None
except Exception as e:
    NO_SIGN = clingo.ast.Sign.NoSign

# errors
ERROR_PROJECT = """\
error: syntax error, unexpected #project statement in {} program
  {}\n"""
ERROR_MINIMIZE = """\
error: syntax error, unexpected clingo optimization statement in {} program
  {}\n"""
ERROR_HEURISTIC = """\
error: syntax error, unexpected clingo heuristic directive in {} program
  {}\n"""
ERROR_DISJOINT = """\
error: syntax error, unexpected disjoint atom in {} program
  {}\n"""
ERROR_CSPLITERAL = """\
error: syntax error, unexpected csp literal in {} program
  {}\n"""
ERROR_KEYWORD = """\
error: syntax error, special predicate depends on non domain atoms in {} program
  {}/{}\n"""
ERROR_HOLDSP = """\
error: syntax error, unexpected holds'/1 predicate in {} program
  {}\n"""

#
# global variables
#
underscores = ""

#
# classes
#

# check program_parser for an usage example
class Capturer:
    
    def __init__(self,stdx):
        self.__original_fd      = stdx.fileno()
        self.__save_original_fd = os.dup(self.__original_fd)
        self.__tmp_file         = tempfile.TemporaryFile()
        os.dup2(self.__tmp_file.fileno(),self.__original_fd)

    def read(self):
        self.__tmp_file.flush()
        self.__tmp_file.seek(0)
        return self.__tmp_file.read()

    def close(self):
        os.dup2(self.__save_original_fd,self.__original_fd)
        os.close(self.__save_original_fd)
        self.__tmp_file.close()

    def translate_error(self,programs,program,string):
        if program != BASE:
            return string
        out = ""
        for i in string.splitlines():
            printed = False
            match = re.match(r'<block>:(\d+):(\d+)-(\d+:)?(\d+): (.*)',i)
            if match:
                # get parsing
                error_line = int(match.group(1))
                col_ini    = int(match.group(2))
                if match.group(3) is not None:
                    line_extra = int(match.group(3)[:-1]) 
                else:
                    line_extra = None
                col_end    = int(match.group(4))
                rest       =     match.group(5)
                # for every position
                positions = programs[program][""].get_positions()
                for pos in positions:
                    if pos.lines >= error_line:
                        # set Location attributes
                        if error_line == 1:
                            col_ini += pos.col - 1
                            if not line_extra:
                                col_end += pos.col - 1
                        loc_line = error_line + pos.line - 1
                        if line_extra is None:
                            loc_line_extra = loc_line
                        else:
                            loc_line_extra = line_extra + pos.line - 1
                        # create Location and print
                        loc = Location(pos.filename, loc_line, col_ini, 
                                       loc_line_extra, col_end)
                        out += "{}{}\n".format(loc,rest)
                        printed = True
                        break
                    else:
                        error_line = error_line - pos.lines
                        if line_extra:
                            line_extra = line_extra - pos.lines
                        else:
                            line_extra = None
            if not printed:
                out += i + "\n"
        # for
        return out

class SilentException(Exception):
    pass

class FatalException(Exception):
    pass

#
# Location, and ProgramPosition
#

class Location(object):
    
    def __init__(self, filename, line, col_ini, line_extra, col_end):
        self.filename   = filename
        self.line       = line
        self.col_ini    = col_ini
        self.line_extra = line_extra
        self.col_end    = col_end

    def get_position(self):
        return ProgramPosition(self.filename, self.line,
                               self.col_ini, self.line_extra - self.line)

    def __repr__(self):
        if not self.line_extra or self.line_extra == self.line:
            extra = ""
        else:
            extra = "{}:".format(self.line_extra)
        args = (self.filename, self.line, self.col_ini, extra, self.col_end)
        return "{}:{}:{}-{}{}: ".format(*args)

# TODO: get rid of this, and use just Location
class ProgramPosition(object):

    def __init__(self, filename, line, col, lines=1):
        self.filename = filename
        self.line     = line
        self.col      = col
        self.lines    = lines # number of lines

