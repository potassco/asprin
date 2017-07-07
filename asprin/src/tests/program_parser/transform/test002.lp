% asprin test002.lp 0
% SATISFIABLE
1 { a(X) : dom(X) }.
dom(1..3).
#show a/1.
 
 #preference(p, subset){ 
  a(X) 
}.
#optimize(p).

#program preference.
a :- not c.
c :- not b.
b :- not a.

%asprin version 3.0.0
%Reading from tests/program_parser/transform/test002.lp
%Solving...
%Answer: 1
%a(3)
%OPTIMUM FOUND
%
%Models       : 1+
%  Optimum    : yes
%  Calls        : 2
%  Time         : 0.043s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%  CPU Time     : 0.040s
