% asprin test002.lp 0
% ERROR
1 { a(X) : dom(X) }.
dom(1..3).
#show a/1.

a(3).

#preference(p, subset){
  a(X) 
}.
#optimize(p).

#program preference.
a :- not b.
b :- not a.

%*** ERROR: (asprin): parsing error, unstratified preference program, use option --meta
%asprin version 3.1.0
%Reading from tests/program_parser/visitor/test002.lp
%UNKNOWN
