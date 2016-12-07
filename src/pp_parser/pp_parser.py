#script (python)

import clingo
import pdb
import transformer


#
# DEFINES
#

BASE       = "base"
SPEC       = "specification"
DOM        = "dom"          # arity 1
GEN_DOM    = "gen_dom"      # arity 2
PREFERENCE = "preference"   # arity 2
PPROGRAM   = "preference"



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
                t = transformer.ProgramTransformer(self.underscores)
                for type, program in programs.items():
                    if type in types:
                        clingo.parse_program("#program "+name+".\n"+program,lambda stm: b.add(t.visit(stm)))


    def __debug_add_program(self,control,name,programs,types):
        l = []
        if name == PPROGRAM:
            with control.builder() as b:
                t = transformer.ProgramTransformer(self.underscores)
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

