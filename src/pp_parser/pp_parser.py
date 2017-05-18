#script (python)

from __future__ import print_function
import clingo
import transformer
import sys
import argparse
import re
from src.utils import utils
from src.utils import printer

#
# DEFINES
#

EMPTY      = utils.EMPTY
# programs
BASE       = utils.BASE
SPEC       = utils.SPEC
GENERATE   = utils.GENERATE
PPROGRAM   = utils.PPROGRAM
# predicate names
DOM        = utils.DOM
GEN_DOM    = utils.GEN_DOM
PREFERENCE = utils.PREFERENCE
# more
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


class ProgramsPrinter:


    def print_programs(self,programs,types):
        for name, programs in programs.items():
            if name in { BASE, GENERATE, SPEC }:
                for type, program in programs.items():
                    if type in types:
                        params = "({})".format(type) if type != "" else ""
                        print("#program {}{}.".format(name,params))
                        print(program.get_string())


    def run(self,control,programs,underscores,types):
        self.print_programs(programs,types)
        l, t = [], transformer.PreferenceProgramTransformer(underscores)
        for name, programs in programs.items():
            if name == PPROGRAM:
                for type, program in programs.items():
                    if type in types:
                        s = "#program " + name + ".\n" + program.get_string()
                        clingo.parse_program(s,lambda x: l.append(t.visit(x)))
        for i in l:
            print(i)


class Parser:


    def __init__(self,control,programs,options,underscores):
        self.__control = control
        self.__programs = programs
        self.__options = options
        self.__underscores = underscores


    def __add_and_ground(self,name,params,string,list):
        capturer = utils.Capturer(sys.stderr)
        try:
            self.__control.add(name,params,string)
            self.__control.ground(list)
        finally:
            printer.Printer().print_captured_error(self.__programs,
                                                   name,capturer.read())
            capturer.close()


    def do_base(self):

        options, control = self.__options, self.__control
        programs = self.__programs

        # constants
        constants = options['constants'].items()
        old = [ key                      for key, value in constants ]
        new = [ clingo.parse_term(value) for key, value in constants ]

        # add and ground
        string =  programs[BASE][""].get_string()
        self.__add_and_ground(BASE,old,string,[(BASE,new)])
        string =  programs[GENERATE][""].get_string()
        self.__add_and_ground(GENERATE,[],string,[(GENERATE,[])])


    def get_domains(self):
        out, control, underscores = "", self.__control, self.__underscores
        for atom in control.symbolic_atoms.by_signature(underscores+GEN_DOM,2):
            args = atom.symbol.arguments
            for atom2 in control.symbolic_atoms.by_signature(str(args[0]),
                                                             int(args[1])):
                out += underscores + DOM + "(" + str(atom2.symbol) + ").\n"
        return out


    def do_spec(self):

        control, programs = self.__control, self.__programs
        underscores, options = self.__underscores, self.__options

        # specification
        constants = options['constants'].items()
        old = [ key                      for key, value in constants ]
        new = [ clingo.parse_term(value) for key, value in constants ]
        string  = programs[SPEC][""].get_string() 
        string += CHECK_SPEC.replace("##",underscores)
        self.__add_and_ground(SPEC,old,string,[(SPEC,new)])

        # get specification errors
        errors = False
        for atom in control.symbolic_atoms.by_signature(underscores+ERROR,2):
            print("error in the preference specification: {} - {}".format(
                  str(atom.symbol.arguments[0]),str(atom.symbol.arguments[1])),file=sys.stderr)
            errors = True

        # get non domain errors
        for i in [(PREFERENCE,2),(PREFERENCE,5),(OPTIMIZE,1)]:
            for atom in control.symbolic_atoms.by_signature(underscores+i[0],i[1]):
                if not atom.is_fact:
                     print("error in the preference specification: non domain atom {}".format(
                           str(atom.symbol).replace(underscores,"",1)),file=sys.stderr)
                     errors = True

        # get preference types, and test if they have a corresponding preference program
        out = set()
        for atom in control.symbolic_atoms.by_signature(underscores+PREFERENCE,2):
            out.add(str(atom.symbol.arguments[1]))
            if str(atom.symbol.arguments[1]) not in programs[PREFERENCE]:
                print("error in the preference specification: preference type {} has no preference program".format(
                         str(atom.symbol.arguments[1])),file=sys.stderr)
                errors = True

        # if errors
        if errors:
            raise Exception("parsing failed")

        return out


    def add_show(self,types):

        # decide if adding #shows to the base, and set 'show_underscores'
        self.__options['show_underscores'], add_base_show = False, True
        for i in self.__options['show']:
            if (i[0]==BASE and i[1]==EMPTY):
                add_base_show = False
            elif (i[0]==PREFERENCE and i[1] in types):
                self.__options['show_underscores'] = True

        if not add_base_show: 
            return

        # else add #show for atoms in base
        show = "\n".join(["#show " + ("" if x[2] else "-") + x[0] + "/" +
                          str(x[1]) + "."
                          for x in self.__control.symbolic_atoms.signatures if
                          not str(x[0]).startswith(self.__underscores)])
        self.__add_and_ground(SHOW,[],show,[(SHOW,[])])


    def add_programs(self,types):
        t = transformer.PreferenceProgramTransformer(self.__underscores)
        with self.__control.builder() as b:
            for name, programs in self.__programs.items():
                if name == PPROGRAM:
                    for type, program in programs.items():
                        if type in types:
                            s = "#program "+name+".\n"+program.get_string()
                            clingo.parse_program(s,lambda x: b.add(t.visit(x)))


    def parse(self):

        # ground base program
        self.do_base()

        # get domains for the specification
        self.__programs[SPEC][""].extend_string(self.get_domains())

        # ground specification and get preference types
        types = self.do_spec()
        types.add("") # add basic case

        # add #show statements if needed (CSP variables are not shown)
        self.add_show(types)

        # print programs?
        if self.__options['print-programs']:
            ProgramsPrinter().run(self.__control, self.__programs, 
                                  self.__underscores, types)
            raise utils.SilentException()

        # translate and add the rest of the programs
        self.add_programs(types)

