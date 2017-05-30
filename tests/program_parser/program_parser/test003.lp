% asprin test011.lp 0
% ERROR

1 { a(X) : dom(X) }.
dom(1..3).
#show a/1.

#preference(p, superset){
  a(X)
}.

#preference(r, pareto){ 
  **p; **p 
}.
%#optimize(r).

