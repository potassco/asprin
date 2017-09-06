% asprin test005.lp 0
% ERROR

% undefined type programs

%
% base program
%

dom(1..3).
1 { a(X) : dom(X) } 2.
1 { b(X) : dom(X) } 2.
#show a/1.
#show b/1.

#preference(p,undefined){
  a(X);
  b(X)
}.
#optimize(p).
