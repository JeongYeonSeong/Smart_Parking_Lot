from collections import defaultdict
import math
from heapq import heapify, heappush, heappop
import configs.config as cf
from configs.sockets import Servers
aws_ip = cf.AWS_IP

# utility: priority queue
class Pq:
    def __init__(self):
        self.queue = []
        
    def __str__(self):
        return str(self.queue)
        
    def insert(self, item):
        heappush(self.queue, item)
    
    def extract_min(self):
        return heappop(self.queue)[1]
    
    def update_priority(self, key, priority):
        for v in self.queue:
            if v[1] == key:
                v[0] = priority
        heapify(self.queue)
    
    def empty(self):
        return len(self.queue) == 0

# utility: Graph
class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = defaultdict(lambda: [])
    
    def add_edge(self, node, target, distance):
        self.graph[node].append([target, distance])

    def set_distance(self, node, target, distance): 
        node = str(node)
        target = str(target)
        for i in self.graph[node]:
            if i[0] == target:
                i[1] = distance
                break
        
        for i in self.graph[target]:
            if i[0] == node:
                i[1] = distance

    def get_distance(self, node, target):
        for i in self.graph[str(node)]:
            if i[0] == str(target):
                return i[1]

    def __str__(self):
        result = ''
        for v in self.V:
            result += f'{v}: {str(self.graph[v])}, \n'
        return result
        
def dijkstra(graph, s):
    Q = Pq() # priority queue of vertices
    		 # [ [distance, vertex], ... ] 
    d = dict.fromkeys(graph.V, math.inf) # distance pair 
                                         # will have default value of Infinity
    pi = dict.fromkeys(graph.V, None) # map of parent vertex
    								  # useful for finding shortest path	
    
    # initialize
    d[s] = 0
    
    # update priority if prior path has larger distance
    def relax(u, v, w):
        if d[v] > d[u] + w:
            d[v] = d[u] + w
            Q.update_priority(v, d[v])
            pi[v] = u
    
    # initialize queue
    for v in graph.V:
        Q.insert([d[v], v])
    
    while not Q.empty():
        u = Q.extract_min()
        for v, w in graph.graph[u]:
            relax(u, v, w)
        
    return d, pi

def shortest_path(s, t, g):
    d, pi = dijkstra(g, s)
    path = [t]
    current = t

    # if parent pointer is None,
    # then it's the source vertex
    while pi[current]:
        path.insert(0, pi[current])
        # set current to parent
        current = pi[current]
        
    if s not in path:
        return f'unable to find shortest path staring from "{s}" to "{t}"'
    
    #get length of pathes
    size = 0
    route = []
    for k, i in enumerate(path):
        route.append(str(i))
        size += d[i]
    
    # 우선순위
    # 오른 쪽 우선
    for i in path:
        if path[-1] in ['4', '20']:
            size -= 5
        elif path[-1] == '12':
            size -= 3
    
    return [i for i in path], size, route
    
# Navigating
class Navigate:
    def __init__(self):
        self.graph = [[2,6], [1,3], [2,4,7], [3,5], [4,8],
            [1,9], [3,11], [5,13],
            [6,10,14], [9,11], [7,10,12,15], [11,13], [8,12,16],
            [9,17], [11,19], [13,21],
            [14,18], [17,19], [15,18,20], [19,21], [16,20]
        ]
        self.parking = [2, 4, 10, 12, 18, 20]
        self.empty_p = [3, 3,  6,  6,  3,  3]
        self.edges = []
        self.init_edges()
        self.g = Graph([str(k) for k in range(1, 22)])
        for i, node in enumerate(self.graph):
            for k in node:
                self.g.add_edge(str(i + 1), str(k), 1)
        
    def routing(self, park=None, prev=0, start=9):
        parks = self.parking[0:]
        
        if len(self.parking) == 0:
            return 'there\'s no parking lot'

        r_back_distance = self.g.get_distance(start, prev)
        
        if prev != 0:
            self.g.set_distance(str(start), str(prev), 9999)
        route = []
        
        for i in parks:
            result = list(shortest_path(str(start), str(i), self.g))
            route.append(result)

        # 우선 순위 정하기
        min = route[0][1]
        index = 0
        for i, data in enumerate(route):
            if i == 0:
                continue

            if min > data[1]:
                min = data[1]
                index = i
        self.route = route[index][2]

        self.g.set_distance(str(start), str(prev), r_back_distance)
        
        return self.route

    def init_edges(self):
        edges = [4,3,3,4,3,3,4]
        for i, edge in enumerate(edges):
            self.edges.append([])
            for k in range(edge):
                self.edges[i].append(1)

server = Servers(Navigate())
