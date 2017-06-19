% asprin test001.lp 0
% ERROR
1 { a(X) : dom(X) }.
dom(1..3).
#show a/1.

#preference(p, subset){
 a(X)
 }.
#optimize(p).

#program preference(subset).
preference(p,(),1,for(a(1)),()) :- holds(X)
c :- not b..
