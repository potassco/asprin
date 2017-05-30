% asprin test006.lp 0
% SATISFIABLE

1 { a(X) : dom(X) } 2.
dom(1..3).
#show a/1.

#preference(1,more(cardinality)){
 a(X)
}.

#preference(2,less(cardinality)){
 a(X)
}.

#preference(3,subset){
 a(X)
}.

#preference(4,superset){
 a(X)
}.

#preference(5,aso){
 a(X) >> not a(X)
}.

#preference(6,poset){
  a(X)
}.

#optimize(6).

%asprin version 3.0.0
%Reading from tests/asprin_lib/test006.lp
%Solving...
%Answer: 1
%a(3)
%Answer: 2
%a(2) a(3)
%OPTIMUM FOUND
%Answer: 3
%a(1)
%Answer: 4
%a(1) a(3)
%OPTIMUM FOUND
%Answer: 5
%a(1) a(2)
%OPTIMUM FOUND
%
%Models       : 5
%  Optimum    : yes
%    Optimal    : 3
%    Calls        : 12
%    Time         : 0.182s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%    CPU Time     : 0.176s
