% asprin test012.lp 0
% SATISFIABLE

1 { a(X) : dom(X) } 2.
dom(1..3).
#show a/1.

#preference(p(1),subset){
  a(X)
}.
#preference(p(2),superset){
  a(X)
} : X=3.
#preference(p(3),superset){
  a(1) & a(2) & not not a(3)
}.
#preference(q,lexico){
  X :: **p(X)
}.
#optimize(q).

%asprin version 3.0.0
%Reading from tests/asprin_lib/test012.lp
%Solving...
%Answer: 1
%a(1) a(2)
%Answer: 2
%a(1)
%Answer: 3
%a(3)
%OPTIMUM FOUND
%
%Models       : 3
%  Optimum    : yes
%  Calls        : 6
%  Time         : 0.075s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%  CPU Time     : 0.072s
