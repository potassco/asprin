#script (python)

from __future__ import print_function
import clingo
import sys
from src.utils import utils
from src.utils import printer
import preference
import approximation

#
# DEFINES
#

EMPTY      = utils.EMPTY
# programs
BASE       = utils.BASE
SPEC       = utils.SPEC
GENERATE   = utils.GENERATE
PPROGRAM   = utils.PPROGRAM
APPROX     = utils.APPROX

# predicate names
DOM        = utils.DOM
GEN_DOM    = utils.GEN_DOM
PREFERENCE = utils.PREFERENCE
# more
SHOW       = "show"
OPTIMIZE   = "optimize"
ERROR      = "error"

# error checking
CHECK_SPEC = """
% P names X
##names(P,X) :- ##preference(P,_,_,name(X),_).

% transitive closure of names
##tr_names(X,Y) :- ##names(X,Y).
##tr_names(X,Y) :- ##names(X,Z), ##tr_names(Z,Y).

%
% errors
%

% two types for one preference name
##error((A,B,C,D)):- ##preference(P,T1), ##preference(P,T2), T1 != T2, 
  A = "preference:", 
  B = P, 
  C = ": error: preference specification error, ", 
  D = "preference name has more than one type".

% naming non existent statement
##error((A,B,C,D,E)):- ##names(X,Y), not ##preference(Y,_), 
  A = "preference:", 
  B = X, 
  C = ": error: preference specification error, ", 
  D = "naming non existent preference statement ",
  E = Y.

% naming loops
##error((A,B,C,D)):- ##tr_names(X,X),
  A = "preference:", 
  B = X, 
  C = ": error: preference specification error, ", 
  D = "naming loop".

% optimizing non existent statement
##error((A,B,C,D)):- ##optimize(X), not ##preference(X,_),
  A = "optimize:", 
  B = X, 
  C = ": error: preference specification error, ", 
  D = "optimizing non existent preference statement".

% no optimize statements
##error((A,B,C)):- { ##optimize(Y) } 0, 
  A = "optimize",  
  B = ": error: preference specification error, ", 
  C = "no optimize statement".

% many optimize statements
##error((A,B,C,D)):- ##optimize(X), 2 { ##optimize(Y) }, 
  A = "optimize:", 
  B = X, 
  C = ": error: preference specification error, ", 
  D = "many optimize statements".

#program """ + utils.WARNINGS + """.
% avoid warnings
##preference(A,B,C, for(D),E) :- ##preference(A,B,C, for(D),E).
##preference(A,B,C,name(D),E) :- ##preference(A,B,C,name(D),E).
##optimize(X) :- ##optimize(X).
##preference(X,Y) :- ##preference(X,Y).
##unsat(X,Y) :- ##unsat(X,Y).
##false :- ##false.
"""

# error printing
ERROR_SPEC = "error: preference specification error, "
ERROR_NON_DOMAIN = ERROR_SPEC + "the body contains non domain atoms\n"
ERROR_PREF_NON_DOMAIN  = "preference:{}: "            + ERROR_NON_DOMAIN
ERROR_ELEM_NON_DOMAIN  = "preference:{}:element:{}: " + ERROR_NON_DOMAIN
ERROR_OPT_NON_DOMAIN   = "optimize:{}: "             + ERROR_NON_DOMAIN
ERROR_NO_PREF_PROGRAM  = "preference:{}: " + ERROR_SPEC + """\
preference type {} has no preference program\n"""


class ProgramsPrinter:

    def print_programs(self,programs,types):
        for name, programs in programs.items():
            if name in { BASE, GENERATE, SPEC }:
                for type, program in programs.items():
                    if type in types:
                        params = "({})".format(type) if type != "" else ""
                        p = printer.Printer()
                        p.do_print("#program {}{}.".format(name,params))
                        p.do_print(program.get_string())

    def run(self,control,programs,types):
        self.print_programs(programs,types)
        l, t = [], preference.PreferenceProgramVisitor()
        for name, programs in programs.items():
            if name == PPROGRAM:
                for type, program in programs.items():
                    if type in types:
                        s = "#program " + name + ".\n" + program.get_string()
                        clingo.parse_program(s,lambda x: l.append(t.visit(x)))
        for i in l:
            printer.Printer().do_print(i)


class Parser:


    def __init__(self, control, programs, options):
        self.__control = control
        self.__programs = programs
        self.__options = options
        self.__underscores = utils.underscores


    def __add_and_ground(self, name, params, string, list):
        capturer = utils.Capturer(sys.stderr)
        try:
            self.__control.add(name,params,string)
            self.__control.ground(list)
        finally:
            s = capturer.translate_error(self.__programs, name, capturer.read())
            capturer.close()
            if s != "":
                printer.Printer().print_error_string(s)


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
        out, control, u = "", self.__control, self.__underscores
        for atom in control.symbolic_atoms.by_signature(u+GEN_DOM,2):
            args = atom.symbol.arguments
            for atom2 in control.symbolic_atoms.by_signature(str(args[0]),
                                                             int(str(args[1]))):
                out += u + DOM + "(" + str(atom2.symbol) + ").\n"
        return out


    def __cat(self, tuple):
        if tuple.arguments:
            return "".join([str(i) for i in tuple.arguments]).replace('"',"")
        else:
            return str(tuple)


    def __non_domain_message(self, atom, predicate):
        # preference statement
        if predicate == (PREFERENCE,2):
            u = self.__underscores
            arg1 = str(atom.symbol.arguments[0]).replace(u, "", 1)
            return ERROR_PREF_NON_DOMAIN.format(arg1)
        # preference element
        elif predicate == (PREFERENCE,5):
            arg1 = str(atom.symbol.arguments[0])
            try: # careful here
                arg2 = str(atom.symbol.arguments[1].arguments[0].arguments[1])
            except Exception as e:
                arg2 = str(atom.symbol.arguments[1])
            return ERROR_ELEM_NON_DOMAIN.format(arg1, arg2)
        # optimize statement
        else:
            arg1 = str(atom.symbol.arguments[0])
            return ERROR_OPT_NON_DOMAIN.format(arg1)


    def do_spec(self):

        control, programs = self.__control, self.__programs
        u, options = self.__underscores, self.__options

        # specification
        constants = options['constants'].items()
        old = [ key                      for key, value in constants ]
        new = [ clingo.parse_term(value) for key, value in constants ]
        string  = programs[SPEC][""].get_string() 
        string += CHECK_SPEC.replace("##",u)
        self.__add_and_ground(SPEC,old,string,[(SPEC,new)])

        # get specification errors
        errors = False
        pr = printer.Printer()
        for atom in control.symbolic_atoms.by_signature(u+ERROR, 1):
            string = self.__cat(atom.symbol.arguments[0]) + "\n"
            pr.print_spec_error(string)
            errors = True

        # get non domain errors
        for i in [(PREFERENCE,2),(PREFERENCE,5),(OPTIMIZE,1)]:
            ui0 = u + i[0]
            for atom in control.symbolic_atoms.by_signature(ui0, i[1]):
                if not atom.is_fact:
                    pr.print_spec_error(self.__non_domain_message(atom, i))
                    errors = True

        # get preference types, and test for a corresponding preference program
        out = set()
        upreference = u + PREFERENCE
        for atom in control.symbolic_atoms.by_signature(upreference,2):
            out.add(str(atom.symbol.arguments[1]))
            if str(atom.symbol.arguments[1]) not in programs[PREFERENCE]:
                arg1 = str(atom.symbol.arguments[0])
                arg2 = str(atom.symbol.arguments[1])
                s = ERROR_NO_PREF_PROGRAM.format(arg1, arg2)
                pr.print_spec_error(s)
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
        # NOTE: without #show statements, csp variables are not shown
        show = "\n".join(["#show " + ("" if x[2] else "-") + x[0] + "/" +
                          str(x[1]) + "."
                          for x in self.__control.symbolic_atoms.signatures if
                          not str(x[0]).startswith(self.__underscores)])
        show += "#show."
        self.__add_and_ground(SHOW,[],show,[(SHOW,[])])


    def add_programs(self, types):
        visitors  = [(PPROGRAM, preference.PreferenceProgramVisitor())]
        visitors += [(APPROX, approximation.ApproximationProgramVisitor())]
        with self.__control.builder() as builder:
            for name, visitor in visitors:
                list = []
                for type, program in self.__programs[name].items():
                    if type in types:
                        s = "#program " + name + ".\n" + program.get_string()
                        clingo.parse_program(s, lambda x: visitor.visit(x))
                visitor.finish(builder)
                #map(b.add, list)
                #map(print, list)
        #raise utils.SilentException() 

    def check_programs_errors(self):
        pass


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
            ProgramsPrinter().run(self.__control, self.__programs, types)
            raise utils.SilentException()

        # translate and add the rest of the programs
        self.add_programs(types)

        #TODO(after improving translation): check for error/1 predicates
        self.check_programs_errors()

