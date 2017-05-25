1 { a(X) : dom(X) }.
1 { b(X) : dom(X) }.
:- not 3 { a(X); b(X) }.

#preference(a,subset) { a(X) : dom(X) }. 
#preference(b,subset) { b(X) : dom(X) }.

dom(1..2).
#show a/1.
#show b/1.

#const type=lexico.
#preference(p,lexico){ 1 :: **a; 2 :: **b } : type = lexico.
#preference(p,pareto){      **a;      **b } : type = pareto.
#optimize(p).

