% asprin test009.lp 0
% ERROR

1 { a(X) : dom(X) } 2.
dom(1..3).
#show a/1.

#preference(1,less(weight)){
  1,X :: a(1)
}.

#optimize(1).
