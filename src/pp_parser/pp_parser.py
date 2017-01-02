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
GENERATE   = "generate"      #from spec_parser
SHOW       = "show"


class Solver:


    def do_base(self,control,programs,options,underscores):

        # base
        old = [ key                      for key, value in options['constants'].items() ]
        new = [ clingo.parse_term(value) for key, value in options['constants'].items() ]
        control.add(BASE,old,programs[BASE][""])
        control.ground([(BASE,new)])

        # show if needed (CSP variables are not shown in this case)
        if not options['show']:
            show = "\n".join(["#show " + ("" if x[2] else "-") + x[0] + "/" + str(x[1]) + "."
                             for x in control.symbolic_atoms.signatures])
            control.add(SHOW,[],show)
            control.ground([(SHOW,[])])

        # generate domains
        control.add(GENERATE,[],programs[GENERATE][""])
        control.ground([(GENERATE,[])])


    def get_domains(self,control,programs,underscores):
        out = ""
        for atom in control.symbolic_atoms.by_signature(underscores+GEN_DOM,2):
            for atom2 in control.symbolic_atoms.by_signature(
                str(atom.symbol.arguments[0]),int(str(atom.symbol.arguments[1]))):
                out += underscores + DOM + "(" + str(atom2.symbol) + ").\n"
        return out


    def do_spec(self,control,programs,underscores,options):

        # specification
        old = [ key                      for key, value in options['constants'].items() ]
        new = [ clingo.parse_term(value) for key, value in options['constants'].items() ]
        control.add(SPEC,old,programs[SPEC][""])
        control.ground([(SPEC,new)])

        # get preference types
        out = set()
        for atom in control.symbolic_atoms.by_signature(underscores+PREFERENCE,2):
            out.add(str(atom.symbol.arguments[1]))
        return out



class Debugger:


    def __init__(self,underscores):
        self.underscores = underscores


    def __add_program(self,control,name,programs,types):
        l = []
        if name == PPROGRAM:
            with control.builder() as b:
                t = transformer.ProgramTransformer(self.underscores)
                for type, program in programs.items():
                    if type in types:
                        clingo.parse_program("#program "+name+".\n"+program,lambda stm: l.append(t.visit(stm)))
        for i in l:
            print i


    def print_programs(self,programs,types):
        print "\n###programs"
        for name, program in programs.items():
            print "##name = " + str(name)
            for name2, program2 in program.items():
                if str(name2) in types:
                    print "#type = " + str(name2)
                    print program2
                    print "#end"


    def debug(self,control,programs,types):
        self.print_programs(programs,types)
        print "\n###translations"
        for name, program in programs.items():
            if name != BASE and name != SPEC:
                self.__add_program(control,name,program,types)
        print "\n###types\n" + str(types) + "\n"
        raise Exception("DEBUGGING: STOPPED")



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


    def parse(self,programs,options,clingo_options):

        # create control object
        control = clingo.Control(clingo_options)

        # ground base program
        self.solver.do_base(control,programs,options,self.underscores)

        # get domains for the specification
        if options['debug']: Debugger(self.underscores).print_programs(programs,set([""]))
        programs[SPEC][""] += self.solver.get_domains(control,programs,self.underscores)

        # ground specification and get preference types
        types = self.solver.do_spec(control,programs,self.underscores,options)
        types.add("") # add basic case

        # translate and add the rest of the programs
        if options['debug']: Debugger(self.underscores).debug(control,programs,types)
        for name, program in programs.items():
            if name != BASE and name != SPEC:
                self.__add_program(control,name,program,types)

        # return
        return control

