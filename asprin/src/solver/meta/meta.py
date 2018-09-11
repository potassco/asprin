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

#
# IMPORTS
#

import clingo
import meta_programs
import scc
#from . import metaD

class Observer:

    def __init__(self, control, replace = False):
        control.register_observer(self, replace)
        self.rules = []
        self.weight_rules = []
        self.output_atoms = []
        self.graph = {}

    def rule(self, choice, head, body):
        self.rules.append((choice, head, body))

    def weight_rule(self, choice, head, lower_bound, body):
        self.weight_rules.append((choice, head, lower_bound, body))

    def output_atom(self, symbol, atom):
        self.output_atoms.append((symbol, atom))

    # TODO: Implement option where we take care about repeated heads and bodies
    def reify(self):

        # start
        out = ""
        literal_tuple, wliteral_tuple, atom_tuple = 1, 1, 1

        # fact 0
        out += "% fact 0\n"
        out += "rule(disjunction(0),normal(0)). atom_tuple(0,0). literal_tuple(0).\n\n"

        # start graph
        graph = scc.Graph()

        # normal rules
        for choice, head, body in self.rules:

            out += "% normal rule\n"
            # body
            out += "literal_tuple({}).".format(literal_tuple) + "\n"
            out += " ".join(["literal_tuple({},{}).".format(literal_tuple, l) for l in body]) + "\n"
            # head
            head_type = "choice" if choice else "disjunction"
            out += "rule({}({}),normal({})).".format(head_type, atom_tuple, literal_tuple) + "\n"
            out += " ".join(["atom_tuple({},{}).".format(atom_tuple, l) for l in head]) + "\n\n"
            # update counters
            literal_tuple += 1
            atom_tuple += 1
            # update graph (this can be interwined with the rules above)
            for l in body:
                if l >= 0:
                    for atom in head:
                        graph.add_edge(atom, l)


        # weight rules
        for choice, head, lower_bound, body in self.weight_rules:
            out += "% weighted rule\n"
            # body
            out += " ".join(["weighted_literal_tuple({},{},{}).".format(wliteral_tuple, l, w) for l, w in body]) + "\n"
            # head
            head_type = "choice" if choice else "disjunction"
            out += "rule({}({}),sum({},{})).".format(head_type, atom_tuple, wliteral_tuple, lower_bound) + "\n"
            out += " ".join(["atom_tuple({},{}).".format(atom_tuple, l) for l in head]) + "\n\n"
            # update counters
            wliteral_tuple += 1
            atom_tuple += 1
            # update graph (this can be interwined with the rules above)
            for l, w in body:
                if l >= 0:
                    for atom in head:
                        graph.add_edge(atom, l)

        # sccs
        out += "% sccs\n"
        out += graph.reify_sccs() + "\n"

        # output atoms
        out += "% output atoms\n"
        for symbol, atom in self.output_atoms:
            out += "output({},{}).\n".format(symbol, atom)

        return out


class Meta:

    def __init__(self, control, observer):
        self.control = control
        self.observer = observer


def run(base, metaD=False):

    # observe rules
    ctl = clingo.Control(["0"])
    #observer = Observer(ctl, False)
    observer = Observer(ctl, True)
    ctl.add("base", [], base)
    ctl.ground([("base", [])])
    #models0 = []
    #with ctl.solve(yield_=True) as handle:
    #    for m in handle:
    #        models0.append(" ".join(sorted([str(x) for x in m.symbols(shown=True)])))
    #    # print(handle.get())
    #models0 = sorted(models0)

    # use reified version
    base = observer.reify()
    print(base)
    return
    if metaD:
        base += meta_programs.metaD_program
    else:
        base += meta_programs.meta_program
    ctl = clingo.Control(["0"])
    ctl.add("base", [], base)
    ctl.ground([("base", [])])
    models1 = []
    with ctl.solve(yield_=True) as handle:
        for m in handle:
            models1.append(" ".join(sorted([str(x) for x in m.symbols(shown=True)])))
        # print(handle.get())
    models1 = sorted(models1)

    # check and print
    print("ERROR" if models0 != models1 else "OK")
    if models0 != models1:
        print(models0)
        print(models1)
    if len(models0):
        models0[0] += "_x "
        print("OK" if models0 != models1 else "ERROR")


#
# programs
#

basic = """
{a}. b.
"""

aggregates = """
{a(X) : dom(X)}.
b(X) :- X = { a(Y) }.
dom(1..2).
#show b/1.
"""

# pigeon hole
pigeon = """
#const n=6.
pigeon(1..n+1). box(1..n+1).
1 { in(X,Y) : box(Y) } 1 :- pigeon(X).
:- 2 { in(X,Y) : pigeon(X) },  box(Y).
a(X,Y,Z) :- in(X,Y), in(Y,Z).
"""

loop = """
a :- b.
b :- a.
b :- c.
a :- c.
{ c }.
"""

many_loops = """
dom(1..320).
{ edge(X,Y) : dom(X), dom(Y) }.
tr(X,Y) :- edge(X,Y).
tr(X,Y) :- tr(X,Z), tr(Z,Y).
:- tr(X,X).
"""
programs = [basic, aggregates, pigeon, loop, many_loops]
#programs = [""" a ; b :- 1 #sum {1:b; 1:c}. {c}."""]
programs = [many_loops]
if __name__ == "__main__":
    # meta
    for program in programs:
        print("##### META  #######")
        print(program)
        run(program)
        print("#####################")
    programs = []
    # metaD
    for program in programs:
        print("##### METAD #######")
        print(program)
        run(program, True)
        print("#####################")

