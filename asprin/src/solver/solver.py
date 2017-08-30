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

# TIMING
import time
times = {}
def start_clock(clock):
    times[clock] = time.clock()
def stop_clock(clock):
    print(time.clock()-times[clock])


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
PROJECT_APPROX = "project_approx"
PREFP = utils.PREFP
PBASE = utils.PBASE
APPROX = utils.APPROX
HEURISTIC = utils.HEURISTIC
UNSATP = utils.UNSATP
UNSATPBASE = utils.UNSATPBASE

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
  ]
PROGRAMS_APPROX = \
  [(DO_HOLDS_APPROX,            ["m","mm"],"""
##""" + HOLDS + """(X,m) :- X = @get_holds_approx(mm)."""),
   (DELETE_MODEL_APPROX,           ["mm"],"""
:-     ##""" + HOLDS + """(X,0) : X = @get_holds_approx(mm); 
   not ##""" + HOLDS + """(X,0) : X = @get_nholds_approx(mm)."""),
   (PROJECT_APPROX,           [],"""
#project  ##""" + HOLDS + """/2."""),
  ]
UNSAT_PREFP  = (PREFP,  ["m1","m2"], "##" + UNSAT_ATOM +"(##m(m1),##m(m2)).")
UNSAT_UNSATP = (UNSATP, ["m1","m2"], "##" + UNSAT_ATOM +"(##m(m1),##m(m2)).")

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
        self.options = Options()
        self.old_holds = None
        self.old_nholds = None
        self.shown = []
        self.solving_result = None
        self.externals  = dict()
        self.improving  = []
        self.not_improving  = []
        self.store_nholds = True
        self.holds_domain = set()
        self.approx_opt_models = []
        self.assumptions = []
        self.last_model = None
        # functions
        self.get_preference_parts_opt = self.get_preference_parts
        # for GeneralController
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
            f1 = clingo.Function(self.model_str, [m1])
            f2 = clingo.Function(self.model_str, [m2])
            external = clingo.Function(self.volatile_str, [f1, f2])
            self.externals[(m1,m2)] = external
        return external

    def get_holds(self):
        return self.holds

    def get_holds_domain(self):
        return list(self.holds_domain)

    def set_holds_domain(self):
        for i in self.control.symbolic_atoms.by_signature(self.holds_str, 2):
            if str(i.symbol.arguments[1]) == "0":
                self.holds_domain.add(i.symbol.arguments[0])
        return self.holds_domain

    def get_nholds(self):
        return self.nholds

    def get_holds_function(self, term, y):
        return clingo.Function(self.holds_str, [term, clingo.Number(y)]) 

    def get(self, atuple, index):
        try:
            return atuple.arguments[index.number]
        except:
            return atuple

    def length(self, atuple):
        try:
            return len(atuple.arguments)
        except:
            return 1 

    def cat(self, tuple):
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
        if self.options.preference_unsat:
            self.control.add(UNSAT_UNSATP[0], UNSAT_UNSATP[1],
                             UNSAT_UNSATP[2].replace(TOKEN, self.underscores))

    def ground_heuristic(self):
        self.control.ground([(HEURISTIC, [])], self)

    def ground_cmd_heuristic(self):
        params = [clingo.parse_term(i) for i in self.options.cmd_heuristic]
        self.control.ground([(CMD_HEURISTIC, params)], self)

    def ground_preference_base(self):
        self.control.ground([(PBASE, [])], self)

    def ground_unsatp_base(self):
        self.control.ground([(UNSATPBASE, [])], self)

    def ground_holds(self, step):
        self.control.ground([(DO_HOLDS, [step])], self)

    def get_preference_parts(self, x, y, better, volatile):
        parts = [(PREFP, [x, y])]
        if better:
            parts.append((NOT_UNSAT_PRG, [x,y]))
        else:
            parts.append((    UNSAT_PRG, [x,y]))
        if volatile:
            parts.append((VOLATILE_EXT,  [x,y]))
        else:
            parts.append((VOLATILE_FACT, [x,y]))
        return parts

    def get_preference_parts_unsatp(self, x, y, better, volatile):
        parts = self.get_preference_parts(x, y, better, volatile)
        parts.append((UNSATP, [x,y]))
        return parts[1:]

    def ground_preference_program(self, volatile):
        control, prev_step = self.control, self.step-1
        parts = self.get_preference_parts(0, prev_step, True, volatile)
        control.ground(parts, self)
        if volatile:
            if self.options.release_last:
                self.relax_previous_models()
            control.assign_external(self.get_external(0,prev_step), True)
            self.improving.append(prev_step)

    def check_errors(self):
        pr, control, u = self.printer, self.control, self.underscores
        error = False
        for atom in control.symbolic_atoms.by_signature(u+"_"+utils.ERROR_PRED, 1):
            string = "\n" + self.cat(atom.symbol.arguments[0])
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
        if self.store_nholds:
            self.nholds = list(self.holds_domain.difference(self.holds))

    def set_solving_result(self, result):
        self.solving_result = None
        if result.satisfiable:
            self.solving_result = SATISFIABLE
        elif result.unsatisfiable:
            self.solving_result = UNSATISFIABLE

    def solve(self):
        result = self.control.solve(assumptions=self.assumptions,
                                    on_model=self.on_model)
        self.set_solving_result(result)

    def solve_unsat(self):
        self.solving_result = UNSATISFIABLE

    def set_control_models(self):
        solve_conf = self.control.configuration.solve
        if self.options.max_models == 0:
            solve_conf.models = 0
        else:
            solve_conf.models = self.options.max_models - self.opt_models

    def symbol2str(self,symbol):
        if symbol.name == CSP:
            return str(symbol.arguments[0]) + "=" + str(symbol.arguments[1])
        return str(symbol)

    def print_shown(self):
        self.printer.do_print(" ".join(map(self.symbol2str, self.shown)))

    def print_str_answer(self):
        self.printer.do_print(STR_ANSWER.format(self.models))

    def print_answer(self):
        self.printer.do_print(STR_ANSWER.format(self.models))
        self.printer.do_print(" ".join(map(self.symbol2str, self.shown)))

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
        self.set_control_models()
        # assumptions
        ass  = [ (self.get_holds_function(x,0), True)  for x in self.holds ]
        ass += [ (self.get_holds_function(x,0), False) for x in self.nholds]
        # solve
        self.old_shown, self.enumerate_flag = self.shown, False
        control.solve(assumptions = ass + self.assumptions,
                         on_model = self.on_model_enumerate)
        self.shown = self.old_shown
        control.configuration.solve.models = old_models

    def relax_previous_models(self):
        for i in self.improving:
            self.control.release_external(self.get_external(0, i))
        self.improving = []

    def ground_holds_delete_better(self):
        self.control.ground([(DO_HOLDS_DELETE_BETTER, [])], self)

    def relax_optimal_models(self):
        for x,y in self.not_improving:
            self.control.assign_external(self.get_external(x,y),False)

    def volatile_optimal_model(self, step, delete_worse, delete_better):
        if delete_worse:
            self.not_improving.append((step,0))
        if delete_better:
            self.not_improving.append((MODEL_DELETE_BETTER,step))
        for x,y in self.not_improving:        #activate
            self.control.assign_external(self.get_external(x,y),True)
        if not self.options.no_opt_improving: #reset
            self.not_improving = []

    def handle_optimal_model(self, step, delete_worse, delete_better, volatile):
        parts = [(DELETE_MODEL, [])]
        if delete_worse: 
            # note: get_preference_parts_opt defaults to get_preference_parts
            parts += self.get_preference_parts_opt(step, 0, False, volatile)
        if delete_better:
            parts += self.get_preference_parts_opt(MODEL_DELETE_BETTER, step,
                                                   False, volatile)
        self.control.ground(parts, self)
        if volatile:
            self.volatile_optimal_model(step, delete_worse, delete_better)


    def end(self):
        self.printer.print_stats(self.control,             self.models,
                                 self.more_models,         self.opt_models,
                                 self.options.non_optimal, self.options.stats)
        raise EndException

    #
    # ground once method
    #

    def ground_open_preference_program(self):
        parts = self.get_preference_parts(0, -1, True, True)
        parts.append((OPEN_HOLDS, [-1]))
        self.control.ground(parts, self)

    def turn_off_preference_program(self):
        self.control.assign_external(self.get_external(0,-1), False)
        self.assumptions = (
            [(self.get_holds_function(i,-1),False) for i in  self.holds_domain]
        )

    def turn_on_preference_program(self):
        self.control.assign_external(self.get_external(0,-1), True)
        self.assumptions = (
            [(self.get_holds_function(i,-1),True)  for i in  self.holds] +
            [(self.get_holds_function(i,-1),False) for i in self.nholds]
        )

    #
    # approximation
    #

    def on_model_approx(self, model):
        # for all models
        self.models += 1
        self.print_str_answer()
        # for non optimal models
        if not model.optimality_proven:
            if self.options.quiet == 0:
                self.on_model(model)
                self.print_shown()
            return
        # for optimal models
        self.on_model(model)
        if self.options.quiet in {0,1}:
            self.print_shown()
        self.approx_opt_models.append(self.holds)
        self.opt_models += 1
        self.print_optimum_string()

    def get_holds_approx(self, i):
        return self.approx_opt_models[int(str(i))]

    def get_nholds_approx(self, i):
        _set = self.holds_domain.difference(self.approx_opt_models[int(str(i))])
        return list(_set)

    def solve_approx(self):
        # approximation programs
        self.control.ground([(APPROX, [])], self)
        for i in PROGRAMS_APPROX:
            self.control.add(i[0], i[1], i[2].replace(TOKEN, self.underscores))
        # set the domain of holds
        self.set_holds_domain()
        # opt_mode
        self.control.configuration.solve.opt_mode = 'optN'
        # project
        if self.options.project:
            self.control.ground([(PROJECT_APPROX,[])], self)
            self.control.configuration.solve.project = 'project'
        # loop
        while True:
            # solve
            prev_opt_models, self.approx_opt_models = self.opt_models, [[]]
            self.set_control_models()
            result = self.control.solve(on_model=self.on_model_approx)
            # break if unsat or computed all
            if not result.satisfiable or \
                self.options.max_models == self.opt_models:
                break
            # add programs
            parts = []
            for mm in range(1, len(self.approx_opt_models)):
                m = mm + prev_opt_models
                parts += [(DELETE_MODEL_APPROX, [mm]),
                          (DO_HOLDS_APPROX,   [m,mm])]
                if self.options.total_order and m>1:
                    continue
                parts += self.get_preference_parts(m, 0, False, False)
                if self.options.delete_better:
                    parts += self.get_preference_parts(0, m, False, False)
            self.control.ground(parts, self)
        # end
        self.more_models = True if result.satisfiable else False
        self.end() 
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
            if self.options.ground_once:
                method = controller.GroundOnceMethodController(self)
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
                method.start_loop()
                # SOLVE
                method.solve()
                if self.solving_result == SATISFIABLE:
                    # SAT
                    general.sat()
                    optimal.sat()
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


