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

#
# IMPORTS
#

import clingo
import controller
from ..utils import printer
from ..utils import utils

#
# DEFINES
#

# nodes and control
START         = "START"
START_LOOP    = "START_LOOP"
SOLVE         = "SOLVE"
SAT           = "SAT"
UNSAT         = "UNSAT"
UNKNOWN       = "UNKNOWN"
END_LOOP      = "END_LOOP"
END           = "END"
SATISFIABLE   = "SATISFIABLE"
UNSATISFIABLE = "UNSATISFIABLE"

# strings
STR_ANSWER             = "Answer: {}"
STR_OPTIMUM_FOUND      = "OPTIMUM FOUND"
STR_OPTIMUM_FOUND_STAR = "OPTIMUM FOUND *"
STR_MODEL_FOUND        = "MODEL FOUND"
STR_MODEL_FOUND_STAR   = "MODEL FOUND *"
STR_UNSATISFIABLE      = "UNSATISFIABLE"

# program names
DO_HOLDS = "do_holds"
DO_HOLDS_APPROX = "do_holds_approx"
DO_HOLDS_DELETE_BETTER = "do_holds_delete_better"
DO_HOLDS_AT_ZERO = "do_holds_at_zero"
OPEN_HOLDS = "open_holds"
VOLATILE_FACT = "volatile_fact"
VOLATILE_EXT = "volatile_external"
DELETE_MODEL = "delete_model"
DELETE_MODEL_APPROX = "delete_model_approx"
UNSAT_PRG = "unsat"
NOT_UNSAT_PRG = "not_unsat"
CMD_HEURISTIC = "cmd_heuristic"
PREFP = utils.PREFP
PBASE = utils.PBASE
APPROX = utils.APPROX
HEURISTIC = utils.HEURISTIC

# predicate and term names
VOLATILE      = utils.VOLATILE
MODEL         = utils.MODEL
HOLDS         = utils.HOLDS
VOLATILE      = utils.VOLATILE
UNSAT_ATOM    = utils.UNSAT
PREFERENCE    = utils.PREFERENCE
HOLDS_AT_ZERO = "holds_at_zero"
CSP           = "$"
MODEL_DELETE_BETTER = clingo.parse_term("delete_better")

# messages
SAME_MODEL = """\
same stable model computed twice, there is an error in the input, \
probably an incorrect preference program"""
WARNING_NO_OPTIMIZE = """WARNING: no optimize statement, \
computing non optimal stable models"""

#
# AUXILIARY PROGRAMS
#

TOKEN    = "##"
PROGRAMS = \
  [(DO_HOLDS_AT_ZERO,       [],"""
#show ##holds_at_zero(X) : ##""" + HOLDS + """(X,0)."""),
   (DO_HOLDS,            ["m"],"""
##""" + HOLDS + """(X,m) :- X = @get_holds()."""),
   (OPEN_HOLDS,          ["m"],"""
{ ##""" + HOLDS + """(X,m) } :- X = @get_holds_domain()."""),
   (VOLATILE_FACT, ["m1","m2"],"""
##""" + VOLATILE + """(##m(m1),##m(m2))."""),
   (VOLATILE_EXT,  ["m1","m2"],"""
#external ##""" + VOLATILE + """(##m(m1),##m(m2))."""),
   (DELETE_MODEL,           [],"""
:-     ##""" + HOLDS + """(X,0) : X = @get_holds(); 
   not ##""" + HOLDS + """(X,0) : X = @get_nholds()."""),
   (UNSAT_PRG,     ["m1","m2"],"""
:- not ##""" + UNSAT_ATOM + """(##m(m1),##m(m2)),
       ##""" +   VOLATILE + """(##m(m1),##m(m2))."""),
   (NOT_UNSAT_PRG, ["m1","m2"],"""
:-     ##""" + UNSAT_ATOM + """(##m(m1),##m(m2)),
       ##""" +   VOLATILE + """(##m(m1),##m(m2))."""),
   (CMD_HEURISTIC,   ["v","m"],"""
#heuristic ##""" + HOLDS + """(X,0) : ##""" + PREFERENCE + 
    """(_,_,_,for(X),_). [v@0,m]"""),
   (DO_HOLDS_DELETE_BETTER,        [],"""
##""" + HOLDS + """(X,""" + str(MODEL_DELETE_BETTER) + """) :- ##""" + 
    HOLDS + """(X,0)."""),
   (DO_HOLDS_APPROX,            ["m"],"""
##""" + HOLDS + """(X,m) :- X = @get_holds_approx(m)."""),
   (DELETE_MODEL_APPROX,           ["m"],"""
:-     ##""" + HOLDS + """(X,0) : X = @get_holds_approx(m); 
   not ##""" + HOLDS + """(X,0) : X = @get_nholds_approx(m)."""),
 ]
UNSAT_PREFP = (PREFP, ["m1","m2"], "##" + UNSAT_ATOM +"(##m(m1),##m(m2)).")


#
# Auxiliary Classes (EndException, Options)
#

class EndException(Exception):
    pass

class Options:
    pass

#
# Solver
#

class Solver:

    def __init__(self, control):
        # parameters
        self.control           = control
        self.underscores       = utils.underscores
        # strings
        self.volatile_str      = self.underscores + VOLATILE
        self.model_str         = self.underscores + MODEL
        self.holds_at_zero_str = self.underscores + HOLDS_AT_ZERO
        self.holds_str         = self.underscores + HOLDS
        # holds
        self.holds             = []
        self.nholds            = []
        # others
        self.options           = Options()
        self.old_holds   = None
        self.old_nholds  = None
        self.shown             = []
        self.solving_result    = None
        self.externals  = dict()
        self.improving  = []
        self.store_nholds = True
        self.holds_domain = set()
        self.approx_opt_models = []
        # for GeneralController
        self.normal_solve = True
        self.normal_sat   = True
        # strings
        self.str_found      = STR_OPTIMUM_FOUND
        self.str_found_star = STR_OPTIMUM_FOUND_STAR
        # printer
        self.printer = printer.Printer()

    #
    # AUXILIARY
    #
    def get_external(self, m1, m2):
        external = self.externals.get((m1,m2))
        if external is None:
            f1 = clingo.Function(self.model_str, [int(m1)])
            f2 = clingo.Function(self.model_str, [int(m2)])
            external = clingo.Function(self.volatile_str, [f1, f2])
            self.externals[(m1,m2)] = external
        return external

    def get_holds(self):
        return self.holds

    def get_holds_domain(self):
        return list(self.holds_domain)

    def set_holds_domain(self):
        for i in self.control.symbolic_atoms.by_signature(self.holds_str, 2):
            symbol = i.symbol
            if str(symbol.arguments[1]) == "0":
                self.holds_domain.add(symbol.arguments[0])
        return self.holds_domain

    def get_nholds(self):
        return self.nholds

    def get(self, atuple, index):
        try:
            return atuple.arguments[index.number]
        except:
            return atuple

    def length(self, atuple):
        try:
            return len(atuple.arguments)
        except:
            return 0 

    def __cat(self, tuple):
        if tuple.arguments:
            return "".join([str(i) for i in tuple.arguments]).replace('"',"")
        else:
            return str(tuple)

    #
    # CLINGO PROXY
    #

    def add_encodings(self):
        for i in PROGRAMS:
            self.control.add(i[0], i[1], i[2].replace(TOKEN, self.underscores))
        self.control.ground([(DO_HOLDS_AT_ZERO, [])], self)

    def no_optimize(self):
        optimize = self.underscores + utils.OPTIMIZE
        for atom in self.control.symbolic_atoms.by_signature(optimize, 1):
            return False
        return True

    def print_no_optimize_warning(self):
        self.printer.print_warning(WARNING_NO_OPTIMIZE)

    def add_unsat_to_preference_program(self):
        self.control.add(UNSAT_PREFP[0], UNSAT_PREFP[1],
                         UNSAT_PREFP[2].replace(TOKEN, self.underscores))

    def ground_approximation(self):
        self.control.ground([(APPROX, [])], self)

    def ground_heuristic(self):
        self.control.ground([(HEURISTIC, [])], self)

    def ground_cmd_heuristic(self):
        params = [clingo.parse_term(i) for i in self.options.cmd_heuristic]
        self.control.ground([(CMD_HEURISTIC, params)], self)
    
    def ground_preference_base(self):
        self.control.ground([(PBASE, [])], self)

    def ground_holds(self):
        control, prev_step = self.control, self.step-1
        control.ground([(DO_HOLDS, [prev_step])], self)

    def ground_open_preference_program(self):
        parts = [(PREFP,         [0,1]),
                 (OPEN_HOLDS,      [1]),
                 (NOT_UNSAT_PRG, [0,1]),
                 (VOLATILE_EXT,  [0,1])]
        self.control.ground(parts, self)

    def ground_preference_program(self, volatile):
        control, prev_step = self.control, self.step-1
        parts = [(PREFP,         [0,prev_step]),
                 (NOT_UNSAT_PRG, [0,prev_step])]
        if volatile:
            parts.append((VOLATILE_EXT,  [0,prev_step]))
        else:
            parts.append((VOLATILE_FACT, [0,prev_step]))
        control.ground(parts, self)
        if volatile:
            control.assign_external(self.get_external(0,prev_step),True)
        self.improving.append(prev_step)

    def check_errors(self):
        pr, control, u = self.printer, self.control, self.underscores
        error = False
        for atom in control.symbolic_atoms.by_signature(u+"_"+utils.ERROR, 1):
            string = "\n" + self.__cat(atom.symbol.arguments[0])
            pr.print_spec_error(string)
            error = True
        if error:
            pr.do_print("")
            raise Exception("parsing failed")

    def on_model(self, model):
        self.holds, self.nholds, self.shown = [], [], []
        for a in model.symbols(shown=True):
            if a.name == self.holds_at_zero_str:
                self.holds.append(a.arguments[0])
            else:
                self.shown.append(a)
        if not self.store_nholds:
            return
        for a in model.symbols(terms=True, complement=True):
            if a.name == self.holds_at_zero_str:
                self.nholds.append(a.arguments[0])

    def __set_solving_result(self, result):
        self.solving_result = None
        if result.satisfiable:
            self.solving_result = SATISFIABLE
        elif result.unsatisfiable:
            self.solving_result = UNSATISFIABLE

    def solve(self):
        result = self.control.solve(on_model=self.on_model)
        self.__set_solving_result(result)

    def solve_unsat(self):
        self.solving_result = UNSATISFIABLE

    def on_model_approx(self, model):
        # TODO: option to print no optimal
        if not model.optimality_proven:
            return
        self.on_model(model)
        self.approx_opt_models.append(self.holds)
        self.models     += 1
        self.opt_models += 1
        if self.options.quiet in {0,1}:
            self.print_answer()
        else:
            self.print_str_answer()
        self.print_optimum_string()

    def __set_control_models(self):
        solve_conf = self.control.configuration.solve
        if self.options.max_models == 0:
            solve_conf.models = 0
        else:
            solve_conf.models = self.options.max_models - self.opt_models
    
    def get_holds_approx(self, i):
        return self.approx_opt_models[int(str(i)) - self.opt_models]

    def get_nholds_approx(self, i):
        _set = self.holds_domain.difference(self.approx_opt_models[int(str(i)) - self.opt_models])
        return list(_set)
# TODO
# n models:
# tests
# nicer
# delete-better
# total-order
# library

    def solve_approx(self):
        self.set_holds_domain()
        self.__set_control_models()
        self.control.configuration.solve.models = 0
        self.control.configuration.solve.opt_mode='optN'
        result = self.control.solve(on_model=self.on_model_approx)
        while result.satisfiable:
            parts = []
            size = len(self.approx_opt_models)
            for i in range(1+self.opt_models, size+self.opt_models):
                parts += [(DELETE_MODEL_APPROX, [i]),
                          (DO_HOLDS_APPROX, [i]),
                          (PREFP,         [i,0]),
                          (UNSAT_PRG,     [i,0]),
                          (VOLATILE_FACT, [i,0])]
            self.control.ground(parts, self)
            self.approx_opt_models = [[]]
            self.__set_control_models()
            self.control.configuration.solve.models = 0
            result = self.control.solve(on_model=self.on_model_approx)
        self.more_models = False
        self.end() 

    def __symbol2str(self,symbol):
        if symbol.name == CSP:
            return str(symbol.arguments[0]) + "=" + str(symbol.arguments[1])
        return str(symbol)

    def print_shown(self):
        self.printer.do_print(" ".join(map(self.__symbol2str, self.shown)))

    def print_str_answer(self):
        self.printer.do_print(STR_ANSWER.format(self.models))

    def print_answer(self):
        self.printer.do_print(STR_ANSWER.format(self.models))
        self.printer.do_print(" ".join(map(self.__symbol2str, self.shown)))

    def print_optimum_string(self):
        self.printer.do_print(self.str_found)

    def print_unsat(self):
        self.printer.do_print(STR_UNSATISFIABLE)

    def check_last_model(self):
        if self.old_holds  == self.holds and (
           self.old_nholds == self.nholds):
                self.printer.do_print()
                raise Exception(SAME_MODEL)
        self.old_holds  = self.holds
        self.old_nholds = self.nholds

    def relax_previous_model(self):
        self.control.release_external(self.get_external(0,self.step-1))

    def same_shown(self):
        if set(self.old_shown) == set(self.shown):
            self.enumerate_flag = True
            return True
        return False

    def same_shown_underscores(self):
        u = self.underscores
        s1 = set([i for i in self.old_shown if not str(i).startswith(u)])
        s2 = set([i for i in     self.shown if not str(i).startswith(u)])
        if s1 == s2:
            self.enumerate_flag = True
            return True
        return False

    def on_model_enumerate(self,model):
        true = model.symbols(shown=True)
        self.shown = [ i for i in true if i.name != self.holds_at_zero_str ]
        # self.same_shown_function is modified by EnumerationController 
        # at controller.py
        if self.enumerate_flag or not self.same_shown_function():
            self.models     += 1
            self.opt_models += 1
            if self.options.quiet in {0,1}:
                self.print_answer()
            else:
                self.print_str_answer()
            self.printer.do_print(self.str_found_star)

    def enumerate(self):
        # models
        control    = self.control
        old_models = self.control.configuration.solve.models
        self.__set_control_models()
        # assumptions
        h = self.holds_str
        ass  = [ (clingo.Function(h, [x,0]), True)  for x in self.holds ]
        ass += [ (clingo.Function(h, [x,0]), False) for x in self.nholds]
        # solve
        self.old_shown, self.enumerate_flag = self.shown, False
        control.solve(assumptions=ass, on_model=self.on_model_enumerate)
        self.shown = self.old_shown
        control.configuration.solve.models = old_models

    def relax_previous_models(self):
        for i in self.improving:
            self.control.release_external(self.get_external(0, i))
        self.improving = []

    def ground_holds_delete_better(self):
        self.control.ground([(DO_HOLDS_DELETE_BETTER, [])], self)

    def handle_optimal_model(self, step, delete_worse, delete_better):
        parts = [(DELETE_MODEL, [])]
        if delete_worse:
            parts += [(PREFP,         [step,0]),
                      (UNSAT_PRG,     [step,0]),
                      (VOLATILE_FACT, [step,0])]
        if delete_better:
            parts += [(PREFP,         [MODEL_DELETE_BETTER,step]),
                      (UNSAT_PRG,     [MODEL_DELETE_BETTER,step]),
                      (VOLATILE_FACT, [MODEL_DELETE_BETTER,step])]
        self.control.ground(parts, self)
       
    def end(self):
        self.printer.print_stats(self.control,             self.models,
                                 self.more_models,         self.opt_models,
                                 self.options.non_optimal, self.options.stats)
        raise EndException

    #
    # OPTIONS
    #

    def set_options(self,options):
        for key,value in options.items():
            setattr(self.options,key,value)

    #
    # RUN()
    #

    def run(self):

        # controllers
        general = controller.GeneralController(self)
        optimal = controller.GeneralControllerHandleOptimal(self)
        enumeration = controller.EnumerationController(self)
        checker = controller.CheckerController(self)
        non_optimal = controller.NonOptimalController(self)
        # MethodController
        if self.options.solving_mode == "approx":
            method = controller.ApproxMethodController(self)
        elif self.options.solving_mode == "heuristic":
            method = controller.HeurMethodController(self)
        else:
            method = controller.GroundManyMethodController(self)

        # loop
        try:
            # START
            general.start()
            checker.start()
            non_optimal.start()
            optimal.start()
            method.start()
            self.printer.do_print("Solving...")
            while True:
                # START_LOOP
                general.start_loop()
                method.start_loop()
                # SOLVE
                method.solve()
                general.solve()
                if self.solving_result == SATISFIABLE:
                    # SAT
                    general.sat()
                elif self.solving_result == UNSATISFIABLE:
                    # UNSAT
                    general.unsat()
                    method.unsat()
                    enumeration.unsat()
                    optimal.unsat()
                    # UNSAT_POST
                    general.unsat_post()
                else:
                    # UNKNOWN
                    pass
                # END_LOOP
                general.end_loop()
        except RuntimeError as e: 
            self.printer.print_error("ERROR (clingo): {}".format(e))
        except EndException as e: 
            # END
            pass


