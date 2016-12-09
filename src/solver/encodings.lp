#script(python)

from src.solver import solver
import logging

def getHolds():
    return solver.holds

def getNHolds():
    return solver.nholds

#end.

#program do_holds_at_zero.
#show ##holds_at_zero(X) : ##holds(X,0).

#program do_holds(m).
##holds(X,m) :- X = @getHolds().

#program openholds(m).
{ ##holds(X,m) } :- X = @getHolds().
{ ##holds(X,m) } :- X = @getNHolds().

#program volatile_fact(m1,m2).
##volatile(##m(m1),##m(m2)).

#program volatile_external(m1,m2).
#external ##volatile(##m(m1),##m(m2)).

#program delete_model.
:- ##holds(X,0) : X = @getHolds(); not ##holds(X,0) : X = @getNHolds().

#program unsat(m1,m2).
:- not ##unsat(##m(m1),##m(m2)), ##volatile(##m(m1),##m(m2)).

#program not_unsat(m1,m2).
:-     ##unsat(##m(m1),##m(m2)), ##volatile(##m(m1),##m(m2)).


