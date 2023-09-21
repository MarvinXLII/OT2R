import os
import sys
FILEDIR = os.path.dirname(os.path.realpath(__file__))
from copy import deepcopy
import hjson
import pickle
import random

sys.path.append(f'{FILEDIR}/../src')
from Manager import Manager
from Pak import MainPak
from DataJson import DataJsonFile


def is_pc(x):
    return x in ['unlock_hikari', 'unlock_ochette', 'unlock_castti', 'unlock_partitio',
                 'unlock_temenos', 'unlock_osvald', 'unlock_throne', 'unlock_agnea']

class Graph:
    def __init__(self):
        self.edges = {}
        self.nodes = set()
        self.slots = set()
        self.visited = set()
        self.ring_dict = {}

    def reset(self):
        self.visited = set()
        for node in self.nodes:
            node.reset()

    def get_rings(self, always_have):
        visited = {n:False for n in self.nodes}
        everything = set(always_have)
        # Rank is ignored here
        everything.add('rank_1')
        everything.add('rank_2')
        inventory = set()
        rings = []
        current_ring = []
        while True:
            new_node_visited = False
            for node in self.nodes:
                if visited[node]: continue
                for cost in node.costs:
                    if cost.issubset(everything):
                        visited[node] = True
                        new_node_visited = True
                        if node.is_slot:
                            current_ring.append(node)
                        else:
                            inventory.update(node.slots)
                            inventory.add(node.name)
                        break

            everything.update(inventory)
            if not new_node_visited:
                if len(inventory) == 0 and len(current_ring) == 0:
                    break
                rings.append(current_ring)
                for node in current_ring:
                    everything.add(node.name)
                    everything.update(node.slots)
                current_ring = []
                inventory = set()

        for ri in rings:
            ri.sort()
            for ni in ri:
                ni.slots.sort()

        for i, ring in enumerate(rings):
            for node in ring:
                self.ring_dict[node] = i

        return rings

    def shuffle(self, start, inventory, always_have=None):
        if always_have is None:
            always_have = []
        inventory = sorted(inventory.difference(always_have))

        num_slots = 0
        for node in self.nodes:
            node.clear_slot()
            num_slots += node.is_slot
        # n = len(inventory) // num_slots
        # n += len(inventory) % num_slots > 0
        # for node in self.nodes:
        #     node.max_num = n

        while len(inventory) > 0:
            # Track which slots are accessible when removing each item.
            # This is used for prioritizing the inventory.
            accessible = {item:set() for item in inventory}
            for i, item in enumerate(inventory):
                inventory.pop(i)
                accessible[item] = self.get_accessible(inventory + always_have)
                inventory.insert(i, item)

            # Give priority to items with the fewest accessible slots
            random.shuffle(inventory)
            inventory.sort(key=lambda item: len(accessible[item]))

            # Assign the item to a slot
            for i in range(len(inventory)):
                item = inventory[i]
                if len(accessible[item]):
                    a = sorted(accessible[item])
                    w = [n.get_weight() for n in a]
                    slot = random.choices(a, w)[0]
                    slot.set_slot(item)
                    inventory.pop(i)
                    break
            else:
                for node in self.nodes:
                    node.increment_max_num()

    # Traverse the graph with an inventory and return all accessible treasure nodes
    def get_accessible(self, inventory):
        pcs = set()
        for x in inventory:
            if is_pc(x):
                pcs.add(x)
        
        inv_set = set(inventory)
        visited = set()
        vacant_events = set()
        num_chapters_finished = 0
        while True:
            inv_size = len(inv_set)
            for node in self.nodes:
                if node not in visited:
                    for cost in node.costs:
                        if cost.issubset(inv_set):
                            visited.add(node)
                            inv_set.update(node.slots)
                            inv_set.add(node.name)
                            if node.is_vacant and node.is_slot:
                                vacant_events.add(node)
                            for s in node.slots:
                                if is_pc(s):
                                    pcs.add(s)
                                assert len(pcs) <= 8
                            num_chapters_finished += node.name.startswith('finish_chapter')
                            break

            if len(pcs) > 2 and num_chapters_finished > 6:
                inv_set.add('rank_1')

            if len(pcs) > 5 and num_chapters_finished > 12:
                inv_set.add('rank_2')

            # If no new items were added, then it is impossible to access any unvisited nodes
            if len(inv_set) == inv_size:
                break

        return vacant_events

    def store_node_costs(self, start):
        visited = {n:False for n in self.nodes}
        queue = [start]
        start.add_cost(set())

        def dfs():
            while queue:
                node = queue.pop()
                for neighbor in node.neighbors:
                    edge = self.get_edge(node, neighbor)
                    if not edge.costs:
                        for nc in node.costs:
                            neighbor.add_cost(nc)
                            neighbor.add_cost(nc)
                    else:
                        for nc in node.costs:
                            for ec in edge.costs:
                                neighbor.add_cost(nc.union(ec))
                                neighbor.add_cost(nc.union(ec))

                    if not visited[neighbor]:
                        visited[neighbor] = True
                        queue.append(neighbor)
                        dfs()
                        # undo visited to ensure all paths to each node are considered
                        visited[neighbor] = False
            
        dfs()
        
    def add_node(self, node):
        self.nodes.add(node)

    def add_edge(self, start, end, cost=None):
        self.add_node(start)
        self.add_node(end)
        edge = self.get_edge(start, end)
        edge.add_cost(cost)

    def get_edge(self, start, end):
        if (start, end) in self.edges:
            return self.edges[(start, end)]
        start.add_neighbor(end)
        self.edges[(start, end)] = Edge(start, end)
        return self.edges[(start, end)]

    def plot(self, filename):
        import pydot
        G = pydot.Dot(graph_type='digraph', rankdir='LR')
        for node in self.nodes:
            ni = pydot.Node(node.name)
            label = node.name
            if node.slots or node.is_slot:
                if node.is_slot:
                    ni.set_shape('square')
                else:
                    ni.set_shape('diamond')
                x = '\n'.join(node.slots)
                label = f"{node.name}\n{x}"
            if node in self.ring_dict:
                ni.set_label(f'{label}\n{self.ring_dict[node]}')
                ni.set_style('filled')
                if label == 'START' or label == 'Virdania':
                    ni.set_fillcolor('lightgreen')
                elif node.slots or node.is_slot:
                    ni.set_fillcolor('red')
                else:
                    ni.set_fillcolor('lightblue')
            if 'finished_flame' in label:
                ni.set_fillcolor('lightpurple')
            G.add_node(ni)

        for (start, end), edge in self.edges.items():
            ei = pydot.Edge(start.name, end.name, arrowhead='none')
            if edge.costs:
                labels = [', '.join(c) for c in edge.costs]
                all_labels = '\n'.join(labels)
                ei.set_label(all_labels)
            G.add_edge(ei)
    
        G.write_png(filename)
        


class Edge:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.costs = []

    def add_cost(self, cost):
        for c in cost:
            self.costs.append(c)

    def is_passable(self, inventory):
        for cost in self.costs:
            if inventory.issuperset(cost):
                return True
        return len(self.costs) == 0

    def __repr__(self):
        return f'{self.start} -> {self.end}'


class Node:
    def __init__(self, name, items=None):
        self.name = name
        self.neighbors = set()
        self.iteration = sys.maxsize
        self.costs = set()

        # NEW STUFF
        self._max_num = 0
        self._is_slot = False
        self.slots = [] if items is None else deepcopy(items)
        self.vanilla = deepcopy(self.slots)


    def add_neighbor(self, node):
        self.neighbors.add(node)

    def reset(self):
        self.iteration = sys.maxsize

    def set_iteration(self, iteration):
        self.iteration = min(self.iteration, iteration)

    def add_cost(self, cost):
        # First check if this cost is a superset of anything
        # Don't add it if so
        for c in self.costs:
            if cost.issuperset(c):
                return
        # Remove all costs that are supersets of the new cost
        remove = set()
        for c in self.costs:
            if cost.issubset(c):
                remove.add(c)
        self.costs = self.costs - remove
        self.costs.add(frozenset(cost))

    @property
    def is_slot(self):
        return self._is_slot

    @is_slot.setter
    def is_slot(self, value):
        self._is_slot = value
        self._max_num = 1 if value else 0

    @property
    def max_num(self):
        return self._max_num

    @max_num.setter
    def max_num(self, value):
        self._max_num = value if self.max_num else 0

    @property
    def is_vacant(self):
        if self.is_slot:
            return len(self.slots) < self.max_num
        return False

    @property
    def is_filled(self):
        return not self.is_vacant

    def increment_max_num(self):
        self.max_num += self.is_slot

    def get_weight(self):
        return self.max_num - len(self.slots)

    def set_slot(self, item):
        assert self.is_vacant
        self.slots.append(item)

    def get_slot(self):
        return self.slots

    def clear_slot(self):
        # Only clear slots of events
        # Non-events must keep any items
        if self.is_slot:
            self.slots = []

    def is_accessible(self, inventory):
        for cost in self.costs:
            if cost.issubset(inventory):
                return True
        return False

    def __lt__(self, other):
        return self.name < other.name

    def __repr__(self):
        return self.name
