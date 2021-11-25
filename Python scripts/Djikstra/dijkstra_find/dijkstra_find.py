import networkx as nx
import math
from time import time
from collections import deque
import matplotlib.pyplot as plt
import json
import itertools
from heapq import heapify, heappush, heappop
import numpy as np

class PriorityQueue:

    REMOVED = '<removed-task>' # placeholder for a removed task

    def __init__(self, tasks_prios=None):
        self.pq = []
        self.entry_finder = {} # mapping of tasks to entries
        self.counter = itertools.count() # unique sequence count -- tie-breaker when prios equal
        if tasks_prios:
            for task, prio in tasks_prios:
                self.add_task(task, prio) # would be nice to use heapify here instead

    def __iter__(self):
        return ((task, prio) for (prio, count, task) in self.pq if task is not self.REMOVED)

    def __len__(self):
        return len(list(self.__iter__()))

    def __str__(self):
        return str(list(self.__iter__()))

    def add_task(self, task, priority=0):
        'Add a new task or update the priority of an existing task'
        if task in self.entry_finder:
            self.remove_task(task)
        count = next(self.counter)
        entry = [priority, count, task]
        self.entry_finder[task] = entry
        heappush(self.pq, entry)

    def remove_task(self, task):
        'Mark an existing task as REMOVED.  Raise KeyError if not found.'
        entry = self.entry_finder.pop(task)
        entry[-1] = self.REMOVED

    def pop_task(self):
        'Remove and return the lowest priority task. Raise KeyError if empty.'
        while self.pq:
            priority, count, task = heappop(self.pq)
            if task is not self.REMOVED:
                del self.entry_finder[task]
                return task, priority # NB a change from the original: we return prio as well
        raise KeyError('pop from an empty priority queue')

def bi_dijkstra_PQ(E, G, start, target):
    # All the same data structures are used, except now there are structures for both the
    # forward and backward directions
    P_f = {start}
    P_b = {target}
    S_f = PriorityQueue()
    S_b = PriorityQueue()
    D_f = {}
    D_b = {}
    p_f = {}
    p_b = {}

    # Forward Initialisation
    for n in G.nodes():
        if n == start:
            D_f[n] = 0
        else:
            if G.has_edge(start, n):
                D_f[n] = G[start][n]["weight"]
            else:
                D_f[n] = math.inf

            p_f[n] = start
            S_f.add_task(n, D_f[n])

    # Backward Initialisation
    for n in G.nodes():
        if n == target:
            D_b[n] = 0
        else:
            if G.has_edge(target, n):
                D_b[n] = G[target][n]["weight"]
            else:
                D_b[n] = math.inf

            p_b[n] = target
            S_b.add_task(n, D_b[n])

    alg_continue = True
    while alg_continue != False:
        # Forward
        # pop_task() removes and returns the lowest priority task
        u, Du = S_f.pop_task()
        if u in P_f: continue

        P_f.add(u)

        for v, Dv in S_f:
            if v in P_f: continue
            if G.has_edge(u, v):
                if D_f[v] > D_f[u] + G[u][v]["weight"]:
                    D_f[v] = D_f[u] + G[u][v]["weight"]
                    p_f[v] = u
                    S_f.add_task(v, D_f[v])

        if u in P_b:
            alg_continue = False
            w = u
            continue
        else:
            pass

        # Backward
        # pop_task() removes and returns the lowest priority task
        u, Du = S_b.pop_task()
        if u in P_b: continue

        P_b.add(u)

        for v, Dv in S_b:
            if v in P_b: continue
            if G.has_edge(u, v):
                if D_b[v] > D_b[u] + G[u][v]["weight"]:
                    D_b[v] = D_b[u] + G[u][v]["weight"]
                    p_b[v] = u
                    S_b.add_task(v, D_b[v])

        if u in P_f:
            alg_continue = False
            w = u
            continue
        else:
            pass

    # The SP at the visited node is calculated
    min_dist = D_f[w] + D_b[w]

    # All nodes are now visited in both the forward and backward direction
    # The distance to these numbers in both directions are added and compared with the minimum
    # distance to the stopping node. If the new distance is smaller, the node is on the SP
    SP_node = w
    for i in G.nodes():
        if D_f[i] + D_b[i] < min_dist:
            min_dist = D_f[i] + D_b[i]
            SP_node = i
            SP = deque()
        else:
            SP = deque([SP_node])

    # The shortest path is created by going through all parent nodes from the min distance connection
    # node in both the forward and backward direction
    next = SP_node
    while next != start:
        for i, k in p_f.items():
            if i == next:
                SP.appendleft(k)
                next = k

    next = SP_node
    while next != target:
        for i, k in p_b.items():
            if i == next:
                SP.append(k)
                next = k

    j = 0
    summ = 0
    x = len(SP)
    y = x - 1
    for i in E:
        if j == y:
            break
        if SP[j] in i and SP[j+1] in i:
            summ += i[2]
            j += 1
    
    return list(SP), summ

def loadJson(file):
    with open(file, 'r') as f:
        data = json.load(f)
        return loadData(data)

def loadData(data):
    E = list()
    # for i in data:
    #     for j in data[i]:
    #         l = (i, j, data[i][j])
    #         E.append(l)
    # return E
    start = data["start"]
    end = data["goal"]
    data = np.array(data["matrix"])
    n, m = data.shape

    names_matr = data.copy()
    num_cell = 0
    for i in range(n):
        for j in range(m):
            names_matr[i][j] = str(num_cell)
            num_cell += 1
    print(names_matr)



    num_cell = 0
    for i in range(n):
        for j in range(m):
            if i == 0 and j == 0:
               l = (str(names_matr[i][j]), str(names_matr[i+1][j]), data[i+1][j])
               E.append(l)
               l = (str(names_matr[i][j]), str(names_matr[i][j+1]), data[i][j+1])
               E.append(l)

            elif i == 0 and j != 0 and j != m-1:
                l = (str(names_matr[i][j]), str(names_matr[i+1][j]), data[i+1][j])
                E.append(l)
                l = (str(names_matr[i][j]), str(names_matr[i][j+1]), data[i][j+1])
                E.append(l)
                l = (str(names_matr[i][j]), str(names_matr[i][j-1]), data[i][j-1])
                E.append(l)

            elif i == 0 and j == m-1:
                l = (str(names_matr[i][j]), str(names_matr[i+1][j]), data[i+1][j])
                E.append(l)
                l = (str(names_matr[i][j]), str(names_matr[i][j-1]), data[i][j-1])
                E.append(l)

            elif j == 0 and i != 0 and i != n-1:
                l = (str(names_matr[i][j]), str(names_matr[i+1][j]), data[i+1][j])
                E.append(l)
                l = (str(names_matr[i][j]), str(names_matr[i][j+1]), data[i][j+1])
                E.append(l)
                l = (str(names_matr[i][j]), str(names_matr[i-1][j]), data[i-1][j])
                E.append(l)

            elif j == 0 and i == n-1:
                l = (str(names_matr[i][j]), str(names_matr[i][j+1]), data[i][j+1])
                E.append(l)
                l = (str(names_matr[i][j]), str(names_matr[i-1][j]), data[i-1][j])
                E.append(l)

            elif i == n-1 and j == m-1:
               l = (str(names_matr[i][j]), str(names_matr[i-1][j]), data[i-1][j])
               E.append(l)
               l = (str(names_matr[i][j]), str(names_matr[i][j-1]), data[i][j-1])
               E.append(l)

            elif i == n-1 and j != m-1:
                l = (str(names_matr[i][j]), str(names_matr[i-1][j]), data[i-1][j])
                E.append(l)
                l = (str(names_matr[i][j]), str(names_matr[i][j-1]), data[i][j-1])
                E.append(l)
                l = (str(names_matr[i][j]), str(names_matr[i][j+1]), data[i][j+1])
                E.append(l)

            elif j == m-1 and i != n-1:
                l = (str(names_matr[i][j]), str(names_matr[i-1][j]), data[i-1][j])
                E.append(l)
                l = (str(names_matr[i][j]), str(names_matr[i][j-1]), data[i][j-1])
                E.append(l)
                l = (str(names_matr[i][j]), str(names_matr[i+1][j]), data[i+1][j])
                E.append(l)

            else:
               l = (str(names_matr[i][j]), str(names_matr[i-1][j]), data[i-1][j])
               E.append(l)
               l = (str(names_matr[i][j]), str(names_matr[i][j-1]), data[i][j-1])
               E.append(l)
               l = (str(names_matr[i][j]), str(names_matr[i+1][j]), data[i+1][j])
               E.append(l)
               l = (str(names_matr[i][j]), str(names_matr[i][j+1]), data[i][j+1])
               E.append(l)

    start = list(start)
    end = list(end)
    start = names_matr[int(start[1])][int(start[3])]
    end = names_matr[int(end[1])][int(end[3])]
    print(start, end)
    print(E)
    return E, start, end
def main():
    graph_json, start, end = loadJson('matrix.json')
    print(graph_json)
    ### Graph 1 ###
    G = nx.Graph()

    # E = (
    #     ("A", "B", 2),
    #     ("A", "C", 7),
    #     ("A", "D", 8),

    #     ("B", "G", 10),
    #     ("B", "C", 8),

    #     ("C", "D", 1),
    #     ("C", "E", 5),
    #     ("C", "G", 9),
    #     ("C", "F", 3),

    #     ("D", "F", 9),
    #     ("G", "E", 4),
    #     ("E", "F", 1)
    # )
    # print(E)
    E = graph_json
    G.add_weighted_edges_from(E)
    pos = nx.circular_layout(G)
    nx.draw_networkx(G, pos, node_size=700)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.savefig('graph.png')

    path, length = bi_dijkstra_PQ(E, G, str(start), str(end))
    print("Shortest Path:", path, length)


if __name__ == '__main__':
    main()