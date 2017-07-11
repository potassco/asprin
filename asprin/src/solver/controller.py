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

class GeneralController:

    def __init__(self, solver, state):
        self.solver             = solver
        self.state              = state
        self.state.step         = 1
        self.state.start_step   = 1
        self.state.last_unsat   = True
        self.state.opt_models   = 0
        self.state.models       = 0
        self.state.more_models  = True
        self.state.old_holds    = None
        self.state.old_nholds   = None
        self.state.normal_solve = True

    def start(self):
        self.solver.add_encodings()
        self.solver.ground_preference_base()

    def start_loop(self):
        if not self.state.last_unsat:
            self.solver.ground_holds()

    def solve(self):
        if self.state.normal_solve:
            self.solver.solve()

    def sat(self):
        self.state.models    += 1
        self.state.last_unsat = False
        self.solver.check_last_model()
        self.solver.print_shown()

    def unsat(self):
        if self.state.last_unsat:
            self.state.more_models = False
            if self.state.models == 0:
                self.solver.print_unsat()
            self.solver.end()
            return
        self.state.last_unsat = True
        self.state.opt_models  += 1
        self.solver.print_optimum_string()
        if self.state.opt_models == self.state.max_models:
            self.solver.end()
        if self.state.steps == self.state.step:
            self.solver.end() # to exit asap in this case

    def unsat_post(self):
        self.state.start_step = self.state.step + 1

    def end_loop(self):
        self.state.step = self.state.step + 1
        if self.state.steps == (self.state.step - 1):
            self.solver.end()


class GeneralControllerHandleOptimal:

    def __init__(self, solver, state):
        self.solver = solver

    def unsat(self):
        self.solver.handle_optimal_models()


class BasicMethodController:

    def __init__(self, solver, state):
        self.solver = solver
        self.state  = state
        self.state.basic_method_controller_on = True

    def start_loop(self):
        if not self.state.basic_method_controller_on:
            return
        if self.state.step > self.state.start_step:
            self.solver.ground_preference_program()

    def unsat(self):
        if not self.state.basic_method_controller_on:
            return
        self.solver.relax_previous_models()


class ApproxMethodController:

    def __init__(self, solver, state):
        self.solver = solver
        self.state  = state
        self.state.normal_solve = False
        self.state.basic_method_controller_on = False

    def start(self):
        self.solver.ground_approximation()

    def solve(self):
        opt_mode = self.solver.control.configuration.solve.opt_mode
        self.solver.control.configuration.solve.opt_mode == "opt"
        if self.state.last_unsat:
            self.solver.solve()
        else:
            self.solver.solve_unsat()
        self.solver.control.configuration.solve.opt_mode == opt_mode


class HeurMethodController:

    def __init__(self, solver, state):
        self.solver = solver
        self.state  = state
        self.state.normal_solve = False
        self.state.basic_method_controller_on = False
        for _solver in self.solver.control.configuration.solver:
            _solver.heuristic="Domain"

    def start(self):
        self.solver.ground_heuristic()

    def solve(self):
        if self.state.last_unsat:
            self.solver.solve()
        else:
            self.solver.solve_unsat()


class EnumerationController:

    def __init__(self, solver, state):
        self.solver = solver
        self.state  = state
        if not state.project:
            if not state.show_underscores:
                state.same_shown_function = solver.same_shown
            else:
                u = solver.same_shown_underscores
                state.same_shown_function = u

    def unsat(self):
        if not self.state.project:
            self.solver.enumerate()


class CheckerController:

    def __init__(self, solver, state):
        self.solver = solver

    def start(self):
        self.solver.check_errors()


class NonOptimalController:
    
    def __init__(self, solver, state):
        self.solver = solver
        self.state = state
    
    def start(self):
        if self.solver.no_optimize():
            self.state.non_optimal = True
            self.solver.print_no_optimize_warning()
        if self.state.non_optimal:
            import solver as _solver
            self.state.str_found      = _solver.STR_MODEL_FOUND
            self.state.str_found_star = _solver.STR_MODEL_FOUND_STAR
            self.solver.add_unsat_to_preference_program()


