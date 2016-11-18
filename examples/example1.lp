1 { a(X) : dom(X) }.
1 { b(X) : dom(X) }.

#preference(a,subset) { 
  a(X) : dom(X)
}.

#preference(b,subset) { 
  b(X) : dom(X)
}.

#preference(c,pareto) {
  **a;
  **b
}.

dom(1..5).
#show a/1.
#show b/1.


#optimize(c).
