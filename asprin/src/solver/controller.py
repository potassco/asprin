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

    def __init__(self, solver):
        solver.step         = 1
        solver.start_step   = 1
        solver.last_unsat   = True
        solver.opt_models   = 0
        solver.models       = 0
        solver.more_models  = True
        solver.old_holds    = None
        solver.old_nholds   = None
        if solver.options.max_models == 1:
            solver.store_nholds = False
        self.improve_limit = True if solver.options.improve_limit is not None \
            else False
        self.solver         = solver

    def start(self):
        solver, options = self.solver, self.solver.options
        if options.trans_ext is not None:
            solver.control.configuration.asp.trans_ext = options.trans_ext
        solver.set_holds_domain()
        solver.add_encodings()
        solver.ground_preference_base()
        if options.cmd_heuristic is not None:
            solver.ground_cmd_heuristic()
            for _solver in solver.control.configuration.solver:
                _solver.heuristic="Domain"
        if options.preference_unsat and options.max_models != 1:
            solver.get_preference_parts_opt = solver.get_preference_parts_unsatp
            solver.ground_unsatp_base()


    def sat(self):
        if not self.solver.normal_sat:
            return
        self.solver.models     += 1
        self.solver.last_unsat  = False
        self.solver.check_last_model()
        if self.solver.options.quiet == 0:
            self.solver.print_answer()
        else:
            self.solver.print_str_answer()
        if self.improve_limit:
            self.solver.set_solve_limit()

    def unsat(self):
        if self.solver.last_unsat:
            self.solver.more_models = False
            if self.solver.models == 0:
                self.solver.print_unsat()
            self.solver.end()
        if self.solver.options.quiet == 1:
            self.solver.print_shown()
        self.solver.last_unsat = True
        self.solver.opt_models  += 1
        self.solver.print_optimum_string()
        if self.solver.opt_models == self.solver.options.max_models:
            self.solver.end()
        if self.solver.options.steps == self.solver.step:
            self.solver.end() # to exit asap in this case
        if self.improve_limit:
            self.solver.reset_solve_limit()

    def unknown(self):
        if self.improve_limit:
            self.solver.reset_solve_limit()

    def unsat_post(self):
        self.solver.start_step = self.solver.step + 1

    def end_loop(self):
        self.solver.step = self.solver.step + 1
        if self.solver.options.steps == (self.solver.step - 1):
            self.solver.end()


class GeneralControllerHandleOptimal:

    def __init__(self, solver):
        self.solver = solver
        self.first  = True
        self.delete_worse  = True
        self.delete_better = self.solver.options.delete_better
        self.total_order   = self.solver.options.total_order
        self.no_opt_improving, self.volatile = False, False
        if solver.options.no_opt_improving:
            if solver.options.max_models != 1:
                self.no_opt_improving = True
            self.volatile = True
        if solver.options.volatile_optimal:
            self.volatile = True

    def start(self):
        if self.delete_better:
            self.solver.ground_holds_delete_better()

    def sat(self):
        if self.no_opt_improving and \
           self.solver.step == self.solver.start_step:
            self.solver.relax_optimal_models()

    def unsat(self):
        if self.total_order and not self.first:
            self.delete_worse  = False
            self.delete_better = False
        self.first = False
        self.solver.handle_optimal_model(self.solver.last_model,
                                         self.delete_worse,
                                         self.delete_better,
                                         self.volatile)


class MethodController:

    def __init__(self, solver):
        self.solver = solver

    def start(self):
        pass

    def start_loop(self):
        pass

    def solve(self):
        pass

    def unsat(self):
        pass


class GroundManyMethodController(MethodController):

    def __init__(self, solver):
        MethodController.__init__(self, solver)
        self.volatile = False
        if (self.solver.options.max_models != 1 or
            self.solver.options.release_last or 
            self.solver.options.volatile_improving):
            self.volatile = True 

    def start_loop(self):
        if not self.solver.last_unsat:
            self.solver.last_model = self.solver.step - 1
            self.solver.ground_holds(self.solver.last_model)
        if self.solver.step > self.solver.start_step:
            self.solver.ground_preference_program(self.volatile)

    def solve(self):
        self.solver.solve()

    def unsat(self):
        self.solver.relax_previous_models()


class GroundOnceMethodController(MethodController):

    def __init__(self, solver):
        MethodController.__init__(self, solver)
        solver.store_nholds = True

    def start(self):
        self.solver.ground_open_preference_program()
        self.solver.turn_off_preference_program()

    def start_loop(self):
        if self.solver.step > self.solver.start_step:
            self.solver.turn_on_preference_program()

    def solve(self):
        self.solver.solve()

    def unsat(self):
        self.solver.last_model = self.solver.step - 1
        self.solver.ground_holds(self.solver.last_model)
        self.solver.turn_off_preference_program()


class ApproxMethodController(MethodController):

    def __init__(self, solver):
        MethodController.__init__(self, solver)

    def start(self):
        self.solver.solve_approx()
        # finishes asprin


class HeurMethodController(MethodController):

    def __init__(self, solver):
        MethodController.__init__(self, solver)

    def start(self):
        self.solver.ground_heuristic()

    def start_loop(self):
        if not self.solver.last_unsat:
            self.solver.last_model = self.solver.step - 1
            self.solver.ground_holds(self.solver.last_model)

    def solve(self):
        if self.solver.last_unsat:
            self.solver.solve_heuristic()
        else:
            self.solver.solve_unsat()


class EnumerationController:

    def __init__(self, solver):
        self.solver = solver
        if not solver.options.project:
            # show_underscores is set by program_parser.py
            if not solver.options.show_underscores:
                solver.same_shown_function = solver.same_shown
            else:
                solver.same_shown_function = solver.same_shown_underscores

    def unsat(self):
        if not self.solver.options.project:
            self.solver.enumerate()


class CheckerController:

    def __init__(self, solver):
        self.solver = solver

    def start(self):
        self.solver.check_errors()


class NonOptimalController:

    def __init__(self, solver):
        self.solver = solver

    def start(self):
        if self.solver.no_optimize():
            # modifying options
            self.solver.options.non_optimal = True
        if self.solver.options.non_optimal:
            import solver as _solver
            self.solver.str_found      = _solver.STR_MODEL_FOUND
            self.solver.str_found_star = _solver.STR_MODEL_FOUND_STAR
            self.solver.add_unsat_to_preference_program()


