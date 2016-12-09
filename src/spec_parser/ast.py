#!/usr/bin/python


#
# DEFINE Predicates
#

PREFERENCE         = "preference"   # arity 2 and 5
OPTIMIZE           = "optimize"     # arity 1
HOLDS              = "holds"        # arity 2
SAT                = "sat"          # arity 1
BF                 = "bf"           # arity 1
DOM                = "dom"          # arity 1
PREFERENCE_DOM     = "pref_dom"     # arity 1
GEN_DOM            = "gen_dom"      # arity 2
GEN_PREFERENCE_DOM = "gen_pref_dom" # arity 2



#
# DEFINE Terms
#

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



#
# Boolean Formula Definition
#

BF_ENCODING = """
#sat(and(X,Y)) :- #sat(X), #sat(Y), #bf(and(X,Y)).
#sat(or (X,Y)) :- #sat(X),          #bf(or (X,Y)).
#sat(or (X,Y)) :- #sat(Y),          #bf(or (X,Y)).
#sat(neg(X  )) :- not #sat(X),      #bf(neg(X  )).
#bf(X) :- #bf(and(X,Y)).
#bf(Y) :- #bf(and(X,Y)).
#bf(X) :- #bf(or (X,Y)).
#bf(Y) :- #bf(or (X,Y)).
#bf(X) :- #bf(neg(X  )).
"""

TRUE_ATOM = """
#true.
"""

# TODO: CHECK PREFERENCE ATOMS
DOM_RULES = """
#pref_dom(X) :- #preference(X,_).
#dom(X)      :- #gen_dom(X,0).
"""


#
# Global Functions
#


# Translate ast to string
def ast2str(ast):
    out = ""
    if ast == None:         return out
    if isinstance(ast,str): return ast
    for e in ast:
        out += ast2str(e)
    return out


# Translate body to string
def body2str(i):
    out = ""
    if isinstance(i,list) and len(i) > 0:
        if isinstance(i[0],str) and i[0] in { "atom", "true", "false", "cmp" }:
            return ast2str(i[1])
        if isinstance(i[0],str) and i[0] in { "csp" }:
            return ast2str(i[2])
        for j in i:
            out += body2str(j)
    return out



# abstract class for preference and optimize statements
class Statement:

    underscores = ""

    domains  = set()

    def __init__(self):
        self.number   = None
        self.name     = None
        self.type     = None
        self.elements = []
        self.body     = None



# preference statement
class PStatement(Statement):


    bfs = False # True if there are boolean formulas which are not literals


    def __create_dom_body(self,element):
        out = []
        for j in element.sets:
            for k in j:
                out += k.get_dom_atoms()
        for k in element.cond:
            out += k.get_dom_atoms()
        Statement.domains.update([item for sublist in [x[1] for x in out] for item in sublist]) # update domains
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
        out = u + PREFERENCE + "({},{}){}{}.\n".format(name,type,arrow,statement_body)

        # pref/5
        elem = 1
        for i in self.elements:

            set = 1

            # body
            if i.body is not None:    body = body2str(i.body)
            else:                     body = self.__create_dom_body(i)
            if statement_body != "":
                if body != "": body += ", "
                body += statement_body
            arrow = " :- " if body != "" else ""

            # head sets
            for j in i.sets:
                for k in j:
                    out += u + PREFERENCE + "({},(({},{}),({})),{},{},{}){}{}.\n".format(
                                name,self.number,elem,",".join(i.vars),set,k.str_body(),k.str_weight(),arrow,body)
                    out += k.str_holds(body)
                    out += k.str_bf   (body)
                    out += k.str_sat  (body)
                set += 1

            # condition set
            for k in i.cond:
                out +=     u + PREFERENCE + "({},(({},{}),({})),{},{},{}){}{}.\n".format(
                                name,self.number,elem,",".join(i.vars),  0,k.str_body(),k.str_weight(),arrow,body)

            elem += 1
        #end for

        return out



# optimize statement
class OStatement(Statement):


    def str(self):
        statement_body = body2str(self.body) if self.body is not None else ""
        arrow = " :- " if statement_body != "" else ""
        return Statement.underscores + OPTIMIZE + "({}){}{}.\n".format(ast2str(self.name),arrow,statement_body)



# program statement
class ProgramStatement(Statement):


    def str(self):
        return ast2str(self.name)



# preference element
class Element:


    def __init__(self):
        self.vars  = set()
        self.preds = []
        self.names = []
        self.body  = None
        self.sets  = []
        self.cond  = []
        self.all_vars  = set() # temporary variable



# exception for WBody (should never rise)
class AstException(Exception):
    pass



# weighted body
class WBody:


    def __init__(self,weight,body,naming=False):
        self.weight      = weight
        self.body        = body  # list
        self.naming      = naming
        self.bf          = None  # reified boolean formula representing the body
        self.atoms_in_bf = set() # extended and csp atoms appearing in (boolean formulas which are not literals)
        self.analyzed    = False


    #
    # BOOLEAN FORMULAS TRANSLATION
    #


    def __translate_ext_atom(self,atom):
        if atom[0] == "true":
            return ATOM+"("+Statement.underscores+TRUE+")", Statement.underscores+TRUE
        elif atom[0] == "false":
            return ATOM+"("+Statement.underscores+FALSE+")", Statement.underscores+FALSE
        elif atom[0] == "atom":
            return ATOM+"("+ast2str(atom[1])+")", ast2str(atom[1])
        elif atom[0] == "cmp":
            return CMP+"(\""+atom[1][1]+"\","+ast2str(atom[1][0])+","+ast2str(atom[1][2])+")", ast2str(atom[1])
        else:
            raise AstException


    def __bf2str(self,bf):
        if bf[0] == "ext_atom":
            atom_reified, atom = self.__translate_ext_atom(bf[1])
            self.atoms_in_bf.add((atom_reified,atom))  # fills self.atoms_in_bf
            return atom_reified
        elif bf[0] == "csp":
            self.atoms_in_bf.add((bf[1],ast2str(bf[2])))
            return bf[1]
        elif bf[0]=="neg":
            return NEG+"("  + self.__bf2str(bf[1][0]) + ")"
        elif bf[0]=="and":
            return AND+"("  + self.__bf2str(bf[1][0]) + "," + self.__bf2str(bf[1][1]) + ")"
        elif bf[0]=="or":
            return OR+"("   + self.__bf2str(bf[1][0]) + "," + self.__bf2str(bf[1][1]) + ")"


    def __translate_lit(self,lit):
        neg  = 0
        if lit[0] == "csp":
            return ("lit",lit[1],ast2str(lit[2]))
        while lit[0]=="neg" and neg<=1:
            neg += 1
            lit  = lit[1][0]
        if lit[0]=="ext_atom":
            atom_reified, atom = self.__translate_ext_atom(lit[1])
            return ("lit",(neg*(NEG+"("))+atom_reified+(neg*")"),(neg*(NOT+" "))+atom)
        return None


    def __translate_bf(self,bf):
        out = self.__translate_lit(bf)
        if out is not None: return out
        string = self.__bf2str(bf)              # fills self.atoms_in_bf
        return ("bf",string,Statement.underscores+SAT+"("+string+")")


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
            self.body[i] = self.__translate_bf(self.body[i]) # fills self.atoms_in_bf
        # fill self.bf the
        self.bf  = "".join([AND+"("+x[1]+"," for x in self.body[:-1]])
        self.bf += self.body[-1][1]
        self.bf += "".join([")"             for x in self.body[:-1]])
        self.analyzed = True


    #
    # FUNCTIONS RETURNING STRINGS
    #


    # return the weight
    def str_weight(self):
        return ast2str(self.weight) if self.weight is not None else "()"


    # return the body with for() or name()
    def str_body(self):
        if self.naming: return NAME+"({})".format(ast2str(self.body))
        if not self.analyzed: self.__analyze_body()
        return FOR+"({})".format(self.bf)


    # return rules for holds/2
    def str_holds(self,body):
        if self.naming: return ""
        if not self.analyzed: self.__analyze_body()
        if body != "": body = ", " + body
        return Statement.underscores + HOLDS + "(" + str(self.bf) + ",0) :- " + ", ".join([x[2] for x in self.body]) + body + ".\n"


    # return rules for bf/1 with the boolean formulas which are not literals
    # sets PStatement.bfs to True when necessary
    def str_bf(self,body):
        if self.naming: return ""
        if body != "": body = " :- " + body
        bfs = [Statement.underscores + BF + "(" + x[1] + ")" + body + "." for x in self.body if x[0]=="bf"]
        if bfs!=[]:
            PStatement.bfs = True
            return "\n".join(bfs)+"\n"
        return ""


    # return rules for sat/1 with extended atoms appearing in (boolean formulas which are not literals)
    def str_sat(self,body):
        if self.naming:       return ""
        if len(self.atoms_in_bf) == 0: return ""
        if body != "": body = ", " + body
        return "\n".join([Statement.underscores + SAT + "(" + x[0] + ") :- " + x[1] + body + "." for x in self.atoms_in_bf]) + "\n"


    #
    # FUNCTIONS FOR GENERATING dom() AND preference_dom() ATOMS
    #


    def __get_arity_termvec(self,termvec):
        if termvec == None: return [0]
        termvec, arity = termvec[0], 1
        while len(termvec)==3:
            arity += 1
            termvec = termvec[0]
        return arity


    def __get_arity_argvec(self,argvec):
        if   len(argvec) == 1: return [ self.__get_arity_termvec(argvec[0]) ]
        elif len(argvec) == 3: return self.__get_arity_argvec(argvec[0]) + [ self.__get_arity_termvec(argvec[2]) ]


    def __get_signature(self,atom):
        name, arity, i = "", [], 0
        if atom[i] == "-":
            name = "-"
            atom = atom[1:]
        name += atom[0]
        if len(atom)==1: return name, [0] # no parenthesis
        argvec = atom[2]
        arity = self.__get_arity_argvec(argvec)
        return name, arity


    def __get_dom_atoms_from_bf(self,bf):
        if bf[0] == "ext_atom":
            if bf[1][0] == "atom":
                name, arity = self.__get_signature(bf[1][1])
                return [ (Statement.underscores + DOM + "(" + ast2str(bf[1][1]) + ")",
                        [ Statement.underscores + GEN_DOM+"("+name+","+str(i)+")." for i in arity ] ) ]
            else: return []
        elif bf[0] == "and" or bf[0] == "or":
            return self.__get_dom_atoms_from_bf(bf[1][0]) + self.__get_dom_atoms_from_bf(bf[1][1])
        elif bf[0] == "neg":
            return self.__get_dom_atoms_from_bf(bf[1][0])
        return [] # csp


    # return the atoms in the body as a list of strings (called before str_ functions)
    def get_dom_atoms(self):
        out = []
        if self.naming:
            name, arity = self.__get_signature(self.body)
            return [ (Statement.underscores + PREFERENCE_DOM + "(" + ast2str(self.body) + ")",[])]
                    #[ Statement.underscores + GEN_PREFERENCE_DOM+"("+name+","+str(i)+")." for i in arity ] ) ] # DOM_RULES
        for i in self.body:
            out += self.__get_dom_atoms_from_bf(i)
        return out



