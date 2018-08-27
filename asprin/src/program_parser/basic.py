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

import clingo.ast
from ..utils import utils
from ..program_parser import transitive_closure
from ..program_parser import visitor


#
# DEFINES
#

# predicates
HOLDS      = utils.HOLDS
HOLDSP     = utils.HOLDSP
PREFERENCE = utils.PREFERENCE
OPTIMIZE   = utils.OPTIMIZE

# ems
M1    = visitor.M1
M2    = visitor.M2
M1_M2 = visitor.M1_M2
ZERO  = visitor.ZERO

# errors
ERROR_PROJECT    = utils.ERROR_PROJECT
ERROR_MINIMIZE   = utils.ERROR_MINIMIZE
ERROR_DISJOINT   = utils.ERROR_DISJOINT
ERROR_CSPLITERAL = utils.ERROR_CSPLITERAL
ERROR_HOLDSP     = utils.ERROR_HOLDSP


class BasicTermTransformer(visitor.TermTransformer):

    def __init__(self, underscores):
        visitor.TermTransformer.__init__(self)
        self.__underscores = underscores

    def set_predicates_info(self):
        self.predicates_info = dict()
        PredicateInfo = visitor.PredicateInfo
        self.predicates_info[(HOLDS, 1)]  = PredicateInfo(None, 0, ZERO, 1)
        info = PredicateInfo(None, 0, None, 0)
        for i in [(OPTIMIZE, 1), (PREFERENCE, 2), (PREFERENCE, 5)]:
            self.predicates_info[i] = info
        self.default = PredicateInfo(None, self.__underscores, None, 0)


class BasicProgramVisitor(visitor.Visitor):

    def __init__(self, builder, type, underscores, constants):
        visitor.Visitor.__init__(self)
        self.type = type
        self.helper = visitor.Helper()
        self.__builder = builder
        self.__underscores = underscores
        self.__constants = constants
        self.__in_program = False
        self.__term_transformer = BasicTermTransformer(underscores)
        self.__term_transformer.set_predicates_info()

    def __add(self, statement):
        if not self.__in_program:
            prg = clingo.ast.Program(statement.location, self.type, [])
            self.__builder.add(prg)
            self.__in_program = True
        self.__builder.add(statement)

    #
    # Statements
    #

    def visit_Rule(self, rule):
        self.visit_children(rule)
        self.__add(rule)

    def visit_Definition(self, d):
        if d.name not in self.__constants:
            self.__add(d)

    def visit_ShowSignature(self, sig):
        if sig.name != "" or sig.arity != 0:
            self.__term_transformer.transform_signature(sig)
        self.__add(sig)

    def visit_Defined(self, defined):
        if defined.name != "" or defined.arity != 0:
            self.__term_transformer.transform_signature(defined)
        self.__add(defined)

    def visit_ShowTerm(self, show):
        self.visit_children(show)
        show.term = self.__term_transformer.reify_term(show.term,
                                                       self.helper.show)
        self.__add(show)

    def visit_Minimize(self, min):
        self.visit_children(min)
        self.__add(min)

    def visit_Script(self, script):
        self.__add(script)

    def visit_Program(self, prg):
        pass # ignore

    def visit_External(self, ext):
        pass # ignore

    def visit_Edge(self, edge):
        self.visit_children(edge)
        tt = self.__term_transformer
        edge.u = tt.reify_term(edge.u, self.helper.edge + "_" + self.type)
        edge.v = tt.reify_term(edge.v, self.helper.edge + "_" + self.type)
        self.__add(edge)

    def visit_Heuristic(self, heur):
        self.visit_children(heur)
        self.__add(heur)

    def visit_ProjectAtom(self,atom):
        string = ERROR_PROJECT.format(self.type, str(atom))
        self.helper.raise_exception(string)

    def visit_ProjectSignature(self, sig):
        string = ERROR_PROJECT.format(self.type, str(sig))
        self.helper.raise_exception(string)


    #
    # Elements
    #

    def visit_SymbolicAtom(self, atom):
        if str(atom.term.type) == "Function":
            if atom.term.name == HOLDSP and len(atom.term.arguments)==1:
                string = ERROR_HOLDSP.format(self.type, str(atom))
                self.helper.raise_exception(string)
            self.__term_transformer.transform_function(atom.term)

    # csp literals are not accepted
    def visit_CSPLiteral(self,csp):
        string = ERROR_CSPLITERAL.format(self.type, str(csp))
        self.helper.raise_exception(string)

    # disjoint atoms are not accepted
    def visit_Disjoint(self,d):
        string = ERROR_DISJOINT.format(self.type, str(d))
        self.helper.raise_exception(string)


class HeuristicProgramVisitor(BasicProgramVisitor):

    def __init__(self, builder, type, underscores, consts):
        BasicProgramVisitor.__init__(self, builder, type, underscores, consts)

    def visit_Minimize(self, min):
        string = ERROR_MINIMIZE.format(self.type, str(min))
        self.helper.raise_exception(string)

