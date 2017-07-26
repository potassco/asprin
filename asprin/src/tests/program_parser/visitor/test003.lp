% asprin test003.lp 0 --heuristic=Domain
% SATISFIABLE

1 { a(X) : dom(X) }.
dom(1..3).
#show a/1.

#preference(p,subset){ a(X) }.
#optimize(p).

#program preference(subset).
#heuristic holds(X) : preference(P,subset), preference(P,_,_,for(X),_). [1,true]


%asprin version 3.0.0.6
%Reading from src/tests/program_parser/visitor/test003.lp
%Solving...
%Answer: 1
%a(1) a(2) a(3)
%Answer: 2
%a(1) a(2)
%Answer: 3
%a(1)
%OPTIMUM FOUND
%Answer: 4
%a(2) a(3)
%Answer: 5
%a(2)
%OPTIMUM FOUND
%Answer: 6
%a(3)
%OPTIMUM FOUND
%
%Models       : 6
%  Optimum    : yes
%  Optimal    : 3
