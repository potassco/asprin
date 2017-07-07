% asprin test024.lp 0
% SATISFIABLE

1 { a(X,Y,Z) : __dom(X), __dom(Y), __dom(Z) }.
__dom(1..2).
#show a/3.

_____x.

#preference(p(1),superset){
  a(A,B,C)
}.
#preference(q,neg){
  **p(X)
}.
#optimize(q).

%asprin version 3.0.0
%Reading from tests/spec_parser/spec_parser/test024.lp
%Solving...
%Answer: 1
%a(1,1,2)
%OPTIMUM FOUND
%Answer: 2
%a(1,2,2)
%OPTIMUM FOUND
%Answer: 3
%a(1,1,1) a(2,1,1)
%Answer: 4
%a(1,1,1)
%OPTIMUM FOUND
%Answer: 5
%a(2,1,1)
%OPTIMUM FOUND
%Answer: 6
%a(2,1,2)
%OPTIMUM FOUND
%Answer: 7
%a(1,2,1) a(2,2,1) a(2,2,2)
%Answer: 8
%a(1,2,1) a(2,2,1)
%Answer: 9
%a(1,2,1)
%OPTIMUM FOUND
%Answer: 10
%a(2,2,1) a(2,2,2)
%Answer: 11
%a(2,2,1)
%OPTIMUM FOUND
%Answer: 12
%a(2,2,2)
%OPTIMUM FOUND
%
%Models       : 12
%  Optimum    : yes
%    Optimal    : 8
%    Calls        : 29
%    Time         : 0.113s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%    CPU Time     : 0.112s
