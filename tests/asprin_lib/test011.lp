% asprin test011.lp 0
% SATISFIABLE

1 { a(X) : dom(X) } 1.
dom(1..5).
#show a/1.

#preference(1,poset){
  a(X);
  a(X) >> a(Y) : dom(X), dom(Y), X > Y
}.
#optimize(1).

%asprin version 3.0.0
%Reading from tests/asprin_lib/test011.lp
%Solving...
%Answer: 1
%a(3)
%Answer: 2
%a(5)
%OPTIMUM FOUND
%
%Models       : 2
%  Optimum    : yes
%  Calls        : 5
%  Time         : 0.053s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%  CPU Time     : 0.048s

