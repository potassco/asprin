% asprin test002.lp 0 --project
% SATISFIABLE


1 { a(X) : dom(X) }.
dom(1..4). 
#show a/1.
{ b(X,Y,Z) : dom(X), dom(Y), dom(Z) }.

#preference(p, subset){
 a(C) & (C > 0) & #true
}.

#optimize(p).

#program preference.
:-.


%asprin version 3.0.0
%Reading from /home/davila/git/asprin/tests/solver/solver/test002.lp
%Solving...
%Answer: 1
%a(3)
%OPTIMUM FOUND
%Answer: 2
%a(4)
%OPTIMUM FOUND
%Answer: 3
%a(3) a(4)
%OPTIMUM FOUND
%Answer: 4
%a(1) a(2) a(3)
%OPTIMUM FOUND
%Answer: 5
%a(1) a(2) a(3) a(4)
%OPTIMUM FOUND
%Answer: 6
%a(1) a(2)
%OPTIMUM FOUND
%Answer: 7
%a(2)
%OPTIMUM FOUND
%Answer: 8
%a(1) a(2) a(4)
%OPTIMUM FOUND
%Answer: 9
%a(1)
%OPTIMUM FOUND
%Answer: 10
%a(2) a(4)
%OPTIMUM FOUND
%Answer: 11
%a(2) a(3)
%OPTIMUM FOUND
%Answer: 12
%a(1) a(3)
%OPTIMUM FOUND
%Answer: 13
%a(1) a(3) a(4)
%OPTIMUM FOUND
%Answer: 14
%a(1) a(4)
%OPTIMUM FOUND
%Answer: 15
%a(2) a(3) a(4)
%OPTIMUM FOUND
%
%Models       : 15
%  Optimum    : yes
%    Optimal    : 15
%    Calls        : 31
%    Time         : 0.116s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%    CPU Time     : 0.116s
%
