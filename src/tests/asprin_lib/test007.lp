% asprin test007.lp 0
% SATISFIABLE

1 { a(X) : dom(X) } 2.
dom(1..3).
#show a/1.

#preference(1,less(weight)){
  1 :: a(X)
}.

#optimize(1).

%asprin version 3.0.0
%Reading from tests/asprin_lib/test007.lp
%Solving...
%Answer: 1
%a(3)
%OPTIMUM FOUND
%Answer: 2
%a(2)
%OPTIMUM FOUND
%Answer: 3
%a(1) a(2)
%OPTIMUM FOUND
%Answer: 4
%a(1)
%OPTIMUM FOUND
%Answer: 5
%a(2) a(3)
%OPTIMUM FOUND
%Answer: 6
%a(1) a(3)
%OPTIMUM FOUND
%
%Models       : 6
%  Optimum    : yes
%    Optimal    : 6
%    Calls        : 19
%    Time         : 0.067s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%    CPU Time     : 0.064s
