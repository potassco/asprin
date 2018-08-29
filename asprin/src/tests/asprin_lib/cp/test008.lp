% asprin test008.lp 0 --const-nb cp_tree=1
% ERROR

1 { a(X) : dom(X) } 2.
dom(1..3).
#show a/1.

#preference(p,cp){
  a(X) : dom(X);
  not a(X) : dom(X)
}.
#optimize(p).
