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

#preference(p(2),less(weight)){
  X :: b(X)
}.

#preference(p(3),aso){
  a(X) >> not a(X) || b(X)
}.

#preference(p(4),poset){
  a(X);
  b(X);
  a(X) >> b(X)
}.

%
% composite preference statements
%

#const composite=pareto.

#preference(q,pareto){
  **p(X)
} : composite=pareto.

#preference(q,lexico){
  X :: **p(X)
} : composite=lexico.

#preference(q,and){
  **q(X)
} : composite=and.

#preference(r,neg){
  **q
}.

%
% optimize statement
%

#const opt=r.
#optimize(opt).

