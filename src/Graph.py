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
from Utility import time_func

def is_pc(x):
    return x in ['item_hikari', 'item_ochette', 'item_castti', 'item_partitio',
                 'item_temenos', 'item_osvald', 'item_throne', 'item_agnea']

class Graph:
    def __init__(self):
        self.edges = {}
        self.nodes = set()
        self.node_dict = {}
        self.slots = set()
        self.visited = set()
        self.ring_dict = {}

    def reset(self):
        self.visited = set()
        for node in self.nodes:
            node.reset()

    def traverse(self, start, inventory=None, rank_on=True):
        self.visited.add(start)
        completed = set()
        inventory = set() if inventory is None else set(inventory)
        rings = [] # for printing logic
        num_pcs = [0]
        num_chapters_finished = [0]

        if rank_on:
            inventory.add('rank_1')
            inventory.add('rank_2')
            inventory.add('rank_3')

        def dfs(iteration):
            # Start from visited nodes with unvisited neighbors
            queue = sorted(self.visited - completed)
            new_items = set()
            ring = []
            while queue:
                node = queue.pop()
                node.set_iteration(iteration)
                all_neighbors_visited = True
                for neighbor in node.neighbors:
                    edge = self.get_edge(node, neighbor)
                    if edge.is_passable(inventory):
                        if neighbor not in self.visited:
                            self.visited.add(neighbor)
                            queue.append(neighbor)
                            new_items.update(neighbor.slots)
                            new_items.add(neighbor.name)
                            ring.append(neighbor)
                            num_chapters_finished[0] += neighbor.name.startswith('finish_chapter')
                    else:
                        all_neighbors_visited = False

                if all_neighbors_visited:
                    completed.add(node)

            inventory.update(new_items)
            rings.append(ring)
            self._add_rank_1(inventory, num_pcs[0], num_chapters_finished)
            self._add_rank_2(inventory, num_pcs[0], num_chapters_finished)
            self._add_rank_3(inventory, num_pcs[0], num_chapters_finished)

        iteration = 1
        while True:
            # might only need to check for changes to visited size
            num_visited = len(self.visited)
            dfs(iteration)
            if num_visited == len(self.visited):
                break
            iteration += 1

        self.ring_dict = {}
        for i, ring in enumerate(rings):
            for node in ring:
                assert node not in self.ring_dict
                self.ring_dict[node] = i+1

        return rings


    def get_rings(self, always_have):
        visited = {n:False for n in self.nodes}
        everything = set(always_have)
        # Rank is ignored here
        everything.add('rank_1')
        everything.add('rank_2')
        everything.add('rank_3')
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
                        if node.is_slot or node.name.startswith('finish_chapter_') or node.name.startswith('get_') or node.name.startswith('access_'):
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

    #@time_func
    def shuffle(self, start, inventory, always_have=None):
        if always_have is None:
            always_have = []
        for node in self.nodes:
            node.clear_slot()

        # Give priority to slots other than finish_chapter_1
        assert self.node_dict['finish_chapter_1'].is_slot
        self.node_dict['finish_chapter_1'].is_slot = False

        self._shuffle(start, inventory, always_have)

        # Ensure finish_chapter_1 slot is on as it is used elsewhere
        # (e.g. number of starting PCs)
        self.node_dict['finish_chapter_1'].is_slot = True

        # Ensure all key items slots have 1 item
        # If any are empty, the shuffle must be redone
        # (shouldn't ever repeat, but done as a precaution)
        for node in self.nodes:
            if node.one_only:
                if not node.is_filled:
                    print(node.name, 'not filled')
                    return False
        return True

    def _shuffle(self, start, inventory, always_have=None):
        if always_have is None:
            always_have = []
        inventory = sorted(set(inventory).difference(always_have))

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
                # Turn on finish_chapter_1 (won't always be on for key item shuffles only)
                # Possible there are more items than slots
                if not self.node_dict['finish_chapter_1'].is_slot:
                    self.node_dict['finish_chapter_1'].is_slot = True

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

            self._add_rank_1(inv_set, len(pcs), num_chapters_finished)
            self._add_rank_2(inv_set, len(pcs), num_chapters_finished)
            self._add_rank_3(inv_set, len(pcs), num_chapters_finished)

            # If no new items were added, then it is impossible to access any unvisited nodes
            if len(inv_set) == inv_size:
                break

        return vacant_events

    @staticmethod
    def _add_rank_1(inventory, num_pcs, num_chap_fin):
        if num_pcs > 3:
            inventory.add('rank_1')
        
    @staticmethod
    def _add_rank_2(inventory, num_pcs, num_chap_fin):
        if num_pcs > 5 and num_chap_fin > 8:
            inventory.add('rank_2')
        
    @staticmethod
    def _add_rank_3(inventory, num_pcs, num_chap_fin):
        if num_pcs == 8 and num_chap_fin > 16:
            inventory.add('rank_3')


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
        if node in self.nodes:
            assert self.node_dict[node.name] == node
        else:
            self.nodes.add(node)
            self.node_dict[node.name] = node

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
                v = self.ring_dict[node]
                label = f'{label}\n{v}'

            ni.set_label(label)
            ni.set_style('filled')

            if node in self.ring_dict:
                if node.name == 'START':
                    ni.set_fillcolor('lightgreen')
                elif node.name == 'Virdania':
                    ni.set_fillcolor('lightgreen')
                elif 'finished_flame' in node.name:
                    ni.set_fillcolor('lightpurple')
                elif node.slots or node.is_slot:
                    ni.set_fillcolor('red')
                elif node in self.ring_dict:
                    ni.set_fillcolor('lightblue')
            else:
                print('NOT VISITED', node.name)

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
        self._one_only = self.name.startswith('get_') or self.name.startswith('finish_altar_')
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
    def one_only(self):
        return self._one_only

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
        if self._one_only:
            self._max_num = 1 if self.max_num else 0
        else:
            self._max_num = value if self.is_slot else 0

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
            self.max_num = 1

    def is_accessible(self, inventory):
        for cost in self.costs:
            if cost.issubset(inventory):
                return True
        return False

    def __lt__(self, other):
        return self.name < other.name

    def __repr__(self):
        return self.name
