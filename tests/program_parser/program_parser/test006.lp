% asprin test006.lp 
% ERROR

1 { a(X) : dom(X) }.
dom(1..3).
#show a/1.

#preference(p, (subset;superset)) {
  a(X)
}.

#optimize(p).

