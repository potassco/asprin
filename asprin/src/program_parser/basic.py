import clingo.ast
from src.utils import utils
from src.program_parser import transitive_closure
from src.program_parser import visitor


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

    def __init__(self, builder, type, underscores):
        visitor.Visitor.__init__(self)
        self.type = type
        self.helper = visitor.Helper()
        self.__builder = builder
        self.__underscores = underscores
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
        self.__add(d)

    def visit_ShowSignature(self, sig):
        self.__term_transformer.transform_signature(sig)
        self.__add(sig)

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

    def __init__(self, builder, type, underscores):
        BasicProgramVisitor.__init__(self, builder, type, underscores)

    def visit_Minimize(self, min):
        string = ERROR_MINIMIZE.format(self.type, str(min))
        self.helper.raise_exception(string)

