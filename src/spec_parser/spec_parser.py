#!/usr/bin/python

import sys
import yacc
from spec_lexer import Lexer
import ast
import errno
import os

#
#TODO:
#
# - get preference program error/1 predicate
# - pretty print pp errors
# - print Models, Calls, Time...
##
# - tell Roland about column numbers in lexer errors in clingo
# - ask Roland about piping to a file redirecting
# - ask Roland how to get the stats (if possible)
# - ask Roland how to prompt nicely errors in base (column and line ok, not block)
#

#
# defines
#

BASE       = "base"
SPEC       = "specification"
GENERATE   = "generate"
PPROGRAM   = "preference"
HEURISTIC  = "heuristic"
APPROX     = "approximation"
EMPTY      = ""
ASPRIN_LIB = "asprin.lib"
HASH_SEM   = "#sem"
STDIN      = "-"

#
# Exception Handling
#
class ParseError(Exception):
    pass


#
# Warnings (TODO: reorganize)
#
def warning(string):
    print "asprin: warning: " + string


#
#
# Ply Preference Specification Parser
#
#

class Parser(object):


    def __init__(self,underscores):

         # start famework
        self.lexer  = Lexer()
        self.tokens = self.lexer.tokens
        self.lexer.underscores = underscores
        #self.parser = yacc.yacc(module=self,debug=False)
        self.parser = yacc.yacc(module=self)

        # programs
        self.p_statements, self.list = 0, []
        self.programs = dict([(BASE,dict([(EMPTY,"")])),(GENERATE,dict([(EMPTY,"")])),(SPEC,dict([(EMPTY,"")])),(PPROGRAM,dict()),(HEURISTIC,dict()),(APPROX,dict())])

        # base
        self.base      = ast.ProgramStatement()
        self.base.name = BASE
        self.base.type = EMPTY

        # others
        self.program   = BASE
        self.constants = []
        self.included  = []
        self.filename  = ""
        self.error     = False


    #
    # AUXILIARY FUNCTIONS
    #

    def __syntax_error(self,p,index):
        column = p.lexpos(index)-self.lexer.lexer.lexdata.rfind('\n',0,p.lexpos(index))
        error = "{}:{}:{}-{}: error: syntax error, unexpected {}\n".format(
                self.filename,p.lineno(index),column,column+len(p[index].value),p[index].value)
        print >> sys.stderr, error
        self.error = True


    def __error(self,string,p,index):
        error =  "{}:{}:{}: error: syntax error, {}\n".format(
                self.filename,p.lineno(index),p.lexpos(index)-self.lexer.lexer.lexdata.rfind('\n',0,p.lexpos(index)),string)
        print >> sys.stderr, error
        self.error = True


    # return the underscores needed
    def __get_underscores(self):
        return "_" + ("_" * self.lexer.underscores)


    def __parse_str(self,string):
        self.element = ast.Element()
        self.parser.parse(string, self.lexer.lexer) # parses into self.list
        self.lexer.reset()


    def __update_program(self,program,type,string):
        _dict = self.programs.get(program)
        if _dict is None: return
        e = _dict.get(type)
        _dict[type] = e + string if e is not None else string


    def __print_list(self):

        ast.Statement.underscores = self.__get_underscores()
        program, type = BASE, EMPTY

        # add elements of the list
        for i in self.list:
            if i[0] == "CODE":
                self.__update_program(program,type,i[1])
            if i[0] == "PREFERENCE" or i[0] == "OPTIMIZE":
                self.__update_program(SPEC,EMPTY,i[1].str())
            if i[0] == "PROGRAM":
                program, type = i[1].name, i[1].type

        # adding generation of domains
        self.__update_program(GENERATE,EMPTY,"\n".join(ast.Statement.domains))

        # adding to specification
        out = ""
        if ast.PStatement.bfs:
            out +=  ast.BF_ENCODING.replace("##",ast.Statement.underscores)
        out += "\n" + ast.TRUE_ATOM.replace("##",ast.Statement.underscores)
        out += "\n" + ast.PREF_DOM_RULE.replace("##",ast.Statement.underscores)
        self.__update_program(SPEC,EMPTY,out)

        return self.programs


    def __parse_file(self,filename,open_file):
        self.filename       = filename
        self.lexer.filename = filename
        self.lexer.program  = (BASE,EMPTY)
        self.program        = BASE
        self.list.append(("PROGRAM",self.base))
        self.__parse_str(open_file.read())


    def __parse_included_files(self,files):
        while True:
            included, self.included = self.included, []
            for i in included: # (filename,fileorigin)
                file = i[0] if os.path.isfile(i[0]) else os.path.join(os.path.dirname(i[1]),i[0])
                if file in files: warning('file {} included more than once'.format(file))
                else:
                    files.append(file)
                    self.__parse_file(file,open(file))
            if self.included == []: return


    #
    # Input:  options [list of files, bool for reading stdin, bool for including asprin lib]
    # Output: string with the translation, underscores, and constants found
    #
    def parse_files(self,options):

        # gather options
        files, asprin_lib = options['files'], options['asprin-lib']

        # input files
        for i in files:
            if i=="-":
                self.__parse_file(STDIN,sys.stdin)
            else:
                self.__parse_file(i,open(i))

        # included files
        self.__parse_included_files(files)

        # asprin.lib
        if asprin_lib and ASPRIN_LIB not in files:
            self.__parse_file(ASPRIN_LIB,open(ASPRIN_LIB))

        # errors
        if self.lexer.error or self.error:
            raise Exception("parsing failed")

        return self.__print_list(), self.__get_underscores(), self.constants, self.lexer.show



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
    #     Si is a set with weighted bodies of boolean formulas, or with weighted naming atoms, or with a combination of both.
    #   A weighted body of boolean formulas has form:
    #     [T ::] BF1, ..., BFn
    #   or
    #     T ::
    #   where T is a tuple of terms, and
    #   BFi is a boolean formula of literals (using 'not', '&', '|', '(' and ')').
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
    #   bitwise operator & is not allowed (Roland said that this operator will be eliminated from the clingo language)
    #
    # Comparison with minimize statements:
    #   asprin accepts boolean formulas
    #   asprin does not accept @ symbol
    #   asprin requires either 'T ::', or a body of boolean formulas, or a naming atom, while clingo requires T
    #   if an element has no COLONS, asprin interprets it as a body of boolean formulas, or a naming atom, while clingo interprets it as T
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

    def p_program(self,p):
        """ program : program CODE
                    | program statement end_statement
                    |
        """
        if len(p) == 3: self.list.append(("CODE",p[2])) # appends to self.list

    def p_program_error(self,p):
        """ program : program error DOT change_state CODE
                    | program error DOT_EOF
        """
        self.__syntax_error(p,2)

    def p_end_statement(self,p):
        """ end_statement : DOT change_state CODE
                          | DOT_EOF
        """
        if len(p) == 4:
            self.list.append(("CODE",p[3])) # appends to self.list

    def p_change_state(self,p):
        """ change_state :
        """
        p.lexer.pop_state()
        self.lexer.code_start = self.lexer.lexer.lexpos


    #
    # PREFERENCE STATEMENT
    #

    def p_statement_1(self,p):
        """ statement : PREFERENCE LPAREN term COMMA term RPAREN LBRACE elem_list RBRACE body
                      | PREFERENCE LPAREN term COMMA term RPAREN LBRACE           RBRACE body
        """
        # create preference statement
        s = ast.PStatement()
        self.p_statements += 1
        s.number = self.p_statements
        s.name     = p[3]
        s.type     = p[5]
        s.elements = p[8] if len(p) == 11 else []
        s.body     = p[len(p)-1]
        self.list.append(("PREFERENCE",s)) # appends to self.list
        # restart element
        self.element = ast.Element()
        if self.program != BASE: self.__error("unexpected preference statement in non base program",p,1)

    #
    # BODY
    #

    def p_body(self,p):
        """ body : COLON litvec
                 |
        """
        p[0] = None
        if len(p)==3: p[0] = p[2]

    def p_litvec(self,p):
        """ litvec : litvec COMMA         ext_atom
                   | litvec COMMA     NOT ext_atom
                   | litvec COMMA NOT NOT ext_atom
                   |                      ext_atom
                   |                  NOT ext_atom
                   |              NOT NOT ext_atom
        """
        p[0] = p[1:]
        if len(p)>=4 and p[0][1]==",": p[0][1]=", "


    #
    # PREFERENCE ELEMENTS
    #

    def p_elem_list(self,p):
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

    def p_elem(self,p):
        """ elem : elem_head
                 | elem_head COND weighted_body_set
        """
        if len(p) == 2:
            p[0] = (p[1],[])
        else:
            p[0] = (p[1],p[3])
        self.element.vars     = self.element.all_vars

    def p_elem_head(self,p):
        """ elem_head : elem_head GTGT weighted_body_set
                      |                weighted_body_set
        """
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_weighted_body_set(self,p):
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

    def p_weighted_body_1(self,p):
        """ weighted_body :                      bfvec_x
        """
        p[0] = ast.WBody(None,p[1])

    def p_weighted_body_3(self,p):
        """ weighted_body : ntermvec_x TWO_COLON bfvec_x
        """
        p[0] = ast.WBody(p[1],p[3])

    def p_weighted_body_5(self,p):
        """ weighted_body : ntermvec_x TWO_COLON
        """
        p[0] = ast.WBody(p[1],[["ext_atom",["true",["#true"]]]])

    def p_weighted_body_6(self,p):
        """ weighted_body :                      POW_NO_WS term
        """
        p[0] = ast.WBody(None,p[2],True)

    def p_weighted_body_7(self,p):
        """ weighted_body : ntermvec_x TWO_COLON POW_NO_WS term
        """
        p[0] = ast.WBody(p[1],p[4],True)


    #
    # VECTORS
    #

    def p_ntermvec_x(self,p):
        """ ntermvec_x : atomvec
                       | na_ntermvec
                       | atomvec COMMA na_ntermvec
        """
        p[0] = p[1:]

    def p_atomvec(self,p):
        """ atomvec : atom
                    | atomvec COMMA atom
        """
        p[0] = p[1:]
        if len(p)==4:
            self.atomvec.append(["ext_atom",["atom",p[3]]])
        else:
            self.atomvec = [["ext_atom",["atom",p[1]]]]

    def p_na_ntermvec(self,p):
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
    def p_bfvec_x_1(self,p):
        """ bfvec_x  : atomvec
        """
        p[0] = self.atomvec

    def p_bfvec_x_2(self,p):
        """ bfvec_x  : na_bfvec
        """
        p[0] = p[1]

    def p_bfvec_x_3(self,p):
        """ bfvec_x :  atomvec COMMA na_bfvec
        """
        p[0] = self.atomvec + p[3]

    def p_na_bfvec(self,p):
        """ na_bfvec : na_bformula COMMA bfvec
                     | na_bformula
        """
        if len(p)==4:
            p[0] = [p[1]] + p[3]
        else:
            p[0] = [p[1]]

    def p_bfvec(self,p):
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
    # using non reachable token NOREACH for making the grammar LALR(1)
    # (atom) is not allowed
    #
    #    """ bformula :               ext_atom
    #                 |         paren_bformula
    #                 | bformula VBAR bformula %prec BFVBAR
    #                 | bformula AND  bformula %prec BFAND
    #                 |          NOT  bformula %prec BFNOT
    #
    #                 | LPAREN     identifier                      NOREACH
    #                 | LPAREN     identifier LPAREN argvec RPAREN NOREACH
    #                 | LPAREN SUB identifier                      NOREACH
    #                 | LPAREN SUB identifier LPAREN argvec RPAREN NOREACH
    #
    #        paren_bformula : LPAREN na_bformula RPAREN
    #
    #        na_bformula :            na_ext_atom
    #                    |         paren_bformula
    #                    | bformula VBAR bformula %prec BFVBAR
    #                    | bformula AND  bformula %prec BFAND
    #                    |          NOT  bformula %prec BFNOT
    #    """

    def p_bformula_1(self,p):
        """ bformula :               ext_atom
        """
        p[0] = p[1]

    def p_bformula_2(self,p):
        """ bformula :         paren_bformula
        """
        p[0] = p[1]

    def p_bformula_3(self,p):
        """ bformula : bformula VBAR bformula %prec BFVBAR
        """
        p[0] = ["or",[p[1],p[3]]]

    def p_bformula_4(self,p):
        """ bformula : bformula  AND bformula %prec BFAND
        """
        p[0] = ["and",[p[1],p[3]]]

    def p_bformula_5(self,p):
        """ bformula :           NOT bformula %prec BFNOT
        """
        p[0] = ["neg",[p[2]]]

    # unreachable
    def p_formula_6(self,p):
        """ bformula : LPAREN     identifier                      NOREACH IF
                     | LPAREN     identifier LPAREN argvec RPAREN NOREACH IF
                     | LPAREN SUB identifier                      NOREACH IF
                     | LPAREN SUB identifier LPAREN argvec RPAREN NOREACH IF
        """
        pass

    def p_paren_formula(self,p):
        """ paren_bformula : LPAREN na_bformula RPAREN
        """
        p[0] = p[2]

    def p_na_bformula_1(self,p):
        """ na_bformula :            na_ext_atom
        """
        p[0] = p[1]

    def p_na_bformula_2(self,p):
        """ na_bformula :         paren_bformula
        """
        p[0] = p[1]

    def p_na_bformula_3(self,p):
        """ na_bformula : bformula VBAR bformula %prec BFVBAR
        """
        p[0] = ["or",[p[1],p[3]]]

    def p_na_bformula_4(self,p):
        """ na_bformula : bformula  AND bformula %prec BFAND
        """
        p[0] = ["and",[p[1],p[3]]]

    def p_na_bformula_5(self,p):
        """ na_bformula :           NOT bformula %prec BFNOT
        """
        p[0] = ["neg",[p[2]]]


    #
    # NOT ATOM TERMS
    #

    def p_na_term(self,p):
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

    def p_na_term_more(self,p):
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

    def p_many_minus(self,p):
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
    def p_ext_atom_1(self,p):
        """ ext_atom : TRUE
        """
        p[0] = ["ext_atom",["true",["#true"]]]

    def p_ext_atom_2(self,p):
        """ ext_atom : FALSE
        """
        p[0] = ["ext_atom",["false",["#false"]]]

    def p_ext_atom_3(self,p):
        """ ext_atom : atom
        """
        p[0] = ["ext_atom",["atom",p[1]]]

    def p_ext_atom_4(self,p):
        """ ext_atom : term cmp term
        """
        p[0] = ["ext_atom",["cmp",p[1:]]]


    #   """ na_ext_atom : TRUE
    #                   | FALSE
    #                   | term cmp term
    #   """
    def p_na_ext_atom_1(self,p):
        """ na_ext_atom : TRUE
        """
        p[0] = ["ext_atom",["true",["#true"]]]

    def p_na_ext_atom_2(self,p):
        """ na_ext_atom : FALSE
        """
        p[0] = ["ext_atom",["false",["#false"]]]

    def p_na_ext_atom_3(self,p):
        """ na_ext_atom : term cmp term
        """
        p[0] = ["ext_atom",["cmp",p[1:]]]


    #
    # VARIABLES
    #
    def p_variable(self,p):
        """ variable : VARIABLE
        """
        p[0] = p[1]
        self.element.all_vars.add(p[1])


    #
    # GRINGO expressions
    #

    def p_term(self,p):
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

    def __handle_sem(self,p):
        self.element.pooling = True
        if len(p)==4:
            if isinstance(p[1],list) and len(p[1])==2 and p[1][0]==HASH_SEM:
                  return [HASH_SEM,p[1][1] + [p[3]]]
            else: return [HASH_SEM,[p[1]]  + [p[3]]]
        return p[1]

    def p_unaryargvec(self,p):
        """ unaryargvec :                  term
                        |  unaryargvec SEM term
        """
        p[0] = self.__handle_sem(p)

    def p_ntermvec(self,p):
        """ ntermvec : term
                     | ntermvec COMMA term
        """
        p[0] = p[1:]

    def p_termvec(self,p):
        """ termvec : ntermvec
                    |
        """
        p[0] = p[1:]

    def p_tuple(self,p):
        """ tuple : ntermvec COMMA
                  | ntermvec
                  |          COMMA
                  |
        """
        p[0] = p[1:]

    def p_tuplevec(self,p):
        """ tuplevec :              tuple
                     | tuplevec SEM tuple
        """
        p[0] = self.__handle_sem(p)

    def p_argvec(self,p):
        """ argvec :            termvec
                   | argvec SEM termvec
        """
        p[0] = self.__handle_sem(p)

    def p_cmp(self,p):
        """ cmp :  GT
                |  LT
                | GEQ
                | LEQ
                |  EQ
                | NEQ
        """
        p[0] = p[1]

    def p_atom(self,p):
        """ atom :     identifier
                 |     identifier LPAREN argvec RPAREN
                 | SUB identifier
                 | SUB identifier LPAREN argvec RPAREN
        """
        p[0] = p[1:]


    def p_identifier(self,p):
        """ identifier : IDENTIFIER
        """
        p[0] = p[1]


    #
    # OPTIMIZE
    #

    def p_statement_2(self,p):
        """ statement : OPTIMIZE LPAREN term RPAREN body
        """
        s = ast.OStatement()
        s.name     = p[3]
        s.body     = p[5]
        self.list.append(("OPTIMIZE",s)) # appends to self.list
        if self.program != BASE: self.__error("unexpected optimize statement in non base program",p,1)


    #
    # PROGRAM
    #

    def __check_preference_program(self,identifier,ntermvec,p,index):
        if identifier == PPROGRAM and len(ntermvec)!=1:
            self.__error("preference program name must consist of a single term",p,index)


    def p_statement_3(self,p):
        """ statement : PROGRAM identifier LPAREN ntermvec RPAREN
                      | PROGRAM identifier
        """
        s      = ast.ProgramStatement()
        s.name = ast.ast2str(p[2])
        s.type = ast.ast2str(p[4]) if len(p)==6 else EMPTY
        self.list.append(("PROGRAM",s)) # appends to self.list
        self.program       = s.name
        self.lexer.program = (s.name,s.type)
        if len(p)==6:
            self.__check_preference_program(p[2],p[4],p,3)


    #
    # CONST
    #

    def p_statement_4(self,p):
        """ statement : CONST identifier EQ term
        """
        if self.program == BASE:
            self.constants.append((ast.ast2str(p[2]),ast.ast2str(p[4])))
        else:
            self.list.append(("CODE","#const " + ast.ast2str(p[2]) + " = " + ast.ast2str(p[4]) + ".\n"))


    #
    # INCLUDE
    #

    def p_statement_5(self,p):
        """ statement : INCLUDE STRING
        """
        self.included.append((p[2][1:-1],self.filename)) # (file name included,current file name)


    #
    # ERROR
    #

    def p_error(self,p):
        return

