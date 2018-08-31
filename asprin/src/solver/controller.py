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

from ..utils import utils
import clingo

class GeneralController:

    def __init__(self, solver):
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
        # check syntax
        if options.check:
            solver.check_errors()
        # non optimal
        if solver.no_optimize():
            # modifying options
            solver.options.non_optimal = True
        if solver.options.non_optimal:
            solver.str_found      = utils.STR_MODEL_FOUND
            solver.str_found_star = utils.STR_MODEL_FOUND_STAR
            solver.add_unsat_to_preference_program()


    def sat(self):
        self.solver.models     += 1
        self.solver.last_unsat  = False
        self.solver.last_model  = self.solver.step
        self.solver.check_last_model()
        if self.solver.options.quiet == 0:
            self.solver.print_answer()
        else:
            self.solver.print_str_answer()

    def unsat(self):
        if self.solver.last_unsat:
            self.solver.more_models = False
            if self.solver.models == 0:
                self.solver.print_unsat()
            elif self.improve_limit:
                self.solver.enumerate_unknown()
            self.solver.end()
        if self.solver.options.quiet == 1:
            self.solver.print_shown()
        self.solver.last_unsat = True
        self.solver.opt_models  += 1
        self.solver.print_optimum_string()
        if self.solver.opt_models == self.solver.options.max_models:
            self.solver.end()
        if self.solver.options.steps == self.solver.step:
            self.solver.print_steps_message()
            self.solver.end() # to exit asap in this case

    def unknown(self):
        if self.solver.last_unsat:
            raise utils.FatalException
        self.solver.print_limit_string()
        self.solver.last_unsat = True # act as if unsat
        if self.solver.options.steps == self.solver.step:
            self.solver.print_steps_message()
            self.solver.end() # to exit asap in this case

    def end_loop(self):
        self.solver.step = self.solver.step + 1
        if self.solver.options.steps == (self.solver.step - 1):
            self.solver.print_steps_message()
            self.solver.end()
        if self.solver.options.clean_up:
            self.solver.clean_up()


class GeneralControllerHandleOptimal:

    def __init__(self, solver):
        self.solver = solver
        self.start_step = True
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
        if self.no_opt_improving and self.start_step:
            self.solver.relax_optimal_models()
        self.start_step = False

    def __preprocess(self):
        if self.total_order and not self.first:
            self.delete_worse  = False
            self.delete_better = False
        self.first = False

    def unsat(self):
        self.start_step = True
        self.__preprocess()
        self.solver.handle_optimal_model(self.solver.last_model,
                                         False,
                                         self.delete_worse,
                                         self.delete_better,
                                         self.volatile)

    def unknown(self):
        self.start_step = True
        self.__preprocess()
        self.solver.handle_optimal_model(self.solver.last_model,
                                         True,
                                         self.delete_worse,
                                         False,
                                         True)


class EnumerationController:

    def __init__(self, solver):
        self.solver = solver
        # show_underscores is set by program_parser.py
        if not solver.options.project and not solver.options.show_underscores:
            solver.same_shown_function = solver.same_shown

    def unsat(self):
        if not self.solver.options.project:
            self.solver.enumerate()
            if self.solver.opt_models == self.solver.options.max_models:
                self.solver.end()


#
# Method Controllers
#

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
        self.ground_holds = 0
        if (self.solver.options.max_models != 1 or
            self.solver.options.release_last or 
            self.solver.options.volatile_improving):
            self.volatile = True 

    def start_loop(self):
        if not self.solver.last_unsat:
            self.solver.ground_holds(self.solver.last_model)
            self.ground_holds = self.solver.last_model
            self.solver.ground_preference_program(self.volatile)

    def solve(self):
        self.solver.solve(
            assumptions=self.solver.assumptions,
            on_model=self.solver.on_model
        )

    def unsat(self):
        self.solver.relax_previous_models()
        if self.ground_holds != self.solver.last_model:
            self.solver.ground_holds(self.solver.last_model)


class GroundOnceMethodController(MethodController):

    def __init__(self, solver):
        MethodController.__init__(self, solver)
        solver.store_nholds = True

    def start(self):
        self.solver.ground_open_preference_program()
        self.solver.turn_off_preference_program()

    def start_loop(self):
        if not self.solver.last_unsat:
            self.solver.turn_on_preference_program()

    def solve(self):
        self.solver.solve(
            assumptions=self.solver.assumptions,
            on_model=self.solver.on_model
        )

    def unsat(self):
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

    def solve(self):
        if self.solver.last_unsat:
            self.solver.solve_heuristic()
        else:
            self.solver.solve_unsat()

    def unsat(self):
        self.solver.ground_holds(self.solver.last_model)


class ImproveLimitController(MethodController):

    def __init__(self, solver, controller):
        MethodController.__init__(self, solver)
        self.solver     = solver
        self.controller = controller
        self.option     = self.solver.options.improve_limit
        self.stats      = solver.control.statistics['solving']['solvers']
        self.conf       = solver.control.configuration.solve
        self.search     = 0
        # limits
        self.previous_limit, self.limit = "", 0

    def start(self):
        self.controller.start()
        self.solver.ground_holds_delete_better()

    def start_loop(self):
        # get previous limit, and set limit
        self.previous_limit = self.conf.solve_limit
        if not self.solver.last_unsat:
            self.limit = (1 if self.search==0 else self.search) * self.option[0]
            if self.limit < self.option[2]:
                self.limit = self.option[2]
            self.conf.solve_limit = str(self.limit) + ",umax"
            if self.limit == 0: # if limit is 0, return
                return
        # call controller
        self.controller.start_loop()

    def solve(self):
        # if improving and limit is 0, return unknown
        if not self.solver.last_unsat and self.limit == 0:
            self.solver.solve_unknown()
        else:
            self.controller.solve()
        # reset previous limit
        self.conf.solve_limit = self.previous_limit
        # gather search results
        if self.solver.solving_result == utils.SATISFIABLE:
            if self.solver.last_unsat:
                self.search  = int(self.stats['conflicts'])
            elif self.option[1]:
                self.search += int(self.stats['conflicts'])

    def unsat(self):
        result = self.solver.solving_result
        self.controller.unsat()
        self.solver.handle_unknown_models(result)

HOLDS      = utils.HOLDS
LAST_HOLDS = utils.LAST_HOLDS
POS        = utils.POS
NEG        = utils.NEG
SHOWN_ATOM = utils.SHOWN_ATOM
PREF_ATOM  = utils.PREF_ATOM
ON_OPT_HEUR_PROGRAM = utils.ON_OPT_HEUR_PROGRAM

ON_OPT_HEUR_RULE = """
#heuristic ##""" + HOLDS + """(X,0) : not ##""" + LAST_HOLDS + """(X). [#v,#m]
"""

ON_OPT_HEUR_EXTERNAL = """
#external ##""" + LAST_HOLDS + """(X) : X = @get_holds_domain().
%#show ##""" + LAST_HOLDS + """/1.
"""


# DONE: TODO: Activate Heuristic
# TODO: Add shown case
# TODO: Move to solver
# TODO: Test
# TODO: Add to weak and heuristic modes
# Do I always get the get_holds_domain()?
# Can I get the previous optimal model? (to simplify the final loop)

class OnOptimal:

    def __init__(self, solver):
        self.solver       = solver
        self.grounded     = False
        self.heuristic    = False
        self.external_name = solver.underscores + LAST_HOLDS
        if self.solver.options.on_opt_heur:
            self.heuristic = True
            for _solver in solver.control.configuration.solver:
                _solver.heuristic="Domain"

    def start_loop(self):
        solver = self.solver
        # return if no heuristics, or not unsat, or first step
        if not self.heuristic or not solver.last_unsat or solver.step == 1:
            return
        # ground if not grounded
        if not self.grounded:
            self.grounded = True
            # create heuristic program
            program = ""
            for sign, atom_type, value, modifier in solver.options.on_opt_heur:
                rule = ON_OPT_HEUR_RULE
                if sign == POS:
                    rule = rule.replace(": not ", ": ")
                rule = rule.replace("#v", value)
                rule = rule.replace("#m", modifier)
                program += rule
            program += ON_OPT_HEUR_EXTERNAL
            program = program.replace("##", solver.underscores)
            # add and ground it
            solver.add_and_ground(ON_OPT_HEUR_PROGRAM, [], program, [])
        # MOVE THIS TO SOLVER
        # assign externals
        holds_domain = solver.get_holds_domain()
        holds = set(solver.get_holds())
        # note: other options could be tried for this loop
        for i in holds_domain:
            external = clingo.Function(self.external_name, [i])
            if i in holds:
                solver.control.assign_external(external, True)
            else:
                solver.control.assign_external(external, False)

