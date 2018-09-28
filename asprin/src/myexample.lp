dom(1..5).
1 { a(X) : dom(X) }.
#show a/1.

#heuristic a(X) : dom(X), X<4. [1,true]
query :- a(1), a(2), a(3).
%query :- a(1).
%query :- a(2).
query :- a(4), a(5).
#preference(p,subset) { 
  a(X)
}.
#optimize(p).
