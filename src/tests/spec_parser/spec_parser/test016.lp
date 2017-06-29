% asprin test016.lp 0
% SATISFIABLE

1 { a(X) : dom(X) }.
dom(1..3).
#show a/1.

#preference(|-1;-2|,subset) { a(X) }.
#preference(3, neg) { **2 }.
#optimize(3).

%asprin version 3.0.0
%Reading from tests/spec_parser/spec_parser/test016.lp
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
%  Time         : 0.064s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%  CPU Time     : 0.060s
