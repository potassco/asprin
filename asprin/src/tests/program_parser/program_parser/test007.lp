% asprin test007.lp 
% ERROR

1 { a(X) : dom(X) }.
dom(1..3).
#show a/1.

#preference(p, subset) {
  a(X)
}.
#preference(p, superset) {}.

#optimize(p).

