% asprin test020.lp 0
% ERROR

1 { a(X) : dom(X) }.
dom(1..3).
#show a/1.

#preference(p,subset){ not not not (a(X)) }.
#optimize(p).

