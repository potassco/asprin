from collections import namedtuple


Info = namedtuple('Info','key item')


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
            out += [(i.item,"+") for i in self.next]
        if self.neg_next:
            out += [(i.item,"-") for i in self.neg_next]
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
            for i in node_a.neg_prev:
                self.__update(next, i.neg_next, i.next)
        
        # neg_next
        if sign:
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
        if sign:
            prev = node_a.prev.copy()
            prev.add(node_a)
            node_b.prev.update(prev)
            for i in node_b.next:
                i.prev.update(prev)
            for i in node_b.neg_next:
                self.__update(prev, i.neg_prev, i.prev)
        
        # neg_prev
        if sign:
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
        for key, item in self.__nodes.items():
            out += str(item) + "\n"
        return out


if __name__ == "__main__":
    graph = [(1,2,True), (2,3,True), (3,4,False), (4,5,True), (5,5,True),
             (7,8,False), (8,7,False), (2,1,False), (5,1,True)]
    tmp = []
    for i in range(1,100):
        for j in graph:
            tmp.append((j[0]*i,j[1]*i,j[2]))
    graph = tmp
    tc = TransitiveClosure()
    for i in graph:
        tc.add(Info(i[0],i[0]),Info(i[1],i[1]),i[2])
    #print tc

