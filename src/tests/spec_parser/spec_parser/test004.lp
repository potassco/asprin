% asprin test004.lp 0
% ERROR

1 { a(X) : dom(X) }.
dom(1..3).
#show a/1.

#preference(p, poset){ not (a(X)) }.
#optimize(p).
