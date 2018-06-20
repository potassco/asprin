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

from __future__ import print_function
from collections import namedtuple


NodeInfo = namedtuple('NodeInfo','key item')


class Node:

    def __init__(self, key, item):
        self.key  = key
        self.item = item
        self.next = set()
        self.prev = set()
        self.neg_next = set()
        self.neg_prev = set()

    def __str__(self):
        out = []
        if self.next:
            out += [(i.key, "+") for i in self.next]
        if self.neg_next:
            out += [(i.key, "-") for i in self.neg_next]
        ret = "#{}\n:{}\n".format(self.key, str(self.item))
        list_ = ["({},{},{})".format(self.key, i[0], i[1]) for i in out]
        return ret + "\n".join(list_)


class TransitiveClosure:

    def __init__(self):
        self.nodes = {}

    #
    # CREATE THE GRAPH
    #

    # add set_1 to set_2, and delete set_1 from set_3
    def __update(self, set_1, set_2, set_3):
        set_2.update(set_1)
        set_3.difference_update(set_1)

    # update graph with (NodeInfo) a
    # do not add item if it is None
    def add_node(self, a):
        node = self.nodes.get(a.key)
        if not node:
            item = [a.item] if a.item is not None else []
            node = Node(a.key, item)
            self.nodes[a.key] = node
        elif a.item is not None:
            node.item.append(a.item)
        return node

    # add edge from (NodeInfo) a to (NodeInfo) b 
    # if flag, then the edge has negative sign
    # if not add_node, then a and b must be in the graph
    def add_edge(self, a, b, flag, add_node=False):

        # nodes
        if add_node:
            node_a = self.add_node(a)
            node_b = self.add_node(b)
        else:
            node_a = self.nodes[a.key]
            node_b = self.nodes[b.key]

        # next
        if not flag: # positive sign
            next = node_b.next.copy()
            next.add(node_b)
            node_a.next.update(next)
            for i in node_a.prev:
                i.next.update(next)
            for i in node_a.neg_prev:
                self.__update(next, i.neg_next, i.next)

        # neg_next
        if not flag: # positive sign
            neg_next = node_b.neg_next
        else:
            neg_next = node_b.neg_next.union(node_b.next)
            neg_next.add(node_b)
        if neg_next:
            self.__update(neg_next, node_a.neg_next, node_a.next)
            for i in node_a.prev:
                self.__update(neg_next, i.neg_next, i.next)
            for i in node_a.neg_prev:
                self.__update(neg_next, i.neg_next, i.next)

        # prev
        if not flag: # positive sign
            prev = node_a.prev.copy()
            prev.add(node_a)
            node_b.prev.update(prev)
            for i in node_b.next:
                i.prev.update(prev)
            for i in node_b.neg_next:
                self.__update(prev, i.neg_prev, i.prev)

        # neg_prev
        if not flag: # positive sign
            neg_prev = node_a.neg_prev
        else:
            neg_prev = node_a.neg_prev.union(node_a.prev)
            neg_prev.add(node_a)
        if neg_prev:
            self.__update(neg_prev, node_b.neg_prev, node_b.prev)
            for i in node_b.next:
                self.__update(neg_prev, i.neg_prev, i.prev)
            for i in node_a.neg_next:
                self.__update(neg_prev, i.neg_prev, i.prev)

    def __str__(self):
        out = ""
        for key, item in self.nodes.items():
            out += str(item) + "\n"
        return out

    #
    # USE THE GRAPH
    #

    # pre: key must be in the graph
    def get_next(self, key):
        out = self.nodes[key].next.union(self.nodes[key].neg_next)
        return [i.key for i in out]

    def get_cycles(self):
        out = []
        for key, value in self.nodes.items():
            if value in value.neg_next:
                out.append(NodeInfo(key, None))
        return out

    def map_items(self, f):
        for node in self.nodes.values():
            for i in node.item:
                f(i)


if __name__ == "__main__":
    graph = [(1,2,True), (2,3,True), (3,4,False), (4,5,True), (5,5,True),
             (7,8,False), (8,7,False), (2,1,False)]#, (5,1,True)]
    tmp = []
    for i in range(1,2):
        for j in graph:
            tmp.append((j[0]*i,j[1]*i,j[2]))
    graph = tmp
    tc = TransitiveClosure()
    for i in graph:
        tc.add_edge(NodeInfo(i[0],i[0]), NodeInfo(i[1],i[1]), i[2], True)
    print(tc)

