#!/usr/bin/python

import lex
# logging
import logging
#logging.basicConfig(filename="q.log", level=logging.DEBUG)



#
# Exception Handling
#
class LexError(Exception):
    pass

class LexIlegalCharacterException(LexError):
    def __init__(self, char):
        self.value = char
    def __str__(self):
        return "Lexer: Illegal character " + repr(self.value)



#
# Lexer
#
class Lexer(object):


    def __init__(self):
        self.lexer = lex.lex(module=self)
        self.lexer.push_state('normal')
        self.code_start = 0
        self.underscores = 0


    def reset(self):
        while self.lexer.lexstate != 'normal':
            self.lexer.pop_state()
        self.code_start = 0


    def __update_underscores(self,t):
        if t.value[0] == "_":
            i = 0
            while t.value[i] == "_": i += 1
            if i>self.underscores: self.underscores = i

    def __eof_error(self,t):
        print("\nlexer error, unexpected <EOF>")
        t.lexer.skip(1)


    #
    # Lexes input:
    #
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

    # List of token names.   This is always required
    tokens = (
        'CODE', # CODE is only used by the defined states
                # the rest are only used in the INITIAL state
        'DOT',
        'DOT_EOF',
        'PREFERENCE',
        'OPTIMIZE',
        'LPAREN',
        'RPAREN',
        'LBRACE',
        'RBRACE',
        #'WS',
        #'NL',
        'SEM',
        'TWO_COLON',
        'COLON',
        'COMMA',
        'IDENTIFIER',
        'COND',
        'GTGT',
        'GT',
        'IF',

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
        #'LBRACK',
        #'RBRACK',
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
        'CSP',
        'CSP_ADD',
        'CSP_SUB',
        'CSP_MUL',
        'CSP_LEQ',
        'CSP_LT',
        'CSP_GEQ',
        'CSP_GT',
        'CSP_EQ',
        'CSP_NEQ',

        'NOREACH', # never reachable token
    )

    # Regular expression rules for simple tokens
    t_PREFERENCE = r'\#preference'
    t_OPTIMIZE   = r'\#optimize'
    t_DOT_EOF    = r'\.\Z'
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
    t_CSP	    = r'\$'
    t_CSP_ADD	= r'\$\+'
    t_CSP_SUB	= r'\$-'
    t_CSP_MUL	= r'\$\*'
    t_CSP_LEQ	= r'\$<='
    t_CSP_LT	= r'\$<'
    t_CSP_GEQ	= r'\$>='
    t_CSP_GT	= r'\$>'
    t_CSP_EQ	= r'(\$==)|(\$=)'
    t_CSP_NEQ	= r'(\$!=)|(\$<>)'


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
        r'\n'
        pass

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
    # Rules for newly defined (not INITIAL) states
    #

    #
    # eof:
    #   return code
    #
    def t_normal_CODE(self,t):
        r'[\000-\377]\Z'
        t.value = t.lexer.lexdata[self.code_start:t.lexer.lexpos]
        return t

    #
    # strings:
    #   pass through them
    #
    def t_normal_STRING(self,t):
        r'\" ( [^\\"\n] | (\\\") | (\\\\) | (\\n) )* \" '
        pass

    #
    # identifier:
    #   update underscores' counter
    #
    def t_normal_IDENTIFIER(self,t):
        r'_*[a-z][\'A-Za-z0-9_]*'
        self.__update_underscores(t)

    #
    # normal: changing state
    #  %*                        -> blockcomment
    #  % or \#!                  ->      comment
    #  #script (python|lua)      ->       script
    #  #preference or #optimize  ->      INITIAL
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

    def t_normal_PREFERENCE(self,t):
        r'(\#preference)|(\#optimize)'
        t.lexer.push_state('INITIAL')
        t.value = t.lexer.lexdata[self.code_start:t.lexpos]
        t.type = 'CODE'
        t.lexer.lexpos = t.lexpos
        return t

    #
    # normal state: pass through characters
    #               until string or change of state (above)
    #
    def t_normal_ANY(self,t):
        r'[\000-\377]'
        pass

    # never reachable token (to avoid warning)
    def t_normal_NOREACH(self,t):
        r'a'
        pass


    #
    # blockcomment state
    #
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

    def t_blockcomment_CODE(self,t):
        r'[\000-\377]\Z'
        self.__eof_error(t)

    def t_blockcomment_ANY(self,t):
        r'[\000-\377]'
        pass


    #
    # comment state
    #
    def t_comment_NL(self,t):
        r'\n'
        t.lexer.pop_state()

    def t_comment_CODE(self,t):
        r'[\000-\377]\Z'
        if self.bc > 0:
            self.__eof_error(t)
            return
        t.value = t.lexer.lexdata[self.code_start:t.lexer.lexpos]
        return t

    def t_comment_ANY(self,t):
        r'[\000-\377]'
        pass


    #
    # script state
    #
    def t_script_END(self,t):
        r'\#end'
        t.lexer.pop_state()

    def t_script_CODE(self,t):
        r'[\000-\377]\Z'
        self.__eof_error(t)

    def t_script_ANY(self,t):
        r'[\000-\377]'
        pass


    #
    # Error handling
    #
    def t_ANY_error(self,t):
        print("\nIllegal character '%s'" % t.value[0])
        t.lexer.skip(1)

