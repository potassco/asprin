#program approximation.
#minimize{ W@L,T : minimize(P,W,L,T,X), optimize(P), holds(X) }.

#program approximation(subset).
minimize(P,1,1,X,X) :- preference(P,subset), preference(P,_,_,for(X),_).

%#program approximation(pareto).
%minimize(P,X,1,Level) :- preference(P,pareto), preference(P,_,_,name(PP),_), 
%                         minimize(PP,X,1,LL), level(PP,LL,Level).



