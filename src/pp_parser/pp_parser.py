#script (python)

import clingo
import transformer
import sys
import argparse
import re
from src.utils import utils

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

class Debugger:

    
    def __add_program(self,underscores,control,name,programs,types):
        l = []
        if name == PPROGRAM:
            with control.builder() as b:
                t = transformer.ProgramTransformer(underscores)
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


    def __init__(self,control,programs,options,underscores):
        self.__control = control
        self.__programs = programs
        self.__options = options
        self.__underscores = underscores


    def __print_error(self,program,string):
        if program != BASE:
            print string
            return
        for i in string.splitlines():
            printed = False
            match = re.match(r'<block>:(\d+):(\d+)-(\d+:)?(\d+)(.*)',i)
            if match:
                error_line = int(match.group(1))
                col_ini    = int(match.group(2))
                extra_line = int(match.group(3)[:-1]) if match.group(3) is not None else None
                col_end    = int(match.group(4))
                rest       =     match.group(5)
                locations = self.__programs[program][""].get_locations()
                for loc in locations:
                    if loc.lines >= error_line:
                        if error_line == 1:
                            col_ini += loc.col - 1
                            if not extra_line:
                                col_end += loc.col - 1
                        print("{}:{}:{}-{}{}{}".format(loc.filename, error_line+loc.line-1,col_ini,
                                                        "{}:".format(extra_line+loc.line-1) if extra_line else "",
                                                        col_end,rest))
                        printed = True
                        break
                    else:
                        error_line = error_line - loc.lines
                        extra_line = extra_line - loc.lines if extra_line else None
            if not printed: 
                print i


    def __add_and_ground(self,name,params,string,list):
        capturer = utils.Capturer(sys.stderr)
        try:
            self.__control.add(name,params,string)
            self.__control.ground(list)
        finally:
            self.__print_error(name,capturer.read())
            capturer.close()


    def do_base(self):

        options, control, programs = self.__options, self.__control, self.__programs

        # constants
        old = [ key                      for key, value in options['constants'].items() ]
        new = [ clingo.parse_term(value) for key, value in options['constants'].items() ]

        # add and ground
        self.__add_and_ground(BASE,old,programs[BASE][""].get_string(),[(BASE,new)])
        self.__add_and_ground(GENERATE,[],programs[GENERATE][""].get_string(),[(GENERATE,[])])

    def get_domains(self):
        out, control, underscores = "", self.__control, self.__underscores
        for atom in control.symbolic_atoms.by_signature(underscores+GEN_DOM,2):
            for atom2 in control.symbolic_atoms.by_signature(
                str(atom.symbol.arguments[0]),int(str(atom.symbol.arguments[1]))):
                out += underscores + DOM + "(" + str(atom2.symbol) + ").\n"
        return out


    def do_spec(self):

        control, programs, underscores = self.__control, self.__programs, self.__underscores
        options = self.__options

        # specification
        old = [ key                      for key, value in options['constants'].items() ]
        new = [ clingo.parse_term(value) for key, value in options['constants'].items() ]
        self.__add_and_ground(SPEC,old,programs[SPEC][""].get_string() + CHECK_SPEC.replace("##",underscores),[(SPEC,new)])

        # get specification errors
        errors = False
        for atom in control.symbolic_atoms.by_signature(underscores+ERROR,2):
            print >> sys.stderr, "error in the preference specification: {} - {}".format(
                     str(atom.symbol.arguments[0]),str(atom.symbol.arguments[1]))
            errors = True

        # get non domain errors
        for i in [(PREFERENCE,2),(PREFERENCE,5),(OPTIMIZE,1)]:
            for atom in control.symbolic_atoms.by_signature(underscores+i[0],i[1]):
                if not atom.is_fact:
                     print >> sys.stderr, "error in the preference specification: non domain atom {}".format(
                              str(atom.symbol).replace(underscores,"",1))
                     errors = True

        # get preference types, and test if they have a corresponding preference program
        out = set()
        for atom in control.symbolic_atoms.by_signature(underscores+PREFERENCE,2):
            out.add(str(atom.symbol.arguments[1]))
            if str(atom.symbol.arguments[1]) not in programs[PREFERENCE]:
                print >> sys.stderr, "error in the preference specification: preference type {} has no preference program".format(
                         str(atom.symbol.arguments[1]))
                errors = True

        # if errors
        if errors:
            raise Exception("parsing failed")

        return out


    def add_show(self,types):

        # set 'show_underscores' and
        # if #show in loaded program: return
        self.__options['show_underscores'], do_return = False, False
        for i in self.__options['show']:
            if (i[0]==BASE and i[1]==EMPTY):
                do_return = True
            elif (i[0]==PREFERENCE and i[1] in types):
                do_return = True
                self.__options['show_underscores'] = True
        if do_return: return

        # else add #show for atoms in base
        show = "\n".join(["#show " + ("" if x[2] else "-") + x[0] + "/" + str(x[1]) + "."
                         for x in self.__control.symbolic_atoms.signatures if not str(x[0]).startswith(self.__underscores)])
        self.__add_and_ground(SHOW,[],show,[(SHOW,[])])


    def add_programs(self,types):
        t = transformer.ProgramTransformer(self.__underscores)
        with self.__control.builder() as b:
            for name, programs in self.__programs.items():
                if name == PPROGRAM:
                    for type, program in programs.items():
                        if type in types:
                            clingo.parse_program("#program "+name+".\n"+program.get_string(),lambda stm: b.add(t.visit(stm)))


    def parse(self):

        # ground base program
        self.do_base()

        # get domains for the specification
        #if options['debug']: Debugger().print_programs(self.__underscores,self.__programs,set([""]))
        self.__programs[SPEC][""].extend_string(self.get_domains())

        # ground specification and get preference types
        types = self.do_spec()
        types.add("") # add basic case

        # add #show statements if needed (CSP variables are not shown in this case)
        self.add_show(types)

        # translate and add the rest of the programs
        if self.__options['debug']: Debugger().debug(self.__underscores,self.__control,self.__programs,types)
        self.add_programs(types)

