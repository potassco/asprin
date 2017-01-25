#script (python)

import solver

class GeneralController:


    def __init__(self,_solver,state):
        self.solver = _solver
        self.state  = state
        self.solver.register_pre(solver.START,self.start_pre)
        self.solver.register_pre(solver.SOLVE,self.solve_pre)
        self.solver.register_pre(solver.SAT,self.sat_pre)
        self.solver.register_pre(solver.UNSAT,self.unsat_pre)
        self.solver.register_post(solver.UNSAT,self.unsat_post)
        self.solver.register_pre(solver.END_LOOP,self.end_loop_pre)
        self.state.step        = 1
        self.state.start_step  = 1
        self.state.last_unsat  = True
        self.state.opt_models  = 0
        self.state.models      = 0
        self.state.more_models = True
        self.state.old_holds   = []
        self.state.old_nholds  = []


    def start_pre(self):
        return [self.solver.load_encodings]


    def solve_pre(self):
        return [self.solver.solve]


    def sat_pre(self):
        self.state.models    += 1
        self.state.last_unsat = False
        return [self.solver.check_last_model,self.solver.print_shown]


    def unsat_pre(self):
        if self.state.last_unsat:
            self.state.more_models = False
            return [self.solver.end]
        self.state.last_unsat = True
        self.state.opt_models  += 1
        out = [self.solver.print_optimum_string]
        if self.state.opt_models == self.state.max_models:
            out.append(self.solver.end)
        if self.state.steps == self.state.step:
            out.append(self.solver.end) # to exit soon
        return out


    def unsat_post(self):
        self.state.start_step = self.state.step+1


    def end_loop_pre(self):
        self.state.step = self.state.step + 1
        if self.state.steps == (self.state.step-1): return [self.solver.end]



class GeneralControllerHandleOptimal:


    def __init__(self,_solver,state):
        self.solver = _solver
        self.solver.register_pre(solver.UNSAT,self.unsat_pre)


    def unsat_pre(self):
        return [self.solver.handle_optimal_models]



class BasicMethodController:


    def __init__(self,_solver,state):
        self.solver = _solver
        self.state  = state
        self.solver.register_pre(solver.START_LOOP,self.start_loop_pre)
        self.solver.register_pre(solver.UNSAT,self.unsat_pre)


    def start_loop_pre(self):
        if self.state.step > self.state.start_step: return [self.solver.ground_preference_program]


    def unsat_pre(self):
        return [self.solver.relax_previous_models]



class EnumerationController:


    def __init__(self,_solver,state):
        self.solver = _solver
        if not state.project:
            state.same_shown_function = _solver.same_shown if not state.show_underscores else _solver.same_shown_underscores
            self.solver.register_pre(solver.UNSAT,self.unsat_pre)


    def unsat_pre(self):
        return [self.solver.enumerate]



