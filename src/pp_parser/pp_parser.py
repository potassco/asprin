#script (python)

import clingo
import transformer
import sys
import argparse

#
# DEFINES
#

BASE       = "base"          #from spec_parser
EMPTY      = ""              #from spec_parser
SPEC       = "specification" #from spec_parser
DOM        = "dom"           #from spec_parser
GEN_DOM    = "gen_dom"       #from spec_parser
PREFERENCE = "preference"    #from spec_parser
PPROGRAM   = "preference"    #from spec_parser
GENERATE   = "generate"      #from spec_parser
SHOW       = "show"
OPTIMIZE   = "optimize"
ERROR      = "error"
CHECK_SPEC = """
% P names X
##names(P,X) :- ##preference(P,_,_,name(X),_).

% transitive closure of names
##tr_names(X,Y) :- ##names(X,Y).
##tr_names(X,Y) :- ##names(X,Z), ##tr_names(Z,Y).

%
% errors
%

% naming loops
##error(X,"loop") :- ##tr_names(X,X).

% naming non existent statement
##error(X,"no_reference") :- ##names(X,Y), not ##preference(Y,_).

% optimizing non existent statement
##error(X,"no_reference") :- ##optimize(X), not ##preference(X,_).

% zero or many optimize statements
##error("","no_optimize")   :- not ##optimize(_).
##error("","many_optimize") :- 2 { ##optimize(X) }.

% avoid warnings
##preference(A,B,C, for(D),E) :- ##preference(A,B,C, for(D),E).
##preference(A,B,C,name(D),E) :- ##preference(A,B,C,name(D),E).
"""

# print nicely

class Solver:


    def do_base(self,control,programs,options,underscores):

        # base
        old = [ key                      for key, value in options['constants'].items() ]
        new = [ clingo.parse_term(value) for key, value in options['constants'].items() ]
        control.add(BASE,old,programs[BASE][""])
        control.ground([(BASE,new)])

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
        control.add(SPEC,old,programs[SPEC][""] + CHECK_SPEC.replace("##",underscores))
        control.ground([(SPEC,new)])

        # get specification errors
        errors = False
        for atom in control.symbolic_atoms.by_signature(underscores+ERROR,2):
            print >> sys.stderr, "error in the preference specification: {} - {}".format(str(atom.symbol.arguments[0]),str(atom.symbol.arguments[1]))
            errors = True

        # get non domain errors
        for i in [(PREFERENCE,2),(PREFERENCE,5),(OPTIMIZE,1)]:
            for atom in control.symbolic_atoms.by_signature(underscores+i[0],i[1]):
                if not atom.is_fact:
                     print >> sys.stderr, "error in the preference specification: non domain atom {}".format(str(atom.symbol).replace(underscores,"",1))
                     errors = True

        # get preference types, and test if they have a corresponding preference program
        out = set()
        for atom in control.symbolic_atoms.by_signature(underscores+PREFERENCE,2):
            out.add(str(atom.symbol.arguments[1]))
            if str(atom.symbol.arguments[1]) not in programs[PREFERENCE]:
                print >> sys.stderr, "error in the preference specification: preference type {} has no preference program".format(str(atom.symbol.arguments[1]))
                errors = True

        # if errors
        if errors:
            raise Exception("parsing failed")

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


    def __add_show(self,control,options,types):

        # set 'show_underscores' and
        # if #show in loaded program: return
        options['show_underscores'], do_return = False, False
        for i in options['show']:
            if (i[0]==BASE and i[1]==EMPTY):
                do_return = True
            elif (i[0]==PREFERENCE and i[1] in types):
                do_return = True
                options['show_underscores'] = True
        if do_return: return

        # else add #show for atoms in base
        show = "\n".join(["#show " + ("" if x[2] else "-") + x[0] + "/" + str(x[1]) + "."
                                 for x in control.symbolic_atoms.signatures if not str(x[0]).startswith(self.underscores)])
        control.add(SHOW,[],show)
        control.ground([(SHOW,[])])


    def parse(self,control,programs,options,clingo_options):

        # ground base program
        self.solver.do_base(control,programs,options,self.underscores)

        # get domains for the specification
        if options['debug']: Debugger(self.underscores).print_programs(programs,set([""]))
        programs[SPEC][""] += self.solver.get_domains(control,programs,self.underscores)

        # ground specification and get preference types
        types = self.solver.do_spec(control,programs,self.underscores,options)
        types.add("") # add basic case

        # add #show statements if needed (CSP variables are not shown in this case)
        self.__add_show(control,options,types)

        # translate and add the rest of the programs
        if options['debug']: Debugger(self.underscores).debug(control,programs,types)
        for name, program in programs.items():
            if name != BASE and name != SPEC:
                self.__add_program(control,name,program,types)
