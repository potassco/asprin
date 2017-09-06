% asprin test026.lp 0 -c x=0 --const-nb y=0 \-\-no-asprin-lib
% SATISFIABLE

{ a(X) : dom(X) } :- x=0, y!=0.
dom(1..3).
#show a/1.

#preference(p,t){}.
#optimize(p).

#program preference(t).
:- y=0.
#program approximation(t).
#program heuristic(t).


%asprin version 3.0.0.6
%Reading from src/tests/spec_parser/spec_parser/test026.lp
%Solving...
%Answer: 1
%
%OPTIMUM FOUND
%Answer: 2
%a(2)
%OPTIMUM FOUND *
%Answer: 3
%a(3)
%OPTIMUM FOUND *
%Answer: 4
%a(2) a(3)
%OPTIMUM FOUND *
%Answer: 5
%a(1)
%OPTIMUM FOUND *
%Answer: 6
%a(1) a(3)
%OPTIMUM FOUND *
%Answer: 7
%a(1) a(2)
%OPTIMUM FOUND *
%Answer: 8
%a(1) a(2) a(3)
%OPTIMUM FOUND *
%
%Models       : 8
%  Optimum    : yes
%  Optimal    : 8
