% asprin test017.lp 0
% ERROR

1 { a(X) : dom(X) } 2.
dom(1..3).
#show a/1.

#preference(p(1),subset){
  { a(X); a }
}.
#optimize(p(1)).

