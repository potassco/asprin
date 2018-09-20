% asprin test006.lp --const-nb cp_tree=1 --const-nb cp_tree_encoding=2 0 --meta=no
% SATISFIABLE

1 { a(X,Y) : dom(X), dom(Y) } 2.
dom(1..2).
#show a/2.

#preference(1,cp){
  a(1,Y)                   : dom(Y);
      a(2,Y) ||     a(1,Y) : dom(Y);
  not a(2,Y) || not a(1,Y) : dom(Y)
}.
#optimize(1).

%asprin version 3.1.0
%Reading from test004.lp
%Solving...
%Answer: 1
%a(1,2)
%Answer: 2
%a(1,2) a(2,2)
%OPTIMUM FOUND
%Answer: 3
%a(1,1) a(2,1)
%OPTIMUM FOUND
%Answer: 4
%a(1,1) a(1,2)
%OPTIMUM FOUND
%
%Models       : 4
%  Optimum    : yes
%  Optimal    : 3
%Calls        : 11
%Time         : 0.176s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%CPU Time     : 0.176s
