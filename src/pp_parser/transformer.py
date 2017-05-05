#script (python)

import clingo
import clingo.ast
import pdb
from collections import namedtuple


#
# DEFINES
#

BASE       = "base"
PPROGRAM   = "preference"
MODEL      = "m"
M1         = "m1"
M2         = "m2"
M1_M2      = "m1_m2"
VOLATILE   = "volatile"
UNSAT      = "unsat"
NODE       = "node"
SHOW       = "show"

#
# GLOBAL VARIABLES
#

modify_conditional_literal    = True
modify_body_aggregate         = True
modify_disjoint               = True


#
# NAMED TUPLE
#
PredicateInfo = namedtuple('PredicateInfo','name domain underscores ems arity')


#
# CLASSES
#

class Transformer:

    underscores, m1, m2, simple_m1, simple_m2 = None, None, None, None, None

    def __init__(self,underscores=""):
        if self.underscores is not None:
            return
        self.underscores = underscores
        self.m1 = clingo.parse_term("{}({})".format(self.underscore(MODEL),self.underscore(M1)))
        self.m2 = clingo.parse_term("{}({})".format(self.underscore(MODEL),self.underscore(M2)))
        self.simple_m1 = clingo.parse_term("{}".format(self.underscore(M1))) # for holds
        self.simple_m2 = clingo.parse_term("{}".format(self.underscore(M2))) # for holds'


    def underscore(self,x):
        return self.underscores + x


    def get_ems(self,loc,ems):
        if   ems == M1:    return [clingo.ast.Symbol(loc,self.simple_m1)]
        elif ems == M2:    return [clingo.ast.Symbol(loc,self.simple_m2)]
        elif ems == M1_M2: return [clingo.ast.Symbol(loc,self.m1), clingo.ast.Symbol(loc,self.m2)]
        else:              return []


    def get_volatile_atom(self,loc):
        return clingo.ast.Literal(loc,clingo.ast.Sign.NoSign,clingo.ast.SymbolicAtom(
               clingo.ast.Function(loc,self.underscore(VOLATILE),self.get_ems(loc,M1_M2),False)))


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


    def __get_predicate_info(self,name,arity):
        predicate_info = self.predicate_infos.get((name,arity))
        return predicate_info if predicate_info is not None else self.default


    def visit_Function(self, term):
        # get info, change name, add underscores, and update arguments
        predicate_info = self.__get_predicate_info(term.name,len(term.arguments))
        if predicate_info.name: term.name = predicate_info.name
        term.name = "_"*predicate_info.underscores + self.underscore(term.name)
        term.arguments += self.get_ems(term.location,predicate_info.ems)
        #return
        return term


    def visit_Symbol(self, term):
        # get symbol
        fun = term.symbol
        assert(fun.type == clingo.SymbolType.Function)
        # get info, change name, add underscores, and update arguments
        predicate_info = self.__get_predicate_info(fun.name,len(fun.arguments))
        if predicate_info.name: fun.name = predicate_info.name
        fun.name = "_"*predicate_info.underscores + self.underscore(fun.name)
        fun.arguments += [ x.symbol for x in self.get_ems(term.location,predicate_info.ems) ]
        #return
        return term


    def update_signature(self,sig):
        # get info, change name, add underscores, and update arity
        predicate_info = self.__get_predicate_info(sig.name,sig.arity)
        if predicate_info.name: sig.name = predicate_info.name
        sig.name = "_"*predicate_info.underscores + self.underscore(sig.name)
        sig.arity += predicate_info.arity
        # return
        return sig



class PreferenceProgramTransformer(Transformer):


    #
    # init
    #

    def __init__(self,underscores=""):
        Transformer.__init__(self,underscores)
        self.term_transformer = TermTransformer(underscores)
        self.type = PPROGRAM

    def __extend_term(self,term):
        return clingo.ast.Function(term.location,"",
                                  [term]+self.get_ems(term.location,M1_M2),False)

    #
    # Statements
    #

    # TODO(EFF): implement
    def __head_is_det(self,rule):
        return False

    def visit_Rule(self,rule):
        if self.__head_is_det(rule): return rule
        if (str(rule.head.type) == "Literal"
            and str(rule.head.atom.type) == "BooleanConstant"
            and str(rule.head.atom.value == False)):
                # add unsat head
                rule.head = clingo.ast.Literal(rule.location,clingo.ast.Sign.NoSign,clingo.ast.SymbolicAtom(
                            clingo.ast.Function(rule.location,self.underscore(UNSAT),self.get_ems(rule.location,M1_M2),False)))
                self.visit(rule.body)
        else: self.visit_children(rule)
        rule.body.append(self.get_volatile_atom(rule.location))
        return rule

    def visit_Definition(self,d):
        return d

    # TODO(EFF): implement
    def __sig_is_det(self,sig):
        return False

    def visit_ShowSignature(self, sig):
        if self.__sig_is_det(sig): return sig
        return self.term_transformer.update_signature(sig)

    # TODO(EFF): implement
    def __body_is_det(self,body):
        return False

    def visit_ShowTerm(self,show):
        if self.__body_is_det(show.body): return show
        show.term = self.__extend_term(show.term)
        self.visit(show.body)
        show.body.append(self.get_volatile_atom(show.location))
        return show

    def visit_Minimize(self,min):
        raise Exception("clingo optimization statements not allowed in " + self.type + "programs: " + str(min))

    def visit_Script(self,script):
        return script

    def visit_Program(self, prg):
        if prg.name == BASE: return prg
        prg.parameters = [clingo.ast.Id(prg.location,self.underscore(M1)),clingo.ast.Id(prg.location,self.underscore(M2))]
        return prg

    def visit_External(self,ext):
        raise Exception("clingo optimization externals not allowed in " + self.type + "programs: " + str(ext))

    # TODO(EFF):do not translate if *all* edge statements are deterministic
    def visit_Edge(self,edge):
        edge.u = self.__extend_term(edge.u)
        edge.v = self.__extend_term(edge.v)
        self.visit(edge.body)
        edge.body.append(self.get_volatile_atom(edge.location))
        return edge

    # TODO(EFF): do not add if head is deterministic
    def visit_Heuristic(self,heur):
        heur.atom = self.term_transformer.visit(heur.atom)
        self.visit(heur.body)
        heur.body.append(self.get_volatile_atom(heur.location))
        return heur

    def visit_ProjectAtom(self,atom):
        raise Exception("clingo projection not allowed in " + self.type + "programs: " + str(atom))

    def visit_ProjectSignature(self, sig):
        raise Exception("clingo projection not allowed in " + self.type + "programs: " + str(atom))

    #
    # Elements
    #

    def visit_SymbolicAtom(self, atom):
        atom.term = self.term_transformer.visit(atom.term)
        return atom

    def visit_ConditionalLiteral(self,c):
        self.visit_children(c)
        if modify_conditional_literal:
            c.condition.append(self.get_volatile_atom(c.location))
        return c

    def visit_BodyAggregate(self,b):
        self.location = b.location
        self.visit_children(b)
        return b

    def visit_BodyAggregateElement(self,b):
        self.visit_children(b)
        if modify_body_aggregate:
            b.condition.append(self.get_volatile_atom(self.location))
        return b

    def visit_Disjoint(self,d):
        self.location = d.location
        self.visit_children(d)
        return d

    def visit_DisjointElement(self,d):
        self.visit_children(d)
        if modify_disjoint:
            d.condition.append(self.get_volatile_atom(self.location))
        return d


