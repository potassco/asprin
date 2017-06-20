import clingo.ast
from src.utils import utils
from src.program_parser.transitive_closure import NodeInfo, TransitiveClosure
from src.program_parser.visitor import PredicateInfo, Helper, \
                                       Visitor, TermTransformer, \
                                       EMPTY, M1, M2, M1_M2, SHOW, EDGE

#
# DEFINES
#


# programs
BASE     = utils.BASE
PPROGRAM = utils.PPROGRAM

# predicate names
HOLDS      = utils.HOLDS
HOLDSP     = utils.HOLDSP
PREFERENCE = utils.PREFERENCE
OPTIMIZE   = utils.OPTIMIZE

# graph
HOLDS_KEY  = (HOLDS,  1)
HOLDSP_KEY = (HOLDSP, 1)
OPEN_NAME  = "open"

ERROR_PROJECT = """\
error: syntax error, unexpected #project statement in {} program
  {}\n"""
ERROR_MINIMIZE = """\
error: syntax error, unexpected clingo optimization statement in {} program
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


class PreferenceTermTransformer(TermTransformer):

    def __init__(self, type):
        TermTransformer.__init__(self)
        self.__type = type

    def set_predicates_info(self, open):
        self.predicates_info = dict()
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
                Helper().raise_exception(string)
            else:
                self.predicates_info[i] = info
        self.default = PredicateInfo(None, 1, None, 0)


class Graph:

    def __init__(self):
        self.__tc = TransitiveClosure()
        self.__open = NodeInfo((Helper().underscore(OPEN_NAME), 0), None)
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
    #   add_atom()* process_rule()
    #

    def add_atom(self, term, in_head, in_body, flag=False):
        if in_head:
            self.__heads.append((term, flag))
        elif in_body:
            self.__bodies.append((term, flag))
        else:
            raise utils.FatalException()

    def __get_info(self, term):
        return NodeInfo((term.name, len(term.arguments)), term)

    def process_rule(self):
        i_heads  = [(self.__get_info(i[0]), i[1]) for i in self.__heads]
        i_bodies = [(self.__get_info(i[0]), i[1]) for i in self.__bodies]
        for i in i_heads:
            self.__tc.add_node(i[0])
            if i[1]:
                self.__tc.add_edge(self.__open, i[0], False)
        for i in i_bodies:
            self.__tc.add_node(i[0])
        for i in i_heads:
            for j in i_bodies:
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


class BodyList:

    def __init__(self, helper):
        self.__bodies = [] # pointed by __show_terms and __edges in PPVisitor
        self.__inside = False
        self.__helper = helper

    def in_(self, body, location):
        self.__inside = True
        # [body, location, predicates, nondet]
        self.__bodies.append([body, location, [], False])

    def out(self):
        self.__inside = False

    def add_atom(self, term):
        if not self.__inside:
            return
        self.__bodies[-1][2].append((term.name, len(term.arguments)))

    def update_volatile(self, open_list):
        for i in self.__bodies:
            # for every predicate in the body
            for j in i[2]:
                # if open: append volatile, mark as nondet, and break
                if j in open_list:
                    i[0].append(self.__helper.get_volatile_atom(i[1]))
                    i[3] = True
                    break

    def get_index(self):
        return len(self.__bodies) - 1

    def is_nondet(self, index):
        return self.__bodies[index][3]


class PreferenceProgramVisitor(Visitor):

    def __init__(self):
        Visitor.__init__(self)
        self.__type = PPROGRAM
        self.__graph = Graph()
        self.__helper = Helper()
        self.__body_list = BodyList(self.__helper)
        self.__term_transformer = PreferenceTermTransformer(self.__type)
        self.__show_signatures = [] # list of signatures
        self.__show_terms = []      # list of (terms, body_list indexes)
        self.__edges = []           # list of (edge, edge, body_list indexes)
        # tracing position
        self.in_Head, self.in_Body = False, False
        self.in_Literal_ConditionalLiteral = False

    # auxiliary
    def __visit_body_literal_list(self, body, location):
        self.in_Body = True
        self.__body_list.in_(body, location)
        self.visit(body)
        self.__body_list.out()
        self.in_Body = False

    # after visiting all, finish()
    def finish(self):
        # get open predicates from the graph
        open_list = self.__graph.get_open()
        # set predicates_info in term_transformer
        self.__term_transformer.set_predicates_info(open_list)
        # tranform items stored in the graph
        self.__graph.map_items(self.__term_transformer.transform_function)
        # update bodies with volatile atom
        self.__body_list.update_volatile(open_list)
        # update show signatures
        map(self.__term_transformer.transform_signature, self.__show_signatures)
        # update show terms
        for i in self.__show_terms:
            if self.__body_list.is_nondet(i[1]):
                self.__term_transformer.extend_function(i[0], M1_M2)
        # update edges
        for i in self.__edges:
            if self.__body_list.is_nondet(i[2]):
                self.__term_transformer.extend_function(i[0], M1_M2)
                self.__term_transformer.extend_function(i[1], M1_M2)

    #
    # Statements
    #

    def visit_Rule(self, rule):
        # head
        self.in_Head = True
        # if empty head
        if (str(rule.head.type) == "Literal"
            and str(rule.head.atom.type) == "BooleanConstant"
            and str(rule.head.atom.value == False)):
            # add unsat head
            ems = self.__helper.get_ems(rule.location, M1_M2)
            unsat = self.__helper.unsat
            fun = clingo.ast.Function(rule.location, unsat, ems, False)
            atom = clingo.ast.SymbolicAtom(fun)
            rule.head = clingo.ast.Literal(rule.location,
                                           clingo.ast.Sign.NoSign, atom)
        else:
            self.visit(rule.head)
        self.in_Head = False
        # body
        self.__visit_body_literal_list(rule.body, rule.location)
        self.__graph.process_rule()
        # return
        return rule

    def visit_Definition(self, d):
        return d

    def visit_ShowSignature(self, sig):
        self.__show_signatures.append(sig)
        return sig

    def visit_ShowTerm(self, show):
        tt = self.__term_transformer
        # reify head term
        show.term = tt.reify_term(show.term, self.__helper.show)
        # process body
        self.__visit_body_literal_list(show.body, show.location)
        # update __show_terms
        self.__show_terms.append((show.term, self.__body_list.get_index()))
        # return
        return show

    def visit_Minimize(self, min):
        string = ERROR_MINIMIZE.format(self.__type, str(min))
        self.__helper.raise_exception(string)

    def visit_Script(self, script):
        return script

    def visit_Program(self, prg):
        if prg.name == BASE:
            return prg
        assert(prg.name == self.__type)
        id1 = clingo.ast.Id(prg.location, self.__helper.underscore(M1))
        id2 = clingo.ast.Id(prg.location, self.__helper.underscore(M2))
        prg.parameters = [id1, id2]
        return prg

    # return it: it will be simply ignored
    def visit_External(self, ext):
        return ext

    # TODO: Warn if computing many models
    def visit_Edge(self, edge):
        tt = self.__term_transformer
        # reify edges
        edge.u = tt.reify_term(edge.u, self.__helper.edge)
        edge.v = tt.reify_term(edge.v, self.__helper.edge)
        # process body
        self.__visit_body_literal_list(edge.body, edge.location)
        # update __edges
        self.__edges.append((edge.u, edge.v, self.__body_list.get_index()))
        # return
        return edge

    # TODO(EFF): do not add if head is deterministic
    # TODO: DO!
    def visit_Heuristic(self,heur):
        heur.atom = self.__term_transformer.visit(heur.atom)
        self.__visit_body_literal_list(heur.body, heur.location)
        return heur

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
        if str(lit.atom.type) == "SymbolicAtom" and \
           str(lit.atom.term.type) == "Function":
            flag = False
            if (self.in_Head and self.in_Literal_ConditionalLiteral) or \
               (self.in_Body and (
                lit.sign != clingo.ast.Sign.NoSign          or \
                self.in_Aggregate                           or \
                self.in_TheoryAtom or self.in_BodyAggregate or \
                (self.in_ConditionalLiteral and 
                 not self.in_Literal_ConditionalLiteral))):
                flag = True
            self.__graph.add_atom(lit.atom.term, self.in_Head,
                                  self.in_Body, flag)
            self.__body_list.add_atom(lit.atom.term)
        self.visit_children(lit)
        return lit

    # csp literals are not accepted
    def visit_CSPLiteral(self,csp):
        string = ERROR_CSPLITERAL.format(self.__type, str(csp))
        self.__helper.raise_exception(string)

    def visit_ConditionalLiteral(self,c):
        self.in_Literal_ConditionalLiteral = True
        self.visit(c.literal)
        self.in_Literal_ConditionalLiteral = False
        self.visit(c.condition)
        c.condition.append(self.__helper.get_volatile_atom(c.location))
        return c

    def visit_Aggregate(self,a):
        self.visit_children(a)
        return a

    def visit_TheoryAtom(self,th):
        self.visit_children(th)
        for i in th.elements:
            i.condition.append(self.__helper.get_volatile_atom(th.location))
        return th

    def visit_BodyAggregate(self,b):
        self.visit_children(b)
        for i in b.elements:
            i.condition.append(self.__helper.get_volatile_atom(b.location))
        return b

    # disjoint atoms are not accepted
    def visit_Disjoint(self,d):
        string = ERROR_DISJOINT.format(self.__type, str(d))
        self.__helper.raise_exception(string)

    def visit_HeadAggregate(self,h):
        self.visit_children(h)
        return h

    def visit_Disjunction(self,d):
        self.visit_children(d)
        return d
