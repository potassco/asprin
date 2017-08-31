% asprin test022.lp 0 -c n=10
% SATISFIABLE

1 { a(X,Y) : dom(Y) } 1 :- dom(X).
dom(1..n).
#show a/2.
:- 2 { a(X,1) }.

#preference(p,maxmin){
  X,Y :: a(X,Y)
}. 
#optimize(p).

%asprin version 3.0.0.6
%Reading from src/tests/asprin_lib/test022.lp
%Solving...
%Answer: 1
%a(2,3) a(3,3) a(5,3) a(7,3) a(8,3) a(4,5) a(9,5) a(10,5) a(1,7) a(6,10)
%Answer: 2
%a(3,4) a(1,6) a(8,7) a(6,9) a(2,10) a(4,10) a(5,10) a(7,10) a(9,10) a(10,10)
%Answer: 3
%a(8,5) a(1,6) a(2,6) a(9,6) a(4,7) a(10,7) a(3,8) a(6,9) a(5,10) a(7,10)
%Answer: 4
%a(1,6) a(3,8) a(8,8) a(6,9) a(2,10) a(4,10) a(5,10) a(7,10) a(9,10) a(10,10)
%Answer: 5
%a(4,7) a(3,8) a(10,8) a(5,9) a(6,9) a(1,10) a(2,10) a(7,10) a(8,10) a(9,10)
%Answer: 6
%a(3,8) a(1,9) a(6,9) a(2,10) a(4,10) a(5,10) a(7,10) a(8,10) a(9,10) a(10,10)
%Answer: 7
%a(6,9) a(1,10) a(2,10) a(3,10) a(4,10) a(5,10) a(7,10) a(8,10) a(9,10) a(10,10)
%Answer: 8
%a(1,10) a(2,10) a(3,10) a(4,10) a(5,10) a(6,10) a(7,10) a(8,10) a(9,10) a(10,10)
%OPTIMUM FOUND
%
%Models       : 8
%  Optimum    : yes
%  Optimal    : 1
