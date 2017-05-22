#script (python)

import solver as solver_module

class GeneralController:


    def __init__(self,solver,state):
        self.solver = solver
        self.state  = state
        self.solver.register_pre(solver_module.START,self.start_pre)
        self.solver.register_pre(solver_module.SOLVE,self.solve_pre)
        self.solver.register_pre(solver_module.SAT,self.sat_pre)
        self.solver.register_pre(solver_module.UNSAT,self.unsat_pre)
        self.solver.register_post(solver_module.UNSAT,self.unsat_post)
        self.solver.register_pre(solver_module.END_LOOP,
                                 self.end_loop_pre)
        self.state.step        = 1
        self.state.start_step  = 1
        self.state.last_unsat  = True
        self.state.opt_models  = 0
        self.state.models      = 0
        self.state.more_models = True
        self.state.old_holds   = None
        self.state.old_nholds  = None


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
            if self.state.models>0:
                out = []
            else:
                out = [self.solver.print_unsat]
            return out + [self.solver.end]
        self.state.last_unsat = True
        self.state.opt_models  += 1
        out = [self.solver.print_optimum_string]
        if self.state.opt_models == self.state.max_models:
            out.append(self.solver.end)
        if self.state.steps == self.state.step:
            out.append(self.solver.end) # to exit asap in this case
        return out


    def unsat_post(self):
        self.state.start_step = self.state.step+1


    def end_loop_pre(self):
        self.state.step = self.state.step + 1
        if self.state.steps == (self.state.step-1): 
            return [self.solver.end]



class GeneralControllerHandleOptimal:


    def __init__(self,solver,state):
        self.solver = solver
        self.solver.register_pre(solver_module.UNSAT,self.unsat_pre)


    def unsat_pre(self):
        return [self.solver.handle_optimal_models]



class BasicMethodController:


    def __init__(self,solver,state):
        self.solver = solver
        self.state  = state
        self.solver.register_pre(solver_module.START_LOOP,
                                 self.start_loop_pre)
        self.solver.register_pre(solver_module.UNSAT,self.unsat_pre)


    def start_loop_pre(self):
        if self.state.step > self.state.start_step: 
            return [self.solver.ground_preference_program]


    def unsat_pre(self):
        return [self.solver.relax_previous_models]



class EnumerationController:


    def __init__(self, solver, state):
        self.solver = solver
        if not state.project:
            if not state.show_underscores:
                state.same_shown_function = solver.same_shown
            else:
                u = solver.same_shown_underscores
                state.same_shown_function = u
            self.solver.register_pre(solver_module.UNSAT,
                                     self.unsat_pre)


    def unsat_pre(self):
        return [self.solver.enumerate]


class CheckerController:

    def __init__(self,solver,state):
        self.solver = solver
        self.state  = state
        self.solver.register_pre(solver_module.START_LOOP,
                                 self.start_loop_pre)

    def start_loop_pre(self):
        if self.state.step == 2:
            return [self.solver.check_errors]
        return []

