from string import Template
from typing import Dict, Tuple, List
import random

from Functions import Function
from Instructions import CallInstruction

from Functions import random_funcion
from Instructions import random_noop

#...Module...

class Module:
    TEMPLATE_FILE = 'snippets/module.template'

    def __init__(self, start : Function, target : Function):
        with open(self.TEMPLATE_FILE, 'r') as templ_file: 
            self.template_string = templ_file.read()
        self.funcitons = []
        self.start = start
        self.target = target
    
    def add_function(self, func : Function):
        self.funcitons.append(func)
        return self

    def __str__(self):
        t = Template(self.template_string)
        headers = '\n'.join(map(lambda f: f.function_header(), [self.start, self.target] + self.funcitons))
        bodies = '\n'.join(map(lambda f: str(f), [self.start, self.target] + self.funcitons))
        return t.safe_substitute(headers=headers, implementations=bodies)

#..........

def generate_random_connected_dag(list_of_nodes, m):
    def is_connected(adjacency_list):
        visited = set()

        def dfs(node):
            visited.add(node)
            for neighbor in adjacency_list[node]:
                if neighbor not in visited:
                    dfs(neighbor)

        dfs(random.choice(list(adjacency_list.keys())))
        return len(visited) == len(adjacency_list)

    n = len(list_of_nodes)
    if m < n - 1 or m > (n * (n-1)) / 2:
        print("Error: Number of edges must be at least n - 1 to ensure connectivity and no more than (n*(n-1))/2.", n, m)
        return None

    adjacency_list = {node: [] for node in list_of_nodes}
    for i in range(0, len(list_of_nodes) - 1):
        adjacency_list[list_of_nodes[i]].append(list_of_nodes[i+1])

    edges = n - 1
    while edges < m:
        src_index = random.randint(0, n-1)
        source = list_of_nodes[src_index]
        if src_index + 1 < n-1:
            destination = list_of_nodes[random.randint(src_index+1, n-1)]
            if destination not in adjacency_list[source]:
                adjacency_list[source].append(destination)
                edges += 1

                if not is_connected(adjacency_list):
                    # If disconnected, remove the edge
                    adjacency_list[source].remove(destination)
                    edges -= 1

    start_nodes = [node for node in list_of_nodes if not any(node in neighbors for neighbors in adjacency_list.values())]
    end_nodes = [node for node in list_of_nodes if not adjacency_list[node]]

    if len(start_nodes) != 1 or len(end_nodes) != 1:
        print("Error: Could not generate a graph with a single start and end node.")
        return None

    call_list = []
    for func, func_call_list in adjacency_list.items():
        for callee in func_call_list:
            call_list.append((func, callee))

    return call_list

def random_module(start_func, target_func, no_functions = 5, callgraph_edges=10) -> Module :
    module = Module(start_func, target_func)

    for _ in range(no_functions-2):
        func = random_funcion(random.randint(0, 5))
        module.add_function(func)

    calls = generate_random_connected_dag([module.start] + module.funcitons + [module.target], callgraph_edges)
    calls = list(map(lambda pair: CallInstruction(pair[0], pair[1]), calls))

    for call in calls:
        call.caller.set_body(call, end_block=False)

    for func in module.funcitons:
        func.set_body(random_noop(func.symbol_table), end_block=True)
    
    module.start.set_body(random_noop(func.symbol_table), end_block=True)
    module.target.set_body(random_noop(func.symbol_table), end_block=True)

    return module