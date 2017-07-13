% asprin test020.lp -c n=3 
% ERROR

1 { a(X,Y) : dom(Y) } 1 :- dom(X).
dom(1..n).
#show a/2.
:- 2 { a(X,n) }.

#preference(p,maxmin){
  X :: a(X,Y)
}. 
#optimize(p).

%asprin version 3.0.0.4
%Reading from /home/davila/git/asprin/asprin/src/tests/asprin_lib/test020.lp
%
%preference:p: error: preference specification error, type 'maxmin' requires a weight tuple of at least 2 elements.
%
% *** ERROR: (asprin): parsing failed
%UNKNOWN
%
