% asprin test012.lp 0
% SATISFIABLE
1 { a(X) : dom(X) }.
dom(1..3).
{ b(X) } :- a(X).

#show a/1. 
#show b/1.

#preference(p, subset){
  a(X) | b(X) 
}.
#optimize(p).

%asprin version 3.0.0
%Reading from tests/spec_parser/spec_parser/test012.lp
%Solving...
%Answer: 1
%a(3)
%OPTIMUM FOUND
%Answer: 2
%a(3) b(3)
%OPTIMUM FOUND *
%Answer: 3
%a(2)
%OPTIMUM FOUND
%Answer: 4
%a(2) b(2)
%OPTIMUM FOUND *
%Answer: 5
%a(1)
%OPTIMUM FOUND
%Answer: 6
%a(1) b(1)
%OPTIMUM FOUND *
%
%Models       : 6
%  Optimum    : yes
%    Optimal    : 6
%    Calls        : 10
%    Time         : 0.060s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%    CPU Time     : 0.056s
