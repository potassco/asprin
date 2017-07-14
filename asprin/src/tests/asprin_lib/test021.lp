% asprin test021.lp 0 
% SATISFIABLE

1 { a(X,Y) : dom(Y) } 1 :- dom(X).
dom(1..n).
#show a/2.
:- 2 { a(X,n) }.

#preference(p,minmax){
  X :: a(X,Y)
}. 
#optimize(p).

%asprin version 3.0.0
%Reading from test021.lp
%bug.lp:5:5-9: info: interval undefined:
%  1..n
%
%<block>:5:5-9: info: interval undefined:
%  1..n
%
%<block>:2:55-67: info: atom does not occur in any rule head:
%  _dom(a(X,Y))
%
%<block>:3:35-47: info: atom does not occur in any rule head:
%  _dom(a(X,Y))
%
%<block>:5:5-9: info: interval undefined:
%  1..n
%
%<block>:5:5-9: info: interval undefined:
%  1..n
%
%<block>:5:5-9: info: interval undefined:
%  1..n
%
%<block>:5:5-9: info: interval undefined:
%  1..n
%
%<block>:5:5-9: info: interval undefined:
%  1..n
%
%<block>:5:5-9: info: interval undefined:
%  1..n
%
%Solving...
%Answer: 1
%
%OPTIMUM FOUND
%
%Models       : 1
%  Optimum    : yes
%Calls        : 4
%Time         : 0.066s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%CPU Time     : 0.060s
