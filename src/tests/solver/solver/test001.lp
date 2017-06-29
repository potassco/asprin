% asprin test001.lp 0 --project
% SATISFIABLE

1 { a(X) : dom(X) }.
dom(1..4). 
#show a/1.
{ b(X,Y,Z) : dom(X), dom(Y), dom(Z) }.

#preference(p, subset){
  a(C)
}.

#optimize(p).

%asprin version 3.0.0
%Reading from tests/solver/solver/test001.lp
%Solving...
%Answer: 1
%a(3)
%OPTIMUM FOUND
%Answer: 2
%a(4)
%OPTIMUM FOUND
%Answer: 3
%a(1) a(2)
%Answer: 4
%a(1)
%OPTIMUM FOUND
%Answer: 5
%a(2)
%OPTIMUM FOUND
%
%Models       : 5
%  Optimum    : yes
%    Optimal    : 4
%    Calls        : 10
%    Time         : 0.071s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%    CPU Time     : 0.068s
