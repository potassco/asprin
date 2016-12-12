#script (python)

import clingo
import transformer


#
# DEFINES
#

BASE       = "base"          #from spec_parser
SPEC       = "specification" #from spec_parser
DOM        = "dom"           #from spec_parser
GEN_DOM    = "gen_dom"       #from spec_parser
PREFERENCE = "preference"    #from spec_parser
PPROGRAM   = "preference"    #from spec_parser



class Solver:


    def do_base(self,control,programs,options):
        old, new = [], []
        for i in options['constants']:
            old_str, sep, new_str = i.partition("=")
            old.append(old_str)
            new.append(clingo.Function(new_str,[]))
        print old
        print new
        control.add(BASE,old,programs[BASE][""])
        control.ground([(BASE,new)])


    def get_domains(self,control,programs,underscores):
        out = ""
        for atom in control.symbolic_atoms.by_signature(underscores+GEN_DOM,2):
            if int(str(atom.symbol.arguments[1])) != 0: # if 0, this is handled in spec_parser
                for atom2 in control.symbolic_atoms.by_signature(
                    str(atom.symbol.arguments[0]),int(str(atom.symbol.arguments[1]))):
                    out += underscores + DOM + "(" + str(atom2.symbol) + ").\n"
        return out


    def do_spec(self,control,programs,underscores,options):
        # TODO: Do once nicely
        # TODO: control in spec_parser that no solapmaient
        old, new = [], []
        for i in options['constants']:
            old_str, sep, new_str = i.partition("=")
            old.append(old_str)
            new.append(clingo.Function(new_str,[]))
        control.add(SPEC,old,programs[SPEC][""])
        control.ground([(SPEC,new)])
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

    def debug(self,control,programs,types):
        print "\n###programs"
        for name, program in programs.items():
            print "##name = " + str(name)
            for name2, program2 in program.items():
                print "#type = " + str(name2)
                print program2
                print "#end"
        print "\n###translations"
        for name, program in programs.items():
            if name != BASE and name != SPEC:
                self.__debug_add_program(control,name,program,types)
        print "\n###types\n\n" + str(types)
        raise Exception("DEBUGGING: STOPPED")

    def parse(self,programs,options,clingo_options):

        # create control object
        control = clingo.Control(clingo_options)

        # ground base program
        self.solver.do_base(control,programs,options)

        # get domains for the specification
        programs[SPEC][""] += self.solver.get_domains(control,programs,self.underscores)

        # ground specification and get preference types
        types = self.solver.do_spec(control,programs,self.underscores,options)
        types.add("") # add basic case

        # translate and add the rest of the programs
        debug = True
        debug = False
        if debug: self.debug(control,programs,types)
        for name, program in programs.items():
            if name != BASE and name != SPEC:
                self.__add_program(control,name,program,types)

        # return
        return control

