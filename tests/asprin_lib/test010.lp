% asprin test010.lp 0
% SATISFIABLE

1 { a(X,Y) : dom(X), dom(Y) } 2.
dom(1..2).
#show a/2.

#preference(1,aso){
  a(X,Y), X > Y >> a(X,Y), not X > Y
%  a(X,Y), X > Y >> #false
}.
#optimize(1).

%asprin version 3.0.0
%Reading from tests/asprin_lib/test010.lp
%Solving...
%Answer: 1
%a(1,2)
%Answer: 2
%a(2,1)
%OPTIMUM FOUND
%
%Models       : 2
%  Optimum    : yes
%  Calls        : 5
%  Time         : 0.066s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%  CPU Time     : 0.064s
