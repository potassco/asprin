% asprin test004.lp 0 --heuristic=Domain
% ERROR

1 { a(X) : dom(X) }.
dom(1..3).
#show a/1.

#preference(p,subset){ a(X) }.
#optimize(p).

#program preference(subset).
%#heuristic holds(X) : preference(P,subset), preference(P,_,_,for(X),_). [1,true]
#heuristic holds(X) : preference(P,subset), better(P). [1,true]
%#heuristic holds'(X) : preference(P,subset). [1,true]
