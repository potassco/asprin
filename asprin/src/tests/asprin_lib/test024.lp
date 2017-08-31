% asprin test024.lp 0 -c n=8
% SATISFIABLE

1 { a(X,Y) : dom(Y) } 1 :- dom(X).
dom(1..n).
#show a/2.
:- 2 { a(X,1) }.

#preference(p,maxmin){
  X,-Y :: a(X,Y)
}. 
#optimize(p).

%asprin version 3.0.0.6
%Reading from src/tests/asprin_lib/test024.lp
%Solving...
%Answer: 1
%a(1,3) a(2,3) a(5,3) a(6,3) a(3,4) a(4,4) a(7,6) a(8,8)
%Answer: 2
%a(4,3) a(7,3) a(1,7) a(2,7) a(3,7) a(5,7) a(6,7) a(8,7)
%Answer: 3
%a(4,3) a(1,6) a(2,6) a(3,6) a(5,6) a(6,6) a(7,6) a(8,6)
%Answer: 4
%a(4,3) a(1,5) a(2,5) a(3,5) a(5,5) a(6,5) a(7,5) a(8,5)
%Answer: 5
%a(4,3) a(1,4) a(2,4) a(3,4) a(5,4) a(6,4) a(7,4) a(8,4)
%Answer: 6
%a(1,3) a(2,3) a(3,3) a(4,3) a(5,3) a(6,3) a(7,3) a(8,3)
%Answer: 7
%a(1,2) a(2,2) a(3,2) a(4,2) a(5,2) a(6,2) a(7,2) a(8,2)
%OPTIMUM FOUND
%Answer: 8
%a(7,1) a(1,2) a(2,2) a(3,2) a(4,2) a(5,2) a(6,2) a(8,2)
%OPTIMUM FOUND
%Answer: 9
%a(1,1) a(2,2) a(3,2) a(4,2) a(5,2) a(6,2) a(7,2) a(8,2)
%OPTIMUM FOUND
%Answer: 10
%a(4,1) a(1,2) a(2,2) a(3,2) a(5,2) a(6,2) a(7,2) a(8,2)
%OPTIMUM FOUND
%Answer: 11
%a(8,1) a(1,2) a(2,2) a(3,2) a(4,2) a(5,2) a(6,2) a(7,2)
%OPTIMUM FOUND
%Answer: 12
%a(6,1) a(1,2) a(2,2) a(3,2) a(4,2) a(5,2) a(7,2) a(8,2)
%OPTIMUM FOUND
%Answer: 13
%a(2,1) a(1,2) a(3,2) a(4,2) a(5,2) a(6,2) a(7,2) a(8,2)
%OPTIMUM FOUND
%Answer: 14
%a(5,1) a(1,2) a(2,2) a(3,2) a(4,2) a(6,2) a(7,2) a(8,2)
%OPTIMUM FOUND
%Answer: 15
%a(3,1) a(1,2) a(2,2) a(4,2) a(5,2) a(6,2) a(7,2) a(8,2)
%OPTIMUM FOUND
%
%Models       : 15
%  Optimum    : yes
%  Optimal    : 9
