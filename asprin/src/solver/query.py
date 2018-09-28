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


# imports
from ..utils import utils


# defines
SATISFIABLE   = utils.SATISFIABLE
UNSATISFIABLE = utils.UNSATISFIABLE


# Query subclasses Factory
def get_query_class(query, opt):
    if query == 1 and opt:
        return Query_1_opt
    elif query == 1 and not opt:
        return Query_1
    elif query == 2:
        return Query_2


# abstract class
class Query:

    def __init__(self, controller, solver, stop):
        self.solver = solver
        self.controller = controller
        self.stop = stop
        #
        self.state = 0
        self.query_opt_models = 0
        self.query_max_models = solver.options.max_models

    def call(self, pre):
        function = getattr(self, "state_" + str(self.state))
        return function(pre, self.solver.solving_result)
    
    def start(self):
        pass

    def query_opt_model(self):
        self.solver.print_query(True)
        self.query_opt_models += 1
        if self.query_max_models == self.query_opt_models:
            self.solver.bool_end = True
            # general.unsat() finishes asprin

# TODO: Add statistics about number of optimal models where the query holds.
#       Now we print in 'Optimal' the total number of optimal models computed,
#       adding up those with and without the query


class Query_1_opt(Query):

    def __init__(self, controller, solver, stop):
        Query.__init__(self, controller, solver, stop)
        # WARNING: We set solver.options.max_models to 0
        solver.options.max_models = 0

    def start(self):
        self.solver.ground_query_program()

    def state_0(self, pre, result):
        self.solver.set_str_found(optimal=True)
        if pre:
            self.solver.set_query(True)
        elif result == SATISFIABLE:
            self.state = 1
        elif result == UNSATISFIABLE:
            if self.query_opt_models == 0:
                self.solver.print_query(False)
            # general.unsat() finishes asprin

    def state_1(self, pre, result):
        if pre:
            self.solver.set_query(True)
        elif result == SATISFIABLE:
            pass
        elif result == UNSATISFIABLE:
            self.state = 2
            self.solver.solving_result == SATISFIABLE
            # This call must be done with care
            self.controller.solve()

    def state_2_sat(self):
        self.state = 3

    def state_2(self, pre, result):
        if pre:
            self.solver.set_query(False)
        elif result == SATISFIABLE:
            self.state_2_sat()
        elif result == UNSATISFIABLE:
            self.state = 0
            self.query_opt_model() # can finish asprin

    def state_3(self, pre, result):
        if pre:
            self.solver.set_query(False)
        elif result == SATISFIABLE:
            pass
        elif result == UNSATISFIABLE:
            self.state = 0


class Query_1(Query_1_opt):

    def __init__(self, controller, solver, stop):
        Query_1_opt.__init__(self, controller, solver, stop)

    def state_2_sat(self):
        self.state = 4

    def state_4(self, pre, result):
        if pre:
            return True # skip solving
        else:
            # we cheat and say we obtained UNSAT
            self.solver.solving_result = UNSATISFIABLE
            self.state = 0
            self.solver.set_str_found(optimal=False)


class Query_2(Query):
    
    def __init__(self, controller, solver, stop):
        Query.__init__(self, controller, solver, stop)
        self.last_solving_result = self.solver.solving_result
        # WARNING: We set solver.options.max_models to 0
        solver.options.max_models = 0

    def state_0(self, pre, result):
        if pre:
            self.solver.set_query(False)
            self.last_solving_result = self.solver.solving_result
        elif result == SATISFIABLE:
            self.state = 1
        elif result == UNSATISFIABLE:
            self.state = 10
            self.solver.solving_result = self.last_solving_result
            # This call must be done with care
            self.controller.solve()

    def state_10(self, pre, result):
        if pre:
            self.solver.set_query(True)
        elif result == SATISFIABLE:
            if self.stop:
                self.solver.bool_end = True
                self.solver.print_query(True)
                # general.sat() finishes asprin
                return
            self.state = 11
        elif result == UNSATISFIABLE:
            if self.query_opt_models == 0:
                self.solver.print_query(False)
                # general.unsat() finishes asprin

    def state_11(self, pre, result):
        if pre:
            self.solver.set_query(True)
        elif result == SATISFIABLE:
            pass
        elif result == UNSATISFIABLE:
            self.state = 10
            self.query_opt_model() # can finish asprin

    def state_1(self, pre, result):
        if pre:
            self.solver.set_query(False)
        elif result == SATISFIABLE:
            pass
        elif result == UNSATISFIABLE:
            self.state = 2
            self.solver.solving_result == SATISFIABLE
            # This call must be done with care
            self.controller.solve()

    def state_2(self, pre, result):
        if pre:
            self.solver.set_query(True)
        elif result == SATISFIABLE:
            if self.stop:
                self.solver.bool_end = True
                self.solver.print_query(True)
                # general.sat() finishes asprin
                return
            self.state = 3
        elif result == UNSATISFIABLE:
            self.state = 0

    def state_3(self, pre, result):
        if pre:
            self.solver.set_query(True)
        elif result == SATISFIABLE:
            pass
        elif result == UNSATISFIABLE:
            self.state = 0
            self.query_opt_model() # can finish asprin





