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

# graph
HOLDS_KEY  = (HOLDS,  1)
HOLDSP_KEY = (HOLDSP, 1)
OPEN_NAME  = "open"
UNSTRAT_NAME = "unstrat"

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
ERROR_HOLDS_H    = utils.ERROR_HOLDS_H
ERROR_HOLDSP_H   = utils.ERROR_HOLDSP_H

# no sign
NO_SIGN = utils.NO_SIGN

# finish() function return value
SKIP   = 1 # do not add to program
DET    = 2 # add deterministic part 
NONDET = 3 # add nondeterministic part


class PreferenceTermTransformer(visitor.TermTransformer):

    def __init__(self, type, underscores):
        visitor.TermTransformer.__init__(self)
        self.__type = type
        self.__underscores = underscores

    def set_predicates_info(self, open):
        self.predicates_info = dict()
        PredicateInfo = visitor.PredicateInfo
        info = PredicateInfo(None, self.__underscores, M1_M2, 2)
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
        self.default = PredicateInfo(None, self.__underscores, None, 0)


class Graph:

    def __init__(self):
        self.__tc = transitive_closure.TransitiveClosure()
        NodeInfo = transitive_closure.NodeInfo
        self.__open = NodeInfo((visitor.Helper().underscore(OPEN_NAME),0), None)
        self.__holds  = NodeInfo(HOLDS_KEY,  None)
        self.__holdsp = NodeInfo(HOLDSP_KEY, None)
        self.__tc.add_node(self.__open)
        self.__tc.add_node(self.__holds)
        self.__tc.add_node(self.__holdsp)
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
        # add edge from __open
        for i in self.__tc.get_cycles():
            self.__tc.add_edge(self.__open, i, False)
        # set unstrat
        unstrat = len(self.__tc.get_next(self.__open.key)) > 0
        # set open
        self.__tc.add_edge(self.__open, self.__holds, True)
        self.__tc.add_edge(self.__open, self.__holdsp, True)
        _open = self.__tc.get_next(self.__open.key)
        # return
        return _open, unstrat

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

    def __init__(self, builder, type, underscores, constants):
        visitor.Visitor.__init__(self)
        self.__builder    = builder
        self.__type       = type
        self.__constants  = constants
        self.__statements = []
        self.__conditions = []
        self.__graph      = Graph()
        self.__helper     = visitor.Helper()
        self.__term_transformer = PreferenceTermTransformer(self.__type,
                                                            underscores)
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

    def __get_program(self, deterministic_type, loc):
        if deterministic_type == DET:
            return clingo.ast.Program(loc, utils.mapbase[self.__type], [])
        return clingo.ast.Program(loc, self.__type, self.__get_params(loc))

    #
    # finish() after visiting all
    #

    def finish(self):
        # get open predicates from the graph, and whether it is unstratified
        open_list, unstrat = self.__graph.get_open()
        # set predicates_info in term_transformer
        self.__term_transformer.set_predicates_info(open_list)
        # tranform items stored in the graph
        self.__graph.map_items(self.__term_transformer.transform_function)
        # iterate over conditions
        for c in self.__conditions:
            if self.__is_nondet(c, open_list):
                self.__add_volatile(c.condition, c.location)
        # iterate over statements
        deterministic_type = None
        for st in self.__statements:
            method = "finish_" + st.type
            ret = getattr(self, method, lambda x, y: DET)(st, open_list)
            if ret is not SKIP:
                if ret != deterministic_type:
                    self.__builder.add(self.__get_program(
                                       ret, st.statement.location))
                    deterministic_type = ret
                self.__builder.add(st.statement)
        return unstrat

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
            return NONDET
        return DET

    def visit_Definition(self, d):
        if d.name not in self.__constants:
            self.__statements.append(Statement("Definition", d))

    def visit_ShowSignature(self, sig):
        self.__statements.append(Statement("ShowSignature", sig))

    def finish_ShowSignature(self, statement, open_list):
        if statement.statement.name != "" or statement.statement.arity != 0:
            self.__term_transformer.transform_signature(statement.statement)
        return DET

    def visit_Defined(self, defined):
        self.__statements.append(Statement("Defined", defined))

    def finish_Defined(self, statement, open_list):
        if statement.statement.name != "" or statement.statement.arity != 0:
            self.__term_transformer.transform_signature(statement.statement)
        return DET

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
            return NONDET
        return DET

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
        return NONDET

    def visit_Heuristic(self, heur):
        self.__statements.append(Statement("Heuristic", heur))
        self.__visit_body(heur.body)
        # head
        term = heur.atom.term
        if str(term.type) == "Function":
            self.__graph.add_atom(term, False, False, False)
            self.__statements[-1].heur_atom = (term.name, len(term.arguments))
        # update graph
        self.__graph.update()

    def finish_Heuristic(self, statement, open_list):
        heur = statement.statement
        # not open -> skip
        if statement.heur_atom not in open_list:
            return SKIP
        # holds
        elif statement.heur_atom == HOLDS_KEY:
            if self.__is_nondet(statement, open_list):
                atom = utils.HOLDS + "("+str(heur.atom.term.arguments[0])+")"
                string = ERROR_HOLDS_H.format(self.__type, atom)
                self.__helper.raise_exception(string)
            zero = clingo.ast.Symbol(heur.location, clingo.parse_term("0"))
            heur.atom.term.arguments[1] = zero
            return DET
        # holds'
        elif statement.heur_atom == HOLDSP_KEY:
            atom = utils.HOLDSP + "("+str(heur.atom.term.arguments[0])+")"
            string = ERROR_HOLDSP_H.format(self.__type, atom)
            self.__helper.raise_exception(string)
        # open and not holds[']
        self.__add_volatile(heur.body, heur.location)
        return NONDET

    def visit_ProjectAtom(self, atom):
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

