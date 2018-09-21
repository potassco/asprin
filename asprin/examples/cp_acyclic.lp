% asprin calls for computing one model:
% asprin cp_acyclic.lp --approximation=weak
% asprin cp_acyclic.lp --approximation=heuristic
%
% asprin calls for computing more than one model:
% asprin cp_acyclic.lp --approximation=weak      --meta=combine 0
% asprin cp_acyclic.lp --approximation=heuristic --meta=combine 0

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

