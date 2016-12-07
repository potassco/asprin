1 { a(X) : dom(X) }.
1 { b(X) : dom(X) }.

#preference(a,subset) { a(X) : dom(X) }. 
#preference(b,subset) { b(X) : dom(X) }.

dom(1..n).
#show a/1.
#show b/1.

#preference(p,pareto){ **a; **b }.

#optimize(p).

