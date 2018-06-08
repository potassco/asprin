% asprin test003.lp --approximation=heuristic 0 -c subset=superset
% SATISFIABLE

dom(1..3).
1 { a(X) : dom(X) }.
#show a/1.

#preference(p,subset) { 
  a(X)
}.
#optimize(p).

%asprin version 3.0.0.6
%Reading from src/tests/program_parser/basic/test003.lp
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
%  Optimal    : 1
