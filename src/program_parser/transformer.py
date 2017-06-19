#script (python)

import clingo
import clingo.ast
from collections import namedtuple
from src.utils import utils
from src.utils import printer
import src.program_parser.transitive as transitive


#
# DEFINES
#

# programs
BASE     = utils.BASE
PPROGRAM = utils.PPROGRAM

# predicate names
VOLATILE   = utils.VOLATILE
HOLDS      = utils.HOLDS
HOLDSP     = utils.HOLDSP
PREFERENCE = utils.PREFERENCE
OPTIMIZE   = utils.OPTIMIZE
UNSAT      = utils.UNSAT

# graph
HOLDS_KEY  = (HOLDS,  1)
HOLDSP_KEY = (HOLDSP, 1)
OPEN_NAME  = "open"
NULL       = 0

# others
MODEL    = utils.MODEL
M1       = "m1"
M2       = "m2"
M1_M2    = "m1_m2"
SHOW     = "show"
EDGE     = "edge"

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

#
# NAMED TUPLE
#
PredicateInfo = namedtuple('PredicateInfo','name underscores ems arity')


#
# CLASS TRANSFORMER
#

class Transformer:


    __underscores, __m1, __m2            = None, None, None # private
    __simple_m1, __simple_m2, __volatile = None, None, None # private
    unsat, show, edge                    = None, None, None # public


    def __init__(self):
        for i in dir(self):
            if i.startswith("visit_"):
                setattr(self, "in_"+i[6:], False)
        if self.__underscores is not None:
            return
        # private
        Transformer.__underscores = utils.underscores
        term = "{}({})".format(self.underscore(MODEL),self.underscore(M1))
        Transformer.__m1 = clingo.parse_term(term)
        term = "{}({})".format(self.underscore(MODEL),self.underscore(M2))
        Transformer.__m2 = clingo.parse_term(term)
        term = "{}".format(self.underscore(M1)) # for holds
        Transformer.__simple_m1 = clingo.parse_term(term)
        term = "{}".format(self.underscore(M2)) # for holds
        Transformer.__simple_m2 = clingo.parse_term(term)
        Transformer.__volatile = self.underscore(VOLATILE)
        Transformer.unsat = self.underscore(UNSAT)
        Transformer.show = self.underscore(SHOW)
        Transformer.edge = self.underscore(EDGE)


    #TODO: collect many messages, and output them together
    def raise_exception(self, string):
        printer.Printer().print_error(string)
        raise Exception("parsing failed")


    def underscore(self,x):
        return self.__underscores + x


    def get_ems(self,loc,ems):
        if   ems == M1:    return [clingo.ast.Symbol(loc,self.__simple_m1)]
        elif ems == M2:    return [clingo.ast.Symbol(loc,self.__simple_m2)]
        elif ems == M1_M2: return [clingo.ast.Symbol(loc,self.__m1), 
                                   clingo.ast.Symbol(loc,self.__m2)]
        else:              return []


    def get_volatile_atom(self,loc):
        no_sign = clingo.ast.Sign.NoSign
        ems = self.get_ems(loc,M1_M2)
        fun = clingo.ast.Function(loc, self.__volatile, ems, False)
        return clingo.ast.Literal(loc,no_sign,clingo.ast.SymbolicAtom(fun))


    def visit_children(self, x, *args, **kwargs):
        for key in x.child_keys:
            setattr(x, key, self.visit(getattr(x, key), *args, **kwargs))
        return x


    def visit(self, x, *args, **kwargs):
        if isinstance(x, clingo.ast.AST):
            attr = "visit_" + str(x.type)
            if hasattr(self, attr):
                setattr(x,"in_"+attr,True)
                tmp = getattr(self, attr)(x, *args, **kwargs)
                setattr(x,"in_"+attr,False)
                return tmp
            else:
                return self.visit_children(x, *args, **kwargs)
        elif isinstance(x, list):
            return [self.visit(y, *args, **kwargs) for y in x]
        elif x is None:
            return x
        else:
            raise TypeError("unexpected type")


#
# CLASS TERM TRANSFORMER
#

class TermTransformer(Transformer):

    def __init__(self, type):
        Transformer.__init__(self)
        self.predicates_info = dict()
        self.default = None
        self.type = type

    def set_predicates_info(self, open):
        info = PredicateInfo(None, 1, M1_M2, 2)
        for i in open:
            self.predicates_info[i] = info
        # HOLDS and HOLDS' appear always in open, and should be always overriden
        self.predicates_info[(HOLDS, 1)]  = PredicateInfo(None, 0, M1, 1)
        self.predicates_info[(HOLDSP, 1)] = PredicateInfo(HOLDS, 0, M2, 1)
        info = PredicateInfo(None, 0, None, 0)
        for i in [(OPTIMIZE, 1), (PREFERENCE, 2), (PREFERENCE, 5)]:
            if i in self.predicates_info:
                string = ERROR_KEYWORD.format(self.type, i[0], i[1])
                self.raise_exception(string)
            else:
                self.predicates_info[i] = info
        self.default = PredicateInfo(None, 1, None, 0)

    def __get_predicate_info(self, name, arity):
        predicate_info = self.predicates_info.get((name, arity))
        if predicate_info is not None:
            return predicate_info
        return self.default

    # call after set_predicates_info()
    def transform_function(self, term):
        # get info, change name, add underscores, and update arguments
        predicate_info = self.__get_predicate_info(term.name,
                                                   len(term.arguments))
        if predicate_info.name:
            term.name = predicate_info.name
        term.name = self.underscore(term.name)
        term.name = "_"*predicate_info.underscores + term.name
        term.arguments += self.get_ems(term.location, predicate_info.ems)

    # call after set_predicates_info()
    def transform_signature(self, sig):
        # get info, change name, add underscores, and update arity
        predicate_info = self.__get_predicate_info(sig.name, sig.arity)
        if predicate_info.name: 
            sig.name = predicate_info.name
        sig.name = self.underscore(sig.name)
        sig.name = "_"*predicate_info.underscores + sig.name
        sig.arity += predicate_info.arity
        # return
        return sig

    # call after set_predicates_info()
    def transform_term_reify(self, term, name):
        # always adds M1_M2
        args = [term] + self.get_ems(term.location, M1_M2)
        return clingo.ast.Function(term.location, name, args, False)


class Graph:

    def __init__(self):
        self.graph = transitive.TransitiveClosure()
        self.open = transitive.Info((utils.underscores+OPEN_NAME, 0), None)
        holds  = transitive.Info(HOLDS_KEY,  None)
        holdsp = transitive.Info(HOLDSP_KEY, None)
        self.graph.add_node(self.open)
        self.graph.add_node(holds)
        self.graph.add_node(holdsp)
        self.graph.add_edge(self.open, holds, True)
        self.graph.add_edge(self.open, holdsp, True)
        self.heads, self.bodies = [], []

    def __str__(self):
        out = str(self.graph)
        out += "\n" + str(self.graph.get_next((utils.underscores+OPEN_NAME, 0)))
        return out

    #
    # parsing a rule: 
    #   add_atom()* process_rule()
    #

    def add_atom(self, term, in_head, in_body, flag=False):
        if in_head:
            self.heads.append((term, flag))
        elif in_body:
            self.bodies.append((term, flag))
        else:
            raise utils.FatalException()

    def __get_info(self, term):
        return transitive.Info((term.name, len(term.arguments)), term)

    def process_rule(self):
        info = transitive.Info
        i_heads  = [(self.__get_info(i[0]), i[1]) for i in self.heads]
        i_bodies = [(self.__get_info(i[0]), i[1]) for i in self.bodies]
        for i in i_heads:
            self.graph.add_node(i[0])
            if i[1]:
                self.graph.add_edge(self.open, i[0], False) 
        for i in i_bodies:
            self.graph.add_node(i[0])
        for i in i_heads:
            for j in i_bodies:
                self.graph.add_edge(j[0], i[0], j[1])
        self.heads, self.bodies = [], []

    #
    # after parsing all rules
    #

    def get_open(self):
        for i in self.graph.get_cycles():
            self.graph.add_edge(self.open, i, False)
        return self.graph.get_next(self.open.key)

    def map_items(self, function):
        self.graph.map_items(function)


class BodyList:

    def __init__(self, get_volatile_atom):
        self.__bodies = []
        self.__inside = False
        self.__get_volatile_atom = get_volatile_atom

    def in_(self, body, location):
        self.__inside = True
        self.__bodies.append((body, location, []))

    def out(self):
        self.__inside = False

    def add(self, term):
        if not self.__inside:
            return
        self.__bodies[-1][2].append((term.name, len(term.arguments)))

    def update_volatile(self, open_list):
        for i in self.__bodies:
            # for every predicate in the body
            for j in i[2]:
                # if open: append volatile and break
                if j in open_list:
                    i[0].append(self.__get_volatile_atom(i[1]))
                    break

#
# CLASS PREFERENCE PROGRAM TRANSFORMER
#

class PreferenceProgramTransformer(Transformer):


    #
    # init
    #

    def __init__(self):
        Transformer.__init__(self)
        self.type = PPROGRAM
        self.graph = Graph()
        self.body_list = BodyList(self.get_volatile_atom) 
        self.term_transformer = TermTransformer(self.type)
        # tracing position
        self.in_Head, self.in_Body = False, False
        self.in_Literal_ConditionalLiteral = False

    def __visit_body_literal_list(self, body, location):
        self.body_list.in_(body, location)
        self.visit(body)
        self.body_list.out()

    #
    # after visiting all, finish()
    # 

    def finish(self):
        # get open predicates from the graph
        open_list = self.graph.get_open()
        # set predicates_info in term_transformer
        self.term_transformer.set_predicates_info(open_list)
        # tranform items stored in the graph
        self.graph.map_items(self.term_transformer.transform_function) 
        # update bodies with volatile atom
        self.body_list.update_volatile(open_list)

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
            ems = self.get_ems(rule.location, M1_M2)
            fun = clingo.ast.Function(rule.location, self.unsat, ems, False)
            atom = clingo.ast.SymbolicAtom(fun)
            rule.head = clingo.ast.Literal(rule.location,
                                           clingo.ast.Sign.NoSign, atom)
        else: self.visit(rule.head)
        self.in_Head = False
        # body
        self.in_Body = True
        self.__visit_body_literal_list(rule.body, rule.location)
        self.graph.process_rule()
        self.in_Body = False
        # return
        return rule

    def visit_Definition(self, d):
        return d

    def visit_ShowSignature(self, sig):
        if self.__sig_is_det(sig): 
            return sig
        return self.term_transformer.transform_signature(sig)

    def visit_ShowTerm(self, show):
        if self.__body_is_det(show.body): 
            return show
        show.term = self.term_transformer.transform_term_reify(show.term,
                                                               self.show)
        self.__visit_body_literal_list(show.body,show.location)
        return show

    def visit_Minimize(self, min):
        string = ERROR_MINIMIZE.format(self.type, str(min))
        self.raise_exception(string)

    def visit_Script(self, script):
        return script

    def visit_Program(self, prg):
        if prg.name == BASE: return prg
        assert(prg.name == self.type)
        id1 = clingo.ast.Id(prg.location,self.underscore(M1))
        id2 = clingo.ast.Id(prg.location,self.underscore(M2))
        prg.parameters = [id1, id2]
        return prg

    def visit_External(self, ext):
        self.visit(ext.atom)
        self.__visit_body_literal_list(ext.body, ext.location)
        return ext

    # TODO(EFF):do not translate if *all* edge statements are deterministic
    # TODO: Warn if computing many models
    def visit_Edge(self, edge):
        e = self.edge
        edge.u = self.term_transformer.transform_term_reify(edge.u, e)
        edge.v = self.term_transformer.transform_term_reify(edge.v, e)
        self.__visit_body_literal_list(edge.body, edge.location)
        return edge

    # TODO(EFF): do not add if head is deterministic
    def visit_Heuristic(self,heur):
        heur.atom = self.term_transformer.visit(heur.atom)
        self.__visit_body_literal_list(heur.body, heur.location)
        return heur

    def visit_ProjectAtom(self,atom):
        string = ERROR_PROJECT.format(self.type, str(atom))
        self.raise_exception(string)

    def visit_ProjectSignature(self, sig):
        string = ERROR_PROJECT.format(self.type, str(sig))
        self.raise_exception(string)


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
            self.graph.add_atom(lit.atom.term, self.in_Head, self.in_Body, flag)
            self.body_list.add(lit.atom.term)
        self.visit_children(lit)
        return lit

    # csp literals are not accepted
    def visit_CSPLiteral(self,csp):
        string = ERROR_CSPLITERAL.format(self.type, str(csp))
        self.raise_exception(string)

    def visit_ConditionalLiteral(self,c):
        self.in_Literal_ConditionalLiteral = True
        self.visit(c.literal)
        self.in_Literal_ConditionalLiteral = False
        self.visit(c.condition)
        c.condition.append(self.get_volatile_atom(c.location))
        return c

    def visit_Aggregate(self,a):
        self.visit_children(a)
        return a
    
    def visit_TheoryAtom(self,th):
        self.visit_children(th)
        for i in th.elements:
            i.condition.append(self.get_volatile_atom(th.location))
        return th

    def visit_BodyAggregate(self,b):
        self.visit_children(b)
        for i in b.elements:
            i.condition.append(self.get_volatile_atom(b.location))
        return b

    # disjoint atoms are not accepted
    def visit_Disjoint(self,d):
        string = ERROR_DISJOINT.format(self.type, str(d))
        self.raise_exception(string)

    def visit_HeadAggregate(self,h):
        self.visit_children(h)
        return h
    
    def visit_Disjunction(self,d):
        self.visit_children(d)
        return d
    
