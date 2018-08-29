% asprin test010.lp 0 --const-nb cp_tree=1
% SATISFIABLE
#const n=10.
1 { a(X) : dom(X) } n-1.
dom(1..n).
#show a/1.

#preference(p,cp){
  a(1);
      a(X) ||     a(X-1) : dom(X), X>1;
  not a(X) || not a(X-1) : dom(X), X>1
}.
#optimize(p).


%asprin version 3.1.0
%Reading from asprin/src/tests/asprin_lib/cp/test010.lp
%Solving...
%Answer: 1
%a(3)
%Answer: 2
%a(4) a(5) a(6) a(7) a(8) a(9)
%Answer: 3
%a(1) a(2) a(3) a(4) a(5) a(6) a(7) a(8) a(10)
%Answer: 4
%a(1) a(2) a(3) a(4) a(5) a(6) a(7) a(8)
%Answer: 5
%a(1) a(2) a(3) a(4) a(5) a(6) a(7) a(8) a(9)
%OPTIMUM FOUND
%
%Models       : 5
%  Optimum    : yes
%  Optimal    : 1
%Calls        : 8
%Time         : 0.178s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%CPU Time     : 0.176s
