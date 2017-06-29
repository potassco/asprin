% asprin test018.lp --project 0
% SATISFIABLE


1 { a(X) : dom(X) }.
dom(1..4). 
#show a/1.
{ b(X,Y,Z) : dom(X), dom(Y), dom(Z) }.

#preference(p, subset){
 a(C) & (C > 1) & #true
}.

#optimize(p).
% *%

%asprin version 3.0.0
%Reading from tests/spec_parser/spec_parser/test018.lp
%Solving...
%Answer: 1
%a(3)
%Answer: 2
%a(1)
%OPTIMUM FOUND
%
%Models       : 2
%  Optimum    : yes
%  Calls        : 4
%  Time         : 0.060s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%  CPU Time     : 0.056s
