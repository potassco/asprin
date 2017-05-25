class GeneralController:

    def __init__(self, solver, state):
        self.solver            = solver
        self.state             = state
        self.state.step        = 1
        self.state.start_step  = 1
        self.state.last_unsat  = True
        self.state.opt_models  = 0
        self.state.models      = 0
        self.state.more_models = True
        self.state.old_holds   = None
        self.state.old_nholds  = None

    def start(self):
        self.solver.load_encodings()

    def solve(self):
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

    def start_loop(self):
        if self.state.step > self.state.start_step: 
            self.solver.ground_preference_program()

    def unsat(self):
        self.solver.relax_previous_models()


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
        self.state  = state

    def start_loop(self):
        if self.state.step == 2:
            self.solver.check_errors()

