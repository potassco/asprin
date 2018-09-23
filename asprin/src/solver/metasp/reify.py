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


# imports
import subprocess
import tempfile
import re


# defines
CLINGO = "clingo"
REIFY_OUTPUT = "--output=reify"
VERSION = "--version"
NO_CLINGO = "clingo binary version not found (when running 'clingo --version')"
OLD_CLINGO = """clingo binary too old (when running 'clingo --version')\
 version 5.3 or newer is needed"""


#
# classes Node and Graph used by reify_from_observer()
#

# by Roland Kaminski, modified by Javier Romero
class Node:

    def __init__(self, name):
        self.name = name
        self.neighbors = []
        self.visited_  = 0
        self.finished_ = 1

    def add_neighbor(self, neighbor): self.neighbors.append(neighbor)
    def get_neighbors(self): return self.neighbors
    def next_neighbors(self): return self.neighbors[self.finished_ - 1:]

    def visit(self, visited): self.visited_ = visited + 1
    def visited(self): return self.visited_ - 1

    def mark(self): self.visited_ = 1
    def marked(self): return self.visited_ >= 1

    def pop(self): self.finished_ = 0
    def popped(self): return self.finished_ == 0
    def inc_finished(self): self.finished_ += 1


# by Roland Kaminski, modified by Javier Romero
class Graph:

    def __init__(self):
        self.graph = {}
        self.sccs = []
        self.singletons = set()

    def add_edge(self, head, body):
        if head == body:
            self.singletons.add(head)
            return
        node = self.graph.get(head, None)
        if not node:
            node = Node(head)
            self.graph[head] = node
        node.add_neighbor(body)

    def reify_sccs(self, prefix=""):
        # compute sccs and update self.singletons
        for _, v in self.graph.items():
            if not v.marked():
                self.tarjan(v)
        # return string
        out = ""
        for idx, item in enumerate(list(self.singletons) + self.sccs):
            out += " ".join(["{}scc({},{}).".format(prefix, idx, i) for i in item]) + "\n"
        return out

    # private
    def next(self, v):
        for y in v.next_neighbors():
            v.inc_finished()
            node = self.graph.get(y, None)
            if node and not node.marked():
                return node
        return None

    # private
    def root(self, v):
        root = True
        for y in v.get_neighbors():
            node = self.graph.get(y, None)
            if node and not node.popped() and node.visited() < v.visited():
                root = False
                v.visit(node.visited())
        return root

    # private
    def tarjan(self, start):

        s, t = [], []
        visited = 0
        s.append(start)
        start.mark()

        def top(s): return s[-1]

        while len(s) > 0:
            x = top(s)
            if x.visited() == 0:
                visited  += 1
                x.visit(visited)
            y = self.next(x)
            if y != None:
                s.append(y)
                y.mark()
            else:
                s.pop()
                if self.root(x):
                    scc = [x.name]
                    x.pop()
                    while len(t) > 0 and top(t).visited() >= x.visited():
                        y = t.pop()
                        y.pop()
                        scc.append(y.name)
                        self.singletons.discard(y.name) # update self.singletons
                    if len(scc)>1:
                        self.sccs.append(scc)           # update self.sccs
                        self.singletons.discard(x.name) # update self.singletons
                else: t.append(x)


#
# reify_from_observer()
#
# * uses a clingo observer with fields:
#   - rules
#   - weight_rules
#   - output_atoms
#   - output_terms
#

# TODO: Implement option where we take care about repeated heads and bodies
def reify_from_observer(observer, prefix=""):

    # start
    out = ""
    literal_tuple, wliteral_tuple, atom_tuple = 1, 1, 1
    p = prefix

    # fact 0
    # out += "% fact 0\n"
    out += "{}rule(disjunction(0),normal(0)). ".format(p)
    out += "{}atom_tuple(0,0). {}literal_tuple(0).\n\n".format(p, p)

    # start graph
    graph = Graph()

    # normal rules
    for choice, head, body in observer.rules:

        # out += "% normal rule\n"
        # body
        if body:
            out += "{}literal_tuple({}).".format(p, literal_tuple) + "\n"
            out += " ".join([
                "{}literal_tuple({},{}).".format(p, literal_tuple, l)
                for l in body
            ]) + "\n"
        # head
        head_type = "choice" if choice else "disjunction"
        out += "{}rule({}({}),normal({})).".format(
            p, head_type, atom_tuple, literal_tuple if body else 0
        ) + "\n"
        out += " ".join([
            "{}atom_tuple({},{}).".format(p, atom_tuple, l) for l in head
        ]) + "\n\n"
        # update counters
        if body:
            literal_tuple += 1
        atom_tuple += 1
        # update graph (this can be interwined with the rules above)
        for l in body:
            if l >= 0:
                for atom in head:
                    graph.add_edge(atom, l)

    # weight rules
    for choice, head, lower_bound, body in observer.weight_rules:
        # out += "% weighted rule\n"
        # body
        out += " ".join([
            "{}weighted_literal_tuple({},{},{}).".format(
                p, wliteral_tuple, l, w
            ) for l, w in body
        ]) + "\n"
        # head
        head_type = "choice" if choice else "disjunction"
        out += "{}rule({}({}),sum({},{})).".format(
            p, head_type, atom_tuple, wliteral_tuple, lower_bound
        ) + "\n"
        out += " ".join([
            "{}atom_tuple({},{}).".format(p, atom_tuple, l) for l in head
        ]) + "\n\n"
        # update counters
        wliteral_tuple += 1
        atom_tuple += 1
        # update graph (this can be interwined with the rules above)
        for l, w in body:
            if l >= 0:
                for atom in head:
                    graph.add_edge(atom, l)

    # sccs
    # out += "% sccs\n"
    out += graph.reify_sccs(p) + "\n"

    # output atoms
    # out += "% output atoms\n"
    for symbol, atom in observer.output_atoms:
        out += "{}output({},{}).\n".format(p, symbol, atom)

    # output terms
    # out += "% output term\n"
    for symbol, condition in observer.output_terms:
        out += "{}output_term({}).\n".format(p, symbol) + "\n"
        out += " ".join([
            "{}output_term({},{}).".format(p, symbol, l) for l in condition
        ]) + "\n"

    return out


#
# reify_from_string()
#
# * uses a clingo binary not older than than clingo-5.3
#

# run command and return stdout as a string
def run_command(command):
    output = subprocess.check_output(command)
    if isinstance(output, bytes):
        return output.decode()
    return output

def check_clingo_version():
    version = run_command([CLINGO, VERSION])
    match = re.match(r'clingo version (\d+)\.(\d+)', version)
    if match:
        first  = int(match.group(1))
        second = int(match.group(2))
        if first > 5 or (first == 5 and second >= 3):
            return
        raise Exception(OLD_CLINGO)
    raise Exception(NO_CLINGO)

def reify_from_string(program, prefix):
    check_clingo_version()
    with tempfile.NamedTemporaryFile(delete=False) as file_in:
        # write program to file_in
        file_in.write(program.encode())
        file_in.flush()
    # run command
    command = [CLINGO, REIFY_OUTPUT, file_in.name]
    output = run_command(command)
    # add prefix and return
    output = re.sub(r'^(\w+)', r'' + prefix + r'\1', output, flags=re.M)
    return output


