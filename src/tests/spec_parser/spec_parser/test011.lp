% asprin test011.lp 0 -c type=superset 
% SATISFIABLE
1 { a(X) : dom(X) } 2.
#show a/1.
dom(1..3).

#preference(a(X),type){
  a(X) 
} : dom(X).
#preference(q,pareto){ **a(X) } : dom(X).
#preference(r,neg) { **q }.
#optimize(r).


%asprin version 3.0.0
%Reading from tests/spec_parser/spec_parser/test011.lp
%Solving...
%Answer: 1
%a(3)
%OPTIMUM FOUND
%Answer: 2
%a(2)
%OPTIMUM FOUND
%Answer: 3
%a(1)
%OPTIMUM FOUND
%
%Models       : 3
%  Optimum    : yes
%    Optimal    : 3
%    Calls        : 10
%    Time         : 0.092s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%    CPU Time     : 0.088s
