% asprin test002.lp --approximation=heuristic 0
% SATISFIABLE

dom(1..3).
1 { a(X) : dom(X) }.
#show a/1.

#preference(p,subset) { 
  a(X)
}.
#optimize(p).

%asprin version 3.0.0.6
%Reading from src/tests/program_parser/basic/test002.lp
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
%  Optimal    : 3
