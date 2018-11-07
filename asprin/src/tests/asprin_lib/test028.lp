% asprin test028.lp 0
% ERROR

1 { a(X,Y) : dom(X), dom(Y) } 2.
dom(1..3).
#preference(p,less(weight)){
  X,Y :: a(X,Y);
  a(X,Z)
}.
#optimize(p).
#show a/2.
