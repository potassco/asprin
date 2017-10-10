% asprin test027.lp 0
% SATISFIABLE

dom(1..3).
1 { a(X) : dom(X) }.
#show a/1.

#preference(p,subset){
  a(X) : dom(X), not X=1
}.
#optimize(p).

%asprin version 3.0.1
%Reading from src/tests/spec_parser/spec_parser/test027.lp
%Solving...
%Answer: 1
%a(3)
%Answer: 2
%a(1)
%OPTIMUM FOUND
%
%Models       : 2
%  Optimum    : yes
%  Optimal    : 1
