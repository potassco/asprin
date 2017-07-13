% asprin test018.lp 0 -c n=2
% SATISFIABLE

1 { a(X,Y) : dom(Y) } 1 :- dom(X).
dom(1..n).
#show a/2.
:- 2 { a(X,n) }.

#preference(p,maxmin){
  X,Y :: a(X,Y)
}. 
#optimize(p).

%asprin version 3.0.0.4
%Reading from src/tests/asprin_lib/test018.lp
%Solving...
%Answer: 1
%a(1,1) a(2,1)
%OPTIMUM FOUND
%Answer: 2
%a(1,1) a(2,2)
%OPTIMUM FOUND
%Answer: 3
%a(2,1) a(1,2)
%OPTIMUM FOUND
%
%Models       : 3
%  Optimum    : yes
%  Optimal    : 3
%Calls        : 10
%Time         : 0.076s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%CPU Time     : 0.072s
%
