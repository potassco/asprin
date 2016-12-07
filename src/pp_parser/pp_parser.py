#script (python)

import clingo
import clingo.ast
import pdb



#
# DEFINES
#

BASE       = "base"
SPEC       = "specification"
DOM        = "dom"          # arity 1
GEN_DOM    = "gen_dom"      # arity 2
PREFERENCE = "preference"   # arity 2
PPROGRAM   = "preference"
M1         = "m1"
M2         = "m2"



#
# GLOBAL VARIABLES
#

modify_conditional_literal    = True
modify_conditional_literal    = False
modify_body_aggregate_element = True
#modify_body_aggregate_element = False



class Transformer:


    def underscore(self,x):
        return self.__underscore + x


    def __init__(self,underscore=""):
        self.__underscore = underscore
        self.m1 = clingo.Function(self.underscore(M1),[])
        self.m2 = clingo.Function(self.underscore(M2),[])
        self.det = set([]) # set([self.underscore("volatile")])
        self.keywords_det   = set(["preference","optimize"])
        self.keywords_undet = set(["unsat"])


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


    def __init__(self,underscore=""):
        Transformer.__init__(self,underscore)


    def visit_Function(self, term):
        if term.name == "holds":
            term.name = self.underscore("holds")
            term.arguments.append(clingo.ast.Symbol(term.location,self.m1))
        elif term.name == "holds'":
            term.name = self.underscore("holds")
            term.arguments.append(clingo.ast.Symbol(term.location,self.m2))
        elif term.name in self.keywords_det:
            term.name = self.underscore(term.name)
        elif term.name in self.keywords_undet:
            term.name = self.underscore(term.name)
            term.arguments.append(clingo.ast.Symbol(term.location,self.m1))
            term.arguments.append(clingo.ast.Symbol(term.location,self.m2))
        elif term.name not in self.det:
            term.name = "_" + self.underscore(term.name)
            term.arguments.append(clingo.ast.Symbol(term.location,self.m1))
            term.arguments.append(clingo.ast.Symbol(term.location,self.m2))
        return term


    def visit_Symbol(self, term):
        # this function is not necessary if gringo's parser is used
        # but this case could occur in a valid AST
        fun = term.symbol
        assert(fun.type == clingo.SymbolType.Function)
        term.symbol = clingo.Function(fun.name, fun.arguments + [self.m1,self.m2], fun.positive)
        return term



class ProgramTransformer(Transformer):


    base, preference, other = "base", "preference", "other"


    def __volatile(self,loc):
        return clingo.ast.Literal(loc,clingo.ast.Sign.None,clingo.ast.SymbolicAtom(
               clingo.ast.Function(loc,self.underscore("volatile"),[clingo.ast.Symbol(loc,self.m1),clingo.ast.Symbol(loc,self.m2)],False)))


    #
    # init and a bit more
    #

    def __init__(self,underscore=""):
        Transformer.__init__(self,underscore)
        self.term_transformer = TermTransformer(underscore)
        self.program = ProgramTransformer.base

    def __translate(self):
        return self.program==ProgramTransformer.preference

    #
    # Statements
    #

    # TODO: implement
    def __head_is_det(self,rule):
        return False

    def visit_Rule(self,rule):
        if not self.__translate(): return rule
        if self.__head_is_det(rule): return rule
        if (str(rule.head.type) == "Literal"
            and str(rule.head.atom.type) == "BooleanConstant"
            and str(rule.head.atom.value == False)):
                rule.head = clingo.ast.Literal(rule.location,clingo.ast.Sign.None,clingo.ast.SymbolicAtom(
                            clingo.ast.Function(rule.location,"unsat",[],False)))
        self.visit_children(rule)
        rule.body.append(self.__volatile(rule.location))
        return rule

    def visit_Definition(self,d):
        return d

    # TODO: implement
    def __sig_is_det(self,sig):
        return False

    def visit_ShowSignature(self, sig):
        if not self.__translate(): return sig
        if self.__sig_is_det: return sig
        sig.arity += 1
        return sig

    # TODO: implement
    def __body_is_det(self,body):
        return False

    def visit_ShowTerm(self,show):
        if not self.__translate(): return show
        if self.__body_is_det(show.body): return show
        show.term = self.term_transformer.visit(show.term)
        self.visit(show.body)
        show.body.append(self.__volatile(show.location))
        return show

    # TODO: handle
    def visit_Minimize(self,min):
        return min

    def visit_Script(self,script):
        return script

    # TODO: extend
    def visit_Program(self, prg):
        if prg.name == "base" and prg.parameters == []:
            self.program = ProgramTransformer.base
        elif prg.name == "preference":
            self.program = ProgramTransformer.preference
            #prg.name = self.underscore("preference")
            prg.parameters = [clingo.ast.Id(prg.location,str(self.m1)),clingo.ast.Id(prg.location,str(self.m2))]
        else:
            self.program = ProgramTransformer.other
        return prg

    # TODO: handle
    def visit_External(self,ext):
        return ext

    # TODO: handle
    def visit_Edge(self,ext):
        return ext

    # TODO: handle
    def visit_Heuristic(self,heur):
        return heur

    # TODO: handle
    def visit_ProjectAtom(self,atom):
        return atom

    # TODO: handle
    def visit_ProjectSignature(self, sig):
        return sig

    #
    # Elements
    #

    def visit_SymbolicAtom(self, atom):
        atom.term = self.term_transformer.visit(atom.term)
        return atom

    def visit_ConditionalLiteral(self,c):
        self.visit_children(c)
        if modify_conditional_literal:
            c.condition.append(self.__volatile(c.location))
        return c

    def visit_BodyAggregate(self,b):
        self.location = b.location
        self.visit_children(b)
        return b

    def visit_BodyAggregateElement(self,b):
        self.visit_children(b)
        if modify_body_aggregate_element:
            b.condition.append(self.__volatile(self.location))
        return b



class Solver:


    def do_base(self,control,programs,underscores):
        control.add(BASE,[],programs[BASE][""])
        control.ground([(BASE,[])])


    def get_domains(self,control,programs,underscores):
        out = ""
        for atom in control.symbolic_atoms.by_signature(underscores+GEN_DOM,2):
            if int(str(atom.symbol.arguments[1])) != 0: # if 0, this is handled in spec_parser
                for atom2 in control.symbolic_atoms.by_signature(
                    str(atom.symbol.arguments[0]),int(str(atom.symbol.arguments[1]))):
                    out += underscores + DOM + "(" + str(atom2.symbol) + ").\n"
        return out


    def do_spec(self,control,programs,underscores):
        control.add(SPEC,[],programs[SPEC][""])
        control.ground([(SPEC,[])])
        out = set()
        for atom in control.symbolic_atoms.by_signature(underscores+PREFERENCE,2):
            out.add(str(atom.symbol.arguments[1]))
        return out



class Parser:


    def __init__(self,underscores):
        self.underscores = underscores
        self.solver      = Solver()


    def __add_program(self,control,name,programs,types):
        l = []
        if name == PPROGRAM:
            with control.builder() as b:
                t = ProgramTransformer(self.underscores)
                for type, program in programs.items():
                    if type in types:
                        clingo.parse_program("#program "+name+".\n"+program,lambda stm: b.add(t.visit(stm)))


    def __debug_add_program(self,control,name,programs,types):
        l = []
        if name == PPROGRAM:
            with control.builder() as b:
                t = ProgramTransformer(self.underscores)
                for type, program in programs.items():
                    if type in types:
                        clingo.parse_program("#program "+name+".\n"+program,lambda stm: l.append(t.visit(stm)))
        for i in l:
            print i


    def parse(self,programs,clingo_options):
        # create control object
        control = clingo.Control(clingo_options)
        # ground base program
        self.solver.do_base(control,programs,self.underscores)
        # get domains for the specification
        programs[SPEC][""] += self.solver.get_domains(control,programs,self.underscores)
        # ground specification and get preference types
        types = self.solver.do_spec(control,programs,self.underscores)
        types.add("") # add basic case
        # translate and add the rest of the programs
        debug = True
        debug = False
        for name, programs in programs.items():
            if name != BASE and name != SPEC:
                if not debug: self.__add_program(control,name,programs,types)
                if     debug: self.__debug_add_program(control,name,programs,types)
        if debug: raise Exception("STOPPED")
        # return
        return control

