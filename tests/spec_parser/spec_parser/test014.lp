% asprin test014.lp 0
% SATISFIABLE
1 { a(X) : dom(X) }.
dom(1..3).
{ b(X) } :- a(X).

#show a/1. 
#show b/1.

#preference(p, subset){
  (not (a(X) &  b(X))) | a(1)
}.
#optimize(p).

%asprin version 3.0.0
%Reading from tests/spec_parser/spec_parser/test014.lp
%Solving...
%Answer: 1
%a(2) a(3) b(2) b(3)
%OPTIMUM FOUND
%
%Models       : 1
%  Optimum    : yes
%  Calls        : 4
%  Time         : 0.057s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%  CPU Time     : 0.052s
%
