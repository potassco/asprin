% asprin test019.lp 0 -c n=3
% SATISFIABLE

1 { a(X,Y) : dom(Y) } 1 :- dom(X).
dom(1..n).
#show a/2.
:- 2 { a(X,1) }.

#preference(p,minmax){
  X,Y :: a(X,Y)
}. 
#optimize(p).

%asprin version 3.0.0
%Reading from src/tests/asprin_lib/test019.lp
%Solving...
%Answer: 1
%a(2,2) a(1,3) a(3,3)
%Answer: 2
%a(1,2) a(2,2) a(3,2)
%OPTIMUM FOUND
%Answer: 3
%a(1,1) a(2,2) a(3,2)
%OPTIMUM FOUND
%Answer: 4
%a(3,1) a(1,2) a(2,2)
%OPTIMUM FOUND
%Answer: 5
%a(2,1) a(1,2) a(3,2)
%OPTIMUM FOUND
%
%Models       : 5
%  Optimum    : yes
%  Optimal    : 4
%Calls        : 14
%Time         : 0.084s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%CPU Time     : 0.080s
