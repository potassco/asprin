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

import os
import sys
from .ply import yacc
from .ply.lex import LexToken
from .spec_lexer import Lexer
from ..utils import printer
from ..utils import utils
from . import ast


#
# defines
#

# programs
EMPTY     = utils.EMPTY
BASE      = utils.BASE
SPEC      = utils.SPEC
GENERATE  = utils.GENERATE
PREFP     = utils.PREFP
HEURISTIC = utils.HEURISTIC
APPROX    = utils.APPROX
UNSATP    = utils.UNSATP

# predicate names
DOM        = utils.DOM
GEN_DOM    = utils.GEN_DOM

# translation tokens
HASH_SEM   = utils.HASH_SEM

# errors
ERROR_PREFIX = "syntax error, "
ERROR_PREFERENCE = ERROR_PREFIX + "preference statement in non base program\n"
ERROR_OPTIMIZE  = ERROR_PREFIX + "optimize statement in non base program\n"
ERROR_PREFERENCE_NAME = ERROR_PREFIX + "incorrect preference name\n"
ERROR_SYNTAX = ERROR_PREFIX + "unexpected {}\n"
ERROR_CLINGO_STATEMENT = ERROR_PREFIX + """\
clingo optimize statement mixed with a preference specification\n"""

# more
PROGRAM      = "PROGRAM"
CODE         = "CODE"
PREFERENCE   = "PREFERENCE"
OPTIMIZE     = "OPTIMIZE"
STDIN        = "-"
END          = "end."
CLINGOPATH   = "CLINGOPATH"
ASPRIN_LIB   = "asprin_lib.lp"
ASPRIN_LIB_RELATIVE = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                   "..", "..", ASPRIN_LIB)
# WARNING: ASPRIN_LIB_RELATIVE must be changed if 
#          asprin_lib.lp location relative to this file changes

# clingo minimize statements
MINIMIZE_NAME = "clingo"
MINIMIZE_TYPE = "clingo_minimize"

#
# Program
#
class Program(object):

    def __init__(self, string):
        self.__positions = [] # list of utils.ProgramPositions
        self.__string = string 

    def get_string(self):
        return self.__string

    def get_positions(self):
        return self.__positions

    def extend_string(self, string):
        self.__string += "\n" + string

    def extend_positions(self, position):
        self.__positions.append(position)

#
#
# Ply Preference Specification Parser
#
#

class Parser(object):


    def __init__(self, underscores, options):

        # start lexer, parser, and printer
        self.options = options
        self.lexer  = Lexer(underscores, options)
        self.tokens = self.lexer.tokens
        #self.parser = yacc.yacc(module=self,debug=False)
        self.parser = yacc.yacc(module=self)
        self.printer = printer.Printer()

        # programs[name][type] is a Program
        self.p_statements, self.list = 0, []
        l = [BASE, GENERATE, SPEC, PREFP, HEURISTIC, APPROX, UNSATP]
        self.programs = dict([(i,dict()) for i in l])

        # base
        self.base      = ast.ProgramStatement()
        self.base.name = BASE
        self.base.type = EMPTY

        # others
        self.constants   = []
        self.included    = []
        self.error       = False
        self.position    = None
        self.element     = None
        self.filename    = None
        self.program     = None

        # clingo optimize statements
        self.preference_statement = False
        self.clingo_statement     = False


    #
    # AUXILIARY FUNCTIONS
    #

    def __handle_clingo_statements(self, preference, p, init, end):
        if preference:
            self.preference_statement = True
        else:
            self.clingo_statement = True
        if self.preference_statement and self.clingo_statement:
            self.__syntax_error(p, init, end, ERROR_CLINGO_STATEMENT)


    def __get_col(self, data, pos):
        return pos - data.rfind('\n', 0, pos)


    # get Location from non terminal p between init and end
    # p[init] and p[end] should be either terminals, or the error token 
    def __get_location(self, p, init, end):
        filename   = self.filename
        line       = p.lineno(init)
        col_ini    = self.__get_col(self.lexer.lexer.lexdata, p.lexpos(init))
        line_extra = p.lineno(end)
        col_end    = self.__get_col(self.lexer.lexer.lexdata, p.lexpos(end))
        if isinstance(p[end], str):
            col_end += len(p[end])
        elif isinstance(p[end], LexToken):
            col_end += len(p[end].value)
        elif init == end:
            col_end += 1
        return utils.Location(filename, line, col_ini, line_extra, col_end)


    # p[init] and p[end] should be either terminals, or the error token 
    def __syntax_error(self, p, init, end, string):
        self.error = True
        location = self.__get_location(p, init, end)
        self.printer.print_error_location(location, string)


    def __update_program(self, program, type, string, position=None):
        # consider only the program names in self.programs
        dictionary = self.programs.get(program)
        if dictionary is None:
            return
        # update the program type
        program = dictionary.get(type)
        if program is None:
            program = Program(string)
            dictionary[type] = program
        else:
            program.extend_string(string)
        if position is not None:
            program.extend_positions(position)


    def __generate_programs(self):

        underscores = "_" + ("_" * self.lexer.get_underscores())
        ast.Statement.underscores = underscores
        program, type = BASE, EMPTY

        # add elements of the list
        for i in self.list:
            if i[0] == CODE:
                code = i[1]
                # if base: add END to mark the end of the code
                if program == BASE and type == EMPTY:
                    code += underscores + END
                self.__update_program(program, type, code, i[2])
            if i[0] == PREFERENCE or i[0] == OPTIMIZE:
                # translate statement
                self.__update_program(SPEC, EMPTY, i[1].str())
            if i[0] == PROGRAM:
                program, type = i[1].name, i[1].type

        # adding generation of domains
        self.__update_program(GENERATE,EMPTY,"\n".join(ast.Statement.domains))

        # adding specification
        out = ""
        if ast.PStatement.bfs:
            out +=  ast.BF_ENCODING.replace("##",underscores)
        out += "\n" + ast.TRUE_ATOM.replace("##",underscores)
        out += "\n" + ast.PREF_DOM_RULE.replace("##",underscores)
        self.__update_program(SPEC,EMPTY,out)

        return self.programs, underscores


    def __parse_file(self, filename):
        # set variables
        self.filename = filename
        self.program  = BASE
        self.element  = ast.Element()
        self.position = utils.ProgramPosition(self.filename, 1, 1)
        # add #program base to list
        self.list.append((PROGRAM, self.base))
        # prepare lexer
        self.lexer.new_file(filename)
        # handle file descriptor, and parse
        fd = sys.stdin if filename == STDIN else open(filename)
        self.parser.parse(fd.read(), self.lexer.lexer) # parses into self.list
        fd.close()


    def __search_in_clingopath(self, file):
        path = os.environ.get(CLINGOPATH)
        if path is None:
            return None
        full = os.path.join(os.path.dirname(path), file)
        if not os.path.isfile(full):
            return None
        return file


    def __parse_included_files(self, files):
        while True:
            included, self.included = self.included, []
            for i in included: # (filename, fileorigin)
                file = i[0]
                if not os.path.isfile(file): # look in the directory
                    file = os.path.join(os.path.dirname(i[1]), i[0])
                    if not os.path.isfile(file): # look in CLINGOPATH
                        file = self.__search_in_clingopath(i[0])
                        if file is None:
                            self.printer.error_included_file(i[0], i[2])
                            self.error = True
                            continue
                abs_file = os.path.abspath(file)
                if abs_file in [j[1] for j in files]: 
                    self.printer.warning_included_file(file, i[2])
                else:
                    files.append((file, abs_file))
                    self.__parse_file(file)
            if self.included == []:
                return


    #
    # Input:  options [list of files, bool for including asprin lib]
    # Output: translation, underscores, constants, and programs with shown 
    #
    def parse_files(self):

        # input files
        files = self.options['files']
        for i in files:
            if i[0]=="-":
                self.__parse_file(STDIN)
            else:
                self.__parse_file(i[0])

        # included files
        self.__parse_included_files(files)

        # asprin_lib.lp
        #filenames = [os.path.basename(i[0]) for i in files]
        #if self.options['asprin-lib'] and ASPRIN_LIB not in filenames:
        if self.options['asprin-lib']:
            if os.path.isfile(ASPRIN_LIB):
                file = ASPRIN_LIB
            else:
                file = ASPRIN_LIB_RELATIVE
            self.__parse_file(file)

        # errors
        if self.lexer.get_error() or self.error:
            raise Exception("parsing failed")

        # return
        programs, underscores = self.__generate_programs()
        return programs, underscores, self.constants, self.lexer.get_show()



    #
    # Syntax:
    #   A preference statement has form:
    #     #preference(name,type) { E1; ...; En } [ : B ].
    #   where
    #     name and type are terms,
    #     Ei are preference elements, and
    #     B is a body of literals.
    #   A preference element has form:
    #     S1 [ >> ... >> Sn ] [ || S0 ] [ : B ]
    #   where
    #     Si is a set with weighted bodies of boolean formulas, 
    #     or with weighted naming atoms, or with a combination of both.
    #   A weighted body of boolean formulas has form:
    #     [T ::] BF1, ..., BFn
    #   or
    #     T ::
    #   where T is a tuple of terms, and
    #   BFi is a boolean formula of literals 
    #   (using 'not', '&', '|', '(' and ')').
    #   The second case is interpreted as:
    #     T :: #true
    #   A weighted naming atom has form:
    #     [T ::] **A
    #   where A is a term.
    #   An optimize statement has form:
    #     #optimize(name) [ : B ].
    #
    # Minor notes:
    #   (atom)             is not allowed (and never needed :)
    #   bitwise operator & is not allowed (Roland said that this operator
    #     will be eliminated from the clingo language)
    #
    # Comparison with minimize statements:
    #   asprin accepts boolean formulas
    #   asprin does not accept @ symbol
    #   asprin requires either 'T ::', or a body of boolean formulas, or 
    #     a naming atom, while clingo requires T
    #   if an element has no COLONS, asprin interprets it as a body of 
    #     boolean formulas, or a naming atom, while clingo interprets it as T
    # Translation: clingo elements
    #   T [: [ Body ] ]
    # without @ symbol, are translated into asprin elements of form
    #   T :: [ Body ]
    # The translation in the other direction is not always possible
    #

    #
    # START
    #

    precedence = (
        ('left', 'DOTS'),
        ('left', 'XOR'),
        ('left', 'QUESTION'),
        ('left', 'AND'),
        ('left', 'ADD', 'SUB'),
        ('left', 'MUL', 'SLASH', 'MOD'),
        ('right','POW'),
        ('right','POW_NO_WS'),
        ('left', 'UMINUS', 'UBNOT'),
        ('left', 'BFVBAR'),
        ('left', 'BFAND'),
        ('left', 'BFNOT'),
    )

    start = 'program'    # the start symbol in our grammar

    #
    # PROGRAM
    #

    def p_program(self, p):
        """ program : program statement change_state CODE
                    | CODE
        """
        self.position.lines = self.lexer.lexer.lineno - self.position.line + 1
        if   len(p) == 5: 
            self.list.append((CODE,p[4],self.position))
        elif len(p) == 2: 
            self.list.append((CODE,p[1],self.position))

    def p_program_error(self, p):
        """ statement : error DOT
        """
        self.__syntax_error(p,1,1,ERROR_SYNTAX.format(p[1].value))

    def p_change_state(self, p):
        """ change_state :
        """
        p.lexer.pop_state()
        lexpos, lineno = self.lexer.lexer.lexpos, self.lexer.lexer.lineno
        self.lexer.set_code_start(lexpos)
        # position 
        col = lexpos - self.lexer.lexer.lexdata.rfind('\n', 0, lexpos)
        self.position = utils.ProgramPosition(self.filename, lineno, col)


    #
    # PREFERENCE STATEMENT
    #

    def p_statement_1(self, p):
        """ statement : PREFERENCE LPAREN term COMMA term RPAREN \
                        LBRACE elem_list RBRACE body DOT
                      | PREFERENCE LPAREN term COMMA term RPAREN \
                        LBRACE           RBRACE body DOT
        """
        # create preference statement
        s = ast.PStatement()
        self.p_statements += 1
        s.number = self.p_statements
        s.name     = p[3]
        s.type     = p[5]
        s.elements = p[8] if len(p) == 12 else []
        s.body     = p[len(p)-2]
        self.list.append((PREFERENCE,s)) # appends to self.list
        # restart element
        self.element = ast.Element()
        # error if not in base
        if self.program != BASE:
            self.__syntax_error(p,1,len(p)-1,ERROR_PREFERENCE)
        # error if there is also a clingo statement
        self.__handle_clingo_statements(True, p, 1, len(p)-1)


    #
    # BODY
    #

    def p_body(self, p):
        """ body : COLON litvec
                 |
        """
        p[0] = None
        if len(p)==3: p[0] = p[2]

    def p_litvec(self, p):
        """ litvec : litvec COMMA         ext_atom
                   | litvec COMMA     NOT ext_atom
                   | litvec COMMA NOT NOT ext_atom
                   |                      ext_atom
                   |                  NOT ext_atom
                   |              NOT NOT ext_atom
        """
        p[0] = p[1:]


    #
    # PREFERENCE ELEMENTS
    #

    def p_elem_list(self, p):
        """ elem_list : elem_list SEM elem body
                      |               elem body
        """
        # set self.element values & append to elem_list
        if len(p) == 5:
            self.element.sets = p[3][0]
            self.element.cond = p[3][1]
            self.element.body = p[4]
            p[0] = p[1] + [self.element]
        else:
            self.element.sets = p[1][0]
            self.element.cond = p[1][1]
            self.element.body = p[2]
            p[0] = [self.element]
        # restart element
        self.element = ast.Element()

    def p_elem(self, p):
        """ elem : elem_head
                 | elem_head COND weighted_body_set
        """
        if len(p) == 2:
            p[0] = (p[1],[])
        else:
            p[0] = (p[1],p[3])
        self.element.vars = self.element.all_vars

    def p_elem_head(self, p):
        """ elem_head : elem_head GTGT weighted_body_set
                      |                weighted_body_set
        """
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_weighted_body_set(self, p):
        """ weighted_body_set : LBRACE weighted_body_vec RBRACE
                              |        weighted_body
        """
        if len(p) == 4:
            p[0] = p[2]
        else:
            p[0] = [p[1]]

    def p_weighted_body_vec(Self,p):
        """ weighted_body_vec : weighted_body_vec SEM weighted_body
                              |                       weighted_body
        """
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]


    #
    # WEIGHTED BODY
    #

    def p_weighted_body_1(self, p):
        """ weighted_body :                      bfvec_x
        """
        p[0] = ast.WBody(None,p[1])

    def p_weighted_body_3(self, p):
        """ weighted_body : ntermvec_x TWO_COLON bfvec_x
        """
        p[0] = ast.WBody(p[1],p[3])

    def p_weighted_body_5(self, p):
        """ weighted_body : ntermvec_x TWO_COLON
        """
        p[0] = ast.WBody(p[1],[["ext_atom",["true",["#true"]]]])

    def p_weighted_body_6(self, p):
        """ weighted_body :                      POW_NO_WS term
        """
        p[0] = ast.WBody(None,p[2],True)

    def p_weighted_body_7(self, p):
        """ weighted_body : ntermvec_x TWO_COLON POW_NO_WS term
        """
        p[0] = ast.WBody(p[1],p[4],True)


    #
    # VECTORS
    #

    def p_ntermvec_x(self, p):
        """ ntermvec_x : atomvec
                       | na_ntermvec
                       | atomvec COMMA na_ntermvec
        """
        p[0] = p[1:]

    def p_atomvec(self, p):
        """ atomvec : atom
                    | atomvec COMMA atom
        """
        p[0] = p[1:]
        if len(p)==4:
            self.atomvec.append(["ext_atom",["atom",p[3]]])
        else:
            self.atomvec = [["ext_atom",["atom",p[1]]]]

    def p_na_ntermvec(self, p):
        """ na_ntermvec : na_term
                        | na_term COMMA ntermvec
        """
        p[0] = p[1:]

    #
    #   """ bfvec_x : atomvec
    #               | na_bfvec
    #               | atomvec COMMA na_bfvec
    #   """
    #
    #   p[0] becomes a list
    #
    def p_bfvec_x_1(self, p):
        """ bfvec_x  : atomvec
        """
        p[0] = self.atomvec

    def p_bfvec_x_2(self, p):
        """ bfvec_x  : na_bfvec
        """
        p[0] = p[1]

    def p_bfvec_x_3(self, p):
        """ bfvec_x :  atomvec COMMA na_bfvec
        """
        p[0] = self.atomvec + p[3]

    def p_na_bfvec(self, p):
        """ na_bfvec : na_bformula COMMA bfvec
                     | na_bformula
        """
        if len(p)==4:
            p[0] = [p[1]] + p[3]
        else:
            p[0] = [p[1]]

    def p_bfvec(self, p):
        """ bfvec    : bfvec COMMA bformula
                     |             bformula
        """
        if len(p)==4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]


    #
    # BOOLEAN FORMULAS
    #

    #
    # using non reachable token NEVER for making the grammar LALR(1)
    # (atom) is not allowed
    #
    #    """ bformula :               ext_atom
    #                 |         paren_bformula
    #                 | bformula VBAR bformula %prec BFVBAR
    #                 | bformula AND  bformula %prec BFAND
    #                 |          NOT  bformula %prec BFNOT
    #
    #                 | LPAREN     identifier                      NEVER
    #                 | LPAREN     identifier LPAREN argvec RPAREN NEVER
    #                 | LPAREN SUB identifier                      NEVER
    #                 | LPAREN SUB identifier LPAREN argvec RPAREN NEVER
    #
    #        paren_bformula : LPAREN na_bformula RPAREN
    #
    #        na_bformula :            na_ext_atom
    #                    |         paren_bformula
    #                    | bformula VBAR bformula %prec BFVBAR
    #                    | bformula AND  bformula %prec BFAND
    #                    |          NOT  bformula %prec BFNOT
    #    """

    def p_bformula_1(self, p):
        """ bformula :               ext_atom
        """
        p[0] = p[1]

    def p_bformula_2(self, p):
        """ bformula :         paren_bformula
        """
        p[0] = p[1]

    def p_bformula_3(self, p):
        """ bformula : bformula VBAR bformula %prec BFVBAR
        """
        p[0] = ["or",[p[1],p[3]]]

    def p_bformula_4(self, p):
        """ bformula : bformula  AND bformula %prec BFAND
        """
        p[0] = ["and",[p[1],p[3]]]

    def p_bformula_5(self, p):
        """ bformula :           NOT bformula %prec BFNOT
        """
        p[0] = ["neg",[p[2]]]

    # unreachable
    def p_formula_6(self, p):
        """ bformula : LPAREN     identifier                      NEVER IF
                     | LPAREN     identifier LPAREN argvec RPAREN NEVER IF
                     | LPAREN SUB identifier                      NEVER IF
                     | LPAREN SUB identifier LPAREN argvec RPAREN NEVER IF
        """
        pass

    def p_paren_formula(self, p):
        """ paren_bformula : LPAREN na_bformula RPAREN
        """
        p[0] = p[2]

    def p_na_bformula_1(self, p):
        """ na_bformula :            na_ext_atom
        """
        p[0] = p[1]

    def p_na_bformula_2(self, p):
        """ na_bformula :         paren_bformula
        """
        p[0] = p[1]

    def p_na_bformula_3(self, p):
        """ na_bformula : bformula VBAR bformula %prec BFVBAR
        """
        p[0] = ["or",[p[1],p[3]]]

    def p_na_bformula_4(self, p):
        """ na_bformula : bformula  AND bformula %prec BFAND
        """
        p[0] = ["and",[p[1],p[3]]]

    def p_na_bformula_5(self, p):
        """ na_bformula :           NOT bformula %prec BFNOT
        """
        p[0] = ["neg",[p[2]]]


    #
    # NOT ATOM TERMS
    #

    def p_na_term(self, p):
        """ na_term : term      DOTS term
                    | term       XOR term
                    | term  QUESTION term
                    | term       ADD term
                    | term       SUB term
                    | term       MUL term
                    | term     SLASH term
                    | term       MOD term
                    | term       POW term
                    | term POW_NO_WS term
                    |            na_term_more
                    | many_minus na_term_more
                    | many_minus SUB identifier LPAREN argvec RPAREN %prec UMINUS
                    | many_minus SUB identifier
        """
        p[0] = p[1:]

    def p_na_term_more(self, p):
        """ na_term_more : BNOT term %prec UBNOT
                         | LPAREN tuplevec RPAREN
                         | AT identifier LPAREN   argvec RPAREN
                         | VBAR unaryargvec VBAR
                         | NUMBER
                         | STRING
                         | INFIMUM
                         | SUPREMUM
                         | variable
                         | ANONYMOUS
        """
        p[0] = p[1:]

    def p_many_minus(self, p):
        """many_minus : SUB
                      | many_minus SUB %prec UMINUS
        """
        p[0] = p[1:]


    #
    # (NOT ATOM) EXTENDED ATOMS
    #
    #   """ ext_atom : TRUE
    #                | FALSE
    #                | atom
    #                | term cmp term
    #   """
    #
    def p_ext_atom_1(self, p):
        """ ext_atom : TRUE
        """
        p[0] = ["ext_atom",["true",["#true"]]]

    def p_ext_atom_2(self, p):
        """ ext_atom : FALSE
        """
        p[0] = ["ext_atom",["false",["#false"]]]

    def p_ext_atom_3(self, p):
        """ ext_atom : atom
        """
        p[0] = ["ext_atom",["atom",p[1]]]

    def p_ext_atom_4(self, p):
        """ ext_atom : term cmp term
        """
        p[0] = ["ext_atom",["cmp",p[1:]]]


    #   """ na_ext_atom : TRUE
    #                   | FALSE
    #                   | term cmp term
    #   """
    def p_na_ext_atom_1(self, p):
        """ na_ext_atom : TRUE
        """
        p[0] = ["ext_atom",["true",["#true"]]]

    def p_na_ext_atom_2(self, p):
        """ na_ext_atom : FALSE
        """
        p[0] = ["ext_atom",["false",["#false"]]]

    def p_na_ext_atom_3(self, p):
        """ na_ext_atom : term cmp term
        """
        p[0] = ["ext_atom",["cmp",p[1:]]]


    #
    # VARIABLES
    #
    def p_variable(self, p):
        """ variable : VARIABLE
        """
        p[0] = p[1]
        self.element.all_vars.add(p[1])


    #
    # GRINGO expressions
    #

    def p_term(self, p):
        """ term : term      DOTS term
                 | term       XOR term
                 | term  QUESTION term
                 | term       ADD term
                 | term       SUB term
                 | term       MUL term
                 | term     SLASH term
                 | term       MOD term
                 | term       POW term
                 | term POW_NO_WS term
                 |            SUB term %prec UMINUS
                 |           BNOT term %prec UBNOT
                 |               LPAREN tuplevec RPAREN
                 |    identifier LPAREN   argvec RPAREN
                 | AT identifier LPAREN   argvec RPAREN
                 | VBAR unaryargvec VBAR
                 | identifier
                 | NUMBER
                 | STRING
                 | INFIMUM
                 | SUPREMUM
                 | variable
                 | ANONYMOUS
        """
        p[0] = p[1:]

    def __handle_sem(self, p):
        self.element.pooling = True
        if len(p)==4:
            if isinstance(p[1],list) and len(p[1])==2 and p[1][0]==HASH_SEM:
                  return [HASH_SEM,p[1][1] + [p[3]]]
            else: return [HASH_SEM,[p[1]]  + [p[3]]]
        return p[1]

    def p_unaryargvec(self, p):
        """ unaryargvec :                  term
                        |  unaryargvec SEM term
        """
        p[0] = self.__handle_sem(p)

    def p_ntermvec(self, p):
        """ ntermvec : term
                     | ntermvec COMMA term
        """
        p[0] = p[1:]

    def p_termvec(self, p):
        """ termvec : ntermvec
                    |
        """
        p[0] = p[1:]

    def p_tuple(self, p):
        """ tuple : ntermvec COMMA
                  | ntermvec
                  |          COMMA
                  |
        """
        p[0] = p[1:]

    def p_tuplevec(self, p):
        """ tuplevec :              tuple
                     | tuplevec SEM tuple
        """
        p[0] = self.__handle_sem(p)

    def p_argvec(self, p):
        """ argvec :            termvec
                   | argvec SEM termvec
        """
        p[0] = self.__handle_sem(p)

    def p_cmp(self, p):
        """ cmp :  GT
                |  LT
                | GEQ
                | LEQ
                |  EQ
                | NEQ
        """
        p[0] = p[1]

    def p_atom(self, p):
        """ atom :     identifier
                 |     identifier LPAREN argvec RPAREN
                 | SUB identifier
                 | SUB identifier LPAREN argvec RPAREN
        """
        p[0] = p[1:]


    def p_identifier(self, p):
        """ identifier : IDENTIFIER
        """
        p[0] = p[1]


    #
    # OPTIMIZE
    #

    def p_statement_2(self, p):
        """ statement : OPTIMIZE LPAREN term RPAREN body DOT
        """
        s = ast.OStatement()
        s.name     = p[3]
        s.body     = p[5]
        self.list.append((OPTIMIZE,s)) # appends to self.list
        if self.program != BASE: 
            self.__syntax_error(p,1,6,ERROR_OPTIMIZE)
        # error if there is also a clingo statement
        self.__handle_clingo_statements(True, p, 1, len(p)-1)


    #
    # PROGRAM
    #

    def p_statement_3(self, p):
        """ statement : PROGRAM identifier LPAREN ntermvec RPAREN DOT
                      | PROGRAM identifier DOT
        """
        s      = ast.ProgramStatement()
        s.name = ast.ast2str(p[2])
        s.type = ast.ast2str(p[4]) if len(p)==7 else EMPTY
        self.list.append((PROGRAM,s)) # appends to self.list
        self.program = s.name
        self.lexer.set_program((s.name,s.type))
        #TODO: Check if there are variables in ntermvec
        if len(p)==7 and p[2]==PREFP and len(p[4])!=1:
            self.__syntax_error(p,3,5,ERROR_PREFERENCE_NAME)


    #
    # CONST
    #

    def p_statement_4(self, p):
        """ statement : CONST identifier EQ term DOT
        """
        if self.program == BASE:
            self.constants.append((ast.ast2str(p[2]),ast.ast2str(p[4])))
        else:
            line = "#const {}={}.".format(ast.ast2str(p[2]), ast.ast2str(p[4]))
            location = self.__get_location(p,1,5)
            self.list.append((CODE, line, location.get_position()))


    #
    # INCLUDE
    #

    def p_statement_5(self, p):
        """ statement : INCLUDE STRING DOT
        """
        location = self.__get_location(p,1,len(p)-1)
        # (file name included, current file name, location)
        self.included.append((p[2][1:-1],self.filename,location))


    #
    # CLINGO OPTIMIZE STATEMENT (not used now)
    #

    def p_statement_6(self, p):
        """ statement : MINIMIZE LBRACE RBRACE DOT
                      | MAXIMIZE LBRACE RBRACE DOT
                      | MINIMIZE LBRACE min_elem_list RBRACE DOT 
                      | MAXIMIZE LBRACE max_elem_list RBRACE DOT 
        """
        # create preference statement
        s = ast.PStatement()
        self.p_statements += 1
        s.number = self.p_statements
        s.name     = MINIMIZE_NAME
        s.type     = MINIMIZE_TYPE
        s.elements = p[3] if len(p) == 6 else []
        s.body     = None
        self.list.append((PREFERENCE,s)) # appends to self.list
        # restart element
        self.element = ast.Element()
        # error if not in base
        if self.program != BASE:
            self.__syntax_error(p, 1, len(p)-1, ERROR_PREFERENCE)
        # add optimize statement
        s = ast.OStatement()
        s.name     = MINIMIZE_NAME
        s.body     = None
        self.list.append((OPTIMIZE,s)) # appends to self.list
        # error if there is also a preference specification
        self.__handle_clingo_statements(False, p, 1, len(p)-1)

    def p_min_elem_list(self, p):
        """ min_elem_list : min_elem_list SEM min_weighted_body
                          |                   min_weighted_body
        """
        # set self.element values & append to elem_list
        if len(p) == 4:
            self.element.sets = [[p[3]]]
            self.element.cond = []
            self.element.body = None
            p[0] = p[1] + [self.element]
        else:
            self.element.sets = [[p[1]]]
            self.element.cond = [] 
            self.element.body = None
            p[0] = [self.element]
        # restart element
        self.element = ast.Element()

    def p_min_weighted_body_1(self, p):
        """ min_weighted_body : min_weight min_tuple COLON bfvec_x
                              | min_weight min_tuple COLON
                              | min_weight min_tuple
        """
        if len(p) == 5:
            p[0] = ast.WBody(p[1]+p[2], p[4])
        else:
            p[0] = ast.WBody(p[1]+p[2], [["ext_atom",["true",["#true"]]]])

    def p_min_weight(self, p):
        """ min_weight : term AT term
                       | term
        """
        if len(p) == 4:
            p[0] = [p[1], ",", p[3]]
        else:
            p[0] = [p[1], ",", "1"] # by default, level 1

    def p_min_tuple(self, p):
        """ min_tuple : COMMA ntermvec
                      |
        """
        p[0] = []
        if len(p)==3:
            p[0] = p[1:]

    # copy from p_min_elem_list, replacing by max
    def p_max_elem_list(self, p):
        """ max_elem_list : max_elem_list SEM max_weighted_body
                          |                   max_weighted_body
        """
        # set self.element values & append to elem_list
        if len(p) == 4:
            self.element.sets = [[p[3]]]
            self.element.cond = []
            self.element.body = None
            p[0] = p[1] + [self.element]
        else:
            self.element.sets = [[p[1]]]
            self.element.cond = [] 
            self.element.body = None
            p[0] = [self.element]
        # restart element
        self.element = ast.Element()

    # copy from p_min_weighted_body, adding minus
    def p_max_weighted_body_1(self, p):
        """ max_weighted_body : min_weight min_tuple COLON bfvec_x
                              | min_weight min_tuple COLON
                              | min_weight min_tuple
        """
        if len(p) == 5:
            p[0] = ast.WBody(["-"]+p[1]+p[2], p[4])
        else:
            p[0] = ast.WBody(["-"]+p[1]+p[2], [["ext_atom",["true",["#true"]]]])


    #
    # ERROR
    #

    def p_error(self, p):
        return

