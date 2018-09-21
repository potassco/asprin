% asprin calls for computing any number of models:
% asprin cp_tree.lp --const-nb cp_tree=1 --meta=no
% asprin cp_tree.lp --const-nb cp_tree=1 --meta=no --approximation=weak
% asprin cp_tree.lp --const-nb cp_tree=1 --meta=no --approximation=heuristic

dom(1..2).
{ a(X) : dom(X) }.
#show a/1.

#preference(p,cp){
  a(1) >> not a(1);
  a(2) >> not a(2) ||     a(1);
  not a(2) >> a(2) || not a(1)
}.
#optimize(p).

