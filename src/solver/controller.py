#script (python)

#from src.solver import solver
import solver
import logging

class GeneralController:

    def __init__(self,_solver,state):
        self.solver = _solver
        self.state  = state
        self.solver.register_pre(solver.START,self.start)
        self.solver.register_pre(solver.SOLVE,self.solve)
        self.solver.register_pre(solver.SAT,self.sat)
        self.solver.register_pre(solver.UNSAT,self.unsat_pre)
        self.solver.register_post(solver.UNSAT,self.unsat_post)
        self.solver.register_pre(solver.END_LOOP,self.end_loop)
        self.state.step       = 1
        self.state.start_step = 1
        self.state.steps      = 0
        self.state.last_unsat = True
        self.state.opt_models = 0
        self.state.models     = 0

    def start(self):
        return [self.solver.ground_base]

    def solve(self):
        return [self.solver.solve]

    def sat(self):
        self.state.models += 1
        self.state.last_unsat = False
        return [self.solver.print_shown]

    def unsat_pre(self):
        if self.state.last_unsat: return [self.solver.end]
        self.state.last_unsat = True
        self.state.opt_models  += 1
        out = [self.solver.print_optimum_string]
        if self.state.max_models == self.state.opt_models:
            out.append(self.solver.end)
        out.append(self.solver.handle_optimal_models)
        return out

    def unsat_post(self):
        self.state.start_step = self.state.step+1

    def end_loop(self):
        state = self.state
        state.step = state.step + 1
        if state.steps == state.step: return [self.solver.end]


class BasicMethodController:

    def __init__(self,_solver,state):
        self.solver = _solver
        self.state  = state
        self.solver.register_pre(solver.START_LOOP,self.start_loop)
        self.solver.register_pre(solver.UNSAT,self.unsat_pre)

    def start_loop(self):
        if self.state.step > self.state.start_step: return [self.solver.ground_preference_program]

    def unsat_pre(self):
        logging.info("BasicMethodController unsat_pre")
        return [self.solver.relax_previous_models]
