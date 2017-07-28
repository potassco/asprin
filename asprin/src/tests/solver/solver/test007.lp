% asprin test007.lp --total-order 0
% SATISFIABLE
1 { a(X) : dom(X) }.
dom(1..5).
#show a/1.

#preference(p,less(cardinality)){ a(X) }.
#optimize(p).

%asprin version 3.0.0.6
%Reading from src/tests/solver/solver/test007.lp
%Solving...
%Answer: 1
%a(3)
%OPTIMUM FOUND
%Answer: 2
%a(4)
%OPTIMUM FOUND
%Answer: 3
%a(5)
%OPTIMUM FOUND
%Answer: 4
%a(1)
%OPTIMUM FOUND
%Answer: 5
%a(2)
%OPTIMUM FOUND
%
%Models       : 5
%  Optimum    : yes
%  Optimal    : 5
