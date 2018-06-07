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
import sys
from threading import Condition
from ..utils import printer
from ..utils import utils

# TIMING
import time
times = {}
FREQUENCY = 1
def start_clock(clock):
    times[clock] = time.clock()
def check_clock(clock):
    return time.clock() - times[clock]


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
STR_SATISFIABLE        = "SATISFIABLE"
STR_LIMIT              = "MODEL FOUND (SEARCH LIMIT)"
STR_BENCHMARK_CLOCK    = "BENCHMARK"
STR_BENCHMARK_FILE     = "benchmark.txt"

# program names
DO_HOLDS = "do_holds"
DO_HOLDS_APPROX = "do_holds_approx"
DO_HOLDS_DELETE_BETTER = "do_holds_delete_better"
DO_HOLDS_AT_ZERO = "do_holds_at_zero"
OPEN_HOLDS = "open_holds"
VOLATILE_FACT = "volatile_fact"
VOLATILE_EXT = "volatile_external"
DELETE_MODEL = "delete_model"
DELETE_MODEL_VOLATILE = "delete_model_volatile"
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
UNSAT_ATOM    = utils.UNSAT
PREFERENCE    = utils.PREFERENCE
HOLDS_AT_ZERO = "holds_at_zero"
CSP           = "$"
MODEL_DELETE_BETTER = clingo.parse_term("delete_better")
DELETE_MODEL_VOLATILE_ATOM = "delete_model_volatile_atom"

# messages
WRONG_APPEND = """\
incorrect input to @append function, this should not happen"""
SAME_MODEL = """\
same stable model computed twice, there is an error in the input, \
probably an incorrect preference program"""
WARNING_NO_OPTIMIZE = """WARNING: no optimize statement, \
computing non optimal stable models"""
STR_BETTER_THAN_UNKNOWN = "BETTER THAN MODEL(S): {}"
STR_UNKNOWN_OPTIMAL = """\nINFO: The following MODEL(S) FOUND (with SEARCH LIMIT) \
are OPTIMAL MODEL(S): {}"""
STR_UNKNOWN_NONOPTIMAL = """\nINFO: All MODEL(S) FOUND (with SEARCH LIMIT) \
*could* be OPTIMAL MODEL(S): {}"""
STR_BENCHMARK_MSG = """Solving Time {}: {:.2f}s"""

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
   (DELETE_MODEL_VOLATILE,           ["m"],"""
#external ##""" + DELETE_MODEL_VOLATILE_ATOM + """(m).
:-     ##""" + HOLDS + """(X,0) : X = @get_holds(); 
   not ##""" + HOLDS + """(X,0) : X = @get_nholds();
   not ##""" + DELETE_MODEL_VOLATILE_ATOM + """(m)."""),
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

    def __init__(self, control, options):
        # control and options
        self.control           = control
        self.options           = Options()
        for key, value in options.items():
            setattr(self.options, key, value)
        # strings
        self.underscores       = utils.underscores
        self.volatile_str      = self.underscores + VOLATILE
        self.model_str         = self.underscores + MODEL
        self.holds_at_zero_str = self.underscores + HOLDS_AT_ZERO
        self.holds_str         = self.underscores + HOLDS
        self.unsat_str         = self.underscores + UNSAT_ATOM
        self.delete_str        = self.underscores + DELETE_MODEL_VOLATILE_ATOM
        # holds
        self.holds             = []
        self.nholds            = []
        # others
        self.step = 1
        self.last_unsat = True
        self.opt_models = 0
        self.models = 0
        self.more_models = True
        self.old_holds = None
        self.old_nholds = None
        self.shown = []
        self.solving_result = None
        self.externals  = dict()
        self.improving  = []
        self.not_improving  = set()
        self.store_nholds = True
        self.holds_domain = set()
        self.approx_opt_models = []
        self.assumptions = []
        self.last_model = None
        self.sequences = {}
        self.unknown = []
        self.unknown_non_optimal = set()
        self.grounded_delete_better = False
        self.mapping = {}
        # solving and signals
        self.condition = Condition()
        self.interrupted = False
        self.solving = False
        # functions
        self.get_preference_parts_opt = self.get_preference_parts
        self.same_shown_function = self.same_shown_underscores
        # strings
        self.str_found      = STR_OPTIMUM_FOUND
        self.str_found_star = STR_OPTIMUM_FOUND_STAR
        # printer
        self.printer = printer.Printer()
        if self.options.max_models == 1 and not self.options.improve_limit:
            self.store_nholds = False
        self.saved_stats = False
        if self.options.benchmark:
            start_clock(STR_BENCHMARK_CLOCK)
            with open(STR_BENCHMARK_FILE, 'w') as f:
                f.write("")

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

    def get_unsat_function(self, term, y):
        return clingo.parse_term("{}({}{}({}),{}{}({}))".format(
            self.unsat_str, 
            self.underscores, MODEL, str(term),
            self.underscores, MODEL, y
            ))

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

    def get_sequence(self, name, elem):
        string = str(name)
        if string in self.sequences:
            self.sequences[string] += 1
        else:
            self.sequences[string]  = 1
        return self.sequences[string]

    def append(self, elem, alist):
        if alist.name == "" and len(alist.arguments):
            return clingo.Function("", [elem] + alist.arguments)
        else:
            return clingo.Function("", [elem] + [alist])

    def get_level(self, levels, max_level, max_depth):
        max_level = int(str(max_level))
        max_depth = int(str(max_depth))
        if str(levels.type) == "Number":
            l = [int(str(levels))]
        else:
            l = [int(str(i)) for i in levels.arguments]
        ###l, max_level, max_depth = [ 2, 1 ], 3, 6
        # l (filled with zeros until max_depth digits) is a number in base max_level+1
        level = 0
        for idx, i in enumerate(l):
            level += i * ((max_level + 1)**(max_depth - idx))
        #print("{} <= {} {} {}".format(level, levels, max_level, max_depth))
        return clingo.Number(level)

    def save_stats(self):
        if not self.saved_stats or check_clock(STR_BENCHMARK_CLOCK) > FREQUENCY:
            self.saved_stats = True
            with open(STR_BENCHMARK_FILE, 'w') as f:
                self.print_stats(file=f)
            start_clock(STR_BENCHMARK_CLOCK)

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
        for atom in control.symbolic_atoms.by_signature(
            u + "_" + utils.ERROR_PRED, 1
        ):
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

    def signal(self):
        if not self.solving:
            self.exit(1)
        else:
            self.control.interrupt()
            self.interrupted = True

    def set_config(self):
        try:
            self.iconfigs = (self.iconfigs + 1) % len(self.options.configs)
        except:
            self.iconfigs = 0
        self.control.configuration.configuration = self.options.configs[self.iconfigs]

    def stop(self, result):
        # set solving result
        if result.satisfiable:
            self.solving_result = SATISFIABLE
        elif result.unsatisfiable:
            self.solving_result = UNSATISFIABLE
        else:
            self.solving_result = UNKNOWN
        # notify
        with self.condition:
            self.condition.notify()

    def solve(self, **kwargs):
        if self.options.configs is not None:
            self.set_config()
        self.solving = True
        with self.condition:
            with self.control.solve(
                async=True, on_finish=self.stop, **kwargs
            ) as handle:
                self.condition.wait(float("inf"))
                handle.wait()
        self.solving = False
        if self.options.benchmark:
            self.save_stats()
        if self.interrupted:
            self.exit(1)

    def solve_heuristic(self):
        h = []
        # gather heuristics
        for _solver in self.control.configuration.solver:
            h.append(_solver.heuristic)
            _solver.heuristic="Domain"
        # solve
        self.solve(assumptions=self.assumptions, on_model=self.on_model)
        # restore heuristics
        i = 0
        for _solver in self.control.configuration.solver:
            _solver.heuristic = h[i]
            i += 1

    def solve_unknown(self):
        self.solving_result = UNKNOWN

    def solve_unsat(self):
        self.solving_result = UNSATISFIABLE

    def set_control_models(self):
        solve_conf = self.control.configuration.solve
        if self.options.max_models == 0:
            solve_conf.models = "0"
        else:
            solve_conf.models = str(self.options.max_models - self.opt_models)

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

    def print_unknowns(self, string, unknowns, mapping):
        if unknowns:
            self.printer.do_print(string.format(
                " ".join([str(mapping[i]) for i in unknowns])
            ))

    def print_unknown_nonoptimal_models(self, unknowns, mapping):
        self.print_unknowns(STR_UNKNOWN_NONOPTIMAL, unknowns, mapping)

    def print_unknown_optimal_models(self, unknowns, mapping):
        self.print_unknowns(STR_UNKNOWN_OPTIMAL, unknowns, mapping)

    def print_better_than_unknown(self, unknowns, mapping):
        self.print_unknowns(STR_BETTER_THAN_UNKNOWN, unknowns, mapping)

    def print_limit_string(self):
        self.printer.do_print(STR_LIMIT)

    def print_optimum_string(self, star=False):
        if not star:
            self.printer.do_print(self.str_found)
        else:
            self.printer.do_print(self.str_found_star)
        #if self.options.benchmark:
        #    time = check_clock(STR_BENCHMARK_CLOCK)
        #    self.printer.do_print(STR_BENCHMARK_MSG.format(self.opt_models, time))

    def print_steps_message(self):
        if self.opt_models == 0:
            self.printer.do_print(STR_SATISFIABLE)

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

    def same_shown_false(self):
        return False

    def on_model_enumerate(self, model):
        true = model.symbols(shown=True)
        self.shown = [i for i in true if i.name != self.holds_at_zero_str]
        # self.same_shown_function is modified by EnumerationController 
        # at controller.py
        if self.opt_models != self.options.max_models and (
            self.enumerate_flag or not self.same_shown_function()
        ):
            self.models     += 1
            self.opt_models += 1
            if self.options.quiet in {0,1}:
                self.print_answer()
            else:
                self.print_str_answer()
            self.print_optimum_string(True)

    def enumerate(self):
        # models
        control, solve_conf = self.control, self.control.configuration.solve
        old_models = self.control.configuration.solve.models
        self.set_control_models()
        if solve_conf.models != "0": # we repeat one
            solve_conf.models = str(int(solve_conf.models) + 1)
        # assumptions
        ass  = [ (self.get_holds_function(x,0),  True) for x in self.holds ]
        ass += [ (self.get_holds_function(x,0), False) for x in self.nholds]
        # solve
        self.old_shown, self.enumerate_flag = self.shown, False
        self.solve(assumptions = ass + self.assumptions,
                   on_model = self.on_model_enumerate)
        self.shown = self.old_shown
        control.configuration.solve.models = old_models

    def relax_previous_models(self):
        for i in self.improving:
            self.control.release_external(self.get_external(0, i))
        self.improving = []

    def ground_holds_delete_better(self):
        if not self.grounded_delete_better:
            self.control.ground([(DO_HOLDS_DELETE_BETTER, [])], self)
            self.grounded_delete_better = True

    def relax_optimal_models(self):
        for x,y in self.not_improving:
            self.control.assign_external(self.get_external(x,y),False)

    def volatile_optimal_model(self, step, delete_worse, delete_better):
        if delete_worse:
            self.not_improving.add((step,0))
        if delete_better:
            self.not_improving.add((MODEL_DELETE_BETTER,step))
        for x,y in self.not_improving:        #activate
            self.control.assign_external(self.get_external(x,y),True)
        if not self.options.no_opt_improving: #reset
            self.not_improving = set()

    def handle_optimal_model(self, step, delete_model_volatile,
                             delete_worse, delete_better, volatile):
        if not delete_model_volatile:
            parts = [(DELETE_MODEL, [])]
        else:
            parts = [(DELETE_MODEL_VOLATILE, [step])]
        if delete_worse: 
            # note: get_preference_parts_opt defaults to get_preference_parts
            #       may be modified by the GeneralController
            parts += self.get_preference_parts_opt(step, 0, False, volatile)
        # TODO: In base setting, use same preference program as for improving
        if delete_better:
            parts += self.get_preference_parts_opt(MODEL_DELETE_BETTER, step,
                                                   False, volatile)
        self.control.ground(parts, self)
        if volatile:
            self.volatile_optimal_model(step, delete_worse, delete_better)

    def clean_up(self):
        self.control.cleanup()

    def print_stats(self, file=sys.stdout):
        self.printer.print_stats(self.control,             self.models,
                                 self.more_models,         self.opt_models,
                                 self.options.non_optimal, self.options.stats,
                                 file)

    def exit(self, code):
        self.print_stats()
        sys.exit(code)

    def end(self):
        self.print_stats()
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
    # weak approximation
    #

    def on_model_approx(self, model):
        # for all models
        self.models += 1
        self.print_str_answer()
        # for models not proved to be optimal
        if not model.optimality_proven and model.cost!=[]:
            if self.options.quiet == 0:
                self.on_model(model)
                self.print_shown()
            elif self.options.quiet == 1 and self.options.max_models == 1:
                self.on_model(model)                            # one model
            return
        # for models proved to be optimal
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
        # set the domain of holds
        self.set_holds_domain()
        # weak approximation programs
        self.control.ground([(APPROX, [])], self)
        for i in PROGRAMS_APPROX:
            self.control.add(i[0], i[1], i[2].replace(TOKEN, self.underscores))
        # opt_mode
        self.control.configuration.solve.opt_mode = 'optN'
        if self.options.max_models == 1:                        # one model
            self.control.configuration.solve.opt_mode = 'opt'
        # project
        if self.options.project:
            self.control.ground([(PROJECT_APPROX,[])], self)
            self.control.configuration.solve.project = 'project'
        # loop
        self.printer.do_print("Solving...")
        while True:
            # solve
            prev_opt_models, self.approx_opt_models = self.opt_models, [[]]
            self.set_control_models()
            if self.options.max_models == 1:                    # one model
                self.control.configuration.solve.models = 0
            self.solve(on_model=self.on_model_approx)
            satisfiable = self.solving_result == SATISFIABLE
            # break if unsat or computed all or one model
            if not satisfiable or self.options.max_models == self.opt_models or \
                self.options.max_models == 1:                   # one model
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
        if self.options.max_models == 1 and satisfiable: # one model
            if self.options.quiet == 1:
                self.print_shown()
            self.opt_models += 1
            self.print_optimum_string()
        if self.opt_models == 0:
            self.print_unsat()
        self.more_models = True if satisfiable else False
        self.end()

    #
    # unknown (--improve-limit)
    #

    def computed_all(self):
        return (self.options.max_models != 0 and \
                self.opt_models == self.options.max_models)

    def enumerate_unknown(self):
        # if no unknowns, or computed all, or project: return
        if not self.unknown:
            self.more_models = False
            return
        if self.computed_all():
            return
        if self.options.improve_limit[4]: # if improve_no_check
            self.print_unknown_nonoptimal_models(self.unknown, self.mapping)
            return
        if self.options.project and not self.options.improve_limit[3]:
            self.print_unknown_optimal_models(self.unknown, self.mapping)
            self.opt_models += len(self.unknown)
            return
        # create boolean array representing unknown
        unknowns = [False] * (self.last_model + 1)
        for i in self.unknown:
            unknowns[i] = True
        # create holds dictionary for unknowns
        holds = {}
        for i in self.control.symbolic_atoms.by_signature(self.holds_str, 2):
            try:
                step = int(i.symbol.arguments[1].number)
                if unknowns[step]:
                    alist = holds.setdefault(step, [])
                    alist.append(i.symbol.arguments[0])
            except:
                pass
        # enumerate iterating over holds
        old = self.same_shown_function
        self.same_shown_function = self.same_shown_false
        for step in self.unknown:
            if self.computed_all():
                return
            # pre
            self.holds  = holds.get(step, [])
            self.nholds = list(self.holds_domain.difference(self.holds))
            delete_model = clingo.parse_term(
                "{}({})".format(self.delete_str, step)
            )
            self.control.assign_external(delete_model, True)
            if self.options.project:
                old = self.options.max_models
                self.options.max_models = self.opt_models + 1
            # enumerate
            self.enumerate()
            # post
            if self.options.project:
                self.options.max_models = old
            self.control.release_external(delete_model)
        self.same_shown_function = old
        self.more_models = False

    def on_model_unknown(self, model):
        self.unknown_non_optimal = set()
        atoms = model.symbols(atoms=True)
        for i in self.unknown:
            if not self.get_unsat_function(MODEL_DELETE_BETTER, i) in atoms:
                self.unknown_non_optimal.add(i)

    def handle_unknown_models(self, result):
        # if improve_no_check, add to unknown list if unknown
        if self.options.improve_limit[4]:
            if result == UNKNOWN:
                self.unknown.append(self.last_model)
                self.mapping[self.last_model] = self.models
            return
        # assumptions
        ass  = [ (self.get_holds_function(x,0),  True) for x in self.holds ]
        ass += [ (self.get_holds_function(x,0), False) for x in self.nholds]
        ass += [                             (x, True) for x in self.shown]
        # turn unknowns on
        for i in self.unknown:
            self.control.assign_external(
                self.get_external(MODEL_DELETE_BETTER, i), True
            )
        # solve
        if self.unknown:
            self.solve(assumptions = ass + self.assumptions,
                       on_model = self.on_model_unknown)
        # print which unknown are not optimal
        self.print_better_than_unknown(self.unknown_non_optimal, self.mapping)
        # initialize array to update unknown
        update_unknown = [self.last_model] if result == UNKNOWN else []
        # release non optimal, and update unknown
        for i in self.unknown:
            if i in self.unknown_non_optimal:
                self.control.release_external(
                    self.get_external(MODEL_DELETE_BETTER, i)
                )
                self.control.release_external(
                    self.get_external(i, 0)
                )
                del self.mapping[i]
            else:
                self.control.assign_external(
                    self.get_external(MODEL_DELETE_BETTER, i), False
                )
                update_unknown.append(i)
        self.unknown = update_unknown
        # update not_improving
        self.not_improving.difference_update(
            [(x,0) for x in self.unknown_non_optimal]
        )
        # if UNKNOWN, add delete better for last model (w/out unsat constraint)
        if result == UNKNOWN:
            x, y  = MODEL_DELETE_BETTER, self.last_model
            parts = [(PREFP, [x, y]), (VOLATILE_EXT,  [x,y])]
            self.control.ground(parts, self)
            # also, add mapping
            self.mapping[self.last_model] = self.models


    #
    # RUN()
    #

    def run(self):

        # controllers
        general = controller.GeneralController(self)
        optimal = controller.GeneralControllerHandleOptimal(self)
        enumeration = controller.EnumerationController(self)
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
        if self.options.improve_limit is not None:
            method = controller.ImproveLimitController(self, method)

        # loop
        try:
            # START
            general.start()
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
                elif self.solving_result == UNKNOWN:
                    # UNKNOWN
                    general.unknown()
                    method.unsat()
                    optimal.unknown()
                # END_LOOP
                general.end_loop()
        except RuntimeError as e:
            self.printer.print_error("ERROR (clingo): {}".format(e))
        except EndException as e:
            # END
            pass


