% asprin test009.lp 0 -c type=subset 
% SATISFIABLE
1 { a(X) : dom(X) }.
#show a/1.
dom(1..3).

#preference(a(X),type){
  a(X) 
} : dom(X).
#preference(q,pareto){ **a(X) } : dom(X).
#optimize(q).

%asprin version 3.0.0
%Reading from tests/spec_parser/spec_parser/test009.lp
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
%    Time         : 0.080s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%    CPU Time     : 0.076s
