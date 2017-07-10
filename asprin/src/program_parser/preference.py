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

# programs
PREFP = utils.PREFP
PBASE = utils.PBASE

# predicates
HOLDS      = utils.HOLDS
HOLDSP     = utils.HOLDSP
PREFERENCE = utils.PREFERENCE
OPTIMIZE   = utils.OPTIMIZE

# graph
HOLDS_KEY  = (HOLDS,  1)
HOLDSP_KEY = (HOLDSP, 1)
OPEN_NAME  = "open"

# ems
M1 = visitor.M1
M2 = visitor.M2
M1_M2 = visitor.M1_M2

# errors
ERROR_PROJECT    = utils.ERROR_PROJECT
ERROR_MINIMIZE   = utils.ERROR_MINIMIZE
ERROR_HEURISTIC  = utils.ERROR_HEURISTIC
ERROR_DISJOINT   = utils.ERROR_DISJOINT
ERROR_CSPLITERAL = utils.ERROR_CSPLITERAL
ERROR_KEYWORD    = utils.ERROR_KEYWORD

# no sign
NO_SIGN = utils.NO_SIGN

class PreferenceTermTransformer(visitor.TermTransformer):

    def __init__(self, type):
        visitor.TermTransformer.__init__(self)
        self.__type = type

    def set_predicates_info(self, open):
        self.predicates_info = dict()
        PredicateInfo = visitor.PredicateInfo
        info = PredicateInfo(None, 1, M1_M2, 2)
        for i in open:
            self.predicates_info[i] = info
        # HOLDS and HOLDS' appear always in open, and should be always overriden
        self.predicates_info[(HOLDS, 1)]  = PredicateInfo(None, 0, M1, 1)
        self.predicates_info[(HOLDSP, 1)] = PredicateInfo(HOLDS, 0, M2, 1)
        info = PredicateInfo(None, 0, None, 0)
        for i in [(OPTIMIZE, 1), (PREFERENCE, 2), (PREFERENCE, 5)]:
            if i in self.predicates_info:
                string = ERROR_KEYWORD.format(self.__type, i[0], i[1])
                visitor.Helper().raise_exception(string)
            else:
                self.predicates_info[i] = info
        self.default = PredicateInfo(None, 1, None, 0)


class Graph:

    def __init__(self):
        self.__tc = transitive_closure.TransitiveClosure()
        NodeInfo = transitive_closure.NodeInfo
        self.__open = NodeInfo((visitor.Helper().underscore(OPEN_NAME),0), None)
        holds  = NodeInfo(HOLDS_KEY,  None)
        holdsp = NodeInfo(HOLDSP_KEY, None)
        self.__tc.add_node(self.__open)
        self.__tc.add_node(holds)
        self.__tc.add_node(holdsp)
        self.__tc.add_edge(self.__open, holds, True)
        self.__tc.add_edge(self.__open, holdsp, True)
        self.__heads, self.__bodies = [], []

    def __str__(self):
        out = str(self.__tc)
        out += "\n" + str(self.__tc.get_next(self.__open.key))
        return out

    #
    # parsing a rule:
    #   add_atom()* update()
    #

    def __get_info(self, term):
        return transitive_closure.NodeInfo((term.name, len(term.arguments)),
                                           term)

    def add_atom(self, term, in_head, in_body, flag):
        info = self.__get_info(term)
        self.__tc.add_node(info)
        if in_head:
            self.__heads.append((info, flag))
            if flag:
                self.__tc.add_edge(self.__open, info, False)
        if in_body:
            self.__bodies.append((info, flag))

    def update(self):
        for i in self.__heads:
            for j in self.__bodies:
                self.__tc.add_edge(j[0], i[0], j[1])
        self.__heads, self.__bodies = [], []

    #
    # after parsing all rules
    #

    def get_open(self):
        for i in self.__tc.get_cycles():
            self.__tc.add_edge(self.__open, i, False)
        return self.__tc.get_next(self.__open.key)

    def map_items(self, function):
        self.__tc.map_items(function)


class Statement:
    def __init__(self, type, statement):
        self.type = type
        self.statement = statement
        self.preds = []


class Condition:
    def __init__(self, condition, location):
        self.condition = condition
        self.location = location
        self.preds = []


class PreferenceProgramVisitor(visitor.Visitor):

    def __init__(self, builder):
        visitor.Visitor.__init__(self)
        self.__builder    = builder
        self.__type       = PREFP
        self.__statements = []
        self.__conditions = []
        self.__graph      = Graph()
        self.__helper     = visitor.Helper()
        self.__term_transformer = PreferenceTermTransformer(self.__type)
        # tracing position
        self.in_Head, self.in_Body, self.in_Condition = False, False, False
        self.in_Literal_ConditionalLiteral = False

    #
    # AUXILIARY FUNCTIONS
    #
    
    def __visit_body(self, body):
        self.in_Body = True
        self.visit(body)
        self.in_Body = False

    def __visit_condition(self, condition, location):
        self.in_Condition = True
        self.__conditions.append(Condition(condition, location))
        self.visit(condition)
        self.in_Condition = False

    # element is either a Statement or a Condition
    def __is_nondet(self, element, open_list):
        for i in element.preds:
            if i in open_list:
                return True
        return False

    def __add_volatile(self, body, location):
        body.append(self.__helper.get_volatile_atom(location))

    def __get_params(self, location):
        id1 = clingo.ast.Id(location, self.__helper.underscore(M1))
        id2 = clingo.ast.Id(location, self.__helper.underscore(M2))
        return [id1, id2]

    def __get_program(self, nondet, loc):
        if not nondet:
            return clingo.ast.Program(loc, PBASE,[])
        return clingo.ast.Program(loc, PREFP, self.__get_params(loc))

    #
    # finish() after visiting all
    #

    def finish(self):
        # get open predicates from the graph
        open_list = self.__graph.get_open()
        # set predicates_info in term_transformer
        self.__term_transformer.set_predicates_info(open_list)
        # tranform items stored in the graph
        self.__graph.map_items(self.__term_transformer.transform_function)
        # iterate over conditions
        for c in self.__conditions:
            if self.__is_nondet(c, open_list):
                self.__add_volatile(c.condition, c.location)
        # iterate over statements
        in_nondet, add = None, self.__builder.add
        for st in self.__statements:
            method = "finish_" + st.type
            nondet = getattr(self, method, lambda x, y: False)(st, open_list)
            if nondet != in_nondet:
                add(self.__get_program(nondet, st.statement.location))
                in_nondet = nondet
            add(st.statement)

    #
    # Statements
    #

    def visit_Rule(self, rule):
        self.__statements.append(Statement("Rule", rule))
        # head
        self.in_Head = True
        # if empty head
        if (str(rule.head.type) == "Literal"
            and str(rule.head.atom.type) == "BooleanConstant"
            and str(rule.head.atom.value == False)):
            # add unsat head
            atom = clingo.ast.SymbolicAtom(clingo.ast.Function(rule.location,
                   self.__helper.unsat,
                   self.__helper.get_ems(rule.location, M1_M2), False))
            rule.head = clingo.ast.Literal(rule.location, NO_SIGN, atom)
            self.__statements[-1].preds.append(HOLDS_KEY) # make it nondet
        else:
            self.visit(rule.head)
        self.in_Head = False
        # body
        self.__visit_body(rule.body)
        # graph
        self.__graph.update()

    def finish_Rule(self, statement, open_list):
        rule = statement.statement
        if self.__is_nondet(statement, open_list):
            self.__add_volatile(rule.body, rule.location)
            return True

    def visit_Definition(self, d):
        self.__statements.append(Statement("Definition", d))

    def visit_ShowSignature(self, sig):
        self.__statements.append(Statement("ShowSignature", sig))

    def finish_ShowSignature(self, statement, open_list):
        self.__term_transformer.transform_signature(statement.statement)

    def visit_ShowTerm(self, show):
        self.__statements.append(Statement("ShowTerm", show))
        self.__visit_body(show.body)
        self.__graph.update()

    def finish_ShowTerm(self, statement, open_list):
        show, tt = statement.statement, self.__term_transformer
        show.term = tt.reify_term(show.term, self.__helper.show)
        if self.__is_nondet(statement, open_list):
            self.__add_volatile(show.body, show.location)
            tt.extend_function(show.term, M1_M2)
            return True

    def visit_Minimize(self, min):
        string = ERROR_MINIMIZE.format(self.__type, str(min))
        self.__helper.raise_exception(string)

    def visit_Script(self, script):
        self.__statements.append(Statement("Script", script))

    def visit_Program(self, prg):
        pass # ignore

    def visit_External(self, ext):
        pass # ignore

    # TODO: Warn if computing many models (as for disjunction...)
    def visit_Edge(self, edge):
        self.__statements.append(Statement("Edge", edge))
        self.__visit_body(edge.body)
        self.__graph.update()

    def finish_Edge(self, statement, open_list):
        edge, tt = statement.statement, self.__term_transformer
        edge.u = tt.reify_term(edge.u, self.__helper.edge)
        tt.extend_function(edge.u, M1_M2)
        edge.v = tt.reify_term(edge.v, self.__helper.edge)
        tt.extend_function(edge.v, M1_M2)
        # could be done only if *some* edge is nondet
        self.__add_volatile(edge.body, edge.location)
        return True

    #TODO: holds(X) in head ok
    def visit_Heuristic(self, heur):
        string = ERROR_HEURISTIC.format(self.__type, str(heur))
        self.__helper.raise_exception(string)
        self.__statements.append(Statement("Heuristic", heur))
        self.__visit_body(heur.body)
        # head
        term = heur.atom.term
        if str(term.type) == "Function":
            self.__graph.add_atom(term, False, False, False)
            self.__statements[-1].preds.append((term.name, len(term.arguments)))
        # update graph
        self.__graph.update()

    #TODO: holds(X) in head ok
    def finish_Heuristic(self, statement, open_list):
        heur = statement.statement
        if self.__is_nondet(statement, open_list):
            self.__add_volatile(heur.body, heur.location)
            return True

    def visit_ProjectAtom(self,atom):
        string = ERROR_PROJECT.format(self.__type, str(atom))
        self.__helper.raise_exception(string)

    def visit_ProjectSignature(self, sig):
        string = ERROR_PROJECT.format(self.__type, str(sig))
        self.__helper.raise_exception(string)

    #
    # Elements
    #

    def visit_Literal(self, lit):
        atom_type = str(lit.atom.type)
        # if lit is a symbolic regular atom
        if atom_type == "SymbolicAtom" and \
           str(lit.atom.term.type) == "Function":
            # set flag
            flag = False
            if (self.in_Head and self.in_Literal_ConditionalLiteral) or \
               (self.in_Body and (
                lit.sign != NO_SIGN                         or \
                self.in_Aggregate                           or \
                self.in_TheoryAtom or self.in_BodyAggregate or \
                (self.in_ConditionalLiteral and 
                 not self.in_Literal_ConditionalLiteral))):
                flag = True
            # update graph and statements list
            term = lit.atom.term
            self.__graph.add_atom(term, self.in_Head, self.in_Body, flag)
            sig = (term.name, len(term.arguments))
            self.__statements[-1].preds.append(sig)
            if self.in_Condition:
                self.__conditions[-1].preds.append(sig)
        # if list is a special Literal, visit the children
        if atom_type not in ["Comparison", "BooleanConstant", "SymbolicAtom"]:
            self.visit_children(lit)

    # csp literals are not accepted
    def visit_CSPLiteral(self, csp):
        string = ERROR_CSPLITERAL.format(self.__type, str(csp))
        self.__helper.raise_exception(string)

    def visit_ConditionalLiteral(self, c):
        self.in_Literal_ConditionalLiteral = True
        self.visit(c.literal)
        self.in_Literal_ConditionalLiteral = False
        self.__visit_condition(c.condition, c.location)

    def visit_Aggregate(self, a):
        self.visit_children(a)

    def visit_TheoryAtom(self, th):
        for i in th.elements:
            self.__visit_condition(i.condition, th.location)

    def visit_BodyAggregate(self, b):
        for i in b.elements:
            self.__visit_condition(i.condition, b.location)

    # disjoint atoms are not accepted
    def visit_Disjoint(self, d):
        string = ERROR_DISJOINT.format(self.__type, str(d))
        self.__helper.raise_exception(string)

