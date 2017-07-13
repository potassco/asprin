% asprin test008.lp 0
% SATISFIABLE

1 { a(X) : dom(X) } 2.
dom(1..3).
#show a/1.

#preference(1,less(weight)){
  1,X :: a(X)
}.

#optimize(1).

%asprin version 3.0.0
%Reading from tests/asprin_lib/test008.lp
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
%  Optimal    : 3
%Calls        : 10
%Time         : 0.056s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%CPU Time     : 0.056s
