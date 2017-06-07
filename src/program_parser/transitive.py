from collections import namedtuple

Info = namedtuple('Info','key item')

class Node:

    def __init__(self, key, item):
        self.key  = key
        self.item = item
        self.next = set()
        self.prev = set()
    
    def __str__(self):
        if self.next:
            return '\n'.join(["({},{})".format(self.item,j.item) for j in self.next])
        return "({})".format(self.item)
        
class TransitiveClosure:

    def __init__(self):
        self.__nodes = {}

    def add(self, a, b):
        # nodea
        nodea = self.__nodes.get(a.key)
        if not nodea:
            nodea = Node(a.key, a.item)
            self.__nodes[a.key] = nodea
        # nodeb
        nodeb = self.__nodes.get(b.key)
        if not nodeb:
            nodeb = Node(b.key, b.item)
            self.__nodes[b.key] = nodeb
        # next
        next = nodeb.next.copy()
        next.add(nodeb)
        nodea.next.update(next)
        for i in nodea.prev:
            i.next.update(next)
        # prev
        prev = nodea.prev.copy()
        prev.add(nodea)
        nodeb.prev.update(prev)
        for i in nodeb.next:
            i.prev.update(prev)

    def __str__(self):
        out = ""
        for key, item in self.__nodes.items():
            out += str(item) + "\n"
        return out

if __name__ == "__main__":
    graph = [(5,2), (6,1), (2,5), (2,3), (5,1), (1,2), (2,6)]
    tc = TransitiveClosure()
    for i in graph:
        tc.add(Info(i[0],i[0]),Info(i[1],i[1]))
    print tc

