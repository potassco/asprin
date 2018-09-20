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
import sys
import math
from threading import Condition
from . import controller
from ..utils import printer
from ..utils import utils
from .metasp import metasp

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
SATISFIABLE   = utils.SATISFIABLE                   # used also by controller
UNSATISFIABLE = "UNSATISFIABLE"

# for meta-programming
META_SIMPLE    = utils.META_SIMPLE
META_COMBINE   = utils.META_COMBINE
METAPROGRAM    = utils.METAPROGRAM
QUERY          = utils.QUERY
QUERY_PROGRAM  = utils.QUERY_PROGRAM
METAUNSAT      = utils.METAUNSAT
METAUNSAT_BASE = utils.METAUNSAT_BASE

# strings
STR_ANSWER             = "Answer: {}"
STR_OPTIMUM_FOUND      = "OPTIMUM FOUND"
STR_OPTIMUM_FOUND_STAR = "OPTIMUM FOUND *"
STR_MODEL_FOUND        = utils.STR_MODEL_FOUND      # used also by controller
STR_MODEL_FOUND_STAR   = utils.STR_MODEL_FOUND_STAR # used also by controller
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
PROJECT_CLINGO = "project_clingo"
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
HOLDS_AT_ZERO = utils.HOLDS_AT_ZERO
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
   (PROJECT_CLINGO,           [],"""
#project  ##""" + HOLDS + """/2."""),
  ]
PROGRAMS_APPROX = \
  [(DO_HOLDS_APPROX,            ["m","mm"],"""
##""" + HOLDS + """(X,m) :- X = @get_holds_approx(mm)."""),
   (DELETE_MODEL_APPROX,           ["mm"],"""
:-     ##""" + HOLDS + """(X,0) : X = @get_holds_approx(mm);
   not ##""" + HOLDS + """(X,0) : X = @get_nholds_approx(mm)."""),
  ]
UNSAT_PREFP  = (PREFP,  ["m1","m2"], "##" + UNSAT_ATOM +"(##m(m1),##m(m2)).")

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

    def __init__(self, control, options, control_proxy, observer):
        # control and options
        self.control           = control
        self.options           = Options()
        for key, value in options.items():
            setattr(self.options, key, value)
        self.control_proxy     = control_proxy
        self.observer = observer
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
        self.shown = []
        self.solving_result = None
        self.externals  = dict()
        self.improving  = []
        self.not_improving  = []
        self.store_holds = True
        self.store_nholds = False
        self.approx_opt_models = []
        self.assumptions = []
        self.last_model = None
        self.sequences = {}
        self.unknown = []
        self.unknown_non_optimal = []
        self.grounded_delete_better = False
        self.mapping = {}
        self.unsat_program = PREFP
        self.unsat_program_base = None
        # for weak mode
        self.control.configuration.solve.opt_mode = 'ignore' # by default ignore
        self.optN = False
        self.on_optimal = None
        # holds and shown domains
        self.set_holds_domain = False
        self.holds_domain = []
        self.set_shown_domain = False
        self.shown_domain = []
        # exiting
        self.exited = False
        # functions
        self.same_shown_function = self.same_shown_underscores
        # strings
        self.str_found      = STR_OPTIMUM_FOUND
        self.str_found_star = STR_OPTIMUM_FOUND_STAR
        # printer
        self.printer = printer.Printer()
        #if self.options.max_models == 1 and not self.options.improve_limit:
        #    self.store_nholds = False
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
        return self.holds_domain

    def do_set_holds_domain(self):
        self.holds_domain = [
            i.symbol.arguments[0] for i in
                self.control.symbolic_atoms.by_signature(self.holds_str, 2)
                if str(i.symbol.arguments[1]) == "0"
        ]

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

    def cat(self, tuple):
        if tuple.arguments:
            return "".join([str(i) for i in tuple.arguments]).replace('"',"")
        else:
            return str(tuple)

    def append(self, elem, alist):
        if alist.name == "" and len(alist.arguments):
            return clingo.Function("", [elem] + alist.arguments)
        else:
            return clingo.Function("", [elem] + [alist])

    def save_stats(self):
        if not self.saved_stats or check_clock(STR_BENCHMARK_CLOCK) > FREQUENCY:
            self.saved_stats = True
            with open(STR_BENCHMARK_FILE, 'w') as f:
                self.print_stats(file=f)
            start_clock(STR_BENCHMARK_CLOCK)


    #
    # USED BY ASPRIN LIBRARY (to be copied at metasp/metasp.py)
    #

    def exp2(self, x):
        return int(math.pow(2,x.number))

    def get(self, atuple, index):
        try:
            return atuple.arguments[index.number]
        except:
            return atuple

    def get_mode(self):
        return self.options.solving_mode

    def get_sequence(self, name, elem):
        string = str(name)
        if string in self.sequences:
            self.sequences[string] += 1
        else:
            self.sequences[string]  = 1
        return self.sequences[string]

    def length(self, atuple):
        try:
            return len(atuple.arguments)
        except:
            return 1

    def log2up(self, x):
        return int(math.ceil(math.log(x.number,2)))

    #
    # CLINGO PROXY
    #

    def add_and_ground(self, name, params, program, params_instances):
        self.control.add(name, params, program)
        self.ground([(name, params_instances)], self)

    def add_encodings(self):
        for i in PROGRAMS:
            self.control.add(i[0], i[1], i[2].replace(TOKEN, self.underscores))
        self.ground([(DO_HOLDS_AT_ZERO, [])], self)

    def add_projection(self):
        self.ground([(PROJECT_CLINGO, [])], self)
        self.control.configuration.solve.project = 'project'

    def add_unsat_to_preference_program(self):
        self.control.add(UNSAT_PREFP[0], UNSAT_PREFP[1],
                         UNSAT_PREFP[2].replace(TOKEN, self.underscores))

    def check_errors(self):
        pr, control, u = self.printer, self.control, self.underscores
        error = False
        for atom in control.symbolic_atoms.by_signature(
            u + "_" + utils.WARN_PRED, 1
        ):
            string = self.cat(atom.symbol.arguments[0]) + "\n"
            pr.print_spec_warning(string)
        for atom in control.symbolic_atoms.by_signature(
            u + "_" + utils.ERROR_PRED, 1
        ):
            string = self.cat(atom.symbol.arguments[0]) + "\n"
            pr.print_spec_error(string)
            error = True
        if error:
            raise Exception("parsing failed")

    def check_last_model(self):
        if self.old_holds  == self.holds:
            self.printer.do_print()
            raise Exception(SAME_MODEL)
        self.old_holds  = self.holds

    def clean_up(self):
        self.control.cleanup()

    def enumerate_on_model(self, model):
        true = model.symbols(shown=True)
        self.shown = [i for i in true if i.name != self.holds_at_zero_str]
        # we may enumerate one more model than what is needed,
        # so we check whether we already computed all models
        if self.options.max_models != 0 and \
           self.options.max_models == self.opt_models:
            return
        # self.same_shown_function is modified by EnumerationController
        # at controller.py
        if self.enumerate_flag or not self.same_shown_function():
            self.models     += 1
            self.opt_models += 1
            if self.options.quiet in {0,1}:
                self.print_answer()
            else:
                self.print_str_answer()
            self.print_optimum_string(True)

    def enumerate(self, add_one=True):
        # models
        control, solve_conf = self.control, self.control.configuration.solve
        old_models = solve_conf.models
        self.set_control_models()
        # we add one if not computing all and add_one (by default)
        if solve_conf.models != "0" and add_one:
            solve_conf.models = str(int(solve_conf.models) + 1)
        # assumptions
        ass  = [ (self.get_holds_function(x,0),  True) for x in self.holds ]
        ass += [ (self.get_holds_function(x,0), False) for x in self.nholds]
        # solve
        self.old_shown, self.enumerate_flag = self.shown, False
        self.solve(assumptions = ass + self.assumptions,
                   on_model = self.enumerate_on_model)
        self.shown = self.old_shown
        solve_conf.models = old_models

    def get_preference_parts(self, x, y, better, volatile):
        if better:
            parts = [(             PREFP, [x, y]), (NOT_UNSAT_PRG, [x,y])]
        else:
            parts = [(self.unsat_program, [x, y]), (    UNSAT_PRG, [x,y])]
        if volatile:
            parts.append((VOLATILE_EXT,  [x,y]))
        else:
            parts.append((VOLATILE_FACT, [x,y]))
        return parts

    def get_shown(self):
        return self.shown

    def get_shown_domain(self):
        return self.shown_domain

    def ground(self, *args):
        self.control_proxy.ground(*args)

    def ground_cmd_heuristic(self):
        params = [clingo.parse_term(i) for i in self.options.cmd_heuristic]
        self.ground([(CMD_HEURISTIC, params)], self)

    def ground_heuristic(self):
        self.ground([(HEURISTIC, [])], self)

    def ground_holds(self, step):
        self.ground([(DO_HOLDS, [step])], self)

    def ground_holds_delete_better(self):
        if not self.grounded_delete_better:
            self.ground([(DO_HOLDS_DELETE_BETTER, [])], self)
            self.grounded_delete_better = True

    def ground_preference_base(self):
        self.ground([(PBASE, [])], self)

    def ground_preference_program(self, volatile):
        control, prev_step = self.control, self.step-1
        parts = self.get_preference_parts(0, prev_step, True, volatile)
        control.ground(parts, self)
        if volatile:
            if self.options.release_last:
                self.relax_previous_models()
            control.assign_external(self.get_external(0,prev_step), True)
            self.improving.append(prev_step)

    def ground_unsatp_base(self):
        self.ground([(self.unsat_program_base, [])], self)

    def handle_optimal_model(self, step, delete_model_volatile,
                             delete_worse, delete_better, volatile):
        if not delete_model_volatile:
            parts = [(DELETE_MODEL, [])]
        else:
            parts = [(DELETE_MODEL_VOLATILE, [step])]
        if delete_worse:
            parts += self.get_preference_parts(step, 0, False, volatile)
        # TODO: In base setting, use same preference program as for improving
        if delete_better:
            parts += self.get_preference_parts(
                MODEL_DELETE_BETTER, step, False, volatile
            )
        self.ground(parts, self)
        if volatile:
            self.handle_volatile_optimal_model(step, delete_worse, delete_better)

    def handle_volatile_optimal_model(self, step, delete_worse, delete_better):
        if delete_worse:
            self.not_improving.append((step,0))
        if delete_better:
            self.not_improving.append((MODEL_DELETE_BETTER,step))
        for x,y in self.not_improving:        #activate
            self.control.assign_external(self.get_external(x,y),True)
        if not self.options.no_opt_improving: #reset
            self.not_improving = []

    def no_optimize(self):
        optimize = self.underscores + utils.OPTIMIZE
        for atom in self.control.symbolic_atoms.by_signature(optimize, 1):
            return False
        return True

    def on_model(self, model):
        self.holds, self.nholds, self.shown = [], [], []
        if self.set_shown_domain:
            self.shown_domain_set(model)
        for a in model.symbols(shown=True):
            if a.name != self.holds_at_zero_str:
                self.shown.append(a)
            elif self.store_holds:
                self.holds.append(a.arguments[0])
        if self.store_nholds:
            self.nholds = [
                x for x in self.holds_domain if x not in set(self.holds)
            ]

    def on_model_single(self, model):
        # call on_model
        self.on_model(model)
        # update numbers and print
        self.models += 1
        self.opt_models += 1
        self.print_str_answer()
        if self.options.quiet in (0, 1):
            self.print_shown()
        self.print_optimum_string()
        if not self.keep_shown:
            self.shown = []

    def set_config(self):
        try:
            self.iconfigs = (self.iconfigs + 1) % len(self.options.configs)
        except:
            self.iconfigs = 0
        self.control.configuration.configuration = self.options.configs[self.iconfigs]

    def set_control_models(self):
        solve_conf = self.control.configuration.solve
        if self.options.max_models == 0:
            solve_conf.models = "0"
        else:
            solve_conf.models = str(self.options.max_models - self.opt_models)

    def set_solving_result(self, result):
        # set solving result
        if result.satisfiable:
            self.solving_result = SATISFIABLE
        elif result.unsatisfiable:
            self.solving_result = UNSATISFIABLE
        else:
            self.solving_result = UNKNOWN

    # TODO: do not allow --preference-unsat and meta?
    def set_unsat_program(self):
        # auxiliary
        def set_and_ground(base, incremental):
            self.unsat_program_base = base
            self.unsat_program = incremental
            self.ground([(self.unsat_program_base, [])], self)
        # meta
        if self.options.meta == META_COMBINE:
            # meta_incremental() creates and adds METAUNSAT_BASE and METAUNSAT
            self.meta_incremental()
            set_and_ground(METAUNSAT_BASE, METAUNSAT)
        # preference_unsat
        if self.options.preference_unsat:
            set_and_ground(UNSATPBASE, UNSATP)

    def shown_domain_append(self, atom):
        if atom.type == clingo.SymbolType.Function and len(atom.name) > 0:
            self.shown_domain.append(atom)
            #name = ("-" if atom.negative else "") + atom.name
            #self.shown_domain.add((name, len(atom.arguments)))

    def shown_domain_set(self, model):
        self.set_shown_domain = False
        # gather all true and false atoms
        tatoms = model.symbols(atoms=True)
        fatoms = model.symbols(atoms=True, complement=True)
        # add shown elements that are true and false atoms
        for atom in model.symbols(shown=True):
            if atom in tatoms:
                self.shown_domain_append(atom)
        for atom in model.symbols(shown=True, complement=True):
            if atom in fatoms:
                self.shown_domain_append(atom)

    def solve(self, *args, **kwargs):
        if self.options.configs is not None:
            self.set_config()
        result = self.control_proxy.solve(*args, **kwargs)
        self.set_solving_result(result)
        return result

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

    def solve_single_on_optimal(self):
        self.control.configuration.solve.models = 1
        self.store_holds, self.store_nholds, self.keep_shown = [True]*3
        if not self.set_holds_domain: # required to store_nholds
            raise utils.FatalException() 
        self.printer.do_print("Solving...")
        while True:
            result = self.solve(on_model=self.on_model_single)
            # unsat
            if self.opt_models == 0:
                self.print_unsat()
                break
            # search space exhausted
            if result.exhausted:
                self.more_models = False
                break
            # computed all models
            if self.options.max_models == self.opt_models:
                break
            # enumerate if no projection
            if not self.options.project:
                self.enumerate() # TODO: prepare for this!
            # execute on_optimal
            self.on_optimal.unsat()
            # delete model
            self.ground([(DELETE_MODEL, [])], self) # TODO: store holds and nholds

    def solve_single(self):
        # if on_optimal, call and return
        if self.on_optimal.on():
            self.solve_single_on_optimal()
            return
        # add projection if needed
        if self.options.project:
            self.add_projection()
        # prepare to solve
        self.control.configuration.solve.models = self.options.max_models
        self.store_holds, self.store_nholds, self.keep_shown = [False]*3
        self.printer.do_print("Solving...")
        # solve and finish
        result = self.solve(on_model=self.on_model_single)
        if result.exhausted:
            self.more_models = False
        if self.opt_models == 0:
           self.print_unsat()

    def solve_unknown(self):
        self.solving_result = UNKNOWN

    def solve_unsat(self):
        self.solving_result = UNSATISFIABLE

    def symbol2str(self,symbol):
        if symbol.name == CSP:
            return str(symbol.arguments[0]) + "=" + str(symbol.arguments[1])
        return str(symbol)

    def print_answer(self):
        self.printer.do_print(STR_ANSWER.format(self.models))
        self.printer.do_print(" ".join(map(self.symbol2str, self.shown)))

    def print_better_than_unknown(self, unknowns, mapping):
        self.print_unknowns(STR_BETTER_THAN_UNKNOWN, unknowns, mapping)

    def print_limit_string(self):
        self.printer.do_print(STR_LIMIT)

    def print_no_optimize_warning(self):
        self.printer.print_warning(WARNING_NO_OPTIMIZE)

    def print_optimum_string(self, star=False):
        if not star:
            self.printer.do_print(self.str_found)
        else:
            self.printer.do_print(self.str_found_star)

    def print_shown(self):
        self.printer.do_print(" ".join(map(self.symbol2str, self.shown)))

    def print_steps_message(self):
        if self.opt_models == 0:
            self.printer.do_print(STR_SATISFIABLE)

    def print_str_answer(self):
        self.printer.do_print(STR_ANSWER.format(self.models))

    def print_unknowns(self, string, unknowns, mapping):
        if unknowns:
            self.printer.do_print(string.format(
                " ".join([str(mapping[i]) for i in unknowns])
            ))

    def print_unknown_nonoptimal_models(self, unknowns, mapping):
        self.print_unknowns(STR_UNKNOWN_NONOPTIMAL, unknowns, mapping)

    def print_unknown_optimal_models(self, unknowns, mapping):
        self.print_unknowns(STR_UNKNOWN_OPTIMAL, unknowns, mapping)

    def print_unsat(self):
        self.printer.do_print(STR_UNSATISFIABLE)

    def relax_previous_models(self):
        for i in self.improving:
            self.control.release_external(self.get_external(0, i))
        self.improving = []

    def relax_optimal_models(self):
        for x,y in self.not_improving:
            self.control.assign_external(self.get_external(x,y),False)

    def same_shown(self):
        if set(self.old_shown) == set(self.shown):
            self.enumerate_flag = True
            return True
        return False

    def same_shown_false(self):
        return False

    def same_shown_underscores(self):
        u = self.underscores
        s1 = set([i for i in self.old_shown if not str(i).startswith(u)])
        s2 = set([i for i in     self.shown if not str(i).startswith(u)])
        if s1 == s2:
            self.enumerate_flag = True
            return True
        return False

    #
    # on_opt_heur option
    #

    def assign_heuristic_externals(self, domain, atoms, external_name):
        for i in domain:
            external = clingo.Function(external_name, [i])
            if i in atoms:
                self.control.assign_external(external, True)
            else:
                self.control.assign_external(external, False)

    #
    # ground once method
    #

    def ground_open_preference_program(self):
        parts = self.get_preference_parts(0, -1, True, True)
        parts.append((OPEN_HOLDS, [-1]))
        self.ground(parts, self)

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
        return [
            x for x in self.holds_domain
            if x not in set(self.approx_opt_models[int(str(i))])
        ]

    def solve_approx(self):
        # approximation programs
        self.ground([(APPROX, [])], self)
        for i in PROGRAMS_APPROX:
            self.control.add(i[0], i[1], i[2].replace(TOKEN, self.underscores))
        # is on on_optimal?
        on_on_optimal = self.on_optimal.on()
        # set opt_mode
        self.control.configuration.solve.opt_mode = 'optN'
        # project
        if self.options.project and not on_on_optimal:
            self.add_projection()
        # loop
        self.printer.do_print("Solving...")
        first = True
        while True:
            # solve
            prev_opt_models, self.approx_opt_models = self.opt_models, [[]]
            self.set_control_models()
            if on_on_optimal: # go one by one
                self.control.configuration.solve.models = 1
            self.solve(on_model=self.on_model_approx)
            satisfiable = self.solving_result == SATISFIABLE
            # break if unsat or computed all
            if not satisfiable or self.options.max_models == self.opt_models:
                break
            # if on on_optimal
            if on_on_optimal:
                if not self.options.project:
                    self.control.configuration.solve.opt_mode = 'ignore'
                    self.enumerate()
                    self.control.configuration.solve.opt_mode = 'optN'
                self.on_optimal.unsat()
            # if first, set unsat programs
            if first:
                self.set_unsat_program()
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
            self.ground(parts, self)
            # if on_optimal
        # end
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

        # if no unknowns, or computed all: return
        if not self.unknown:
            self.more_models = False
            return
        if self.computed_all():
            return
        # if quick: print message and update opt_models
        if self.options.improve_limit[3]:
            self.print_unknown_optimal_models(self.unknown, self.mapping)
            self.opt_models += len(self.unknown)
            return
        # if improve_no_check: print message
        if self.options.improve_limit[4]:
            self.print_unknown_nonoptimal_models(self.unknown, self.mapping)
            return

        # ELSE: print *shown* atoms
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
            self.nholds = [
                x for x in self.holds_domain if x not in set(self.holds)
            ]
            delete_model = clingo.parse_term(
                "{}({})".format(self.delete_str, step)
            )
            self.control.assign_external(delete_model, True)
            if self.options.project:
                old = self.options.max_models
                self.options.max_models = self.opt_models + 1
            # enumerate
            self.enumerate(add_one=False)
            # post
            if self.options.project:
                self.options.max_models = old
            self.control.release_external(delete_model)
        self.same_shown_function = old
        self.more_models = False

    def on_model_unknown(self, model):
        atoms = model.symbols(atoms=True)
        for i in self.unknown:
            if not self.get_unsat_function(MODEL_DELETE_BETTER, i) in atoms:
                self.unknown_non_optimal.append(i)

    def handle_unknown_models(self, result):

        # if improve_no_check, add to unknown list if unknown
        if self.options.improve_limit[4]:
            if result == UNKNOWN:
                self.unknown.append(self.last_model)
                self.mapping[self.last_model] = self.models
            return

        # else check if some unknowns are worse than the latest model
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
        self.unknown_non_optimal = []
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
        self.not_improving = [
            x for x in self.not_improving
            if x not in set([(y,0) for y in self.unknown_non_optimal])
        ]
        # if UNKNOWN, add delete better for last model (w/out unsat constraint)
        if result == UNKNOWN:
            x, y  = MODEL_DELETE_BETTER, self.last_model
            parts = [(self.unsat_program, [x, y]), (VOLATILE_EXT,  [x,y])]
            self.ground(parts, self)
            #self.control.ground(parts, self)
            # also, add mapping
            self.mapping[self.last_model] = self.models
        #
        # leftover from merge
        #
        #self.not_improving.difference_update(
        #    [(x,0) for x in self.unknown_non_optimal]
        #)
        ## add delete better for last model (without unsat constraint)
        #x, y  = MODEL_DELETE_BETTER, self.last_model
        #parts = [(PREFP, [x, y]), (VOLATILE_EXT,  [x,y])]
        #self.ground(parts, self)

    #
    # meta-programming
    #

    def meta_simple(self):
        # choose meta implementation
        if self.options.meta_binary:
            meta = metasp.MetaspBinary(self)
        else:
            meta = metasp.MetaspPython(self)
        # get meta program
        meta_program = meta.get_meta_program()
        # add and ground
        self.control.add(METAPROGRAM, [], meta_program)
        self.ground([(METAPROGRAM, [])])
        # if query: adds the query and grounds
        if self.options.meta_query:
            qname, qprogram = QUERY, QUERY_PROGRAM
            self.control.add(qname, [], qprogram)
            self.ground([(qname, [])])
        # solve single
        self.solve_single()

    def meta_incremental(self):
        # choose meta implementation
        if self.options.meta_binary:
            meta = metasp.MetaspBinary(self)
        else:
            meta = metasp.MetaspPython(self)
        # get programs
        base, params, incremental = meta.get_incremental_program()
        # add to control
        self.control.add(METAUNSAT_BASE, [], base)
        self.control.add(METAUNSAT, params, incremental)

    #
    # exiting
    #

    def print_stats(self, interrupted=False, solved=True, copy_statistics=None):
        self.printer.print_stats(
            self.control, self.models, self.more_models, self.opt_models,
            self.options.non_optimal, self.options.stats,
            interrupted, solved, copy_statistics
        )

    def signal_on_solving(self):
        self.print_stats(interrupted=True)
        self.exit(1)

    def signal_on_not_solving(self):
        self.print_stats(
            interrupted=True, copy_statistics=self.control_proxy.statistics
        )
        self.exit(1)

    def signal_after_solving(self):
        self.print_stats()

    def exit(self, code):
        self.exited = True
        sys.exit(code)

    def end(self):
        self.print_stats()
        raise EndException


    #
    # run()
    #

    def run(self):

        # controllers
        general = controller.GeneralController(self)
        optimal = controller.GeneralControllerHandleOptimal(self)
        enumeration = controller.EnumerationController(self)
        self.on_optimal = on_optimal = controller.OnOptimalController(self)
        # MethodController
        if self.options.solving_mode == "weak":
            method = controller.ApproxMethodController(self)
            self.on_optimal = on_optimal
        elif self.options.solving_mode == "heuristic":
            method = controller.HeurMethodController(self)
        elif self.options.meta in [META_SIMPLE]:
            method = controller.MetaMethodController(self)
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
            method.start() # Approx and Meta finish here
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
                    on_optimal.unsat()
                elif self.solving_result == UNKNOWN:
                    # UNKNOWN
                    general.unknown()
                    method.unsat()
                    optimal.unknown()
                    on_optimal.unsat()
                # END_LOOP
                general.end_loop()
        except RuntimeError as e:
            if not self.exited:
                self.printer.print_error("ERROR (clingo): {}".format(e))
            sys.exit(1)
        except EndException as e:
            # END
            pass


