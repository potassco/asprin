% asprin test028.lp 0 --minimize
% SATISFIABLE

dom(1..3).
1 { a(X) : dom(X) }.
#show a/1.
b(3).

#minimize{ 1,X : a(X), not b(X) }.

%
% not does not work as expected, this is interpreted as:
%#minimize{ 1,X : a(X), not b(X), dom(a(X)), dom(b(X)) }.
%dom(a(1..3)).
%dom(b(3)).
%

%asprin version 3.0.2
%Reading from src/tests/spec_parser/spec_parser/test028.lp
%Solving...
%Answer: 1
%a(3)
%OPTIMUM FOUND
%Answer: 2
%a(2)
%OPTIMUM FOUND *
%Answer: 3
%a(2) a(3)
%OPTIMUM FOUND *
%Answer: 4
%a(1)
%OPTIMUM FOUND *
%Answer: 5
%a(1) a(2)
%OPTIMUM FOUND *
%Answer: 6
%a(1) a(3)
%OPTIMUM FOUND *
%Answer: 7
%a(1) a(2) a(3)
%OPTIMUM FOUND *
%
%Models       : 7
%  Optimum    : yes
%  Optimal    : 7
%
