#!/usr/bin/python

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

