% asprin test010.lp 0 --approximation=weak
% SATISFIABLE

1 { a(X) : dom(X) }.
1 { b(X) : dom(X) }.
ok(a) :- a(X) : dom(X).
ok(b) :- b(X) : dom(X).
:- not ok(a), not ok(b).
dom(1..3).
#show b/1.
#show a/1.
#preference(p(1),subset) { a(X) }. 
#preference(p(2),subset) { b(X) }. 
#preference(q(X),subset) { a(X) } : dom(X).
#preference(p(3),lexico) { X :: **p(X) : X = 1..2}.
#preference(p(3),lexico) { X+10 :: **q(X) }.

#preference(p(4),lexico) { X :: **p(X) : X = 1..3 }.
#preference(pp,pareto) { **p(X) }.
#optimize(pp).


%asprin version 3.0.0.6
%Reading from src/tests/solver/solver/test010.lp
%Solving...
%Answer: 1
%a(1) a(2) a(3) b(1) b(2) b(3)
%Answer: 2
%a(1) a(2) a(3) b(3)
%OPTIMUM FOUND
%Answer: 3
%a(1) a(2) a(3) b(1)
%OPTIMUM FOUND
%Answer: 4
%a(3) b(1) b(2) b(3)
%OPTIMUM FOUND
%Answer: 5
%a(2) b(1) b(2) b(3)
%OPTIMUM FOUND
%Answer: 6
%a(1) a(2) a(3) b(2)
%OPTIMUM FOUND
%Answer: 7
%a(1) b(1) b(2) b(3)
%OPTIMUM FOUND
%
%Models       : 7
%  Optimum    : yes
%  Optimal    : 6
