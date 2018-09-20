% asprin test007.lp 0 --const-nb cp_tree=1 --meta=no
% ERROR

1 { a(X) : dom(X) } 2.
dom(1..3).
#show a/1.

#preference(p(1),subset){
  a(X)
}.
#preference(p(2),cp){
  a(X)
} : X=3.
#preference(p(3),superset){
  a(1) & a(2) & not not a(3)
}.
#preference(r,and){
  { **p(1) ; **p(2) }
}.
#optimize(r).
