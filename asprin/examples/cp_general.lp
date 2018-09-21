% asprin calls for computing any number of models:
% asprin cp_general.lp --meta=simple
% asprin cp_general.lp --meta=combine
%
% asprin calls for computing any number of models when the diameter is known (2 in this case):
% asprin cp_general.lp --meta=simple  --const-nb cp_nontree_diameter=2
% asprin cp_general.lp --meta=combine --const-nb cp_nontree_diameter=2

dom(1..3).
{ a(X) : dom(X) }.
#show a/1.

next(1,2). next(2,3). next(3,1).

#preference(p,cp){
  a(X) >> not a(X) || a(Y) : next(X,Y)
}.
#optimize(p).
