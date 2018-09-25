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

class Query:

    def __init__(self, controller, solver):
        self.solver = solver
        self.controller = controller
        self.state = 0

    def call(self, pre):
        function = getattr(self, "state_" + str(self.state))
        function(pre, self.solver.solving_result)

class Query0:

    def __init__(self, controller, solver):
        Query.__init__(self, controller, solver)

    def state_0(self, pre, result):
        if pre:
            self.solver.set_query(True)
        elif result == SATISFIABLE:
            self.state = 1
        elif result == UNSATISFIABLE:
            self.solver.print_query_false()
            # finishes asprin

    def state_1(self, pre, result):
        if pre:
            self.solver.set_query(True)
        elif result == SATISFIABLE:
            pass
        elif result == UNSATISFIABLE:
            self.state = 2
            self.solver.solving_result == SATISFIABLE
            self.controller.solve()

    def state_2(self, pre, result):
        if pre:
            self.solver.set_query(False)
        elif result == SATISFIABLE:
            self.state = 3
        elif result == UNSATISFIABLE:
            self.solver.print_query_true()
            # Finish asprin: TODO: Fix
            self.solver.end()
    
    def state_3(self, pre, result):
        if pre:
            self.solver.set_query(False)
        elif result == SATISFIABLE:
            pass
        elif result == UNSATISFIABLE:
            self.state = 0

