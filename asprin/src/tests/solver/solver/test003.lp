% asprin test003.lp --non-optimal 0
% SATISFIABLE

1 { a(X) : dom(X) }.
dom(1..3).
#show a/1.
#preference(p,subset){ a(X) }.
#optimize(p).

%asprin version 3.0.0.3
%Reading from asprin/src/tests/solver/solver/test003.lp
%Solving...
%Answer: 1
%a(3)
%MODEL FOUND
%Answer: 2
%a(2)
%MODEL FOUND
%Answer: 3
%a(1) a(2)
%MODEL FOUND
%Answer: 4
%a(1) a(2) a(3)
%MODEL FOUND
%Answer: 5
%a(1)
%MODEL FOUND
%Answer: 6
%a(2) a(3)
%MODEL FOUND
%Answer: 7
%a(1) a(3)
%MODEL FOUND
%
%Models       : 7
%Calls        : 22
%Time         : 0.085s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
%CPU Time     : 0.080s
