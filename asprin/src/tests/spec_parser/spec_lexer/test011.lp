% asprin test011.lp 0 
% ERROR

1 { a(X) : dom(X) }.
{ b }.
dom(1..3).
#preference(p,subset){ a(X) }. #optimize(p).

#project a/1.
