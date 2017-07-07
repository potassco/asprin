% asprin test002.lp  0
% SATISFIABLE

1 { a(X) : X=1..3 }.
#preference(p,subset){ a(1;2); a(3) & a(3) }.
#optimize(p).

%asprin version 3.0.0
%Reading from tests/spec_parser/spec_parser/test002.lp
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
%    Time         : 0.055s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%    CPU Time     : 0.052s
%
