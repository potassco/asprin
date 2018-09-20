% asprin test021.lp 0
% SATISFIABLE

1 { a(X,Y) : dom1(X), dom2(Y) }.
dom1(1..2).
dom2(3..4).
#show a/2.

#preference(p,less(weight)) { 1, X, Y :: a(X,Y) }.
#optimize(p).

%asprin version 3.1.0
%Reading from tests/spec_parser/spec_parser/test021.lp
%Solving...
%Answer: 1
%a(1,4)
%OPTIMUM FOUND
%Answer: 2
%a(2,4)
%OPTIMUM FOUND
%Answer: 3
%a(2,3)
%OPTIMUM FOUND
%Answer: 4
%a(1,3)
%OPTIMUM FOUND
%
%Models       : 4
%  Optimum    : yes
%  Optimal    : 4
%Calls        : 13
%Time         : 0.110s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%CPU Time     : 0.108s
