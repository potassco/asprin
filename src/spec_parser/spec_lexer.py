#!/usr/bin/python

import lex
import sys

#
# DEFINES
#

BASE  = "base" #from spec_parser
EMPTY = ""     #from spec_parser

#
# Lexer
#
class Lexer(object):


    def __init__(self):
        self.lexer = lex.lex(module=self)
        self.underscores  = 0
        self.show         = set()
        self.filename     = ""
        self.error        = False
        # resettable 
        self.lexer.push_state('normal')
        self.bc            = 0
        self.code_start    = 0
        self.lexer.lineno  = 1
        self.program       = (BASE,EMPTY)
        self.eof           = False


    def reset(self):
        while self.lexer.lexstate != 'normal':
            self.lexer.pop_state()
        self.bc            = 0
        self.code_start    = 0
        self.lexer.lineno  = 1
        self.program       = (BASE,EMPTY)
        self.eof           = False

    def __update_underscores(self,t):
        if t.value[0] == "_":
            i = 0
            while t.value[i] == "_": i += 1
            if i>self.underscores: self.underscores = i


    def __error(self,string,lexpos):
        error = "{}:{}:{}: error: lexer error, unexpected {}\n".format(
                self.filename,self.lexer.lineno,lexpos-self.lexer.lexdata.rfind('\n',0,lexpos),string)
        print >> sys.stderr, error
        self.error = True


    def __eof_error(self,t):
        self.__error("<EOF>",t.lexpos)
        t.lexer.skip(1)


    def __eof_ok(self,t):
        if self.eof:   # the second time, returns None 
            return None
        t.value        = t.lexer.lexdata[self.code_start:t.lexer.lexpos]
        t.type         = 'CODE'
        t.lexer.lexpos = t.lexpos
        self.eof       = True
        return t       # the first time, returns CODE


    #
    # Lexer input:
    #

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

        'NOREACH', # never reachable token
        'IF',      # added to expressions with NOREACH to avoid warning
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
    t_MOD	    = r'\\\\'
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


    #
    # INITIAL
    #

    def t_NOT(self,t):
        r'not'
        return t

    def t_WS(self,t):
        r'[\t\r ]+'
        pass

    def t_NL(self,t):
        r'\n+'
        self.lexer.lineno  += len(t.value)

    def t_POW(self,t):
        r'\*\*'
        if len(t.lexer.lexdata) > t.lexer.lexpos:
            if t.lexer.lexdata[t.lexer.lexpos] not in { '\t', '\r', ' ', '\n' }:
                t.type = "POW_NO_WS"
        return t

    def t_BLOCKCOMMENT(self,t):
        r'%\*'
        self.bc = 1
        t.lexer.push_state('blockcomment')

    def t_COMMENT(self,t):
        r'%|(\#!)'
        t.lexer.push_state('comment')

    def t_IDENTIFIER(self,t):
        r'_*[a-z][\'A-Za-z0-9_]*'
        self.__update_underscores(t)
        return t


    #
    # Rules for normal state
    #

    def t_normal_eof(self,t):
        return self.__eof_ok(t)

    # strings: pass
    def t_normal_STRING(self,t):
        r'\" ( [^\\"\n] | (\\\") | (\\\\) | (\\n) )* \" '
        pass

    # identifier: update underscores'
    def t_normal_IDENTIFIER(self,t):
        r'_*[a-z][\'A-Za-z0-9_]*'
        self.__update_underscores(t)

    # show: update self.show
    def t_normal_SHOW(self,t):
        r'\#show [\n\t\r ]* ([-\$]?_*[a-z][\'A-Za-z0-9_]* [\n\t\r ]* / [\n\t\r ]* (0|([1-9][0-9]*)))? [\n\t\r ]* \.'
        t.lexer.lexpos = t.lexpos + 1
        self.show.add(self.program)


    #
    # changing state:
    #  %*                   -> blockcomment
    #  % or \#!             ->      comment
    #  #script (python|lua) ->       script
    #  #directive           ->      INITIAL
    #
    def t_normal_BLOCKCOMMENT(self,t):
        r'%\*'
        self.bc = 1
        t.lexer.push_state('blockcomment')

    def t_normal_COMMENT(self,t):
        r'%|(\#!)'
        t.lexer.push_state('comment')

    def t_normal_SCRIPT(self,t):
        r'\#script[\t\r ]*\([\t\r ]*(python|lua)[\t\r ]*\)'
        t.lexer.push_state('script')
        t.lexer.lexpos = t.lexpos

    # push INITIAL state, reset lexer lexpos, and return CODE
    def t_normal_DIRECTIVE(self,t):
        r'(\#preference)|(\#optimize)|(\#program)|(\#const)|(\#include)'
        t.lexer.push_state('INITIAL')
        t.value = t.lexer.lexdata[self.code_start:t.lexpos]
        t.type = 'CODE'
        t.lexer.lexpos = t.lexpos
        return t

    def t_normal_NL(self,t):
        r'\n'
        self.lexer.lineno += 1

    def t_normal_ANY(self,t):
        r'[\000-\377]'
        pass


    #
    # blockcomment state
    #
    def t_blockcomment_eof(self,t):
        self.__eof_error(t)
        return None
    
    def t_blockcomment_ENDBLOCKCOMMENT(self,t):
        r'\*%'
        self.bc -= 1
        if self.bc == 0: t.lexer.pop_state()

    def t_blockcomment_BLOCKCOMMENT(self,t):
        r'%\*'
        self.bc += 1

    def t_blockcomment_COMMENT(self,t):
        r'%'
        t.lexer.push_state('comment')

    def t_blockcomment_NL(self,t):
        r'\n'
        self.lexer.lineno += 1

    def t_blockcomment_ANY(self,t):
        r'[\000-\377]'
        pass


    #
    # comment state
    #
    def t_comment_eof(self,t):
        if self.bc > 0:
            self.__eof_error(t)
            return None 
        return self.__eof_ok(t)

    def t_comment_NL(self,t):
        r'\n'
        t.lexer.lineno += 1
        t.lexer.pop_state()

    def t_comment_ANY(self,t):
        r'[\000-\377]'
        pass


    #
    # script state
    #
    def t_script_eof(self,t):
        self.__eof_error(t)
        return None

    def t_script_END(self,t):
        r'\#end'
        t.lexer.pop_state()

    def t_script_NL(self,t):
        r'\n'
        self.lexer.lineno += 1

    def t_script_ANY(self,t):
        r'[\000-\377]'
        pass


    #
    # Error handling
    #
    def t_ANY_error(self,t):
        self.__error(t.value[0],t.lexpos)
        t.lexer.skip(1)

