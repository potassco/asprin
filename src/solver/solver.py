#script (python)

#
# IMPORTS
#

import clingo
import pdb
import controller



#
# LOGGING
#

import logging
#logging.basicConfig(level=logging.INFO)



#
# DEFINES
#

# nodes and control
START         = "START"
START_LOOP    = "START_LOOP"
SOLVE         = "SOLVE"
SAT           = "SAT"
UNSAT         = "UNSAT"
UNKNOWN       = "UNKNOWN"
END_LOOP      = "END_LOOP"
END           = "END"
SATISFIABLE   = "SATISFIABLE"
UNSATISFIABLE = "UNSATISFIABLE"

# strings
OPTIMUM_FOUND = "OPTIMUM FOUND"

# program names
ENCODINGS     = "src/solver/encodings.lp"
DO_HOLDS      = "_do_holds"
PREFERENCE    = "_preference"
NOT_UNSAT_PRG = "_not_unsat"
UNSAT_PRG     =     "_unsat"
VOLATILE_EXT  = "_volatile_external"
VOLATILE_FACT = "_volatile_fact"
DELETE_MODEL  = "_delete_model"

# predicate and term names
VOLATILE      = "_volatile"
HOLDS_AT_ZERO = "_holds_at_zero"


#
# GLOBAL VARIABLES
#

holds, nholds = [], []



#
# Auxiliary Classes (EndException, State)
#

class EndException(Exception):
    pass

class State:
    pass



#
# Solver
#

class Solver:

    def __init__(self,control):
        self.state = State()
        self.solving_result = None
        self.control = control
        self.pre  = dict(START=[],START_LOOP=[],SOLVE=[],SAT=[],UNSAT=[],UNKNOWN=[],END_LOOP=[],END=[])
        self.post = dict(START=[],START_LOOP=[],SOLVE=[],SAT=[],UNSAT=[],UNKNOWN=[],END_LOOP=[],END=[])
        self.shown = []
        self.state.max_models = 1


    #
    # CLINGO PROXY
    #

    def ground_base(self):
        control = self.control
        control.load(ENCODINGS)
        base = [("base",[])]
        control.ground(base)

    def ground_preference_program(self):
        state, control, prev_step = self.state, self.control, self.state.step-1
        control.ground([(DO_HOLDS,       [prev_step]),(PREFERENCE,    [0,prev_step]),
                        (NOT_UNSAT_PRG,[0,prev_step]),(VOLATILE_EXT,[0,prev_step])])
        control.assign_external(clingo.Function(VOLATILE,[0,prev_step]),True)

    def print_optimum_string(self):
        print OPTIMUM_FOUND

    def print_shown(self):
        print "Answer: "
        print '%s' % ' '.join(map(str,self.shown))

    def on_model(self,model):
        global holds, nholds
        holds, nholds, self.shown = [], [], []
        for a in model.symbols(shown=True):
            if (a.name == HOLDS_AT_ZERO): holds.append(a.arguments[0])
            else:                            self.shown.append(a)
        for a in model.symbols(terms=True,complement=True):
            if (a.name == HOLDS_AT_ZERO): nholds.append(a.arguments[0])

    def solve(self):
        control = self.control
        result = control.solve(on_model=self.on_model)
        self.solving_result = None
        if result.satisfiable:     self.solving_result =   SATISFIABLE
        elif result.unsatisfiable: self.solving_result = UNSATISFIABLE

    def relax_previous_model(self):
        state, control = self.state, self.control
        control.release_external(clingo.Function("_volatile",[0,state.step-1]))

    def relax_previous_models(self):
        state, control = self.state, self.control
        for i in range(state.start_step,state.step):
            control.release_external(clingo.Function("_volatile",[0,i]))

    def handle_optimal_models(self):
        state, control, prev_step = self.state, self.control, self.state.step-1
        preference   = [(PREFERENCE,   [prev_step,0])]
        unsat        = [(UNSAT_PRG,    [prev_step,0])]
        delete_model = [(DELETE_MODEL,            [])]
        volatile     = [(VOLATILE_FACT,[prev_step,0])]
        control.ground(preference + unsat + delete_model + volatile)

    def end(self):
        print
        print "Models\t\t: "  + str(self.state.models)
        print "  Optimum\t: " + ("yes" if self.state.opt_models>0 else "no")
        print "  Optimal\t: " + str(self.state.opt_models)
        raise EndException

    #
    # OPTIONS
    #

    def set_options(self,options):
        for key,value in options.items():
            setattr(self.state,key,value)


    #
    # RUN()
    #

    def register_pre(self,node,function):
        self.pre[node].append(function)

    def register_post(self,node,function):
        self.post[node].append(function)

    def action(self,node):
        logging.info("%s",node)
        actions = []
        for i in self.pre[node]:
            ret = i()
            if ret != None: actions += ret
        for i in actions:                    i()
        for i in self.post[node]:            i()

    def run(self):
        controller.GeneralController(self,self.state)
        controller.BasicMethodController(self,self.state)
        try:
            self.action(START)
            print "Solving..."
            while True:
                self.action(START_LOOP)
                self.action(SOLVE)
                logging.info("Solving_result = %s",self.solving_result)
                if   self.solving_result ==   SATISFIABLE: self.action(SAT)
                elif self.solving_result == UNSATISFIABLE: self.action(UNSAT)
                else:                                      self.action(UNKNOWN)
                self.action(END_LOOP)
        except RuntimeError as e: print "ERROR (clingo): " + str(e)
        except EndException as e: self.action(END)


