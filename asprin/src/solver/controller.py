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

class GeneralController:

    def __init__(self, solver):
        self.improve_limit = True if solver.options.improve_limit is not None \
            else False
        self.solver = solver
        self.bool_set_unsat_program = True

    def start(self):
        solver, options = self.solver, self.solver.options
        if options.trans_ext is not None:
            solver.control.configuration.asp.trans_ext = options.trans_ext
        # store nholds and set holds domain
        if solver.options.max_models != 1:
            solver.store_nholds = True
        if solver.store_nholds:
            solver.set_holds_domain = True
        if solver.set_holds_domain:
            solver.do_set_holds_domain()
        #
        solver.add_encodings()
        solver.ground_preference_base()
        # --dom-heur
        if options.cmd_heuristic is not None:
            solver.ground_cmd_heuristic()
            for _solver in solver.control.configuration.solver:
                _solver.heuristic="Domain"
        # check syntax
        if options.check:
            solver.check_errors()
        # non optimal
        if solver.no_optimize() or solver.options.non_optimal:
            solver.str_found      = utils.STR_MODEL_FOUND
            solver.str_found_star = utils.STR_MODEL_FOUND_STAR
            # solve and finish asprin
            self.solver.solve_single()
            self.solver.end()

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
        # set_unsat_program
        if self.bool_set_unsat_program:
            self.solver.set_unsat_program()
            self.bool_set_unsat_program = False

    def unknown(self):
        if self.solver.last_unsat:
            raise utils.FatalException
        self.solver.print_limit_string()
        self.solver.last_unsat = True # act as if unsat
        if self.solver.options.steps == self.solver.step:
            self.solver.print_steps_message()
            self.solver.end() # to exit asap in this case
        # set_unsat_program
        if self.bool_set_unsat_program:
            self.solver.set_unsat_program()
            self.bool_set_unsat_program = False

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
        self.solver.store_nholds = True

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


class MetaMethodController(MethodController):

    def __init__(self, solver):
        MethodController.__init__(self, solver)
        self.solver = solver
        self.solver.set_holds_domain = True

    def start(self):
        # run meta
        self.solver.meta_simple()
        # finishes asprin
        self.solver.end()


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
        # store nholds
        self.solver.store_nholds = True

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


#
# class OnOptimal
#

# defines (from utils)
HOLDS      = utils.HOLDS
LAST_HOLDS = utils.LAST_HOLDS
LAST_SHOWN = utils.LAST_SHOWN
POS        = utils.POS
NEG        = utils.NEG
SHOWN_ATOM = utils.SHOWN_ATOM
PREF_ATOM  = utils.PREF_ATOM
ON_OPT_HEUR_PROGRAM = utils.ON_OPT_HEUR_PROGRAM

# heuristic and external rules
HEUR_RULE = """
#heuristic ##""" + HOLDS + """(X,0) : not ##""" + LAST_HOLDS + """(X). [#v,#m]
"""
HEUR_EXTERNAL_HOLDS = """
#external ##""" + LAST_HOLDS + """(X) : X = @get_holds_domain().
"""
HEUR_EXTERNAL_SHOWN = """
#external ##""" + LAST_SHOWN + """(X) : X = @get_shown_domain().
"""

#
# Note: Option --on-opt-heur does not change anything while enumerating
#       optimal models with the same preference atoms (OPTIMUM FOUND *)
#

class OnOptimalController:

    def __init__(self, solver):
        self.solver     = solver
        self.grounded   = False
        self.heuristic  = False
        self.pref       = False
        self.shown      = False
        self.shown_rule = ""
        # for on_opt_heur
        if self.solver.options.on_opt_heur:
            self.heuristic = True
            # activate domain heuristic
            for _solver in solver.control.configuration.solver:
                _solver.heuristic="Domain"
            # find PREF_ATOM and SHOWN_ATOM options, and update domain flags
            for sign, atom_type, value, modifier in solver.options.on_opt_heur:
                if atom_type == PREF_ATOM:
                    self.pref = True
                    self.solver.set_holds_domain = True
                elif atom_type == SHOWN_ATOM:
                    self.shown = True
                    self.solver.set_shown_domain = True

    def on(self):
        return self.heuristic

    def create_shown_heuristic_rules(self):
        # gather signatures
        sigs = set()
        for atom in self.solver.shown_domain:
            sigs.add((atom.negative, atom.name, len(atom.arguments)))
        sigs = sorted(list(sigs))
        # for every signature, add heuristics and externals
        for negative, name, arity in sigs:
            atom = ("-" if negative else "") + name
            if arity > 0:
                variables = ",".join(["X" + str(i) for i in range(arity)])
                atom += "(" + variables + ")"
            rule = HEUR_RULE.replace("##" + HOLDS + "(X,0)", atom)
            rule = rule.replace(LAST_HOLDS, LAST_SHOWN)
            rule = rule.replace("(X).", "(" + atom + ").")
            self.shown_rule += rule

    def unsat(self):

        # return if no heuristics
        if not self.heuristic:
            return
        solver = self.solver

        # ground if not grounded
        if not self.grounded:
            self.grounded = True
            # if needed: create shown heuristic rules
            if self.shown == True:
                self.create_shown_heuristic_rules()
            # create heuristic program
            program = ""
            ## iterate over options
            for sign, atom_type, value, modifier in solver.options.on_opt_heur:
                rule = HEUR_RULE
                if atom_type == SHOWN_ATOM:
                    rule = self.shown_rule
                if sign == POS:
                    rule = rule.replace(": not ", ": ")
                rule = rule.replace("#v", value)
                rule = rule.replace("#m", modifier)
                program += rule
            ## add externals
            if self.pref:
                program += HEUR_EXTERNAL_HOLDS
            if self.shown:
                program += HEUR_EXTERNAL_SHOWN
            ## replace ##
            program = program.replace("##", solver.underscores)
            # add and ground it
            solver.add_and_ground(ON_OPT_HEUR_PROGRAM, [], program, [])

        # assign externals
        if self.pref:
            solver.assign_heuristic_externals(
                solver.get_holds_domain(),
                set(solver.get_holds()),
                solver.underscores + LAST_HOLDS
            )
        if self.shown:
            solver.assign_heuristic_externals(
                solver.get_shown_domain(),
                set(solver.get_shown()),
                solver.underscores + LAST_SHOWN
            )
