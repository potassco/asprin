#!/usr/bin/python
#

class Statement:

    underscores = ""

    def __init__(self):
        self.number   = None
        self.name     = None
        self.type     = None
        self.elements = []
        self.body     = None


def ast2str(ast):
    out = ""
    if ast == None:         return out
    if isinstance(ast,str): return ast
    for e in ast:
        out += ast2str(e)
    return out

class PStatement(Statement):

    def __has_var(self,ast):
        if ast == None:         return False
        if isinstance(ast,str): return (ast[0]>="A" and ast[0]<="Z")
        for e in ast:
            if self.__has_var(e): return True
        return False

    def __create_body(self,preds,names):
        preds = set([ ast2str(x) for x in preds if self.__has_var(x) ])
        bodyp = ", ".join(["dom("+pred+")" for pred in preds])
        names = set([ ast2str(x) for x in names if self.__has_var(x) ])
        bodyn = ", ".join(["pref_dom("+name+")" for name in names])
        if bodyp!="" and bodyn!="": return bodyp + ", " + bodyn
        return bodyp + bodyn

    def str(self):

        # underscores
        u = Statement.underscores

        # tostring
        name = ast2str(self.name)
        type = ast2str(self.type)

        # pref/2
        body = ast2str(self.body) if self.body is not None else ""
        if body!="": body = " :- " + body
        out = u + "preference({},{}){}.\n".format(name,type,body)

        # pref/5
        elem = 1
        for i in self.elements:
            set = 1

            # body
            if i.body is not None:    body = ast2str(i.body)
            else:                     body = self.__create_body(i.preds,i.names)
            if self.body is not None and self.body is not "":
                if body !="": body += ", "
                body += ast2str(self.body)
            arrow = " :- " if body!="" else ""

            # head sets
            for j in i.sets:
                for k in j:
                    out += u + "preference({},(({},{}),({})),{},{},{}){}{}.\n".format(
                                name,self.number,elem,",".join(i.vars),set,k.str_body(),k.str_weight(),arrow,body)
                    out += k.str_rule(body)
                    out += k.str_bfs (body)
                    out += k.str_ats (body)
                    out += "\n"
                set += 1

            # condition set
            for k in i.cond:
                out += u + "preference({},(({},{}),({})),{},{},{}){}{}.\n".format(
                            name,self.number,elem,",".join(i.vars),0,  k.str_body(),k.str_weight(),arrow,body)
                out += "\n"
            elem += 1

        x = """
sat(and(X,Y)) :- sat(X), sat(Y), bf(and(X,Y)).
sat(or (X,Y)) :- sat(X),         bf(or (X,Y)).
sat(or (X,Y)) :- sat(Y),         bf(or (X,Y)).
sat(neg(X  )) :- not sat(X),     bf(neg(X  )).
bf(X) :- bf(and(X,Y)).
bf(Y) :- bf(and(X,Y)).
bf(X) :- bf(or (X,Y)).
bf(Y) :- bf(or (X,Y)).
bf(X) :- bf(neg(X  )).
        """
        return out

class OStatement(Statement):

    def str(self):
        return Statement.underscores + "optimize({}) :- {}.\n".format(ast2str(self.name),ast2str(self.body))


class Element:

    def __init__(self):
        self.vars  = set()
        self.preds = []
        self.names = []
        self.body  = None
        self.sets  = []
        self.cond  = []

    #def __repr__(self):
    #    out = ""
    #    for i in self.sets:
    #        out += "# "
    #        for j in i:
    #            out += str(j) + " "
    #    if len(self.cond)>0: out += "|| "
    #    for j in self.cond:
    #        out += str(j) + " "
    #    if self.body is not None: out += ": " + ast2str(self.body)
    #     return out


class WBody:

    def __init__(self,weight,body,naming=False):
        self.weight    = weight
        self.body      = body  # list
        self.naming    = naming
        self.bf        = None  # reified boolean formula representing the body
        self.bf_ats    = set() # atoms in boolean formulas (not literals) in the body
        self.analyzed  = False

    def __bf2str(self,bf):
        if bf[0] == "atom":
            atom = ast2str(bf[1][0])
            self.bf_ats.add(atom)  # fills self.bf_ats
            return "atom(" +                    atom + ")"
        if bf[0]=="neg":
            return "neg("  + self.__bf2str(bf[1][0]) + ")"
        if bf[0]=="and":
            return "and("  + self.__bf2str(bf[1][0]) + "," + self.__bf2str(bf[1][1]) + ")"
        if bf[0]=="or":
            return "or("   + self.__bf2str(bf[1][0]) + "," + self.__bf2str(bf[1][1]) + ")"

    def __translate_lit(self,lit):
        neg  = 0
        while lit[0]=="neg" and neg<=1:
            neg += 1
            lit  = lit[1][0]
        if lit[0]=="atom":
            atom = ast2str(lit[1][0])
            return ("lit",(neg*"neg(")+"atom("+atom+")"+(neg*")"),(neg*"not ")+atom)
        return None

    def __translate_bf(self,bf):
        out = self.__translate_lit(bf)
        if out is not None: return out
        string = self.__bf2str(bf)
        return ("bf",string,"sat("+string+")") # fills self.bf_ats

    def __analyze_body(self):
        # translate body
        for i in range(len(self.body)):
            self.body[i] = self.__translate_bf(self.body[i]) # fills self.bf_ats
        # fill self.bf
        self.bf  = "".join(["and("+x[1]+"," for x in self.body[:-1]])
        self.bf += self.body[-1][1]
        self.bf += "".join([")"             for x in self.body[:-1]])
        self.analyzed = True

    def str_weight(self):
        return ast2str(self.weight) if self.weight is not None else "()"

    def str_body(self):
        if self.naming: return "name({})".format(ast2str(self.body))
        if not self.analyzed: self.__analyze_body()
        return "for({})".format(self.bf)

    def str_rule(self,body):
        if self.naming: return ""
        if not self.analyzed: self.__analyze_body()
        if body != "": body = ", " + body
        return Statement.underscores + "holds(" + str(self.bf) + ",0) :- " + ", ".join([x[2] for x in self.body]) + body + ".\n"

    def str_bfs(self,body):
        if self.naming: return ""
        if body != "": body = " :- " + body
        bfs = ["bf(" + x[1] + ")" + body + "." for x in self.body if x[0]=="bf"]
        if bfs!=[]: return "\n".join(bfs)+"\n"
        return ""

    def str_ats(self,body):
        if self.naming:       return ""
        if len(self.bf_ats) == 0: return ""
        if body != "": body = ", " + body
        return "\n".join(["sat(atom(" + x + ")) :- " + x + body + "." for x in self.bf_ats]) + "\n"

    #def __repr__(self):
    #    weight = ast2str(self.weight) if self.weight is not None else "()"
    #    if not self.naming: return "({},for({}))".format(weight,ast2str(self.body))
    #    return "({},name({}))".format(weight,ast2str(self.body))

