#script (python)

import clingo
import clingo.ast
import pdb



#
# DEFINES
#

BASE       = "base"
PPROGRAM   = "preference"
M1         = "m1"
MODEL      = "m"
M2         = "m2"
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



# used by class Predicate
def get_empty(location):
    return []


class PredicateTuple:


    def __init__(self,deterministic=False,underscores="",
                 arguments=get_empty,arity=0):
        self.deterministic = deterministic
        self.underscores   = underscores
        self.arguments     = arguments # function with parameter location
        self.arity         = arity



class Transformer:


    def __init__(self,underscore=""):
        self.__underscore = underscore
        self.m1 = clingo.Function(self.underscore(MODEL),[clingo.Function(self.underscore(M1),[])])
        self.m2 = clingo.Function(self.underscore(MODEL),[clingo.Function(self.underscore(M2),[])])


    def underscore(self,x):
        return self.__underscore + x


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


    def get_m1_m2(self,loc):
        return [clingo.ast.Symbol(loc,self.m1),clingo.ast.Symbol(loc,self.m2)]


    def get_m1(self,loc):
        return [clingo.ast.Symbol(loc,clingo.Function(self.underscore(M1),[]))]


    def get_m2(self,loc):
        return [clingo.ast.Symbol(loc,clingo.Function(self.underscore(M2),[]))]


    def get_volatile(self,loc):
        return clingo.ast.Literal(loc,clingo.ast.Sign.None,clingo.ast.SymbolicAtom(
               clingo.ast.Function(loc,self.underscore(VOLATILE),self.get_m1_m2(loc),False)))



class TermTransformer(Transformer):


    def __init__(self,underscore=""):
        Transformer.__init__(self,underscore)
        self.predicates = dict([(("holds",1),     PredicateTuple(arguments=self.get_m1,arity=1)),
                                (("holds'",1),    PredicateTuple(arguments=self.get_m2,arity=1)),
                                (("optimize",1),  PredicateTuple(deterministic=True)),
                                (("preference",2),PredicateTuple(deterministic=True)),
                                (("preference",5),PredicateTuple(deterministic=True)),
                               ])
        self.default = PredicateTuple(underscores="_",arguments=self.get_m1_m2,arity=2)


    def __get_predicate(self,name,arity):
        predicate = self.predicates.get((name,arity))
        return predicate if predicate is not None else self.default


    def __handle_holdsp(self,term):
        if term.name == "holds'" and len(term.arguments)==1: return "holds"
        return term.name


    def visit_Function(self, term):
        # get predicate tuple
        predicate = self.__get_predicate(term.name,len(term.arguments))
        # handle holds'
        term.name = self.__handle_holdsp(term)
        # modify term
        term.name       = predicate.underscores + self.underscore(term.name)
        term.arguments += predicate.arguments(term.location)
        #return
        return term


    def visit_Symbol(self, term):
        # get symbol
        fun = term.symbol
        assert(fun.type == clingo.SymbolType.Function)
        # get predicate
        predicate = self.__get_predicate(fun.name,len(fun.arguments))
        # handle holds'
        term.name = self.__handle_holdsp(term)
        # modify term
        term.symbol = clingo.Function(predicate.underscores + self.underscore(fun.name),
                                      fun.arguments + [ x.symbol for x in predicate.arguments(term.location)],
                                      fun.positive)
        #return
        return term


    def update_signature(self,sig):
        predicate  = self.__get_predicate(sig.name,sig.arity)
        sig.name   = predicate.underscores + self.underscore(sig.name)
        sig.arity += predicate.arity
        return sig



class ProgramTransformer(Transformer):


    #
    # init
    #

    def __init__(self,underscore=""):
        Transformer.__init__(self,underscore)
        self.term_transformer = TermTransformer(underscore)
        self.type = PPROGRAM

    def __extend_term(self,term):
        return clingo.ast.Function(term.location,"",
                                  [term]+self.get_m1_m2(term.location),False)

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
                rule.head = clingo.ast.Literal(rule.location,clingo.ast.Sign.None,clingo.ast.SymbolicAtom(
                            clingo.ast.Function(rule.location,self.underscore(UNSAT),self.get_m1_m2(rule.location),False)))
                self.visit(rule.body)
        else: self.visit_children(rule)
        rule.body.append(self.get_volatile(rule.location))
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
        show.body.append(self.get_volatile(show.location))
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
        edge.body.append(self.get_volatile(edge.location))
        return edge

    # TODO(EFF): do not add if head is deterministic
    def visit_Heuristic(self,heur):
        heur.atom = self.term_transformer.visit(heur.atom)
        self.visit(heur.body)
        heur.body.append(self.get_volatile(heur.location))
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
            c.condition.append(self.get_volatile(c.location))
        return c

    def visit_BodyAggregate(self,b):
        self.location = b.location
        self.visit_children(b)
        return b

    def visit_BodyAggregateElement(self,b):
        self.visit_children(b)
        if modify_body_aggregate:
            b.condition.append(self.get_volatile(self.location))
        return b

    def visit_Disjoint(self,d):
        self.location = d.location
        self.visit_children(d)
        return d

    def visit_DisjointElement(self,d):
        self.visit_children(d)
        if modify_disjoint:
            d.condition.append(self.get_volatile(self.location))
        return d


