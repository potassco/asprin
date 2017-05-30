% asprin test019.lp 0
% SATISFIABLE

1 { a(X) : dom(X) }.
dom(1..3).
#show a/1.

#preference(p,subset){ not not not a(X) }.
#optimize(p).

%asprin version 3.0.0
%Reading from tests/spec_parser/spec_parser/test019.lp
%Solving...
%Answer: 1
%a(3)
%Answer: 2
%a(2) a(3)
%Answer: 3
%a(1) a(2) a(3)
%OPTIMUM FOUND
%
%Models       : 3
%  Optimum    : yes
%  Calls        : 6
%  Time         : 0.056s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%  CPU Time     : 0.056s
