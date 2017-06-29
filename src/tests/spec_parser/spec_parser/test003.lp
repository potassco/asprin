% asprin test003.lp 0
% SATISFIABLE

1 { a(X) : dom(X) }.
dom(1..3).
#show a/1.

#preference(p, poset){ not a(X) }.
#optimize(p).

%asprin version 3.0.0
%Reading from tests/spec_parser/spec_parser/test003.lp
%Solving...
%Answer: 1
%a(3)
%OPTIMUM FOUND
%Answer: 2
%a(2)
%OPTIMUM FOUND
%Answer: 3
%a(1)
%OPTIMUM FOUND
%
%Models       : 3
%  Optimum    : yes
%    Optimal    : 3
%    Calls        : 10
%    Time         : 0.063s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%    CPU Time     : 0.060s
%
