#program preference.
:- not better(P),  optimize(P).
required(P,better) :- optimize(P).
    
% to avoid warnings
better(P)     :- #false, better(P).     % to avoid warnings
required(P,Q) :- #false, required(P,Q). % to avoid warnings

%
% errors
%
error(X) :- #false, error(X).               % to avoid warnings
error_type(X,Y) :- #false, error_type(X,Y). % to avoid warnings

%%% no formulas
error(("preference:",P,": error: preference specification error, type '",T,"' does not allow formulas.")) :-
             preference(P,T), error_type(T,no_formulas), 
             preference(P,_,_,for(X),_).

%%% no weights
error(("preference:",P,": error: preference specification error, type '",T,"' does not allow weights.")) :-
             preference(P,T), error_type(T,no_weights),
             preference(P,_,_,_,W), W != ().

%%% no ordering
error(("preference:",P,": error: preference specification error, type '",T,"' does not allow using '>>'.")) :-
             preference(P,T), error_type(T,no_ordering),
             preference(P,_,R,_,_), R > 1.

%%% no sets
error(("preference:",P,": error: preference specification error, type '",T,"' does not allow sets.")) :-
             preference(P,T), error_type(T,no_sets), 
             preference(P,E,S,X,_), preference(P,E,S,Y,_), X > Y.

%%% no names
error(("preference:",P,": error: preference specification error, type '",T,"' does not allow naming atoms.")) :-
             preference(P,T), error_type(T,no_naming),
             preference(P,_,_,name(X),_).
           
%%% single 
error(("preference:",P,": error: preference specification error, type '",T,"' does not allow more than one preference element.")) :-
             preference(P,T), error_type(T,single), 
             2 { preference(P,_,_,_,_) }.
           
% no condition
error(("preference:",P,": error: preference specification error, type '",T,"' does not allow using '||'.")) :-
             preference(P,poset), error_type(T,no_condition), 
             preference(P,_,0,_,_).
           
#program preference(and).

required(Q,better) :- preference(P,and), required(P,better), preference(P,_,_,name(Q),_).
better(P) :- preference(P,and), required(P,better); 
	            better(Q) : preference(P,_,_,name(Q),_).
            
required(P,better) :- preference(P,and), required(P,bettereq). 
required(P,eq)        :- preference(P,and), required(P,bettereq). 
bettereq(P) :- preference(P,and), required(P,bettereq),
                  1 #sum { 1: better(P); 1: eq(P) }.

required(Q,eq) :- preference(P,and), required(P,eq), preference(P,_,_,name(Q),_).
eq(P) :- preference(P,and), required(P,eq); 
	     eq(Q) : preference(P,_,_,name(Q),_).

required(P,worse) :- preference(P,and), required(P,worseeq). 
required(P,eq)    :- preference(P,and), required(P,worseeq). 
worseeq(P) :- preference(P,and), required(P,worseeq),
              1 #sum { 1: worse(P); 1: eq(P) }.

required(Q,worse) :- preference(P,and), required(P,worse), preference(P,_,_,name(Q),_).
worse(P) :- preference(P,and), required(P,worse); 
	        worse(Q) : preference(P,_,_,name(Q),_).

required(P,bettereq) :- preference(P,and), required(P,unc). 
required(P,worseeq)     :- preference(P,and), required(P,unc). 
unc(P) :- preference(P,and); required(P,unc); 
          not bettereq(P); not worseeq(P).

% errors
error_type(and,no_formulas).
error_type(and,no_weights).
error_type(and,no_ordering).
error_type(and,no_condition).
error_type(and,no_sets).


#program preference(aso).

required(P,aso) :- preference(P,aso), required(P,_).
preference(P,aso,Id) :- preference(P,aso), required(P,aso), preference(P,Id,_,_,_).

nohead(P,Id) :- preference(P,aso,Id), 
                not holds(X) : preference(P,Id,H,for(X),_), H!=0.

nohead'(P,Id) :- preference(P,aso,Id), 
                 not holds'(X) : preference(P,Id,H,for(X),_), H!=0.

value'(P,Id,V) :- preference(P,aso,Id),
                  V = #min { 1   : not holds'(X), preference(P,Id,0,for(X),_);
                             1   : nohead'(P,Id);
                             Pos : holds'(X), preference(P,Id,Pos,for(X),_), Pos != 0}.
 
better(P,Id) :- preference(P,aso,Id), value'(P,Id,V), required(P,aso,better), 
                   V > #min { 1   : not holds(X), preference(P,Id,0,for(X),_);
                              1   : nohead(P,Id);
                              Pos : holds(X), preference(P,Id,Pos,for(X),_), Pos != 0}.
 
bettereq(P,Id) :- preference(P,aso,Id), value'(P,Id,V), required(P,aso,bettereq),
                     V >= #min { 1   : not holds(X), preference(P,Id,0,for(X),_);
                                 1   : nohead(P,Id);
                                 Pos : holds(X), preference(P,Id,Pos,for(X),_), Pos != 0}.

required(P,aso,better)   :- preference(P,aso), required(P,better).                             
required(P,aso,bettereq) :- preference(P,aso), required(P,better).                             
better(P) :- preference(P,aso), required(P,better),
                bettereq(P,Id1) : preference(P,aso,Id1);
                better(P,Id2), preference(P,aso,Id2).

required(P,aso,bettereq) :- preference(P,aso), required(P,bettereq).                            
bettereq(P) :- preference(P,aso), required(P,bettereq),
                  bettereq(P,Id) : preference(P,aso,Id).

              
eq(P,Id) :- preference(P,aso,Id), value'(P,Id,V), required(P,aso,eq),
            V = #min { 1   : not holds(X), preference(P,Id,0,for(X),_);
                       1   : nohead(P,Id);
                       Pos : holds(X), preference(P,Id,Pos,for(X),_), Pos != 0}.
 
worseeq(P,Id) :- preference(P,aso,Id), value'(P,Id,V), required(P,aso,worseeq),
                 V <= #min { 1   : not holds(X), preference(P,Id,0,for(X),_);
                             1   : nohead(P,Id);
                             Pos : holds(X), preference(P,Id,Pos,for(X),_), Pos != 0}.
 
worse(P,Id) :- preference(P,aso,Id), value'(P,Id,V), required(P,aso,worse),
               V < #min { 1   : not holds(X), preference(P,Id,0,for(X),_);
                          1   : nohead(P,Id);
                          Pos : holds(X), preference(P,Id,Pos,for(X),_), Pos != 0}.

required(P,aso,eq) :- preference(P,aso), required(P,eq).                             
eq(P) :- preference(P,aso), required(P,eq),
         eq(P,Id) : preference(P,aso,Id).

required(P,aso,worseeq) :- preference(P,aso), required(P,worseeq).                             
worseeq(P) :- preference(P,aso), required(P,worseeq),
              worseeq(P,Id) : preference(P,aso,Id).

required(P,aso,worseeq) :- preference(P,aso), required(P,worse).                             
required(P,aso,worse)   :- preference(P,aso), required(P,worse).                             
worse(P) :- preference(P,aso), required(P,worse),
            worseeq(P,Id1) : preference(P,aso,Id1);
            worse(P,Id2); preference(P,aso,Id2).

required(P,bettereq) :- preference(P,aso), required(P,unc). 
required(P,worseeq)     :- preference(P,aso), required(P,unc). 
unc(P) :- preference(P,aso); required(P,unc); 
          not bettereq(P); not worseeq(P).


% errors
error_type(aso,no_naming).
error_type(aso,no_weights).
error_type(aso,no_sets).


#program preference(less(cardinality)).

better(P) :- preference(P,less(cardinality)), required(P,better),
                1 #sum { -1,X : holds(X),  preference(P,_,_,for(X),_); 
                          1,X : holds'(X), preference(P,_,_,for(X),_)}.

required(P,better) :- required(P,bettereq).
required(P,eq)        :- required(P,bettereq).
bettereq(P) :- preference(P,less(cardinality)), required(P,bettereq),
                  1 #sum { 1: eq(P); 1: better(P) }.

eq(P) :- preference(P,less(cardinality)), required(P,eq),
         0 #sum { -1,X : holds(X),  preference(P,_,_,for(X),_); 
                   1,X : holds'(X), preference(P,_,_,for(X),_)}0. 

required(P,worse) :- required(P,worseeq).
required(P,eq)    :- required(P,worseeq).
worseeq(P) :- preference(P,less(cardinality)), required(P,worseeq),
              1 #sum { 1: eq(P); 1: worse(P) }.

worse(P) :- preference(P,less(cardinality)), required(P,worse),
            #sum { -1,X : holds(X),  preference(P,_,_,for(X),_); 
                    1,X : holds'(X), preference(P,_,_,for(X),_)}-1.


% errors
error_type(less(cardinality),no_naming).
error_type(less(cardinality),no_ordering).
error_type(less(cardinality),no_condition).
error_type(less(cardinality),no_weights).
error_type(less(cardinality),no_sets).

#program preference(less(weight)).


better(P) :- preference(P,less(weight)), required(P,better),
             1 #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @head(T); 
                       W,T : holds'(X), preference(P,_,_,for(X),T), W = @head(T)}.

bettereq(P) :- preference(P,less(weight)), required(P,bettereq),
                  0 #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @head(T); 
                            W,T : holds'(X), preference(P,_,_,for(X),T), W = @head(T)}. 

eq(P) :- preference(P,less(weight)), required(P,eq),
         0 #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @head(T); 
                   W,T : holds'(X), preference(P,_,_,for(X),T), W = @head(T)}0. 

worseeq(P) :- preference(P,less(weight)), required(P,worseeq),
              #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @head(T); 
                      W,T : holds'(X), preference(P,_,_,for(X),T), W = @head(T)}0.

worse(P) :- preference(P,less(weight)), required(P,worse),
            #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @head(T); 
                    W,T : holds'(X), preference(P,_,_,for(X),T), W = @head(T)}-1.

% errors
error_type(less(weight),no_naming).
error_type(less(weight),no_ordering).
error_type(less(weight),no_condition).
error_type(less(weight),no_sets).

#program preference(lexico).

required(Q,better) :- preference(P,lexico), required(P,better), preference(P,_,_,name(Q),_).
required(Q,eq)        :- preference(P,lexico), required(P,better), preference(P,_,_,name(Q),_).
better(P) :- preference(P,lexico), required(P,better),
                better(R); preference(P,_,_,name(R),(L));
	            eq(Q)      : preference(P,_,_,name(Q),(LL)), LL > L.

required(P,better) :- preference(P,lexico), required(P,bettereq). 
required(P,eq)        :- preference(P,lexico), required(P,bettereq). 
bettereq(P) :- preference(P,lexico), required(P,bettereq),
                  1 #sum { 1: better(P); 1: eq(P) }.

required(Q,eq) :- preference(P,lexico), required(P,eq), preference(P,_,_,name(Q),_).
eq(P) :- preference(P,lexico), required(P,eq),
         eq(Q) : preference(P,_,_,name(Q),_).

required(P,worse) :- preference(P,lexico), required(P,worseeq). 
required(P,eq)    :- preference(P,lexico), required(P,worseeq). 
worseeq(P) :- preference(P,lexico), required(P,worseeq),
              1 #sum { 1: worse(P); 1: eq(P) }.

required(Q,worse) :- preference(P,lexico), required(P,worse), preference(P,_,_,name(Q),_).
required(Q,eq)    :- preference(P,lexico), required(P,worse), preference(P,_,_,name(Q),_).
worse(P) :- preference(P,lexico), required(P,worse),
            worse(R); preference(P,_,_,name(R),(L));
	        eq(Q) : preference(P,_,_,name(Q),(LL)), LL > L.

required(P,bettereq) :- preference(P,lexico), required(P,unc). 
required(P,worseeq)     :- preference(P,lexico), required(P,unc). 
unc(P) :- preference(P,lexico); required(P,unc); 
          not bettereq(P); not worseeq(P).

% errors
error_type(lexico,no_formulas).
error_type(lexico,no_ordering).
error_type(lexico,no_condition).
error_type(lexico,no_sets).

#program preference(more(cardinality)).

better(P) :- preference(P,more(cardinality)), required(P,better),
                #sum { -1,X : holds(X),  preference(P,_,_,for(X),_); 
                        1,X : holds'(X), preference(P,_,_,for(X),_)}-1.

required(P,better) :- required(P,bettereq).
required(P,eq)        :- required(P,bettereq).
bettereq(P) :- preference(P,more(cardinality)), required(P,bettereq),
                  1 #sum { 1: eq(P); 1: better(P) }.

eq(P) :- preference(P,more(cardinality)), required(P,eq),
         0 #sum { -1,X : holds(X),  preference(P,_,_,for(X),_); 
                   1,X : holds'(X), preference(P,_,_,for(X),_)}0. 

required(P,worse) :- required(P,worseeq).
required(P,eq)    :- required(P,worseeq).
worseeq(P) :- preference(P,more(cardinality)), required(P,worseeq),
              1 #sum { 1: eq(P); 1: worse(P) }.

worse(P) :- preference(P,more(cardinality)), required(P,worse),
            1 #sum { -1,X : holds(X),  preference(P,_,_,for(X),_); 
                      1,X : holds'(X), preference(P,_,_,for(X),_)}.


% errors
error_type(more(cardinality),no_naming).
error_type(more(cardinality),no_ordering).
error_type(more(cardinality),no_condition).
error_type(more(cardinality),no_weights).
error_type(more(cardinality),no_sets).

#program preference(more(weight)).

better(P) :- preference(P,more(weight)), required(P,better),
                #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @head(T); 
                        W,T : holds'(X), preference(P,_,_,for(X),T), W = @head(T)}-1.

bettereq(P) :- preference(P,more(weight)), required(P,bettereq),
                  #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @head(T); 
                          W,T : holds'(X), preference(P,_,_,for(X),T), W = @head(T)}0. 

eq(P) :- preference(P,more(weight)), required(P,eq),
         0 #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @head(T); 
                   W,T : holds'(X), preference(P,_,_,for(X),T), W = @head(T)}0. 

worseeq(P) :- preference(P,more(weight)), required(P,worseeq),
              0 #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @head(T); 
                        W,T : holds'(X), preference(P,_,_,for(X),T), W = @head(T)}.

worse(P) :- preference(P,more(weight)), required(P,worse),
            1 #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @head(T); 
                      W,T : holds'(X), preference(P,_,_,for(X),T), W = @head(T)}.
                     
% errors
error_type(more(weight),no_naming).
error_type(more(weight),no_ordering).
error_type(more(weight),no_condition).
error_type(more(weight),no_sets).


#program preference(neg).

required(Q,worse) :- preference(P,neg), required(P,better), preference(P,_,_,name(Q),_).
better(P) :- preference(P,neg), required(P,better),
	            worse(Q), preference(P,_,_,name(Q),_).

required(P,better) :- preference(P,neg), required(P,bettereq). 
required(P,eq)        :- preference(P,neg), required(P,bettereq). 
bettereq(P) :- preference(P,neg), required(P,bettereq),
                  1 #sum { 1: better(P); 1: eq(P) }.

required(Q,eq) :- preference(P,neg), required(P,eq), preference(P,_,_,name(Q),_).
eq(P) :- preference(P,neg), required(P,eq),
	     eq(Q), preference(P,_,_,name(Q),_).

required(P,worse) :- preference(P,neg), required(P,worseeq). 
required(P,eq)    :- preference(P,neg), required(P,worseeq). 
worseeq(P) :- preference(P,neg), required(P,worseeq),
              1 #sum { 1: worse(P); 1: eq(P) }.

required(Q,better) :- preference(P,neg), required(P,worse), preference(P,_,_,name(Q),_).
worse(P) :- preference(P,neg), required(P,worse),
	        better(Q), preference(P,_,_,name(Q),_).

required(P,bettereq) :- preference(P,neg), required(P,unc). 
required(P,worseeq)     :- preference(P,neg), required(P,unc). 
unc(P) :- preference(P,neg); required(P,unc); 
          not bettereq(P); not worseeq(P).
      
% errors
error_type(neg,no_formulas).
error_type(neg,no_weights).
error_type(neg,no_ordering).
error_type(neg,no_condition).
error_type(neg,no_sets).
error_type(neg,single).


#program preference(pareto).

required(Q,better)   :- preference(P,pareto), required(P,better), preference(P,_,_,name(Q),_).
required(Q,bettereq) :- preference(P,pareto), required(P,better), preference(P,_,_,name(Q),_).
better(P) :- preference(P,pareto), required(P,better),
	            bettereq(Q) : preference(P,_,_,name(Q),_);
                better(R);    preference(P,_,_,name(R),_).

required(Q,bettereq) :- preference(P,pareto), required(P,bettereq), preference(P,_,_,name(Q),_).
bettereq(P) :- preference(P,pareto), required(P,bettereq),
	              bettereq(Q) : preference(P,_,_,name(Q),_).

required(Q,eq) :- preference(P,pareto), required(P,eq), preference(P,_,_,name(Q),_).
eq(P) :- preference(P,pareto), required(P,eq),
	     eq(Q) : preference(P,_,_,name(Q),_).

required(Q,worseeq) :- preference(P,pareto), required(P,worseeq), preference(P,_,_,name(Q),_).
worseeq(P) :- preference(P,pareto), required(P,worseeq),
	          worseeq(Q) : preference(P,_,_,name(Q),_).

required(Q,worse)   :- preference(P,pareto), required(P,worse), preference(P,_,_,name(Q),_).
required(Q,worseeq) :- preference(P,pareto), required(P,worse), preference(P,_,_,name(Q),_).
worse(P) :- preference(P,pareto), required(P,worse),
	        worseeq(Q) : preference(P,_,_,name(Q),_);
            worse(R);    preference(P,_,_,name(R),_).

required(P,bettereq) :- preference(P,pareto), required(P,unc). 
required(P,worseeq)     :- preference(P,pareto), required(P,unc). 
unc(P) :- preference(P,pareto); required(P,unc); 
          not bettereq(P); not worseeq(P).

% errors
error_type(pareto,no_formulas).
error_type(pareto,no_weights).
error_type(pareto,no_ordering).
error_type(pareto,no_condition).
error_type(pareto,no_sets).

#program preference(poset).

%
% qualitative preferences
%

required(P)       :- preference(P,poset), required(P,_).
required(P,noteq) :- preference(P,poset), required(P,X), X != eq.

poset(P,X) :- preference(P,poset), required(P),
              preference(P,_,_,for(X),_).

poset(P,X,Y) :- preference(P,poset), required(P,noteq),
                preference(P,I,1,for(X),_), preference(P,I,2,for(Y),_).

% transitive closure
poset(P,X,Y) :- preference(P,poset), required(P,noteq),
                poset(P,X,Z), poset(P,Z,Y).

% better

better(P,X) :- preference(P,poset), required(P,better), 
               poset(P,X), holds(X), not holds'(X).

notbetter(P) :- preference(P,poset), required(P,better),
                poset(P,X), not holds(X), holds'(X),
                not better(P,Y) : poset(P,Y,X).

better(P) :- preference(P,poset), required(P,better),
             1 #sum { 1: better(P,X) }, not notbetter(P).

% bettereq
required(P,eq)        :- preference(P,poset), required(P,bettereq).
required(P,better)    :- preference(P,poset), required(P,bettereq).
bettereq(P)  :- preference(P,poset), required(P,bettereq),
                1 #sum { 1: eq(P); 1: better(P) }.

% eq
eq(P) :- preference(P,poset), required(P,eq),
         holds(X) : poset(P,X), holds'(X);
         not holds(X) : poset(P,X), not holds'(X).


% worseeq
required(P,eq)    :- preference(P,poset), required(P,worseeq).
required(P,worse) :- preference(P,poset), required(P,worseeq).
worseeq(P)  :- preference(P,poset), required(P,worseeq),
               1 #sum { 1: eq(P); 1: worse(P) }.


% worse
worse(P,X) :- preference(P,poset), required(P,worse),
              poset(P,X), holds'(X), not holds(X).

notworse(P) :- preference(P,poset), required(P,worse),
               poset(P,X), not holds'(X), holds(X),
		       not worse(P,Y) : poset(P,Y,X).

worse(P) :- preference(P,poset), required(P,worse),
            1 #sum { 1: worse(P,X) }, not notworse(P).

% unc
required(P,bettereq) :- preference(P,poset), required(P,unc).
required(P,worseeq)  :- preference(P,poset), required(P,unc).
unc(P) :- preference(P,poset), required(P,unc),
          not bettereq(P), not worseeq(P).

% errors
error_type(poset,no_naming).
error_type(poset,no_weights).
error_type(poset,no_sets).
error_type(poset,no_condition).

#program preference(subset).

better(P) :- preference(P,subset); required(P,better); 
                not holds(X) : preference(P,_,_,for(X),_), not holds'(X);
                1 #sum { 1 : not holds(X), holds'(X), preference(P,_,_,for(X),_)}.

bettereq(P) :- preference(P,subset); required(P,bettereq); 
                  not holds(X) : preference(P,_,_,for(X),_), not holds'(X).

required(P,bettereq) :- preference(P,subset); required(P,eq). 
required(P,worseeq)     :- preference(P,subset); required(P,eq). 
eq(P) :- preference(P,subset); required(P,eq); 
         bettereq(P); worseeq(P).

worseeq(P) :- preference(P,subset); required(P,worseeq); 
              holds(X) : preference(P,_,_,for(X),_), holds'(X).

worse(P) :- preference(P,subset); required(P,worse); 
            holds(X) : preference(P,_,_,for(X),_), holds'(X);
            1 #sum { 1 : holds(X), not holds'(X), preference(P,_,_,for(X),_)}.

required(P,bettereq) :- preference(P,subset); required(P,unc). 
required(P,worseeq)     :- preference(P,subset); required(P,unc). 
unc(P) :- preference(P,subset); required(P,unc); 
          not bettereq(P); not worseeq(P).

% errors
error_type(subset,no_naming).
error_type(subset,no_ordering).
error_type(subset,no_condition).
error_type(subset,no_weights).
error_type(subset,no_sets).


#program preference(superset).

better(P) :- preference(P,superset); required(P,better); 
                holds(X) : preference(P,_,_,for(X),_), holds'(X);
                1 #sum { 1 : holds(X), not holds'(X), preference(P,_,_,for(X),_)}.

bettereq(P) :- preference(P,superset); required(P,bettereq); 
                  holds(X) : preference(P,_,_,for(X),_), holds'(X).

required(P,bettereq) :- preference(P,superset); required(P,eq). 
required(P,worseeq)     :- preference(P,superset); required(P,eq). 
eq(P) :- preference(P,superset); required(P,eq); 
         bettereq(P); worseeq(P).

worseeq(P) :- preference(P,superset); required(P,worseeq); 
              not holds(X) : preference(P,_,_,for(X),_), not holds'(X).

worse(P) :- preference(P,superset); required(P,worse); 
            not holds(X) : preference(P,_,_,for(X),_), not holds'(X);
            1 #sum { 1 : not holds(X), holds'(X), preference(P,_,_,for(X),_)}.

required(P,bettereq) :- preference(P,superset); required(P,unc). 
required(P,worseeq)     :- preference(P,superset); required(P,unc). 
unc(P) :- preference(P,superset); required(P,unc); 
          not bettereq(P); not worseeq(P).

% errors
error_type(superset,no_naming).
error_type(superset,no_ordering).
error_type(superset,no_condition).
error_type(superset,no_weights).
error_type(superset,no_sets).

#program preference(clingo_minimize).

level(P,L) :- preference(P,clingo_minimize), preference(P,_,_,_,T), L = @second(T).
           
better(P) :- preference(P,clingo_minimize),
             level(P,L), better(P,L), 
             eq(P,LL) : level(P,LL), LL>L.

bettereq(P) :- better(P), preference(P,clingo_minimize).
bettereq(P) :-     eq(P), preference(P,clingo_minimize).

eq(P) :- preference(P,clingo_minimize),
         eq(P,L) : level(P,L).
           
worseeq(P) :-    eq(P), preference(P,clingo_minimize).
worseeq(P) :- worse(P), preference(P,clingo_minimize).
           
worse(P) :- preference(P,clingo_minimize),
           level(P,L), worse(P,L), 
           eq(P,LL) : level(P,LL), LL>L.

better(P,L) :- preference(P,clingo_minimize), required(P,better), level(P,L),
  1 #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @head(T), L=@second(T); 
            W,T : holds'(X), preference(P,_,_,for(X),T), W = @head(T), L=@second(T)}.

bettereq(P,L) :- preference(P,clingo_minimize), required(P,better), level(P,L),
  0 #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @head(T), L=@second(T); 
            W,T : holds'(X), preference(P,_,_,for(X),T), W = @head(T), L=@second(T)}.

eq(P,L) :- preference(P,clingo_minimize), required(P,better), level(P,L),
  0 #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @head(T), L=@second(T); 
            W,T : holds'(X), preference(P,_,_,for(X),T), W = @head(T), L=@second(T)}0.

worseeq(P,L) :- preference(P,clingo_minimize), required(P,better), level(P,L),
  #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @head(T), L=@second(T); 
          W,T : holds'(X), preference(P,_,_,for(X),T), W = @head(T), L=@second(T)}0.

worse(P,L) :- preference(P,clingo_minimize), required(P,better), level(P,L),
  #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @head(T), L=@second(T); 
          W,T : holds'(X), preference(P,_,_,for(X),T), W = @head(T), L=@second(T)}-1.

% errors
error_type(clingo_minimize,no_naming).
error_type(clingo_minimize,no_ordering).
error_type(clingo_minimize,no_condition).
error_type(clingo_minimize,no_sets).


#program preference. % to avoid warnings

better(P)     :- #false, better(P).
required(P,Q) :- #false, required(P,Q).

error(X) :- #false, error(X).
error_type(X,Y) :- #false, error_type(X,Y).

