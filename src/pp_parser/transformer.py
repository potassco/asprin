#script (python)

import clingo
import clingo.ast
from collections import namedtuple
from src.utils import utils
from src.utils import printer

#
# DEFINES
#

BASE     = "base"
PPROGRAM = "preference"
MODEL    = "m"
M1       = "m1"
M2       = "m2"
M1_M2    = "m1_m2"
VOLATILE = "volatile"
UNSAT    = "unsat"
SHOW     = "show"
EDGE     = "edge"

ERROR_PROJECT = """\
error: syntax error, unexpected #project statement in {} program
  {}\n"""
ERROR_MINIMIZE = """\
error: syntax error, unexpected clingo optimization statement in {} program
  {}\n"""

#
# NAMED TUPLE
#
PredicateInfo = namedtuple('PredicateInfo','name domain underscores ems arity')


#
# CLASS TRANSFORMER
#

class Transformer:


    __underscores, __m1, __m2            = None, None, None # private
    __simple_m1, __simple_m2, __volatile = None, None, None # private
    unsat, show, edge                    = None, None, None # public


    def __init__(self,underscores=""):
        if self.__underscores is not None:
            return
        # private
        Transformer.__underscores = underscores
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
                return getattr(self, attr)(x, *args, **kwargs)
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


    def __init__(self,underscores=""):
        Transformer.__init__(self,underscores)
        self.predicate_infos = dict([
            (("holds",1),      PredicateInfo(None,False,0,M1,1)),
            (("holds'",1),     PredicateInfo("holds",False,0,M2,1)),
            (("optimize",1),   PredicateInfo(None,True,0,None,0)),
            (("preference",2), PredicateInfo(None,True,0,None,0)),
            (("preference",5), PredicateInfo(None,True,0,None,0))])
        self.default = PredicateInfo(None,False,1,M1_M2,2)


    def __get_predicate_info(self, name, arity):
        predicate_info = self.predicate_infos.get((name, arity))
        if predicate_info is not None:
            return predicate_info
        return self.default


    def visit_Function(self, term):
        # get info, change name, add underscores, and update arguments
        predicate_info = self.__get_predicate_info(term.name, 
                                                   len(term.arguments))
        if predicate_info.name: 
            term.name = predicate_info.name
        term.name = self.underscore(term.name)
        term.name = "_"*predicate_info.underscores + term.name
        term.arguments += self.get_ems(term.location, predicate_info.ems)
        #return
        return term


    def visit_Symbol(self, term):
        raise utils.FatalException


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


    def transform_term_reify(self, term, name):
        # always adds M1_M2
        args = [term] + self.get_ems(term.location, M1_M2)
        return clingo.ast.Function(term.location, name, args, False)


#
# CLASS PREFERENCE PROGRAM TRANSFORMER
#

class PreferenceProgramTransformer(Transformer):


    #
    # init
    #

    def __init__(self, underscores=""):
        Transformer.__init__(self, underscores)
        self.term_transformer = TermTransformer(underscores)
        self.type = PPROGRAM


    def __visit_body_literal_list(self, body, location):
        self.visit(body)
        body.append(self.get_volatile_atom(location))

    #TODO: collect many messages, and output them together
    def __raise_exception(self, string):
        printer.Printer().do_print(string)
        raise Exception("parsing failed")

    #
    # Statements
    #


    # TODO(EFF): implement
    def __head_is_det(self, rule):
        return False


    def visit_Rule(self, rule):
        if self.__head_is_det(rule): return rule
        # if empty head
        if (str(rule.head.type) == "Literal"
            and str(rule.head.atom.type) == "BooleanConstant"
            and str(rule.head.atom.value == False)):
                # add unsat head
                ems = self.get_ems(rule.location, M1_M2)
                fun = clingo.ast.Function(rule.location, self.unsat, ems,
                                          False)
                atom = clingo.ast.SymbolicAtom(fun)
                rule.head = clingo.ast.Literal(rule.location,
                                               clingo.ast.Sign.NoSign,
                                               atom)
        else: self.visit(rule.head)
        self.__visit_body_literal_list(rule.body,rule.location)
        return rule


    def visit_Definition(self, d):
        return d


    # TODO(EFF): implement
    def __sig_is_det(self, sig):
        return False


    def visit_ShowSignature(self, sig):
        if self.__sig_is_det(sig): 
            return sig
        return self.term_transformer.transform_signature(sig)


    # TODO(EFF): implement
    def __body_is_det(self, body):
        return False


    def visit_ShowTerm(self, show):
        if self.__body_is_det(show.body): 
            return show
        show.term = self.term_transformer.transform_term_reify(show.term,
                                                               self.show)
        self.__visit_body_literal_list(show.body,show.location)
        return show


    def visit_Minimize(self, min):
        string = ERROR_MINIMIZE.format(self.type, str(min))
        self.__raise_exception(string)


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
        self.__raise_exception(string)


    def visit_ProjectSignature(self, sig):
        string = ERROR_PROJECT.format(self.type, str(sig))
        self.__raise_exception(string)


    #
    # Elements
    #

    def visit_SymbolicAtom(self, atom):
        atom.term = self.term_transformer.visit(atom.term)
        return atom


    def visit_ConditionalLiteral(self,c):
        self.visit_children(c)
        c.condition.append(self.get_volatile_atom(c.location))
        return c


    def visit_BodyAggregate(self,b):
        self.visit_children(b)
        for i in b.elements:
            i.condition.append(self.get_volatile_atom(b.location))
        return b


    def visit_Disjoint(self,d):
        self.visit_children(d)
        for i in d.elements:
            i.condition.append(self.get_volatile_atom(i.location))
        return d


