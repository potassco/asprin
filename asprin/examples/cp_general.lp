% asprin calls:
% asprin cp_general.lp 0 --meta=simple
% asprin cp_general.lp 0 --meta=simple  --const-nb cp_nontree_diameter=2
% asprin cp_general.lp 0 --meta=combine
% asprin cp_general.lp 0 --meta=combine --const-nb cp_nontree_diameter=2

dom(1..3).
{ a(X) : dom(X) }.
#show a/1.

#preference(p,cp){
  a(1) >> not a(1) || a(3);
  a(2) >> not a(2) || a(1);
  a(3) >> not a(3) || a(2)
}.
#optimize(p).

