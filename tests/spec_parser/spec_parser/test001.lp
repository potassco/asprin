% asprin test001.lp
% SATISFIABLE

1 { a(X) : X=1..3 }.
#preference(p,subset){ a(1;2) }.
#optimize(p).

%asprin version 3.0.0
%Reading from spec_parser/spec_parser/test001.lp
%Solving...
%Answer: 1
%a(3)
%OPTIMUM FOUND
%
%Models       : 1
%  Optimum    : yes
%  Calls        : 4
%  Time         : 0.042s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%  CPU Time     : 0.036s
%
