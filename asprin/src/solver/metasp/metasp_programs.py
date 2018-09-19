meta_program = """
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This file is part of clingo.                                            %
% Copyright (C) 2015  Martin Gebser                                       %
% Copyright (C) 2015  Roland Kaminski                                     %
% Copyright (C) 2015  Torsten Schaub                                      %
%                                                                         %
% This program is free software: you can redistribute it and/or modify    %
% it under the terms of the GNU General Public License as published by    %
% the Free Software Foundation, either version 3 of the License, or       %
% (at your option) any later version.                                     %
%                                                                         %
% This program is distributed in the hope that it will be useful,         %
% but WITHOUT ANY WARRANTY; without even the implied warranty of          %
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           %
% GNU General Public License for more details.                            %
%                                                                         %
% You should have received a copy of the GNU General Public License       %
% along with this program.  If not, see <http://www.gnu.org/licenses/>.   %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

##conjunction(B) :- ##literal_tuple(B),
        ##hold(L) : ##literal_tuple(B, L), L > 0;
    not ##hold(L) : ##literal_tuple(B,-L), L > 0.

##body(normal(B)) :- ##rule(_,normal(B)), ##conjunction(B).
##body(sum(B,G))  :- ##rule(_,sum(B,G)),
    #sum { W,L :     ##hold(L), ##weighted_literal_tuple(B, L,W), L > 0 ;
           W,L : not ##hold(L), ##weighted_literal_tuple(B,-L,W), L > 0 } >= G.

  ##hold(A) : ##atom_tuple(H,A)   :- ##rule(disjunction(H),B), ##body(B).
{ ##hold(A) : ##atom_tuple(H,A) } :- ##rule(     choice(H),B), ##body(B).

% commented by Javier for MetaspPython
%*
##optimize(J,W,Q) :- ##output(_optimize(J,W,Q),B), ##conjunction(B).
 :- ##output(_query,B), not ##conjunction(B).

##hide(_criteria(J,W,Q)) :- ##output(_criteria(J,W,Q),_).
##hide(_query)           :- ##output(_query,_).
##hide(_optimize(J,W,Q)) :- ##output(_optimize(J,W,Q),_).
#show.
#show T : ##output(T,B), ##conjunction(B), not ##hide(T).
*%

% added by Javier for MetaspPython
#show.
#show T : ##output(T,L), ##hold(L).


"""

metaD_program = """

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This file is part of clingo.                                            %
%                                                                         %
% Authors: Martin Gebser, Roland Kaminski, Torsten Schaub                 %
%                                                                         %
% This program is free software: you can redistribute it and/or modify    %
% it under the terms of the GNU General Public License as published by    %
% the Free Software Foundation, either version 3 of the License, or       %
% (at your option) any later version.                                     %
%                                                                         %
% This program is distributed in the hope that it will be useful,         %
% but WITHOUT ANY WARRANTY; without even the implied warranty of          %
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           %
% GNU General Public License for more details.                            %
%                                                                         %
% You should have received a copy of the GNU General Public License       %
% along with this program.  If not, see <http://www.gnu.org/licenses/>.   %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% NOTE: assumes that a rule has no more than one head

##sum(B,G,T) :- ##rule(_,sum(B,G)), T = #sum { W,L : ##weighted_literal_tuple(B,L,W) }.

% extract supports of atoms and facts

##supp(A,B) :- ##rule(     choice(H),B), ##atom_tuple(H,A).
##supp(A,B) :- ##rule(disjunction(H),B), ##atom_tuple(H,A).

##supp(A) :- ##supp(A,_).

##atom(|L|) :- ##weighted_literal_tuple(_,L,_).
##atom(|L|) :- ##literal_tuple(_,L).
##atom( A ) :- ##atom_tuple(_,A).

##fact(A) :- ##rule(disjunction(H),normal(B)), ##atom_tuple(H,A), not ##literal_tuple(B,_).

% generate interpretation

##true(atom(A))                :- ##fact(A).
##true(atom(A)); ##fail(atom(A)) :- ##supp(A), not ##fact(A).
                 ##fail(atom(A)) :- ##atom(A), not ##supp(A).

##true(normal(B)) :- ##literal_tuple(B),
    ##true(atom(L)) : ##literal_tuple(B, L), L > 0;
    ##fail(atom(L)) : ##literal_tuple(B,-L), L > 0.
##fail(normal(B)) :- ##literal_tuple(B, L), ##fail(atom(L)), L > 0.
##fail(normal(B)) :- ##literal_tuple(B,-L), ##true(atom(L)), L > 0.

##true(sum(B,G)) :- ##sum(B,G,T),
    #sum { W,L : ##true(atom(L)), ##weighted_literal_tuple(B, L,W), L > 0 ;
           W,L : ##fail(atom(L)), ##weighted_literal_tuple(B,-L,W), L > 0 } >= G.
##fail(sum(B,G)) :- ##sum(B,G,T),
    #sum { W,L : ##fail(atom(L)), ##weighted_literal_tuple(B, L,W), L > 0 ;
           W,L : ##true(atom(L)), ##weighted_literal_tuple(B,-L,W), L > 0 } >= T-G+1.

% verify supported model properties

##bot :- ##rule(disjunction(H),B), ##true(B), ##fail(atom(A)) : ##atom_tuple(H,A).
##bot :- ##true(atom(A)), ##fail(B) : ##supp(A,B).

% verify acyclic derivability

##internal(C,normal(B)) :- ##scc(C,A), ##supp(A,normal(B)), ##scc(C,A'), ##literal_tuple(B,A').
##internal(C,sum(B,G))  :- ##scc(C,A), ##supp(A,sum(B,G)),  ##scc(C,A'), ##weighted_literal_tuple(B,A',W).

##external(C,normal(B)) :- ##scc(C,A), ##supp(A,normal(B)), not ##internal(C,normal(B)).
##external(C,sum(B,G))  :- ##scc(C,A), ##supp(A,sum(B,G)),  not ##internal(C,sum(B,G)).

##steps(C,Z-1) :- ##scc(C,_), Z = { ##scc(C,A) : not ##fact(A) }.

##wait(C,atom(A),0)   :- ##scc(C,A), ##fail(B) : ##external(C,B).
##wait(C,normal(B),I) :- ##internal(C,normal(B)), ##literal_tuple(B,A), ##wait(C,atom(A),I), ##steps(C,Z), I < Z.
##wait(C,sum(B,G),I)  :- ##internal(C,sum(B,G)), ##steps(C,Z), I = 0..Z-1, ##sum(B,G,T),
    #sum { W,L :   ##fail(atom(L)),   ##weighted_literal_tuple(B, L,W), L > 0, not ##scc(C,L) ;
           W,L : ##wait(C,atom(L),I), ##weighted_literal_tuple(B, L,W), L > 0,     ##scc(C,L) ;
           W,L :   ##true(atom(L)),   ##weighted_literal_tuple(B,-L,W), L > 0               } >= T-G+1.
##wait(C,atom(A),I)   :- ##wait(C,atom(A),0), ##steps(C,Z), I = 1..Z, ##wait(C,B,I-1) : ##supp(A,B), ##internal(C,B).

##bot :- ##scc(C,A), ##true(atom(A)), ##wait(C,atom(A),Z), ##steps(C,Z).

% saturate interpretations that are not answer sets

##true(atom(A)) :- ##supp(A), not ##fact(A), ##bot.
##fail(atom(A)) :- ##supp(A), not ##fact(A), ##bot.

%
% added by Javier
%

%#show.
%#show T : ##output(T,L), ##true(atom(L)).
#defined ##literal_tuple/1.
#defined ##literal_tuple/2.
#defined ##rule/2.
#defined ##atom_tuple/2.
#defined ##weighted_literal_tuple/3.
#defined ##scc/2.
"""

metaD_program_inc_base = """

% NOTE: assumes that a rule has no more than one head

##sum(B,G,T) :- ##rule(_,sum(B,G)), T = #sum { W,L : ##weighted_literal_tuple(B,L,W) }.

% extract supports of atoms and facts

##supp(A,B) :- ##rule(     choice(H),B), ##atom_tuple(H,A).
##supp(A,B) :- ##rule(disjunction(H),B), ##atom_tuple(H,A).

##supp(A) :- ##supp(A,_).

##atom(|L|) :- ##weighted_literal_tuple(_,L,_).
##atom(|L|) :- ##literal_tuple(_,L).
##atom( A ) :- ##atom_tuple(_,A).

##fact(A) :- ##rule(disjunction(H),normal(B)), ##atom_tuple(H,A), not ##literal_tuple(B,_).

% verify acyclic derivability

##internal(C,normal(B)) :- ##scc(C,A), ##supp(A,normal(B)), ##scc(C,A'), ##literal_tuple(B,A').
##internal(C,sum(B,G))  :- ##scc(C,A), ##supp(A,sum(B,G)),  ##scc(C,A'), ##weighted_literal_tuple(B,A',W).

##external(C,normal(B)) :- ##scc(C,A), ##supp(A,normal(B)), not ##internal(C,normal(B)).
##external(C,sum(B,G))  :- ##scc(C,A), ##supp(A,sum(B,G)),  not ##internal(C,sum(B,G)).

##steps(C,Z-1) :- ##scc(C,_), Z = { ##scc(C,A) : not ##fact(A) }.

%
% added by Javier
%

#defined ##literal_tuple/1.
#defined ##literal_tuple/2.
#defined ##rule/2.
#defined ##atom_tuple/2.
#defined ##weighted_literal_tuple/3.
#defined ##scc/2.
"""

metaD_program_parameters = ["m1", "m2"]

metaD_program_inc = """
% generate interpretation

##true(m1,m2,atom(A))                        :- ##fact(A),                not ##fixed(A). % added not fixed(A)
##true(m1,m2,atom(A)); ##fail(m1,m2,atom(A)) :- ##supp(A), not ##fact(A), not ##fixed(A). % added not fixed(A)
                       ##fail(m1,m2,atom(A)) :- ##atom(A), not ##supp(A), not ##fixed(A). % added not fixed(A)

##true(m1,m2,normal(B)) :- ##literal_tuple(B),
    ##true(m1,m2,atom(L)) : ##literal_tuple(B, L), L > 0;
    ##fail(m1,m2,atom(L)) : ##literal_tuple(B,-L), L > 0.
##fail(m1,m2,normal(B)) :- ##literal_tuple(B, L), ##fail(m1,m2,atom(L)), L > 0.
##fail(m1,m2,normal(B)) :- ##literal_tuple(B,-L), ##true(m1,m2,atom(L)), L > 0.

##true(m1,m2,sum(B,G)) :- ##sum(B,G,T),
    #sum { W,L : ##true(m1,m2,atom(L)), ##weighted_literal_tuple(B, L,W), L > 0 ;
           W,L : ##fail(m1,m2,atom(L)), ##weighted_literal_tuple(B,-L,W), L > 0 } >= G.
##fail(m1,m2,sum(B,G)) :- ##sum(B,G,T),
    #sum { W,L : ##fail(m1,m2,atom(L)), ##weighted_literal_tuple(B, L,W), L > 0 ;
           W,L : ##true(m1,m2,atom(L)), ##weighted_literal_tuple(B,-L,W), L > 0 } >= T-G+1.

% verify supported model properties

##bot(m1,m2) :- ##rule(disjunction(H),B), ##true(m1,m2,B), ##fail(m1,m2,atom(A)) : ##atom_tuple(H,A).
##bot(m1,m2) :- ##true(m1,m2,atom(A)), ##fail(m1,m2,B) : ##supp(A,B).

% verify acyclic derivability

##wait(m1,m2,C,atom(A),0)   :- ##scc(C,A), ##fail(m1,m2,B) : ##external(C,B).
##wait(m1,m2,C,normal(B),I) :- ##internal(C,normal(B)), ##literal_tuple(B,A), ##wait(m1,m2,C,atom(A),I), ##steps(C,Z), I < Z.
##wait(m1,m2,C,sum(B,G),I)  :- ##internal(C,sum(B,G)), ##steps(C,Z), I = 0..Z-1, ##sum(B,G,T),
    #sum { W,L :   ##fail(m1,m2,atom(L)),   ##weighted_literal_tuple(B, L,W), L > 0, not ##scc(C,L) ;
           W,L : ##wait(m1,m2,C,atom(L),I), ##weighted_literal_tuple(B, L,W), L > 0,     ##scc(C,L) ;
           W,L :   ##true(m1,m2,atom(L)),   ##weighted_literal_tuple(B,-L,W), L > 0               } >= T-G+1.
##wait(m1,m2,C,atom(A),I)   :- ##wait(m1,m2,C,atom(A),0), ##steps(C,Z), I = 1..Z, ##wait(m1,m2,C,B,I-1) : ##supp(A,B), ##internal(C,B).

##bot(m1,m2) :- ##scc(C,A), ##true(m1,m2,atom(A)), ##wait(m1,m2,C,atom(A),Z), ##steps(C,Z).

% saturate interpretations that are not answer sets

##true(m1,m2,atom(A)) :- ##supp(A), not ##fact(A), ##bot(m1,m2), not ##fixed(A).
##fail(m1,m2,atom(A)) :- ##supp(A), not ##fact(A), ##bot(m1,m2), not ##fixed(A).

%
% added by Javier
%

#defined ##literal_tuple/1.
#defined ##literal_tuple/2.
#defined ##rule/2.
#defined ##atom_tuple/2.
#defined ##weighted_literal_tuple/3.
#defined ##scc/2.

"""


