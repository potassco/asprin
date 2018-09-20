% asprin test028.lp 0
% SATISFIABLE

dom(1..3).
1 { a(X) : dom(X) }.
#show a/1.
b(3).

#optimize(p).
#preference(p,subset){ a(X); not a(X) }.

%
% OLD:
% not does not work as expected, this is interpreted as:
%#minimize{ 1,X : a(X), not b(X), dom(a(X)), dom(b(X)) }.
%dom(a(1..3)).
%dom(b(3)).
%


%asprin version 3.1.0
%Reading from tests/spec_parser/spec_parser/test028.lp
%Solving...
%Answer: 1
%a(3)
%OPTIMUM FOUND
%Answer: 2
%a(2)
%OPTIMUM FOUND
%Answer: 3
%a(1) a(2)
%OPTIMUM FOUND
%Answer: 4
%a(1) a(2) a(3)
%OPTIMUM FOUND
%Answer: 5
%a(2) a(3)
%OPTIMUM FOUND
%Answer: 6
%a(1)
%OPTIMUM FOUND
%Answer: 7
%a(1) a(3)
%OPTIMUM FOUND
%
%Models       : 7
%  Optimum    : yes
%  Optimal    : 7
%Calls        : 22
%Time         : 0.129s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%CPU Time     : 0.136s
