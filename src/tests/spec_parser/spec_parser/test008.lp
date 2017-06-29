% asprin test008.lp 0
% SATISFIABLE

1 { a(X) : dom(X) }.
dom(1..3).
#show a/1.

#preference(p, superset){
  a(X)
}.

#preference(q, subset) {
  a(X)
}.

#preference(r, pareto){ 
  **p; **q
}.
#optimize(r).

%asprin version 3.0.0
%Reading from tests/spec_parser/spec_parser/test008.lp
%Solving...
%Answer: 1
%a(3)
%OPTIMUM FOUND
%Answer: 2
%a(1)
%OPTIMUM FOUND
%Answer: 3
%a(1) a(2)
%OPTIMUM FOUND
%Answer: 4
%a(1) a(2) a(3)
%OPTIMUM FOUND
%Answer: 5
%a(2)
%OPTIMUM FOUND
%Answer: 6
%a(2) a(3)
%OPTIMUM FOUND
%Answer: 7
%a(1) a(3)
%OPTIMUM FOUND
%
%Models       : 7
%  Optimum    : yes
%    Optimal    : 7
%    Calls        : 22
%    Time         : 0.136s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%    CPU Time     : 0.136s
%
