% asprin test021.lp 0
% SATISFIABLE

1 { a(X,Y) : dom1(X), dom2(Y) }.
dom1(1..2).
dom2(3..4).
#show a/2.

#minimize { 1@X, X, Y: a(X,Y) }.

%asprin version 3.0.0
%Reading from tests/spec_parser/spec_parser/test021.lp
%Solving...
%Answer: 1
%a(1,4)
%OPTIMUM FOUND
%Answer: 2
%a(1,3)
%OPTIMUM FOUND
%
%Models       : 2
%  Optimum    : yes
%    Optimal    : 2
%    Calls        : 7
%    Time         : 0.080s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%    CPU Time     : 0.076s
%
