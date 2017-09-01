% asprin test026.lp 0
% SATISFIABLE

{ a(1..4) }.
:- a(1).
:- a(2).

1{ b; c; d }1.

#preference(p,poset){
  a(X) >> a(X+1);
  b >> c;
  c >> d; 
  a(3) >> c;
  c' >> b
}.
c' :- c.
#optimize(p).


%asprin version 3.0.0.6
%Reading from src/tests/asprin_lib/test026.lp
%Solving...
%Answer: 1
%d
%Answer: 2
%a(4) d
%Answer: 3
%a(3) a(4) d
%Answer: 4
%a(3) a(4) b
%Answer: 5
%a(3) a(4) c c'
%OPTIMUM FOUND
%
%Models       : 5
%  Optimum    : yes
%  Optimal    : 1
