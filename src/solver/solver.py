#script (python)

#
# IMPORTS
#

import clingo
import pdb
import controller
import os


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
OPTIMUM_FOUND      = "OPTIMUM FOUND"
OPTIMUM_FOUND_STAR = "OPTIMUM FOUND *"

# program names
#ENCODINGS        = os.path.dirname(os.path.realpath(__file__)) + "/encodings.lp"
SCRIPT           = "script"
DO_HOLDS_AT_ZERO = "do_holds_at_zero"
DO_HOLDS         = "do_holds"
OPEN_HOLDS       = "open_holds"
VOLATILE_FACT    = "volatile_fact"
VOLATILE_EXT     = "volatile_external"
DELETE_MODEL     = "delete_model"
UNSAT_PRG        = "unsat"
NOT_UNSAT_PRG    = "not_unsat"
PREFERENCE       = "preference" #from pp_parser

# predicate and term names
VOLATILE      = "volatile"      #from pp_parser
MODEL         = "m"             #from pp_parser
HOLDS         = "holds"
HOLDS_AT_ZERO = "holds_at_zero"
CSP           = "$"

#
# GLOBAL VARIABLES
#

holds, nholds = [], []


#
# AUXILIARY PROGRAMS
#

script = """
#script(python)
def getHolds():
    return solver.holds
def getNHolds():
    return solver.nholds
#end.
"""

token    = "##"

programs = \
  [(SCRIPT,                 [],script),
   (DO_HOLDS_AT_ZERO,       [],"#show ##holds_at_zero(X) : ##holds(X,0)."),
   (DO_HOLDS,            ["m"],"##holds(X,m) :- X = @getHolds()."),
   (OPEN_HOLDS,          ["m"],"{ ##holds(X,m) } :- X = @getHolds().  { ##holds(X,m) } :- X = @getNHolds()."),
   (VOLATILE_FACT, ["m1","m2"],"##volatile(##m(m1),##m(m2))."),
   (VOLATILE_EXT,  ["m1","m2"],"#external ##volatile(##m(m1),##m(m2))."),
   (DELETE_MODEL,           [],":- ##holds(X,0) : X = @getHolds(); not ##holds(X,0) : X = @getNHolds()."),
   (UNSAT_PRG,     ["m1","m2"],":- not ##unsat(##m(m1),##m(m2)), ##volatile(##m(m1),##m(m2))."),
   (NOT_UNSAT_PRG, ["m1","m2"],":-     ##unsat(##m(m1),##m(m2)), ##volatile(##m(m1),##m(m2)).")
  ]



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

    def __init__(self,control,underscores):
        # parameters
        self.control           = control
        self.underscores       = underscores
        # strings
        self.volatile_str      = underscores + VOLATILE
        self.model_str         = underscores + MODEL
        self.holds_at_zero_str = underscores + HOLDS_AT_ZERO
        self.holds_str         = underscores + HOLDS
        # others
        self.state             = State()
        self.state.max_models  = 1
        self.shown             = []
        self.solving_result    = None
        self.pre  = dict([(START,[]),(START_LOOP,[]),(SOLVE,[]),(SAT,[]),(UNSAT,[]),(UNKNOWN,[]),(END_LOOP,[]),(END,[])])
        self.post = dict([(START,[]),(START_LOOP,[]),(SOLVE,[]),(SAT,[]),(UNSAT,[]),(UNKNOWN,[]),(END_LOOP,[]),(END,[])])

    #
    # AUXILIARY
    #
    def get_volatile(self,m1,m2):
        return clingo.Function(self.volatile_str,[
               clingo.Function(self.model_str,[int(m1)]),
               clingo.Function(self.model_str,[int(m2)])])


    #
    # CLINGO PROXY
    #


    def load_encodings(self):
        for i in programs:
            self.control.add(i[0],i[1],i[2].replace(token,self.underscores))
        self.control.ground([(DO_HOLDS_AT_ZERO,[])])


    def ground_preference_program(self):
        tate, control, prev_step = self.state, self.control, self.state.step-1
        control.ground([(DO_HOLDS,       [prev_step]),(PREFERENCE,    [0,prev_step]),
                        (NOT_UNSAT_PRG,[0,prev_step]),(VOLATILE_EXT,[0,prev_step])])
        control.assign_external(self.get_volatile(0,prev_step),True)


    def on_model(self,model):
        global holds, nholds
        holds, nholds, self.shown = [], [], []
        for a in model.symbols(shown=True):
            if a.name == self.holds_at_zero_str: holds.append(a.arguments[0])
            else:                                self.shown.append(a)
        for a in model.symbols(terms=True,complement=True):
            if a.name == self.holds_at_zero_str: nholds.append(a.arguments[0])


    def solve(self):
        result = self.control.solve(on_model=self.on_model)
        self.solving_result = None
        if result.satisfiable:     self.solving_result =   SATISFIABLE
        elif result.unsatisfiable: self.solving_result = UNSATISFIABLE


    def __symbol2str(self,symbol):
        if symbol.name == CSP:
            return str(symbol.arguments[0]) + "=" + str(symbol.arguments[1])
        return str(symbol)


    def print_shown(self):
        print "Answer: " + str(self.state.models)
        print '%s' % ' '.join(map(self.__symbol2str,self.shown))


    def print_optimum_string(self):
        print OPTIMUM_FOUND


    def check_last_model(self):
        global holds, nholds
        if self.state.old_holds == holds and self.state.old_nholds == nholds:
            raise Exception("same stable model computed twice, there is an error in the input (f.e., an incorrect or missing preference program)")
        self.state.old_holds  =  holds
        self.state.old_nholds = nholds


    def relax_previous_model(self):
        state, control = self.state, self.control
        control.release_external(self.get_volatile(0,state.step-1))


    def same_shown(self):
        if set(self.old_shown) == set(self.shown):
            self.enumerate_flag = True
            return True
        return False


    # used is some atoms not in base are shown
    def same_shown_underscores(self):
        if set([i for i in self.old_shown if not str(i).startswith(self.underscores)]) == \
           set([i for i in     self.shown if not str(i).startswith(self.underscores)]):
            self.enumerate_flag = True
            return True
        return False


    def on_model_enumerate(self,model):
        global holds, nholds
        self.shown = [ i for i in model.symbols(shown=True) if i.name != self.holds_at_zero_str ]
        if self.enumerate_flag or not self.state.same_shown_function():
            self.state.models     += 1
            self.state.opt_models += 1
            self.print_shown()
            print OPTIMUM_FOUND_STAR


    def enumerate(self):
        global holds, nholds
        # models
        control, old_models = self.control, self.control.configuration.solve.models
        if self.state.max_models == 0: control.configuration.solve.models = 0
        else:                          control.configuration.solve.models = self.state.max_models - self.state.opt_models
        # assumptions
        assumptions = [ (clingo.Function(self.holds_str,[x,0]),True)  for x in holds ] + \
                      [ (clingo.Function(self.holds_str,[x,0]),False) for x in nholds]
        # solve
        self.old_shown, self.enumerate_flag = self.shown, False
        control.solve(self.on_model_enumerate,assumptions)
        self.shown = self.old_shown
        control.configuration.solve.models = old_models


    def relax_previous_models(self):
        state, control = self.state, self.control
        for i in range(state.start_step,state.step):
            control.release_external(self.get_volatile(0,i))


    def handle_optimal_models(self):
        state, control, prev_step = self.state, self.control, self.state.step-1
        preference   = [(PREFERENCE,   [prev_step,0])]
        unsat        = [(UNSAT_PRG,    [prev_step,0])]
        delete_model = [(DELETE_MODEL,            [])]
        volatile     = [(VOLATILE_FACT,[prev_step,0])]
        control.ground(preference + unsat + delete_model + volatile)


    def end(self):
        state = self.state
        print
        print "Models\t\t: "  + str(state.models) + ("+" if state.more_models else "")
        print "  Optimum\t: " + ("yes" if state.opt_models>0 else "no")
        print "  Optimal\t: " + str(state.opt_models)
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
        actions = []
        for i in self.pre[node]:
            ret = i()
            if ret != None: actions += ret
        for i in actions:                    i()
        for i in self.post[node]:            i()


    def run(self):

        # controllers
        controller.GeneralController(self,self.state)
        controller.BasicMethodController(self,self.state)
        controller.EnumerationController(self,self.state)
        controller.GeneralControllerHandleOptimal(self,self.state)

        # loop
        try:
            self.action(START)
            print "Solving..."
            while True:
                self.action(START_LOOP)
                self.action(SOLVE)
                if   self.solving_result ==   SATISFIABLE: self.action(SAT)
                elif self.solving_result == UNSATISFIABLE: self.action(UNSAT)
                else:                                      self.action(UNKNOWN)
                self.action(END_LOOP)
        except RuntimeError as e: print "ERROR (clingo): " + str(e)
        except EndException as e: self.action(END)


