#script(python)

from src.solver import solver
import logging

def getHolds():
    return solver.holds

def getNHolds():
    return solver.nholds

#end.

#program base.
#show _holds_at_zero(X) : _holds(X,0).

#program _do_holds(_m).
_holds(X,_m) :- X = @getHolds().

#program _openholds(_m).
{ _holds(X,_m) } :- X = @getHolds().
{ _holds(X,_m) } :- X = @getNHolds().

#program _volatile_fact(_m1,_m2).
_volatile(_m1,_m2).

#program _volatile_external(_m1,_m2).
#external _volatile(_m1,_m2).

#program _delete_model.
:- _holds(X,0) : X = @getHolds(); not _holds(X,0) : X = @getNHolds().

#program _unsat(_m1,_m2).
:- not _unsat(_m1,_m2), _volatile(_m1,_m2).

#program _not_unsat(_m1,_m2).
:-     _unsat(_m1,_m2), _volatile(_m1,_m2).


