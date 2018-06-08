% asprin test004.lp --approximation=heuristic 0
% ERROR

dom(1..3).
1 { a(X) : dom(X) }.
#show a/1.

#preference(p,subset) { 
  a(X)
}.
#optimize(p).

#program heuristic(subset).
#heuristic Y : Y=holds(X), preference(P,subset), preference(P,_,_,for(X),_).

