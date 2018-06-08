% asprin test001.lp --approximation=heuristic 0
% SATISFIABLE

%
% base program
%

dom(1..3).
1 { a(X) : dom(X) } 2.
1 { b(X) : dom(X) } 2.
#show a/1.
#show b/1.

%
% basic preference statements
%

#preference(p(1),subset){
  a(X)
}.

%*
#preference(p(2),less(weight)){
  X :: b(X)
}.

#preference(p(3),aso){
  a(X) >> not a(X) || b(X)
}.
*%
#preference(p(4),poset){
  a(X);
  b(X);
  a(X) >> b(X)
}.

%
% composite preference statements
%
%*
#preference(q,pareto){
  **p(X)
}.

#preference(r,neg){
  **q
}.
*%
%
% optimize statement
%

#optimize(p(4)).

%asprin version 3.0.0.6
%Reading from ../mine/example_poset.lp
%Solving...
%Answer: 1
%a(3) b(1)
%Answer: 2
%a(3) b(1) b(3)
%Answer: 3
%a(2) a(3) b(1) b(3)
%OPTIMUM FOUND
%Answer: 4
%a(2) b(2)
%Answer: 5
%a(1) a(2) b(2)
%Answer: 6
%a(1) a(2) b(2) b(3)
%OPTIMUM FOUND
%Answer: 7
%a(1) a(3) b(3)
%Answer: 8
%a(1) a(3) b(2) b(3)
%OPTIMUM FOUND
%Answer: 9
%a(1) a(3) b(1) b(2)
%OPTIMUM FOUND
%Answer: 10
%a(2) a(3) b(1) b(2)
%OPTIMUM FOUND
%Answer: 11
%a(2) a(3) b(2) b(3)
%OPTIMUM FOUND
%Answer: 12
%a(1) a(2) b(1) b(2)
%OPTIMUM FOUND
%Answer: 13
%a(1) a(2) b(1) b(3)
%OPTIMUM FOUND
%Answer: 14
%a(1) a(3) b(1) b(3)
%OPTIMUM FOUND
%
%Models       : 14
%  Optimum    : yes
