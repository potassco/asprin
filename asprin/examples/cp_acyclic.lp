% asprin calls:
% asprin cp_acyclic.lp 1 --approximation=weak
% asprin cp_acyclic.lp 1 --approximation=heuristic
% asprin cp_acyclic.lp 0 --approximation=weak      --meta=combine
% asprin cp_acyclic.lp 0 --approximation=heuristic --meta=combine

dom(1..3).
{ a(X) : dom(X) }.
#show a/1.

#preference(p,cp){
  a(1) >> not a(1);
  a(2) >> not a(2);
  a(3) >> not a(3) || {     a(1);     a(2) };
  a(3) >> not a(3) || { not a(1);     a(2) };
  not a(3) >> a(3) || {     a(1); not a(2) };
  not a(3) >> a(3) || { not a(1); not a(2) }
}.
#optimize(p).

