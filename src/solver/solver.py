#script (python)

#
# IMPORTS
#

from __future__ import print_function
import clingo
import pdb
import controller
from src.utils import printer
import os
import sys

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
STR_OPTIMUM_FOUND      = "OPTIMUM FOUND"
STR_OPTIMUM_FOUND_STAR = "OPTIMUM FOUND *"
STR_UNSATISFIABLE      = "UNSATISFIABLE"

# program names
#ENCODINGS        = os.path.dirname(os.path.realpath(__file__)) + "/encodings.lp"
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

# exceptions
SAME_MODEL = "same stable model computed twice, there is an error in the input (f.e., an incorrect or missing preference program)"

#
# AUXILIARY PROGRAMS
#

token    = "##"
programs = \
  [(DO_HOLDS_AT_ZERO,       [],"""
#show ##holds_at_zero(X) : ##holds(X,0)."""),
   (DO_HOLDS,            ["m"],"""
##holds(X,m) :- X = @getHolds()."""),
   (OPEN_HOLDS,          ["m"],"""
{ ##holds(X,m) } :- X = @getHolds().  
{ ##holds(X,m) } :- X = @getNHolds()."""),
   (VOLATILE_FACT, ["m1","m2"],"""
##volatile(##m(m1),##m(m2))."""),
   (VOLATILE_EXT,  ["m1","m2"],"""
#external ##volatile(##m(m1),##m(m2))."""),
   (DELETE_MODEL,           [],"""
:- ##holds(X,0) : X = @getHolds(); not ##holds(X,0) : X = @getNHolds()."""),
   (UNSAT_PRG,     ["m1","m2"],"""
:- not ##unsat(##m(m1),##m(m2)), ##volatile(##m(m1),##m(m2))."""),
   (NOT_UNSAT_PRG, ["m1","m2"],"""
:-     ##unsat(##m(m1),##m(m2)), ##volatile(##m(m1),##m(m2)).""")
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
        # holds
        self.holds             = []
        self.nholds            = []
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

    def getHolds(self):
        return self.holds
    
    def getNHolds(self):
        return self.nholds

    def head(atuple):
        try:
            return atuple.arguments[0]
        except:
            return atuple

    def __cat(self, tuple):
        if tuple.arguments:
            return "".join([str(i) for i in tuple.arguments]).replace('"',"")
        else:
            return str(tuple)

    #
    # CLINGO PROXY
    #


    def load_encodings(self):
        for i in programs:
            self.control.add(i[0],i[1],i[2].replace(token,self.underscores))
        self.control.ground([(DO_HOLDS_AT_ZERO,[])],self)


    def ground_preference_program(self):
        state, control, prev_step = self.state, self.control, self.state.step-1
        control.ground([(DO_HOLDS,       [prev_step]),
                        (PREFERENCE,     [0,prev_step]),
                        (NOT_UNSAT_PRG,  [0,prev_step]),
                        (VOLATILE_EXT,   [0,prev_step])],self)
        control.assign_external(self.get_volatile(0,prev_step),True)

    #TODO: move to pp_parser when translation improved
    def check_errors(self):
        # get preference program errors
        pr, control, u = printer.Printer(), self.control, self.underscores
        for atom in control.symbolic_atoms.by_signature(u+"_error", 3):
            string = "\nerror: " + self.__cat(atom.symbol.arguments[0]) + "\n"
            pr.print_spec_error(string)
            raise Exception("parsing failed")

    def on_model(self,model):
        self.holds, self.nholds, self.shown = [], [], []
        for a in model.symbols(shown=True):
            if a.name == self.holds_at_zero_str: 
                self.holds.append(a.arguments[0])
            else:
                self.shown.append(a)
        #TODO: improve on nholds, we do not need it always
        for a in model.symbols(terms=True,complement=True):
            if a.name == self.holds_at_zero_str: 
                self.nholds.append(a.arguments[0])


    def solve(self):
        result = self.control.solve(on_model=self.on_model)
        self.solving_result = None
        if result.satisfiable:
            self.solving_result = SATISFIABLE
        elif result.unsatisfiable:
            self.solving_result = UNSATISFIABLE


    def __symbol2str(self,symbol):
        if symbol.name == CSP:
            return str(symbol.arguments[0]) + "=" + str(symbol.arguments[1])
        return str(symbol)


    def print_shown(self):
        print("Answer: {}".format(self.state.models))
        print(" ".join(map(self.__symbol2str,self.shown)))


    def print_optimum_string(self):
        print(STR_OPTIMUM_FOUND)


    def print_unsat(self):
        print(STR_UNSATISFIABLE)


    def check_last_model(self):
        if self.state.old_holds == self.holds and (
           self.state.old_nholds == self.nholds):
                raise Exception(SAME_MODEL)
        self.state.old_holds  = self.holds
        self.state.old_nholds = self.nholds


    def relax_previous_model(self):
        state, control = self.state, self.control
        control.release_external(self.get_volatile(0,state.step-1))


    def same_shown(self):
        if set(self.old_shown) == set(self.shown):
            self.enumerate_flag = True
            return True
        return False


    def same_shown_underscores(self):
        u = self.underscores
        s1 = set([i for i in self.old_shown if not str(i).startswith(u)])
        s2 = set([i for i in     self.shown if not str(i).startswith(u)])
        if s1 == s2:
            self.enumerate_flag = True
            return True
        return False


    def on_model_enumerate(self,model):
        true = model.symbols(shown=True)
        self.shown = [ i for i in true if i.name != self.holds_at_zero_str ]
        # self.state.same_shown_function is modified by EnumerationController 
        # at controller.py
        if self.enumerate_flag or not self.state.same_shown_function():
            self.state.models     += 1
            self.state.opt_models += 1
            self.print_shown()
            print(STR_OPTIMUM_FOUND_STAR)


    def enumerate(self):
        # models
        control    = self.control
        old_models = self.control.configuration.solve.models
        if self.state.max_models == 0: 
            control.configuration.solve.models = 0
        else:
            control.configuration.solve.models = (self.state.max_models -                                                         self.state.opt_models)
        # assumptions
        h = self.holds_str
        ass  = [ (clingo.Function(h, [x,0]), True)  for x in self.holds ]
        ass += [ (clingo.Function(h, [x,0]), False) for x in self.nholds]
        # solve
        self.old_shown, self.enumerate_flag = self.shown, False
        control.solve(ass, self.on_model_enumerate)
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
        control.ground(preference + unsat + delete_model + volatile,self)


    def end(self):
        state, p = self.state, printer.Printer()
        p.print_stats(self.control, state.models, state.more_models,
                      state.opt_models,state.stats)
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

    # pre functions modify the state, and return a list of solver methods
    def register_pre(self,node,function):
        self.pre[node].append(function)


    # post functions modify the state
    def register_post(self,node,function):
        self.post[node].append(function)


    def action(self,node):
        actions = []
        for i in self.pre[node]:
            ret = i()
            if ret != None: actions += ret
        for i in actions:
            #print(i)
            i()
        for i in self.post[node]:
            i()


    def run(self):

        # controllers
        controller.GeneralController(self, self.state)
        controller.BasicMethodController(self, self.state)
        controller.EnumerationController(self, self.state)
        controller.GeneralControllerHandleOptimal(self, self.state)
        controller.CheckerController(self, self.state)

        for node in {START_LOOP}:
            for i in self.post[node]:
                print(i)

        # loop
        try:
            self.action(START)
            print("Solving...")
            while True:
                self.action(START_LOOP)
                self.action(SOLVE)
                if   self.solving_result ==   SATISFIABLE: self.action(SAT)
                elif self.solving_result == UNSATISFIABLE: self.action(UNSAT)
                else:                                      self.action(UNKNOWN)
                self.action(END_LOOP)
        except RuntimeError as e: print("ERROR (clingo): {}".format(e))
        except EndException as e: self.action(END)


