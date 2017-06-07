from collections import namedtuple


Info = namedtuple('Info','key item')


class Node:

    def __init__(self, key, item):
        self.key  = key
        self.item = item
        self.next = set()
        self.prev = set()
        self.not_next = set()
        self.not_prev = set()
    
    def __str__(self):
        out = []
        if self.next:
            out += [(i.item,"+") for i in self.next]
        if self.not_next:
            out += [(i.item,"-") for i in self.not_next]
        if out == []:
            return "({})".format(self.item)
        else:
            out = ["({},{},{})".format(self.item,i[0],i[1]) for i in out]
            return "\n".join(out)
        

class TransitiveClosure:

    def __init__(self):
        self.__nodes = {}

    # add set_1 to set_2, and delete set_1 from set_3
    def __update(self, set_1, set_2, set_3):
        set_2.update(set_1)
        set_3.difference_update(set_1)
    
    def add(self, a, b, sign):
        
        # node_a
        node_a = self.__nodes.get(a.key)
        if not node_a:
            node_a = Node(a.key, a.item)
            self.__nodes[a.key] = node_a
        
        # node_b
        node_b = self.__nodes.get(b.key)
        if not node_b:
            node_b = Node(b.key, b.item)
            self.__nodes[b.key] = node_b
        
        # next
        if sign:
            next = node_b.next.copy()
            next.add(node_b)
            node_a.next.update(next)
            for i in node_a.prev:
                i.next.update(next)
            for i in node_a.not_prev:
                self.__update(next, i.not_next, i.next)
        
        # not_next
        if sign:
            not_next = node_b.not_next
        else:
            not_next = node_b.not_next.union(node_b.next)
            not_next.add(node_b)
        if not_next:
            self.__update(not_next, node_a.not_next, node_a.next)
            for i in node_a.prev:
                self.__update(not_next, i.not_next, i.next)
            for i in node_a.not_prev:
                self.__update(not_next, i.not_next, i.next)
        
        # prev
        if sign:
            prev = node_a.prev.copy()
            prev.add(node_a)
            node_b.prev.update(prev)
            for i in node_b.next:
                i.prev.update(prev)
            for i in node_b.not_next:
                self.__update(prev, i.not_prev, i.prev)
        
        # not_prev
        if sign:
            not_prev = node_a.not_prev
        else:
            not_prev = node_a.not_prev.union(node_a.prev)
            not_prev.add(node_a)
        if not_prev:
            self.__update(not_prev, node_b.not_prev, node_b.prev)
            for i in node_b.next:
                self.__update(not_prev, i.not_prev, i.prev)
            for i in node_a.not_next:
                self.__update(not_prev, i.not_prev, i.prev)

    def __str__(self):
        out = ""
        for key, item in self.__nodes.items():
            out += str(item) + "\n"
        return out


if __name__ == "__main__":
    graph = [(1,2,True), (2,3,True), (3,4,False), (4,5,True), (5,5,True), (2,1,False), (5,1,True)]
    tc = TransitiveClosure()
    for i in graph:
        tc.add(Info(i[0],i[0]),Info(i[1],i[1]),i[2])
    print tc

