% asprin test009.lp -c n=10 --solving-mode=approx 0  --project
% SATISFIABLE
1 { a(1..n) }.
a(X,Y) :- a(X), Y=1..X.
{ b(X,0) } :- a(X).
%{ b(X,a(1..10)) } :- b(X,0).
#preference(p,subset){
  a(X,Y)
}.
#optimize(p).
#show a/1.
%#show b/2.


%asprin version 3.0.0.6
%Reading from src/tests/solver/solver/test009.lp
%Solving...
%Answer: 1
%a(3)
%OPTIMUM FOUND
%Answer: 2
%a(6)
%OPTIMUM FOUND
%Answer: 3
%a(1) a(2) a(4)
%Answer: 4
%a(1) a(2)
%Answer: 5
%a(1)
%OPTIMUM FOUND
%Answer: 6
%a(2) a(4)
%Answer: 7
%a(2)
%OPTIMUM FOUND
%Answer: 8
%a(4)
%OPTIMUM FOUND
%Answer: 9
%a(5)
%OPTIMUM FOUND
%Answer: 10
%a(9)
%OPTIMUM FOUND
%Answer: 11
%a(10)
%OPTIMUM FOUND
%Answer: 12
%a(7)
%OPTIMUM FOUND
%Answer: 13
%a(8)
%OPTIMUM FOUND
%
%Models       : 13
%  Optimum    : yes
%  Optimal    : 10
