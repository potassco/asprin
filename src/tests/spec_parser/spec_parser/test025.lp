% asprin test0025.lp 0
% ERROR
1 { a(X) : dom(X) }.
dom(1..2).
#show a/1.
#show b/1.
b(casa).

#preference(p, subset){ a(X) }.
#optimize(p).
#program preference.
#const casa=haus.
#show casa.
#show a/1.
%a(1) | a(2).

#show a : #true.
#show xxx : holds(X).


#edge (a,b) : holds(X).
#edge (b,a) : c.

#heuristic aa : holds(X). [1, true]
#heuristic bb : cc. [1, true]
