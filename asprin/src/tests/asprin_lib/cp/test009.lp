% asprin test009.lp 0 --const-nb cp_tree=1 --meta=no
% ERROR

1 { a(X) : dom(X) } 2.
dom(1..3).
#show a/1.

b(X) :- a(X).

#preference(p,cp){
      b(X) ||     a(X);
  not b(X) || not a(X);
      a(X) ||     b(X);
  not a(X) || not b(X)
}.
#optimize(p).
