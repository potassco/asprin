# MIT License
# 
# Copyright (c) 2017 Javier Romero
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -*- coding: utf-8 -*-

# this file should be reimplemented at some point...

from ..utils import utils


#
# defines 
#

# predicates
PREFERENCE         = "preference"   # arity 2 and 5
OPTIMIZE           = "optimize"     # arity 1
HOLDS              = "holds"        # arity 2
SAT                = "sat"          # arity 1
BF                 = "bf"           # arity 1
DOM                = "dom"          # arity 1
PREFERENCE_DOM     = "pref_dom"     # arity 1
GEN_DOM            = "gen_dom"      # arity 2
GEN_PREFERENCE_DOM = "gen_pref_dom" # arity 2

# terms
TRUE  = "true"
FALSE = "false"
ATOM  = "atom"
CMP   = "cmp"
NEG   = "neg"
AND   = "and"
OR    = "or"
NOT   = "not"
NAME  = "name"
FOR   = "for"
EXT_ATOM = "ext_atom"
HASH_SEM = utils.HASH_SEM

# boolean formulas
BF_ENCODING = """
##sat(and(X,Y)) :- ##sat(X), ##sat(Y), ##bf(and(X,Y)).
##sat(or (X,Y)) :- ##sat(X),           ##bf(or (X,Y)).
##sat(or (X,Y)) :- ##sat(Y),           ##bf(or (X,Y)).
##sat(neg(X  )) :- not ##sat(X),       ##bf(neg(X  )).
##bf(X) :- ##bf(and(X,Y)).
##bf(Y) :- ##bf(and(X,Y)).
##bf(X) :- ##bf(or (X,Y)).
##bf(Y) :- ##bf(or (X,Y)).
##bf(X) :- ##bf(neg(X  )).
"""

# true atom
TRUE_ATOM = """
##true.
"""

# rule for pref_dom/1
PREF_DOM_RULE = """
##pref_dom(X) :- ##preference(X,_).
"""


#
# Global Functions
#

#
# Note: an ast is either None, a string, or a list
#

# Translate ast to string
def ast2str(ast):
    if ast == None:
        return ""
    if isinstance(ast,str): 
        return ast
    char, alist = "", ast
    if len(ast)==2 and ast[0]==HASH_SEM: # pooling
        char, alist = ";", ast[1]
    return char.join([ast2str(e) for e in alist])


# Translate body to string
def body2str(i):
    if isinstance(i, list):
        if len(i) > 0 and i[0] == EXT_ATOM:
            return ast2str(i[1][1])
        return "".join([body2str(x) for x in i])
    return i + " "

# get variables from ast
def get_vars(ast):
    if ast == None: return []
    if isinstance(ast,str):
        return [ast] if len(ast)>0 and (ast[0]>="A" and ast[0]<="Z") else []
    return [ i for l in map(get_vars,ast) for i in l ]


# has an ast any variables?
def has_vars(ast):
    if ast == None: return False
    if isinstance(ast,str):
        return (len(ast)>0 and (ast[0]>="A" and ast[0]<="Z"))
    for i in ast:
        if has_vars(i): return True
    return False


#
# abstract class for preference and optimize statements
#
class Statement:

    underscores = ""
    domains  = set()

    def __init__(self):
        self.number   = None
        self.name     = None
        self.type     = None
        self.elements = []
        self.body     = None


#
# preference statement
#
class PStatement(Statement):


    bfs = False # True if there are boolean formulas which are not literals


    def __create_dom_body(self, element):
        out = [k for i in element.sets for j in i for k in j.get_dom_atoms()]
        for k in element.cond:
            out += k.get_dom_atoms()
        Statement.domains.update([x[1] for x in out if x[1] is not None])
        return ", ".join(x[0] for x in out)


    def str(self):

        # underscores
        u = Statement.underscores

        # tostring
        name = ast2str(self.name)
        type = ast2str(self.type)

        # pref/2
        statement_body = body2str(self.body) if self.body is not None else ""
        arrow = " :- " if statement_body != "" else ""
        out  = u + PREFERENCE 
        out += "({},{}){}{}.\n".format(name, type, arrow, statement_body)

        # handle pooling
        for i in self.elements:
            if i.pooling:
                self.elements = [k for j in self.elements for k in j.unpool()]
                break

        # pref/5
        elem = 1
        for i in self.elements:

            set = 1
            # body
            if i.body is not None:
                body = body2str(i.body)
            else:
                body = self.__create_dom_body(i)
            if statement_body != "":
                if body != "": 
                    body += ", "
                body += statement_body
            arrow = " :- " if body != "" else ""

            # WARNING: src/solver/metasp/metasp.py
            # assumes rules for preference/2, preference/5, optimize/1
            # start at the beginning of a line and finish at the end

            # head sets
            for j in i.sets:
                for k in j:
                    out += u + PREFERENCE
                    s = "({},({},{},({})),{},{},{}){}{}.\n"
                    out += s.format(name, self.number, elem, ",".join(i.vars),
                                    set, k.str_body(), k.str_weight(), arrow,
                                    body)
                    out += k.str_holds(body)
                    out += k.str_bf   (body)
                    out += k.str_sat  (body)
                set += 1

            # condition set
            for k in i.cond:
                out += u + PREFERENCE
                s = "({},({},{},({})),{},{},{}){}{}.\n"
                out += s.format(name, self.number, elem, ",".join(i.vars), 0,
                                k.str_body(), k.str_weight(), arrow, body)
                out += k.str_holds(body)
                out += k.str_bf   (body)
                out += k.str_sat  (body)

            elem += 1
        #end for

        return out


#
# optimize statement
#
class OStatement(Statement):

    def str(self):
        statement_body = body2str(self.body) if self.body is not None else ""
        arrow = " :- " if statement_body != "" else ""
        out = Statement.underscores + OPTIMIZE 
        out += "({}){}{}.\n".format(ast2str(self.name), arrow, statement_body)
        return out


#
# program statement
#
class ProgramStatement(Statement):

    def str(self):
        return ast2str(self.name)


#
# preference element
#
class Element:


    def __init__(self):
        self.sets     = []
        self.cond     = []
        self.body     = None
        self.vars     = set()
        self.all_vars = set() # temporary variable
        self.pooling  = False


    def get_vars(self):
        vars = [ k for i in self.sets for j in i for k in j.get_vars() ]
        for j in self.cond:
            vars += j.get_vars()
        return set(vars)


    def unpool(self):
        if not self.pooling: return [self]
        sets = [[]]
        for i in self.sets: # sets
            set = [[]]
            for j in i:              # weighted elements
                wBodies = j.unpool() # a list of WBodies
                set = [x + [y] for x in set for y in wBodies]
            sets = [x + [y] for x in sets for y in set]
        cond = [[]]
        for i in self.cond: # cond
            wBodies = i.unpool() # a list of WBodies
            cond = [x + [y] for x in cond for y in wBodies]
        element_pairs = [(x,y) for x in sets for y in cond]
        elements = []
        for i in element_pairs:
            e = Element()
            e.sets = i[0]
            e.cond = i[1]
            e.body = self.body
            e.vars = e.get_vars()
            elements.append(e)
        return elements


#
# weighted body
#
class WBody:


    def __init__(self,weight,body,naming=False):
        self.weight      = weight
        self.body        = body  # list
        self.naming      = naming
        # reified boolean formula representing the body
        self.bf          = None  
        # extended atoms appearing in (boolean formulas which are not literals)
        self.atoms_in_bf = set() 
        self.analyzed    = False


    #
    # UNPOOLING
    #


    def get_vars(self):
        vars  = []
        vars += get_vars(self.weight)
        vars += get_vars(self.body)
        return vars


    def __unpool_term(self, term):
        if term == None:              return [None]
        if not isinstance(term,list): return [term]
        if len(term)==2 and term[0] == HASH_SEM:
            out = []
            for i in term[1]:
                out += self.__unpool_term(i)
            return out
        out = [[]]
        for i in term:
            out = [x + [y] for x in out for y in self.__unpool_term(i)]
        return out


    def unpool(self):
        weights = self.__unpool_term(self.weight)
        bodies  = self.__unpool_term(self.body)
        return [WBody(i,j,self.naming) for i in weights for j in bodies]


    #
    # BOOLEAN FORMULAS TRANSLATION
    #


    def __translate_ext_atom(self, atom):
        u = Statement.underscores
        if atom[0] == "true":
            out = ATOM + "(" + u + TRUE + ")"
            return out, u + TRUE
        elif atom[0] == "false":
            out = ATOM + "(" + u + FALSE + ")"
            return out, u + FALSE
        elif atom[0] == "atom":
            return ATOM + "(" + ast2str(atom[1]) + ")", ast2str(atom[1])
        elif atom[0] == "cmp":
            out  = CMP + "(\"" + atom[1][1] + "\"," + ast2str(atom[1][0]) + ","
            out += ast2str(atom[1][2]) + ")"
            return out, ast2str(atom[1])
        else:
            raise utils.FatalException


    def __bf2str(self, bf):
        if bf[0] == "ext_atom":
            atom_reified, atom = self.__translate_ext_atom(bf[1])
            # fills self.atoms_in_bf
            self.atoms_in_bf.add((atom_reified, atom)) 
            return atom_reified
        elif bf[0] == "csp":
            self.atoms_in_bf.add((bf[1], ast2str(bf[2])))
            return bf[1]
        elif bf[0] == "neg":
            return NEG + "("  + self.__bf2str(bf[1][0]) + ")"
        elif bf[0] == "and":
            return AND+ "("  + self.__bf2str(
                   bf[1][0]) + "," + self.__bf2str(bf[1][1]) + ")"
        elif bf[0] == "or":
            return OR + "(" + self.__bf2str(
                   bf[1][0]) + "," + self.__bf2str(bf[1][1]) + ")"


    def __translate_lit(self, lit):
        neg  = 0
        while lit[0] == "neg" and neg<=1:
            neg += 1
            lit  = lit[1][0]
        if lit[0] == "ext_atom":
            atom_reified, atom = self.__translate_ext_atom(lit[1])
            return ("lit", (neg*(NEG+"(")) + atom_reified + (neg*")"),
                   (neg*(NOT+" ")) + atom)
        return None


    def __translate_bf(self, bf):
        out = self.__translate_lit(bf)
        if out is not None: 
            return out
        string = self.__bf2str(bf) # fills self.atoms_in_bf
        return ("bf", string, Statement.underscores + SAT + "(" + string +")")


    #
    # WARNING: must be called in the first str_ function (now str_body)
    #
    # modifies elements of self.body with triples
    #   (type,reified,string)
    # where:
    #   - type may be bf or lit
    #   - reified is what will be used to write for()
    #   - string  is what will be used to generate holds/2
    # it also fills self.atoms_in_bf with the atoms appearing in the body
    # and     fills self.bf     with the reified version of the body
    #
    def __analyze_body(self):
        # translate body
        for i in range(len(self.body)):
            # fills self.atoms_in_bf
            self.body[i] = self.__translate_bf(self.body[i]) 
        # fill self.bf 
        self.bf  = "".join([AND + "(" + x[1] + "," for x in self.body[:-1]])
        self.bf += self.body[-1][1]
        self.bf += "".join([                   ")" for x in self.body[:-1]])
        self.analyzed = True


    #
    # FUNCTIONS RETURNING STRINGS
    #


    # return the weight
    def str_weight(self):
        return "(" + ast2str(self.weight) + ")"


    # return the body with for() or name()
    # analyzes the body
    def str_body(self):
        if self.naming: 
            return NAME + "({})".format(ast2str(self.body))
        self.__analyze_body()
        return FOR + "({})".format(self.bf)


    # return rules for holds/2
    def str_holds(self, body):
        if self.naming:
            return ""
        if body != "":
            body = ", " + body
        head = Statement.underscores + HOLDS + "(" + str(self.bf) + ",0) :- "
        return head + ", ".join([x[2] for x in self.body]) + body + ".\n"


    # return rules for bf/1 with the boolean formulas which are not literals
    # sets PStatement.bfs to True when necessary
    def str_bf(self, body):
        if self.naming: 
            return ""
        if body != "": 
            body = " :- " + body
        init = Statement.underscores + BF + "(" 
        bfs = [init + x[1] + ")" + body + "." for x in self.body if x[0]=="bf"]
        if bfs != []:
            PStatement.bfs = True
            return "\n".join(bfs)+"\n"
        return ""


    # return rules for sat/1 with extended atoms appearing in
    # boolean formulas which are not literals
    def str_sat(self, body):
        if self.naming:
            return ""
        if len(self.atoms_in_bf) == 0:
            return ""
        if body != "":
            body = ", " + body
        init = Statement.underscores + SAT + "("
        end  = body + "."
        list = [init + x[0] + ") :- " + x[1] + end for x in self.atoms_in_bf]
        return "\n".join(list) + "\n"


    #
    # FUNCTIONS FOR GENERATING dom() AND preference_dom() ATOMS
    #

    def __get_arity_and_vars_termvec(self, termvec):
        # basic case
        if termvec == None or len(termvec)==0: 
            return 0, False
        # move to ntermvec
        ntermvec, arity, _has_vars = termvec, 1, False
        # iterate
        while len(ntermvec)==3:
            arity   += 1
            if not _has_vars:
                _has_vars = has_vars(ntermvec[2])
            ntermvec =  ntermvec[0]
        if not _has_vars: 
            _has_vars = has_vars(ntermvec[0])
        # return
        return arity, _has_vars


    def __get_signature_atom(self,atom):
        # strong negation?
        if atom[0] == "-":
            name = "-"
            atom = atom[1:]
        else: 
            name = ""
        # name
        name += atom[0]
        # if arity is 0
        if len(atom)==1:
            return None
        # else get arity, and whether are there variables, and return
        arity, _has_vars = self.__get_arity_and_vars_termvec(atom[2][0])
        return (name, arity) if _has_vars else None


    def __get_dom_atoms_from_bf(self,bf):
        if bf[0] == "ext_atom":
            if bf[1][0] == "atom":
                # (name,arity) for non ground atoms
                sig = self.__get_signature_atom(bf[1][1]) 
                if sig is None: 
                    return []
                u = Statement.underscores
                out1 = u +     DOM + "(" +          ast2str(bf[1][1]) + ")"
                out2 = u + GEN_DOM + "(" + sig[0] + "," + str(sig[1]) + ")."
                return [(out1, out2)]
            else: 
                return []
        elif bf[0] == "and" or bf[0] == "or":
            out1 =        self.__get_dom_atoms_from_bf(bf[1][0]) 
            return out1 + self.__get_dom_atoms_from_bf(bf[1][1])
        elif bf[0] == "neg":
            return self.__get_dom_atoms_from_bf(bf[1][0])
        else: 
            raise Exception("ERROR at __get_dom_atoms_from_bf")


    def get_dom_atoms(self):
        if self.naming:
            sig = self.__get_signature_atom(self.body)
            if sig is not None:
                init = Statement.underscores + PREFERENCE_DOM
                return [(init + "(" + ast2str(self.body) + ")", None)]
            else:
                return []
        return [item for list in map(self.__get_dom_atoms_from_bf,
                                     self.body) for item in list]


