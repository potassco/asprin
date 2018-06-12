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
  preference(P,T), error_type(T,no_condition),
  preference(P,_,0,_,_).

% weights length
error(("preference:",P,": error: preference specification error, type '",T,"' requires a weight tuple of at least ",N," elements.")) :-
  preference(P,T), error_type(T,(min_weight_length,N)),
  preference(P,_,_,_,W), @length(W) < N.

% weights length
error(("preference:",P,": error: preference specification error, type '",T,"' requires a weight tuple of at most ",N," elements.")) :-
  preference(P,T), error_type(T,(max_weight_length,N)),
  preference(P,_,_,_,W), @length(W) > N.

% naming unique weights
error(("preference:",P,": error: preference specification error, type '",T,"' requires different weights for every named preference statement")) :- 
  preference(P,T), error_type(T,naming_unique_weights),
  preference(P,_,_,name(P1),W), 
  preference(P,_,_,name(P2),W), P1 != P2.

%
% Python functions
%
% asprin provides the following functions,
% which are part of src/solver/solver.py,
% and may be called using @function() syntax
% (see, for example, less(weight) preference program)
%

%
%    def get(self, atuple, index):
%        try:
%            return atuple.arguments[index]
%        except:
%            return atuple
%
%    def length(self, atuple):
%        try:
%            return len(atuple.arguments)
%        except:
%            return 1
%
%    def log2up(x):
%        return int(math.ceil(math.log(x.number,2)))
%
%    def get_sequence(self, name, elem):
%        string = str(name)
%        # self.sequences is initially {}
%        if string in self.sequences:
%            self.sequences[string] += 1
%        else:
%            self.sequences[string]  = 1
%        return self.sequences[string]
%

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

rule(P,Id,L) :- preference(P,aso), required(P,_),
                preference(P,Id,_,_,_),
                L = #max{ H : preference(P,Id,H,_,_)}, L>1.

index(P,Id,1..L-1) :- preference(P,aso), required(P,_),
                      preference(P,Id,_,_,_),
                      L = #max{ H : preference(P,Id,H,_,_) }.

nohead(P,Id)  :- preference(P,aso), required(P,_),
                 rule(P,Id,_),
                 not holds(X) : preference(P,Id,H,for(X),_), H!=0.
nohead'(P,Id) :- preference(P,aso), required(P,_),
                 rule(P,Id,_),
                 not holds'(X) : preference(P,Id,H,for(X),_), H!=0.

aso(P,Id,R) :- 
  preference(P,aso),
  rule(P,Id,_),
  required(P,R,L,U),
  L #sum{  1,Idx : not holds(X), preference(P,Id,0,for(X),_), index(P,Id,Idx);
           1,Idx : nohead(P,Id), index(P,Id,Idx);
           1,Idx : holds(X), preference(P,Id,Pos,for(X),_), Pos != 0, index(P,Id,Idx), Idx>=Pos;
          -1,Idx : not holds'(X), preference(P,Id,0,for(X),_), index(P,Id,Idx);
          -1,Idx : nohead'(P,Id), index(P,Id,Idx);
          -1,Idx : holds'(X), preference(P,Id,Pos,for(X),_), Pos != 0, index(P,Id,Idx), Idx>=Pos} U.

required(P,  better,   1,#sup) :- preference(P,aso), required(P,aso,  better).
required(P,bettereq,   0,#sup) :- preference(P,aso), required(P,aso,bettereq).
required(P,      eq,   0,   0) :- preference(P,aso), required(P,aso,      eq).
required(P, worseeq,#inf,   0) :- preference(P,aso), required(P,aso, worseeq).
required(P,   worse,#inf,  -1) :- preference(P,aso), required(P,aso,   worse).

required(P,aso,better)   :- preference(P,aso), required(P,better).
required(P,aso,bettereq) :- preference(P,aso), required(P,better).
better(P) :- preference(P,aso), required(P,better),
             aso(P,Id1,bettereq) : rule(P,Id1,_);
             aso(P,Id2,  better),  rule(P,Id2,_).

required(P,aso,bettereq) :- preference(P,aso), required(P,bettereq).
bettereq(P) :- preference(P,aso), required(P,bettereq),
               aso(P,Id,bettereq) : rule(P,Id,_).

required(P,aso,eq) :- preference(P,aso), required(P,eq).
eq(P) :- preference(P,aso), required(P,eq),
         aso(P,Id,eq) : rule(P,Id,_).

required(P,aso,worseeq) :- preference(P,aso), required(P,worseeq).
worseeq(P) :- preference(P,aso), required(P,worseeq),
              aso(P,Id,worseeq) : rule(P,Id,_).

required(P,aso,worseeq) :- preference(P,aso), required(P,worse).
required(P,aso,worse)   :- preference(P,aso), required(P,worse).
worse(P) :- preference(P,aso), required(P,worse),
            aso(P,Id1,worseeq) : rule(P,Id1,_);
            aso(P,Id2,  worse),  rule(P,Id2,_).

% errors
error_type(aso,no_naming).
error_type(aso,no_weights).
error_type(aso,no_sets).


#program preference(less(cardinality)).

better(P) :- preference(P,less(cardinality)), required(P,better),
             1 #sum { -1,X : holds(X),  preference(P,_,_,for(X),_);
                       1,X : holds'(X), preference(P,_,_,for(X),_)}.

bettereq(P) :- preference(P,less(cardinality)), required(P,bettereq),
               0 #sum { -1,X : holds(X),  preference(P,_,_,for(X),_);
                         1,X : holds'(X), preference(P,_,_,for(X),_)}.

eq(P) :- preference(P,less(cardinality)), required(P,eq),
         0 #sum { -1,X : holds(X),  preference(P,_,_,for(X),_); 
                   1,X : holds'(X), preference(P,_,_,for(X),_)} 0.

worseeq(P) :- preference(P,less(cardinality)), required(P,worseeq),
              #sum { -1,X : holds(X),  preference(P,_,_,for(X),_);
                      1,X : holds'(X), preference(P,_,_,for(X),_)} 0.

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
             1 #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @get(T,0); 
                       W,T : holds'(X), preference(P,_,_,for(X),T), W = @get(T,0)}.

bettereq(P) :- preference(P,less(weight)), required(P,bettereq),
               0 #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @get(T,0); 
                         W,T : holds'(X), preference(P,_,_,for(X),T), W = @get(T,0)}. 

eq(P) :- preference(P,less(weight)), required(P,eq),
         0 #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @get(T,0); 
                   W,T : holds'(X), preference(P,_,_,for(X),T), W = @get(T,0)}0. 

worseeq(P) :- preference(P,less(weight)), required(P,worseeq),
              #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @get(T,0); 
                      W,T : holds'(X), preference(P,_,_,for(X),T), W = @get(T,0)}0.

worse(P) :- preference(P,less(weight)), required(P,worse),
            #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @get(T,0); 
                    W,T : holds'(X), preference(P,_,_,for(X),T), W = @get(T,0)}-1.

% errors
error_type(less(weight),no_naming).
error_type(less(weight),no_ordering).
error_type(less(weight),no_condition).
error_type(less(weight),no_sets).

#program preference(lexico).

many(P) :- preference(P,lexico), 
           2 #sum { 1,Q: preference(P,_,_,name(Q),_) }.

required(Q,better) :- preference(P,lexico), required(P,better), preference(P,_,_,name(Q),_).
required(Q,eq)     :- preference(P,lexico), required(P,better), preference(P,_,_,name(Q),_),
                      many(P).

better(P) :- preference(P,lexico), required(P,better),
             better(R); preference(P,_,_,name(R),(L));
             eq(Q)    : preference(P,_,_,name(Q),(LL)), LL > L, many(P).

required(P,better) :- preference(P,lexico), required(P,bettereq).
required(P,eq)     :- preference(P,lexico), required(P,bettereq).
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
required(Q,eq)    :- preference(P,lexico), required(P,worse), preference(P,_,_,name(Q),_), 
                     many(P).
worse(P) :- preference(P,lexico), required(P,worse),
            worse(R); preference(P,_,_,name(R),(L));
            eq(Q) : preference(P,_,_,name(Q),(LL)), LL > L, many(P).

required(P,bettereq) :- preference(P,lexico), required(P,unc). 
required(P,worseeq)     :- preference(P,lexico), required(P,unc). 
unc(P) :- preference(P,lexico); required(P,unc); 
          not bettereq(P); not worseeq(P).

% errors
error_type(lexico,no_formulas).
error_type(lexico,no_ordering).
error_type(lexico,no_condition).
error_type(lexico,no_sets).
error_type(lexico,(min_weight_length,1)).
error_type(lexico,(max_weight_length,1)).
error_type(lexico,naming_unique_weights).

#program preference(more(cardinality)).

better(P) :- preference(P,more(cardinality)), required(P,better),
             #sum { -1,X : holds(X),  preference(P,_,_,for(X),_); 
                     1,X : holds'(X), preference(P,_,_,for(X),_)}-1.

bettereq(P) :- preference(P,more(cardinality)), required(P,bettereq),
               #sum { -1,X : holds(X),  preference(P,_,_,for(X),_); 
                       1,X : holds'(X), preference(P,_,_,for(X),_)} 0.

eq(P) :- preference(P,more(cardinality)), required(P,eq),
         0 #sum { -1,X : holds(X),  preference(P,_,_,for(X),_); 
                   1,X : holds'(X), preference(P,_,_,for(X),_)}0. 

worseeq(P) :- preference(P,more(cardinality)), required(P,worseeq),
              0 #sum { -1,X : holds(X),  preference(P,_,_,for(X),_);
                        1,X : holds'(X), preference(P,_,_,for(X),_)}.

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
             #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @get(T,0);
                     W,T : holds'(X), preference(P,_,_,for(X),T), W = @get(T,0)}-1.

bettereq(P) :- preference(P,more(weight)), required(P,bettereq),
               #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @get(T,0);
                       W,T : holds'(X), preference(P,_,_,for(X),T), W = @get(T,0)}0.

eq(P) :- preference(P,more(weight)), required(P,eq),
         0 #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @get(T,0);
                   W,T : holds'(X), preference(P,_,_,for(X),T), W = @get(T,0)}0.

worseeq(P) :- preference(P,more(weight)), required(P,worseeq),
              0 #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @get(T,0);
                        W,T : holds'(X), preference(P,_,_,for(X),T), W = @get(T,0)}.

worse(P) :- preference(P,more(weight)), required(P,worse),
            1 #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @get(T,0);
                      W,T : holds'(X), preference(P,_,_,for(X),T), W = @get(T,0)}.
                     
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

many(P) :- preference(P,pareto),
           2 #sum { 1,Q: preference(P,_,_,name(Q),_) }.

required(Q,better)   :- preference(P,pareto), required(P,better), preference(P,_,_,name(Q),_).
required(Q,bettereq) :- preference(P,pareto), required(P,better), preference(P,_,_,name(Q),_),
                        many(P).

better(P) :- preference(P,pareto), required(P,better),
             bettereq(Q) : preference(P,_,_,name(Q),_), many(P);
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
required(Q,worseeq) :- preference(P,pareto), required(P,worse), preference(P,_,_,name(Q),_),
                       many(P).
worse(P) :- preference(P,pareto), required(P,worse),
            worseeq(Q) : preference(P,_,_,name(Q),_), many(P);
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
#const tc_poset=1.
poset(P,X,Y) :- preference(P,poset), required(P,noteq),
                poset(P,X,Z), poset(P,Z,Y), tc_poset=1.

% better

better(P,X) :- preference(P,poset), required(P,better), 
               poset(P,X), holds(X), not holds'(X).

notbetter(P) :- preference(P,poset), required(P,better),
                poset(P,X), not holds(X), holds'(X),
                not better(P,Y) : poset(P,Y,X).

better(P) :- preference(P,poset), required(P,better),
             better(P,_), not notbetter(P).

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
%%% poset relation must be strict
error(("preference:",P,
  ": error: preference specification error, type 'poset', ",
  "the order relation defined by the preference elements must be acyclic.")) :-
  preference(P,poset), poset(P,X,X).

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

required(P) :- preference(P,clingo_minimize), required(P,_).

level(P,L) :- preference(P,clingo_minimize), required(P),
              preference(P,_,_,_,T), L = @get(T,1).

two_levels(P) :- preference(P,clingo_minimize), required(P),
                 level(P,L), level(P,LL), LL > L.

% better
required_level(P,better) :- preference(P,clingo_minimize), required(P,better).
required_level(P,    eq) :- preference(P,clingo_minimize), required(P,better),
                            two_levels(P).
better(P) :- preference(P,clingo_minimize), required(P,better),
             level(P,L), better(P,L), 
             eq(P,LL) : level(P,LL), LL>L.

% bettereq
required(P,better) :- preference(P,clingo_minimize), required(P,bettereq).
required(P,    eq) :- preference(P,clingo_minimize), required(P,bettereq).
bettereq(P) :- preference(P,clingo_minimize), required(P,bettereq),
               better(P).
bettereq(P) :- preference(P,clingo_minimize), required(P,bettereq),
               eq(P).

% eq
required_level(P,eq) :- preference(P,clingo_minimize), required(P,eq).
eq(P) :- preference(P,clingo_minimize), required(P,eq),
         eq(P,L) : level(P,L).
           
% worseeq
required(P,worse) :- preference(P,clingo_minimize), required(P,worseeq).
required(P,   eq) :- preference(P,clingo_minimize), required(P,worseeq).
worseeq(P) :- preference(P,clingo_minimize), required(P,worseeq),
              worse(P).
worseeq(P) :- preference(P,clingo_minimize), required(P,worseeq),
              eq(P).

% worse
required_level(P,worse) :- preference(P,clingo_minimize), required(P,worse).
required_level(P,   eq) :- preference(P,clingo_minimize), required(P,worse), 
                           two_levels(P).
worse(P) :- preference(P,clingo_minimize), required(P,worse),
            level(P,L), worse(P,L), 
            eq(P,LL) : level(P,LL), LL>L.

% levels: better, eq and worse
better(P,L) :- preference(P,clingo_minimize), required_level(P,better), level(P,L),
  1 #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @get(T,0), L=@get(T,1); 
            W,T : holds'(X), preference(P,_,_,for(X),T), W = @get(T,0), L=@get(T,1)}.

eq(P,L) :- preference(P,clingo_minimize), required_level(P,eq), level(P,L),
  0 #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @get(T,0), L=@get(T,1); 
            W,T : holds'(X), preference(P,_,_,for(X),T), W = @get(T,0), L=@get(T,1)}0.

worse(P,L) :- preference(P,clingo_minimize), required_level(P,worse), level(P,L),
  #sum { -W,T : holds(X),  preference(P,_,_,for(X),T), W = @get(T,0), L=@get(T,1); 
          W,T : holds'(X), preference(P,_,_,for(X),T), W = @get(T,0), L=@get(T,1)}-1.

% errors
error_type(clingo_minimize,no_naming).
error_type(clingo_minimize,no_ordering).
error_type(clingo_minimize,no_condition).
error_type(clingo_minimize,no_sets).


#program preference(maxmin).

%%% get groups
group(P,@get(T,0)) :- preference(P,maxmin), preference(P,_,_,_,T).

% value of holds'
value_h'(P,V)   :- preference(P,maxmin), V = #min { VV : value_h'(P,G,VV) }.
value_h'(P,G,V) :- preference(P,maxmin), group(P,G),
  V = #sum { W,T : holds'(X), preference(P,_,_,for(X),T),
                   G = @get(T,0), W = @get(T,1) }.

% bettereq/2 and worseeq/2 for every group
bettereq(P,G) :- preference(P,maxmin), group(P,G), value_h'(P,V),
  V <= #sum { W,T : holds(X), preference(P,_,_,for(X),T), 
                    G = @get(T,0), W = @get(T,1) }.
worseeq(P,G) :- preference(P,maxmin), group(P,G), value_h'(P,V),
  V >= #sum { W,T : holds(X), preference(P,_,_,for(X),T), 
                    G = @get(T,0), W = @get(T,1) }.

% better/1, bettereq/1, eq/1, worseeq/1, worse/1
better(P) :- preference(P,maxmin), required(P,better), 
             group(P,_), not worseeq(P,G) : group(P,G).

bettereq(P) :- preference(P,maxmin), required(P,bettereq),
               bettereq(P,G) : group(P,G).

required(P,bettereq) :- preference(P,maxmin), required(P,eq).
required(P,worseeq)  :- preference(P,maxmin), required(P,eq).
eq(P) :- preference(P,maxmin), required(P,eq),
         bettereq(P), worseeq(P).

worseeq(P) :- preference(P,maxmin), required(P,worseeq),
              worseeq(P,G).
worseeq(P) :- preference(P,maxmin), required(P,worseeq),
              not group(P,_).

worse(P) :- preference(P,maxmin), required(P,worse),
            worseeq(P,G), not bettereq(P,G).

% errors
error_type(maxmin,no_naming).
error_type(maxmin,no_ordering).
error_type(maxmin,no_condition).
error_type(maxmin,no_sets).
error_type(maxmin,(min_weight_length,2)).

#program preference(minmax).

%%% get groups
group(P,@get(T,0)) :- preference(P,minmax), preference(P,_,_,_,T).

% value of holds'
value_h'(P,V)   :- preference(P,minmax), V = #max { VV : value_h'(P,G,VV) }.
value_h'(P,G,V) :- preference(P,minmax), group(P,G),
  V = #sum { W,T : holds'(X), preference(P,_,_,for(X),T),
                   G = @get(T,0), W = @get(T,1) }.

% bettereq/2 and worseeq/2 for every group
bettereq(P,G) :- preference(P,minmax), group(P,G), value_h'(P,V),
  V >= #sum { W,T : holds(X), preference(P,_,_,for(X),T), 
                    G = @get(T,0), W = @get(T,1) }.
worseeq(P,G) :- preference(P,minmax), group(P,G), value_h'(P,V),
  V <= #sum { W,T : holds(X), preference(P,_,_,for(X),T), 
                    G = @get(T,0), W = @get(T,1) }.

% better/1, bettereq/1, eq/1, worseeq/1, worse/1
better(P) :- preference(P,minmax), required(P,better),
             group(P,_), not worseeq(P,G) : group(P,G).

bettereq(P) :- preference(P,minmax), required(P,bettereq),
               bettereq(P,G) : group(P,G).

required(P,bettereq) :- preference(P,minmax), required(P,eq).
required(P,worseeq)  :- preference(P,minmax), required(P,eq).
eq(P) :- preference(P,minmax), required(P,eq),
         bettereq(P), worseeq(P).

worseeq(P) :- preference(P,minmax), required(P,worseeq),
              worseeq(P,G).
worseeq(P) :- preference(P,minmax), required(P,worseeq),
              not group(P,_).

worse(P) :- preference(P,minmax), required(P,worse),
            worseeq(P,G), not bettereq(P,G).

% errors
error_type(minmax,no_naming).
error_type(minmax,no_ordering).
error_type(minmax,no_condition).
error_type(minmax,no_sets).
error_type(minmax,(min_weight_length,2)).

#program preference. % to avoid warnings

better(P)     :- #false, better(P).
required(P,Q) :- #false, required(P,Q).

error(X) :- #false, error(X).
error_type(X,Y) :- #false, error_type(X,Y).

%
% heuristic approximation programs:
% - used with option --approximation=heuristic
%

#program heuristic.

%
% For some P, the levels L in
%   heuristic(P,_,L,_)
% have the form: 1, 2, ...
%
% To use composite preferences, we have to define
%   levels(P,L)
% where L is the number of (lexico) levels of P
%

% heuristic directive
#heuristic holds(X) : heuristic(P,X,V,M), optimize(P). [V,M]

%
% generate heuristic/4 from wc/5
%

% project wc/5 on wc/2
wc(P,L) :- wc(P,_,L,_,_).

% for P and L, there is a bit at position B
bit(P,L,B) :- wc(P,L),
              S = #sum{  W,T: wc(P,W,L,T,X), W>0;
                        -W,T: wc(P,W,L,T,X), W<0},
              B=0..(@log2up(S+1)-1).

% for P and L, the bit B may hold
{ holds(bit(P,L,B)) } :- wc(P,L), bit(P,L,B).

% for P and L, atoms bit(P,L,B) encode in binary the value of the sum
:- wc(P,L), 0 != #sum{ -(@exp2(B)): holds(bit(P,L,B));
                               W,T: wc(P,W,L,T,X), W>0,     holds(X);
                              -W,T: wc(P,W,L,T,X), W<0, not holds(X)}.

% define heuristic/4 and levels/2
heuristic(P,bit(P,L1,B),1+B+S,false) :- wc(P,L1),
                                        bit(P,L1,B),
                                        S = #sum{ L3,L2: levels_per_level(P,L2,L3), L2<L1 }.
levels_per_level(P,L1,L2) :- wc(P,L1),
                             L2 = #sum{ 1,B: bit(P,L1,B) }.
levels(P,L1) :- wc(P,_),
                L1 = #sum{ L3,L2: levels_per_level(P,L2,L3) }.

% minors
wc(A,B,C,D,E) :- #false, wc(A,B,C,D,E). % to avoid warnings

#program heuristic(subset).
heuristic(P,X,1,false) :- preference(P,subset), preference(P,_,_,for(X),_).
levels(P,1) :- preference(P,subset).

#program heuristic(superset).
heuristic(P,X,1,true) :- preference(P,superset), preference(P,_,_,for(X),_).
levels(P,1) :- preference(P,superset).

#program heuristic(less(cardinality)).
wc(P,1,1,X,X) :- preference(P,less(cardinality)),
                 preference(P,_,_,for(X),_).
levels(P,1) :- preference(P,less(cardinality)).

#program heuristic(more(cardinality)).
wc(P,-1,1,X,X) :- preference(P,more(cardinality)),
                  preference(P,_,_,for(X),_).
levels(P,1) :- preference(P,more(cardinality)).

#program heuristic(less(weight)).
wc(P,@get(T,0),1,T,X) :- preference(P,less(weight)),
                         preference(P,_,_,for(X),T).
levels(P,1) :- preference(P,less(weight)).

#program heuristic(more(weight)).
wc(P,-@get(T,0),1,T,X) :- preference(P,more(weight)),
                          preference(P,_,_,for(X),T).
levels(P,1) :- preference(P,more(weight)).

#program heuristic(clingo_minimize).

% map levels to 1..n
level(P,L1,L) :- preference(P,clingo_minimize),
                 preference(P,_,_,_,T), L1=@get(T,1),
                 L = #sum{1, L2: preference(P,_,_,_,TT), L2=@get(TT,1), L2 <= L1 }.

% define wc/5
wc(P,W,LL,T,X) :- preference(P,clingo_minimize),
                  preference(P,_,_,for(X),T),
                  W=@get(T,0), L=@get(T,1),
                  level(P,L,LL).

% number of levels (overestimation)
levels(P,L) :- preference(P,clingo_minimize),
               L = #max{ LL: level(P,_,LL); 0 }.

#program heuristic(poset).

poset(P,X) :- preference(P,poset),
              preference(P,_,_,for(X),_).

poset(P,X,Y) :- preference(P,poset),
                preference(P,I,1,for(X),_), preference(P,I,2,for(Y),_).

#const heuristic_tc_poset=1.
poset(P,X,Y) :- preference(P,poset),
                poset(P,X,Z), poset(P,Z,Y), heuristic_tc_poset=1.

% 3 options
#const heuristic_poset=2.

% option 1

heuristic(P,X,1,true) :- preference(P,poset), heuristic_poset=1,
                         poset(P,X),
                         assigned(P,Y) : poset(P,Y,X).

assigned(P,X) :- preference(P,poset), heuristic_poset=1,
                 poset(P,X),     holds(X).
assigned(P,X) :- preference(P,poset), heuristic_poset=1,
                 poset(P,X), not holds(X).

levels(P,1) :- preference(P,poset), heuristic_poset=1.

% option 2

step(P,X,1)   :- preference(P,poset), heuristic_poset=2,
                 poset(P,X).
step(P,X,S+1) :- preference(P,poset), heuristic_poset=2,
                 step(P,X,S), step(P,Y,S), poset(P,Y,X).

max_step(P,S) :- preference(P,poset), heuristic_poset=2,
                 step(P,_,S), not step(P,_,S+1).

heuristic(P,X,M-S+1,true) :- preference(P,poset), heuristic_poset=2,
                             max_step(P,M),
                             step(P,X,S), not step(P,X,S+1).

levels(P,M) :- preference(P,poset), heuristic_poset=2,
               max_step(P,M).

% option 3

cost(P,X,C+1) :- preference(P,poset), heuristic_poset=3,
                 poset(P,X),
                 C = #sum{ CC,Y : poset(P,X,Y), cost(P,Y,CC) }.

wc(P,-C,1,X,X) :- cost(P,X,C), heuristic_poset=3.


#program heuristic(aso).

rule(P,Id,L) :- preference(P,aso),
                preference(P,Id,_,_,_),
                L = #max{ H : preference(P,Id,H,_,_)}, L>1.
index(P,Id,1..L-1) :- rule(P,Id,L).

% 3 options
#const heuristic_aso=1.

% options 1 and 2

opt12(P) :- preference(P,aso), heuristic_aso=1.
opt12(P) :- preference(P,aso), heuristic_aso=2.

holds(aso(P,Id,Idx)) :- preference(P,aso), opt12(P),
                        index(P,Id,Idx),
                        not holds(X), preference(P,Id,0,for(X),_).
holds(aso(P,Id,Idx)) :- preference(P,aso), opt12(P),
                        index(P,Id,Idx),
                        not holds(X) : preference(P,Id,H,for(X),_), H!=0.
holds(aso(P,Id,Idx)) :- preference(P,aso), opt12(P),
                        index(P,Id,Idx), Idx>=Pos,
                        holds(X), preference(P,Id,Pos,for(X),_), Pos != 0.

% option 1
heuristic(P,aso(P,Id,Idx),1,true) :- preference(P,aso), heuristic_aso=1,
                                     index(P,Id,Idx).
levels(P,1) :- preference(P,aso), heuristic_aso=1.

% option 2
pos(P,N,Id1)   :- preference(P,aso), heuristic_aso=2,
                  rule(P,Id1,_),
                  N=@get_sequence(("heuristic_aso",P),Id1).

heuristic(P,aso(P,Id,Idx),N,true) :- preference(P,aso), heuristic_aso=2,
                                     index(P,Id,Idx), pos(P,N,Id).
levels(P,N) :- preference(P,aso), heuristic_aso=2,
               pos(P,N,_), not pos(P,N+1,_).


% option 3
holds(aso(P,Id,1))   :- preference(P,aso), heuristic_aso=3,
                        rule(P,Id,L),
                        not holds(X), preference(P,Id,0,for(X),_).
holds(aso(P,Id,1))   :- preference(P,aso), heuristic_aso=3,
                        rule(P,Id,L),
                        not holds(X) : preference(P,Id,Idx,for(X),_), Idx!=0.
holds(aso(P,Id,Idx)) :- preference(P,aso), heuristic_aso=3,
                        rule(P,Id,L), L>Idx,
                        holds(X), preference(P,Id,Idx,for(X),_), Idx!=0,
                        not holds(aso(P,Id,Idx')) : Idx'=1..(Idx-1).

max_index(P,I) :- preference(P,aso), heuristic_aso=3,
                  rule(P,_,I), not rule(P,_,I+1).

heuristic(P,aso(P,Id,Idx),I-Idx+1,true) :- preference(P,aso), heuristic_aso=3,
                                           index(P,Id,Idx), max_index(P,I).
levels(P,I) :- preference(P,aso), heuristic_aso=3,
               max_index(P,I).

%
% minmax and maxmin
%

#program heuristic(minmax).
as_minmax(P)                     :- preference(P,minmax), preference(P,_,_,for(X),T).
elem(P,@get(T,0), @get(T,1),T,X) :- preference(P,minmax), preference(P,_,_,for(X),T).

#program heuristic(maxmin).
as_minmax(P)                     :- preference(P,maxmin), preference(P,_,_,for(X),T).
elem(P,@get(T,0),-@get(T,1),T,X) :- preference(P,maxmin), preference(P,_,_,for(X),T).

#program heuristic. % (as_minmax, uses as_minmax/1 and elem/5

% for P, in group G, there is a bit at position B
bit(P,G,B) :- as_minmax(P), elem(P,G,_,_,_),
              S = #sum{  W,T: elem(P,G,W,T,X), W>0;
                        -W,T: elem(P,G,W,T,X), W<0},
              B=0..(@log2up(S+1)-1).

% for P, in group G, the bit B may be true
{ true(bit(P,G,B)) } :- as_minmax(P), bit(P,G,B).

% for P, in group G, atoms bit(P,G,B) encode in binary the value of the group
:- as_minmax(P), elem(P,G,_,_,_),
   0 != #sum{ -(@exp2(B)): true(bit(P,G,B));
               W,T: elem(P,G,W,T,X), W>0,     holds(X);
              -W,T: elem(P,G,W,T,X), W<0, not holds(X)}.

% for P, bit B holds if it is true at some group which is not not-maximal
holds(bit(P,B))  :- as_minmax(P),    true(bit(P,G,B)), not not_max(P,G,B).

% for P, define when group G is not-maximal before bit B
not_max(P,G,B-1) :- as_minmax(P), not true(bit(P,G,B)),  holds(bit(P,B)), B>0,
                    elem(P,G,_,_,_).
not_max(P,G,B-1) :- as_minmax(P), not_max(P,G,B), B>0.

% define heuristic/4 and levels/2
heuristic(P,bit(P,B),B+1,false) :- as_minmax(P), bit(P,_,B).
levels(P,L) :- as_minmax(P), L = #sum{ 1,B: bit(P,_,B) }.

% to avoid warnings
as_minmax(P)    :- #false,    as_minmax(P).
elem(A,B,C,D,E) :- #false, elem(A,B,C,D,E).


%
% composite preference heuristic
%

#program heuristic(neg).
heuristic(P,X,L,MM) :- preference(P,neg), preference(P,_,_,name(PP),_),
                       heuristic(PP,X,L,M), inverse(P,M,MM).
inverse(P,true,false) :- preference(P,neg).
inverse(P,false,true) :- preference(P,neg).
levels(P,L) :- preference(P,neg), preference(P,_,_,name(PP),_), levels(PP,L).

#program heuristic.  % (as lexico, uses as_lexico/1 and level/3)

heuristic(P,X,L+S,M) :- as_lexico(P),
                        level(P,P1,L1),
                        heuristic(P1,X,L,M),
                        S = #sum{ LS2,P2,L2: level(P,P2,L2), L2 < L1,
                                             levels(P2,LS2)         }.

% max level
max_level(P,MAX) :- as_lexico(P),
                    MAX = #max { L: level(P,_,L) }.

% start
sum_levels(P,MIN-1,0)  :- as_lexico(P),
                          MIN = #min { L: level(P,_,L) }.
% progress
sum_levels(P,L+1,   S) :- as_lexico(P),
                          sum_levels(P,L,S),
                          max_level(P,MAX), L < MAX.
sum_levels(P,L+1,SS+S) :- as_lexico(P),
                          sum_levels(P,L,S),
                          level(P,P1,L+1), levels(P1,SS).
% sum up
levels(P,S) :- as_lexico(P),
               max_level(P,MAX), S = #max{ SS: sum_levels(P,MAX,SS); 0 }.
               % 0 is added to avoid warnings, but it is not needed

% to avoid warnings
as_lexico(P) :- #false, as_lexico(P).
level(A,B,C) :- #false, level(A,B,C).

#program heuristic(lexico).

%%%
%%% With the next commented rule
%%% clingo does not terminate grounding because of recursion through heuristic/4
%%%
%%% heuristic(P,X,L+O,M) :- preference(P,lexico),
%%%                         preference(P,_,_,name(P1),L1), P != P1,
%%%                         heuristic(P1,X,L,M),
%%%                         O = #sum{ L3,L2 : preference(P,_,_,name(P2),L2),
%%%                                           L2 < L1, P2 != P, P2 != P1,
%%%                                           heuristic(P2,_,L3,_)}.
%%% 

as_lexico(P)  :- preference(P,lexico).
level(P,P1,L) :- preference(P,lexico),
                 preference(P,_,_,name(P1),L).

#program heuristic(pareto).

% 2 options
#const heuristic_pareto=2.

% option 1
heuristic(P,X,L,M) :- preference(P,pareto), heuristic_pareto=1,
                      preference(P,_,_,name(P1),_),
                      heuristic(P1,X,L,M).

% option 2 (as lexico)
as_lexico(P)  :- preference(P,pareto), heuristic_pareto=2.
level(P,P1,L) :- preference(P,pareto), heuristic_pareto=2,
                 preference(P,_,_,name(P1),_),
                 L = #sum{1, P2: preference(P,_,_,name(P2),_), P2 <= P1 }.

#program heuristic(and).

% 2 options
#const heuristic_and=2.

% option 1

heuristic(P,X,L,M) :- preference(P,and), heuristic_and=1,
                      preference(P,_,_,name(P1),_),
                      heuristic(P1,X,L,M).

% option 2 (as lexico)
as_lexico(P)  :- preference(P,and), heuristic_and=2.
level(P,P1,L) :- preference(P,and), heuristic_and=2,
                 preference(P,_,_,name(P1),_),
                 L = #sum{1, P2: preference(P,_,_,name(P2),_), P2 <= P1 }.

%
% weak approximation programs:
% - used with option --approximation=weak
%

#program weak.

%
% For some P, the levels L in
%   wc(P,_,L,_,_)
% have the form: 1, 2, ...
%
% To use composite preferences, we have to define
%   levels(P,L)
% where L is the number of (lexico) levels of P
%

:~ wc(P,W,L,T,X), optimize(P), holds(X). [W@L,T]

% minors
wc(A,B,C,D,E) :- #false, wc(A,B,C,D,E). % to avoid warnings

#program weak(subset).
wc(P,1,1,X,X) :- preference(P,subset), preference(P,_,_,for(X),_).
levels(P,1) :- preference(P,subset).

#program weak(superset).
wc(P,-1,1,X,X) :- preference(P,superset), preference(P,_,_,for(X),_).
levels(P,1) :- preference(P,superset).

#program weak(less(cardinality)).
wc(P,1,1,X,X) :- preference(P,less(cardinality)), preference(P,_,_,for(X),_).
levels(P,1) :- preference(P,less(cardinality)).

#program weak(more(cardinality)).
wc(P,-1,1,X,X) :- preference(P,more(cardinality)), preference(P,_,_,for(X),_).
levels(P,1) :- preference(P,more(cardinality)).

#program weak(less(weight)).
wc(P,W,1,T,X) :- preference(P,less(weight)), preference(P,_,_,for(X),T),
                 W=@get(T,0).
levels(P,1) :- preference(P,less(weight)).

#program weak(more(weight)).
wc(P,-W,1,T,X) :- preference(P,more(weight)), preference(P,_,_,for(X),T),
                  W=@get(T,0).
levels(P,1) :- preference(P,more(weight)).

%
% clingo minimize
%

#program weak(clingo_minimize).

% map levels to 1..n
level(P,L1,L) :- preference(P,clingo_minimize),
                 preference(P,_,_,_,T), L1=@get(T,1),
                 L = #sum{1, L2: preference(P,_,_,_,TT), L2=@get(TT,1), L2 <= L1 }.

% define wc/5
wc(P,W,LL,T,X) :- preference(P,clingo_minimize),
                  preference(P,_,_,for(X),T),
                  W=@get(T,0), L=@get(T,1),
                  level(P,L,LL).

% number of levels (overestimation)
levels(P,L) :- preference(P,clingo_minimize),
               L = #max{ LL: level(P,_,LL); 0 }.


%
% minmax and maxmin
%

#program weak(minmax).
as_minmax(P)                     :- preference(P,minmax), preference(P,_,_,for(X),T).
elem(P,@get(T,0), @get(T,1),T,X) :- preference(P,minmax), preference(P,_,_,for(X),T).

#program weak(maxmin).
as_minmax(P)                     :- preference(P,maxmin), preference(P,_,_,for(X),T).
elem(P,@get(T,0),-@get(T,1),T,X) :- preference(P,maxmin), preference(P,_,_,for(X),T).

#program weak. % (as_minmax, uses as_minmax/1 and elem/5

% for P, in group G, there is a bit at position B
bit(P,G,B) :- as_minmax(P), elem(P,G,_,_,_),
              S = #sum{  W,T: elem(P,G,W,T,X), W>0;
                        -W,T: elem(P,G,W,T,X), W<0},
              B=0..(@log2up(S+1)-1).

% for P, in group G, the bit B may be true
{ true(bit(P,G,B)) } :- as_minmax(P), bit(P,G,B).

% for P, in group G, atoms bit(P,G,B) encode in binary the value of the group
:- as_minmax(P), elem(P,G,_,_,_),
   0 != #sum{ -(@exp2(B)): true(bit(P,G,B));
               W,T: elem(P,G,W,T,X), W>0,     holds(X);
              -W,T: elem(P,G,W,T,X), W<0, not holds(X)}.

% for P, bit B holds if it is true at some group which is not not-maximal
holds(bit(P,B))  :- as_minmax(P),    true(bit(P,G,B)), not not_max(P,G,B).

% for P, define when group G is not-maximal before bit B
not_max(P,G,B-1) :- as_minmax(P), not true(bit(P,G,B)),  holds(bit(P,B)), B>0,
                    elem(P,G,_,_,_).
not_max(P,G,B-1) :- as_minmax(P), not_max(P,G,B), B>0.

% map to weak constraints
wc(P,1,B+1,0,bit(P,B)) :- as_minmax(P), bit(P,_,B).
levels(P,L) :- as_minmax(P), L = #sum{ 1,B: bit(P,_,B) }.

% to avoid warnings
as_minmax(P)    :- #false,    as_minmax(P).
elem(A,B,C,D,E) :- #false, elem(A,B,C,D,E).


%
% aso
%
#program weak(aso).

rule(P,Id,L) :- preference(P,aso),
                preference(P,Id,_,_,_),
                L = #max{ H : preference(P,Id,H,_,_)}, L>1.
index(P,Id,1..L-1) :- rule(P,Id,L).

% 3 options
#const approx_aso=1.

% options 1 and 2

opt12(P) :- preference(P,aso), approx_aso=1.
opt12(P) :- preference(P,aso), approx_aso=2.

holds(aso(P,Id,Idx)) :- preference(P,aso), opt12(P),
                        index(P,Id,Idx),
                        not holds(X), preference(P,Id,0,for(X),_).
holds(aso(P,Id,Idx)) :- preference(P,aso), opt12(P),
                        index(P,Id,Idx),
                        not holds(X) : preference(P,Id,H,for(X),_), H!=0.
holds(aso(P,Id,Idx)) :- preference(P,aso), opt12(P),
                        index(P,Id,Idx), Idx>=Pos,
                        holds(X), preference(P,Id,Pos,for(X),_), Pos != 0.

% option 1
levels(P,1)                       :- preference(P,aso), approx_aso=1.
wc(P,-1,1,(Id,Idx),aso(P,Id,Idx)) :- preference(P,aso), approx_aso=1,
                                     index(P,Id,Idx).
% option 2 (to lexico)
pos(P,N,Id)   :- preference(P,aso), approx_aso=2,
                 rule(P,Id,_),
                 N=@get_sequence(("weak_aso",P),Id).

levels(P,L)                        :- preference(P,aso), approx_aso=2,
                                      L = #sum{ 1,Id: rule(P,Id,_) }.
wc(P,-1,N,Idx,aso(P,Id,Idx)) :- preference(P,aso), approx_aso=2,
                                index(P,Id,Idx), pos(P,N,Id).


% option 3 (to lexico)
holds(aso(P,Id,1))   :- preference(P,aso), approx_aso=3,
                        rule(P,Id,L),
                        not holds(X), preference(P,Id,0,for(X),_).
holds(aso(P,Id,1))   :- preference(P,aso), approx_aso=3,
                        rule(P,Id,L),
                        not holds(X) : preference(P,Id,Idx,for(X),_), Idx!=0.
holds(aso(P,Id,Idx)) :- preference(P,aso), approx_aso=3,
                        rule(P,Id,L), L>Idx,
                        holds(X), preference(P,Id,Idx,for(X),_), Idx!=0,
                        not holds(aso(P,Id,Idx')) : Idx'=1..(Idx-1).

levels(P,L) :- preference(P,aso), approx_aso=3,
               rule(P,_,L), not rule(P,_,L+1).
wc(P,-1,L-Idx+1,Id,aso(P,Id,Idx)) :- preference(P,aso), approx_aso=3,
                                     index(P,Id,Idx), levels(P,L).

% we could also do a level per each position of each rule...

%
% poset
%
#program weak(poset).

poset(P,X) :- preference(P,poset),
              preference(P,_,_,for(X),_).

poset(P,X,Y) :- preference(P,poset),
                preference(P,I,1,for(X),_), preference(P,I,2,for(Y),_).

#const approx_tc_poset=1.
poset(P,X,Y) :- preference(P,poset),
                poset(P,X,Z), poset(P,Z,Y), approx_tc_poset=1.

% 2 options
#const approx_poset=2.

% option 1

step(P,X,1)   :- preference(P,poset), approx_poset=1,
                 poset(P,X).
step(P,X,S+1) :- preference(P,poset), approx_poset=1,
                 step(P,X,S), step(P,Y,S), poset(P,Y,X).


levels(P,S) :- preference(P,poset), approx_poset=1,
               step(P,_,S), not step(P,_,S+1).
wc(P,-1,-S,X,X) :- preference(P,poset), approx_poset=1,
                   step(P,X,S), not step(P,X,S+1).

% option 2

cost(P,X,C+1) :- preference(P,poset), approx_poset=2,
                 poset(P,X),
                 C = #sum{ CC,Y : poset(P,X,Y), cost(P,Y,CC) }.

levels(P,1)    :- preference(P,poset), approx_poset=2.
wc(P,-C,1,X,X) :- preference(P,poset), approx_poset=2,
                  cost(P,X,C).

%
% composite preference weak
%

#program weak(neg).
wc(P,-W,L,T,X) :- preference(P,neg), preference(P,_,_,name(PP),_),
                  wc(PP,W,L,T,X).
levels(P,L) :- preference(P,neg), preference(P,_,_,name(PP),_), levels(PP,L).


#program weak.  % (as lexico, uses as_lexico/1 and level/3)

wc(P,W,L+S,T,X) :- as_lexico(P),
                   level(P,P1,L1),
                   wc(P1,W,L,T,X),
                   S = #sum{ LS2,P2,L2: level(P,P2,L2), L2 < L1, levels(P2,LS2) }.

% max level
max_level(P,MAX) :- as_lexico(P),
                    MAX = #max { L: level(P,_,L) }.

% start
sum_levels(P,MIN-1,0)  :- as_lexico(P),
                          MIN = #min { L: level(P,_,L) }.
% progress
sum_levels(P,L+1,   S) :- as_lexico(P),
                          sum_levels(P,L,S),
                          max_level(P,MAX), L < MAX.
sum_levels(P,L+1,SS+S) :- as_lexico(P),
                          sum_levels(P,L,S),
                          level(P,P1,L+1), levels(P1,SS).
% sum up
levels(P,S) :- as_lexico(P),
               max_level(P,MAX), S = #max{ SS: sum_levels(P,MAX,SS); 0 }.
               % 0 is added to avoid warnings, but it is not needed

% to avoid warnings
as_lexico(P) :- #false, as_lexico(P).
level(A,B,C) :- #false, level(A,B,C).

#program weak(lexico).

%%%
%%% With the next commented rule
%%% clingo does not terminate grounding because of recursion through wc/5
%%%
%%% wc(P,W,L+O,T,X) :- preference(P,lexico),
%%%                    preference(P,_,_,name(P1),L1), P != P1,
%%%                    wc(P1,W,L,T,X),
%%%                    O = #sum{ L3,L2 : preference(P,_,_,name(P2),L2),
%%%                                      L2 < L1, P2 != P, P2 != P1,
%%%                                      wc(P2,_,L3,_,_)}.
%%% 

as_lexico(P)  :- preference(P,lexico).
level(P,P1,L) :- preference(P,lexico),
                 preference(P,_,_,name(P1),L).


#program weak(pareto).

% 2 options
#const approx_pareto=2.

% option 1
wc(P,W,L,T,X) :- preference(P,pareto), approx_pareto=1,
                 preference(P,_,_,name(P1),_),
                 wc(P1,W,L,T,X).

% option 2 (as lexico)
as_lexico(P)  :- preference(P,pareto), approx_pareto=2.
level(P,P1,L) :- preference(P,pareto), approx_pareto=2,
                 preference(P,_,_,name(P1),_),
                 L = #sum{1, P2: preference(P,_,_,name(P2),_), P2 <= P1 }.


#program weak(and). % same as pareto

% 2 options
#const approx_and=2.

% option 1
wc(P,W,L,T,X) :- preference(P,and), approx_and=1,
                 preference(P,_,_,name(P1),_),
                 wc(P1,W,L,T,X).

% option 2 (as lexico)
as_lexico(P)  :- preference(P,and), approx_and=2.
level(P,P1,L) :- preference(P,and), approx_and=2,
                 preference(P,_,_,name(P1),_),
                 L = #sum{1, P2: preference(P,_,_,name(P2),_), P2 <= P1 }.

