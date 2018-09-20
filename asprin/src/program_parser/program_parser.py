# MIT License
# 
# Copyright (c) 2017 Javier Romero
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -*- coding: utf-8 -*-

from __future__ import print_function
import clingo
import sys
from ..utils import utils
from ..utils import printer
from . import preference
from . import basic

#
# DEFINES
#

EMPTY      = utils.EMPTY

# programs
BASE         = utils.BASE
SPEC         = utils.SPEC
GENERATE     = utils.GENERATE
PREFP        = utils.PREFP
APPROX       = utils.APPROX
HEURISTIC    = utils.HEURISTIC
UNSATP       = utils.UNSATP
CONSTANTS_NB = utils.CONSTANTS_NB

# underscores
U_PREFP     = utils.U_PREFP
U_APPROX    = utils.U_APPROX
U_HEURISTIC = utils.U_HEURISTIC
U_UNSATP    = utils.U_UNSATP

# predicate names
DOM        = utils.DOM
GEN_DOM    = utils.GEN_DOM
PREFERENCE = utils.PREFERENCE
SHOW       = utils.SHOW
OPTIMIZE   = utils.OPTIMIZE
ERROR_PRED = utils.ERROR_PRED
WARN_PRED  = utils.WARN_PRED

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

% many optimize statements
##error((A,B,C,D)):- ##optimize(X), 2 { ##optimize(Y) }, 
  A = "optimize:", 
  B = X, 
  C = ": error: preference specification error, ", 
  D = "many optimize statements".

%
% warnings
%

% no optimize statements
##warning((A,B)):- { ##optimize(Y) } 0, 
  A = "WARNING: no optimize statement, ",
  B = "computing non optimal stable models".

% avoid clingo warnings
#defined ##preference/5.
#defined ##preference/2.
#defined ##optimize/1.
#defined ##unsat/2.
#defined ##false/0.
#defined ##optimize/1.
#defined ##holds/2.
"""

# error printing
ERROR_SPEC = "error: preference specification error, "
ERROR_NON_DOMAIN = ERROR_SPEC + "the body contains non domain atoms\n"
ERROR_PREF_NON_DOMAIN  = "preference:{}: "            + ERROR_NON_DOMAIN
ERROR_ELEM_NON_DOMAIN  = "preference:{}:element:{}: " + ERROR_NON_DOMAIN
ERROR_OPT_NON_DOMAIN   = "optimize:{}: "             + ERROR_NON_DOMAIN
ERROR_NO_PREF_PROGRAM  = "preference:{}: " + ERROR_SPEC + """\
preference type '{}' has no preference program\n"""
ERROR_NO_HEURISTIC_PROGRAM  = "preference:{}: " + ERROR_SPEC + """\
preference type '{}' has no heuristic approximation program\n"""
ERROR_NO_APPROX_PROGRAM  = "preference:{}: " + ERROR_SPEC + """\
preference type '{}' has no weak approximation program\n"""
ERROR_NO_UNSATP_PROGRAM  = "preference:{}: " + ERROR_SPEC + """\
preference type '{}' has no """ + UNSATP + """ program\n"""
ERROR_UNSTRAT_PROGRAM = """\
parsing error, unstratified {} program, use option --meta"""

# for meta-programming
META_COMBINE = utils.META_COMBINE
META_OPEN = utils.META_OPEN

class BuilderProxy:

    def __init__(self, builder):
        self.builder = builder
        self.printer = printer.Printer()

    def add(self, statement):
        self.printer.do_print(statement)
        self.builder.add(statement)


class ObserverBuilderProxy:

    def __init__(self, builder, observer):
        self.builder = builder
        self.observer = observer

    def add(self, statement):
        self.builder.add(statement)
        self.observer.add_statement(statement)


class Parser:

    def __init__(self, control, programs, options, observer):
        self.__control = control
        self.__programs = programs
        self.__options = options
        self.__underscores = utils.underscores
        self.__observer = observer

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

    def print_basic_programs(self, types):
        for name in [BASE, GENERATE, SPEC]:
            for type, program in self.__programs[name].items():
                if type in types:
                    params = "({})".format(type) if type != "" else ""
                    p = printer.Printer()
                    p.do_print("#program {}{}.".format(name,params))
                    p.do_print(program.get_string())

    def do_base(self):
        options, control = self.__options, self.__control
        programs = self.__programs
        # constants
        constants = options['constants'].items()
        old = [ key                      for key, value in constants ]
        new = [ clingo.parse_term(value) for key, value in constants ]
        # add and ground
        string_base =  programs[BASE][""].get_string()
        self.__add_and_ground(BASE, old, string_base, [(BASE,new)])
        string_generate =  programs[GENERATE][""].get_string()
        self.__add_and_ground(GENERATE, [], string_generate, [(GENERATE,[])])
        # observe
        if self.__observer:
            self.__observer.add_base(string_base, old, new)


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

    def __program_exists(self, atom):
        # get programs
        programs = [(PREFERENCE, ERROR_NO_PREF_PROGRAM)]
        if self.__options['solving_mode'] == 'heuristic':
            programs.append((HEURISTIC, ERROR_NO_HEURISTIC_PROGRAM))
        elif self.__options['solving_mode'] == 'weak':
            programs.append((APPROX, ERROR_NO_APPROX_PROGRAM))
        if self.__options['preference_unsat']:
            programs.append((UNSATP, ERROR_NO_UNSATP_PROGRAM))
        # arguments of atom
        arg1 = str(atom.symbol.arguments[0])
        arg2 = str(atom.symbol.arguments[1])
        # loop
        ok = True
        for program, error in programs:
            if arg2 not in self.__programs[program]:
                printer.Printer().print_spec_error(error.format(arg1, arg2))
                ok = False
        return ok

    def do_spec(self):

        control, programs = self.__control, self.__programs
        u, options = self.__underscores, self.__options

        # specification
        constants = options['constants'].items()
        old = [ key                      for key, value in constants ]
        new = [ clingo.parse_term(value) for key, value in constants ]
        string  = programs[SPEC][""].get_string() 
        if options['check']:
            string += CHECK_SPEC.replace("##",u)
        self.__add_and_ground(SPEC,old,string,[(SPEC,new)])

        pr = printer.Printer()
        errors = False

        if options['check']:
            # get specification warnings and errors
            for atom in control.symbolic_atoms.by_signature(u+WARN_PRED, 1):
                string = self.__cat(atom.symbol.arguments[0]) + "\n"
                pr.print_spec_warning(string)
            for atom in control.symbolic_atoms.by_signature(u+ERROR_PRED, 1):
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

        # get preference types, and test for corresponding programs
        out = set()
        upreference = u + PREFERENCE
        for atom in control.symbolic_atoms.by_signature(upreference,2):
            out.add(str(atom.symbol.arguments[1]))
            if options['check']:
                ok = self.__program_exists(atom)
                if not ok:
                    errors = True

        # observe
        if self.__observer:
            self.__observer.add_specification(string, old, new)
        
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

    def add_constants_nonbase(self):
        if not self.__options['constants_nb']:
            return
        constants_nb = self.__options['constants_nb'].items()
        program = " ".join("#const {}={}.".format(x,y) for x,y in constants_nb)
        self.__add_and_ground(CONSTANTS_NB, [], program, [(CONSTANTS_NB,[])])
        # observe
        if self.__observer:
            self.__observer.add_constants_nb(program, [], [])

    def add_programs(self, types, builder, observer_builder=None):
        # visitors
        constants = self.__options['constants_nb']
        # set preference and preference_unsat builders
        preference_builder, preference_unsat_builder = builder, builder
        if observer_builder and self.__options['meta'] == META_COMBINE and \
           self.__options['preference_unsat']:
            preference_unsat_builder = observer_builder
        elif observer_builder:
            preference_builder = observer_builder
        # do preference
        v = preference.PreferenceProgramVisitor(
            preference_builder, PREFP, U_PREFP, constants
        )
        visitors = [(PREFP, v)]
        # do approximations
        if self.__options['solving_mode'] == 'weak':
            v = basic.BasicProgramVisitor(
                builder, APPROX, U_APPROX, constants
            )
            visitors.append((APPROX,v))
        elif self.__options['solving_mode'] == 'heuristic':
            v = basic.HeuristicProgramVisitor(
                builder, HEURISTIC, U_HEURISTIC, constants
            )
            visitors.append((HEURISTIC,v))
        # do preference unsat
        if self.__options['preference_unsat']:
            v = preference.PreferenceProgramVisitor(
                preference_unsat_builder, UNSATP, U_UNSATP, constants
            )
            visitors.append((UNSATP,v))
        # add programs
        for name, visitor in visitors:
            for type_, program in self.__programs[name].items():
                if type_ in types:
                    s = "#program " + name + ".\n" + program.get_string()
                    clingo.parse_program(s, lambda x: visitor.visit(x))
            ret = visitor.finish()
            # error if unsat preference program not stratified and not meta
            if ret and self.__options['meta'] == META_OPEN and \
               self.__options['max_models'] != 1 and \
               ((not self.__options['preference_unsat'] and name ==  PREFP) or
                (    self.__options['preference_unsat'] and name == UNSATP)):
                raise Exception(ERROR_UNSTRAT_PROGRAM.format(name))

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

        # add nonbase constants
        self.add_constants_nonbase()

        # option --print-programs
        if self.__options['print-programs']:
            self.print_basic_programs(types)
            with self.__control.builder() as _builder:
                builder = BuilderProxy(_builder)
                self.add_programs(types, builder)
            raise utils.SilentException() # end

        # translate and add the rest of the programs
        with self.__control.builder() as builder:
            observer_builder = None
            if self.__observer:
                observer_builder = ObserverBuilderProxy(builder, self.__observer)
            self.add_programs(types, builder, observer_builder)

