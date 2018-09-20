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

#!/usr/bin/python

from .ply import lex
from ..utils import utils
from ..utils import printer

#
# DEFINES
#

BASE  = utils.BASE
EMPTY = utils.EMPTY
ERROR_LEXER="lexer error, unexpected {}\n"


#
# Lexer
#

class Lexer(object):


    def __init__(self, underscores, options):
        self.__underscores = underscores
        self.__options     = options
        self.__show        = set()
        self.__error       = False
        self.lexer = lex.lex(module=self)
        self.lexer.push_state('normal')


    def new_file(self, filename):
        self.__filename   = filename
        self.__program    = (BASE, EMPTY)
        self.__code_start = 0
        self.__bc         = 0
        self.__eof        = False
        self.lexer.lineno = 1
        while self.lexer.lexstate != 'normal':
            self.lexer.pop_state()


    #
    # GET & SET
    #

    def get_underscores(self):
        return self.__underscores
    
    def get_error(self):
        return self.__error
    
    def get_show(self):
        return self.__show
    
    def set_program(self, program):
        self.__program = program

    def set_code_start(self, code_start):
        self.__code_start = code_start


    #
    # AUXILIARY FUNCTIONS
    #

    def __update_underscores(self, t):
        if t.value[0] == "_":
            i = 0
            while t.value[i] == "_": 
                i += 1
            if i>self.__underscores: 
                self.__underscores = i

    def __print_error(self, string, lexpos):
        col_ini = lexpos-self.lexer.lexdata.rfind('\n', 0, lexpos)
        loc = utils.Location(self.__filename, self.lexer.lineno,
                             col_ini, self.lexer.lineno, col_ini+len(string))
        printer.Printer().print_error_location(loc,ERROR_LEXER.format(string))


    def __eof_error(self, t):
        self.__error = True
        t.lexer.skip(1)
        self.__print_error("<EOF>", t.lexpos)

    def __eof_ok(self, t):
        if self.__eof:   # the second time, returns None 
            return None
        t.value        = t.lexer.lexdata[self.__code_start:t.lexer.lexpos]
        t.type         = 'CODE'
        t.lexer.lexpos = t.lexpos
        self.__eof     = True
        return t       # the first time, returns CODE


    #
    # START OF LEXING RULES
    #

    # Declare the state
    states = (
          ('comment',     'exclusive'),
          ('blockcomment','exclusive'),
          ('script',      'exclusive'),
          ('normal',      'exclusive'),
    )

    # List of token names. This is always required
    tokens = (
        'CODE', # CODE is only used by the defined states
                # the rest are only used in the INITIAL state
        'DOT',
        'PREFERENCE',
        'OPTIMIZE',
        'PROGRAM',
        'CONST',
        'INCLUDE',
        'LPAREN',
        'RPAREN',
        'LBRACE',
        'RBRACE',
        'SEM',
        'TWO_COLON',
        'COLON',
        'COMMA',
        'IDENTIFIER',
        'COND',
        'GTGT',
        'GT',
        'NOT',
        'INFIMUM',
        'SUPREMUM',
        'ANONYMOUS',
        'NUMBER',
        'VARIABLE',
        'STRING',
        'TRUE',
        'FALSE',
        'DOTS',
        'VBAR',
        'ADD',
        'SUB',
        'POW',
        'POW_NO_WS',
        'MOD',
        'MUL',
        'LT',
        'GEQ',
        'LEQ',
        'NEQ',
        'EQ',
        'SLASH',
        'AT',
        'AND',
        'XOR',
        'BNOT',
        'QUESTION',
        'MINIMIZE',
        'MAXIMIZE',
        'NEVER', # never reachable token
        'IF',    # added to expressions with NEVER to avoid warning
    )

    # Regular expression rules for simple tokens
    t_PREFERENCE = r'\#preference'
    t_OPTIMIZE   = r'\#optimize'
    t_PROGRAM    = r'\#program'
    t_CONST      = r'\#const'
    t_INCLUDE    = r'\#include'
    t_DOT        = r'\.'
    t_LPAREN     = r'\('
    t_RPAREN     = r'\)'
    t_LBRACE     = r'\{'
    t_RBRACE     = r'\}'
    t_SEM        = r';'
    t_TWO_COLON  = r'::'
    t_IF         = r':-'
    t_COLON      = r':'
    t_COMMA      = r','
    t_COND       = r'\|\|'
    t_GT         = r'>'
    t_INFIMUM   = r'\#inf(imum)?'
    t_SUPREMUM  = r'\#sup(remum)?'
    t_ANONYMOUS = r'_'
    t_NUMBER    = r'0|([1-9][0-9]*)'
    t_VARIABLE  = r'_*[A-Z][\'A-Za-z0-9_]*'
    t_STRING    = r'\" ( [^\\"\n] | (\\\") | (\\\\) | (\\n) )* \" '
    t_TRUE	    = r'\#true'
    t_FALSE	    = r'\#false'
    t_DOTS	    = r'\.\.'
    t_VBAR	    = r'\|'
    t_ADD	    = r'\+'
    t_SUB	    = r'\-'
    #t_POW	    = r'\*\*'
    t_MOD	    = r'\\'
    t_MUL	    = r'\*'
    t_GTGT	    = r'>>'
    t_LT	    = r'<'
    t_GEQ	    = r'>='
    t_LEQ	    = r'<='
    t_EQ	    = r'(==)|(=)'
    t_NEQ	    = r'(\!=)|(<>)'
    t_SLASH	    = r'\/'
    t_AT	    = r'\@'
    t_AND	    = r'\&'
    t_XOR	    = r'\^'
    t_BNOT	    = r'\~'
    t_QUESTION	= r'\?'
    t_MINIMIZE = r'\#minimize'
    t_MAXIMIZE = r'\#maximize'


    #
    # INITIAL state
    #

    def t_NOT(self, t):
        r'not'
        return t

    def t_WS(self, t):
        r'[\t\r ]+'
        pass

    def t_NL(self, t):
        r'\n+'
        self.lexer.lineno  += len(t.value)

    def t_POW(self, t):
        r'\*\*'
        if len(t.lexer.lexdata) > t.lexer.lexpos:
            if t.lexer.lexdata[t.lexer.lexpos] not in { '\t', '\r', ' ', '\n' }:
                t.type = "POW_NO_WS"
        return t

    def t_BLOCKCOMMENT(self, t):
        r'%\*'
        self.__bc = 1
        t.lexer.push_state('blockcomment')

    def t_COMMENT(self, t):
        r'%|(\#!)'
        t.lexer.push_state('comment')

    def t_IDENTIFIER(self, t):
        r'_*[a-z][\'A-Za-z0-9_]*'
        self.__update_underscores(t)
        return t

    def t_eof(self, t):
        self.__eof_error(t)
        return None


    #
    # normal state
    #

    def t_normal_eof(self, t):
        return self.__eof_ok(t)

    # strings: pass
    def t_normal_STRING(self, t):
        r'\" ( [^\\"\n] | (\\\") | (\\\\) | (\\n) )* \" '
        pass

    # identifier: update underscores'
    def t_normal_IDENTIFIER(self, t):
        r'_*[a-z][\'A-Za-z0-9_]*'
        self.__update_underscores(t)

    # show: update self.__show
    def t_normal_SHOW(self, t):
        r'\#show [\n\t\r ]* ([-\$]?_*[a-z][\'A-Za-z0-9_]* [\n\t\r ]* / [\n\t\r ]* (0|([1-9][0-9]*)))? [\n\t\r ]* \.'
        t.lexer.lexpos = t.lexpos + 1
        self.__show.add(self.__program)

    # project: return error
    def t_normal_PROJECT(self, t):
        r'\#project'
        self.__error = True
        t.lexer.skip(8)
        self.__print_error(t.value, t.lexpos)

    # optimization: in base return error, else continue
    def t_normal_OPTIMIZATION(self, t):
        r'(\#minimize)|(\#maximize)|(:~)'
        if self.__program == (BASE, EMPTY):
            self.__error = True
            t.lexer.skip(len(t.value))
            self.__print_error(t.value, t.lexpos)


    #
    # changing state:
    #  %*                   -> blockcomment
    #  % or \#!             ->      comment
    #  #script (python|lua) ->       script
    #  #directive           ->      INITIAL
    #

    def t_normal_BLOCKCOMMENT(self, t):
        r'%\*'
        self.__bc = 1
        t.lexer.push_state('blockcomment')

    def t_normal_COMMENT(self, t):
        r'%|(\#!)'
        t.lexer.push_state('comment')

    def t_normal_SCRIPT(self, t):
        r'\#script[\t\r ]*\([\t\r ]*(python|lua)[\t\r ]*\)'
        t.lexer.push_state('script')
        t.lexer.lexpos = t.lexpos

    # push INITIAL state, reset lexer lexpos, and return CODE
    def t_normal_DIRECTIVE(self, t):
        r'(\#preference)|(\#optimize)|(\#program)|(\#const)|(\#include)'
        #r'(\#preference)|(\#optimize)|(\#program)|(\#const)|(\#include)|(\#minimize)|(\#maximize)'
        #if ((t.value == "#maximize" or t.value == "#minimize") and
        #    ((self.__program != (BASE, EMPTY)) or
        #     not self.__options['minimize'])):
        #    t.lexer.lexpos = t.lexpos + 1
        #    return
        t.lexer.push_state('INITIAL')
        t.value = t.lexer.lexdata[self.__code_start:t.lexpos]
        t.type = 'CODE'
        t.lexer.lexpos = t.lexpos
        return t

    def t_normal_NL(self, t):
        r'\n'
        self.lexer.lineno += 1

    def t_normal_ANY(self, t):
        r'[\000-\377]'
        pass


    #
    # blockcomment state
    #

    def t_blockcomment_eof(self, t):
        self.__eof_error(t)
        return None
    
    def t_blockcomment_ENDBLOCKCOMMENT(self, t):
        r'\*%'
        self.__bc -= 1
        if self.__bc == 0: 
            t.lexer.pop_state()

    def t_blockcomment_BLOCKCOMMENT(self, t):
        r'%\*'
        self.__bc += 1

    def t_blockcomment_COMMENT(self, t):
        r'%'
        t.lexer.push_state('comment')

    def t_blockcomment_NL(self, t):
        r'\n'
        self.lexer.lineno += 1

    def t_blockcomment_ANY(self, t):
        r'[\000-\377]'
        pass


    #
    # comment state
    #

    def t_comment_eof(self, t):
        if self.__bc > 0:
            self.__eof_error(t)
            return None 
        return self.__eof_ok(t)

    def t_comment_NL(self, t):
        r'\n'
        t.lexer.lineno += 1
        t.lexer.pop_state()

    def t_comment_ANY(self, t):
        r'[\000-\377]'
        pass


    #
    # script state
    #

    def t_script_eof(self, t):
        self.__eof_error(t)
        return None

    def t_script_END(self, t):
        r'\#end'
        t.lexer.pop_state()

    def t_script_NL(self, t):
        r'\n'
        self.lexer.lineno += 1

    def t_script_ANY(self, t):
        r'[\000-\377]'
        pass


    #
    # error handling
    #

    def t_ANY_error(self, t):
        self.__error = True
        t.lexer.skip(1)
        self.__print_error(t.value[0],t.lexpos)

