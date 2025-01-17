from string import Template
from typing import Dict, Tuple, List
import random
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from Functions import Function
from Instructions import CallInstruction

from Functions import random_funcion, generate_complete_cfg_block
from Instructions import NoOp, randim_binary_op_for_all_symbols

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

    def is_func_name_valid(self, func_name):
        return func_name not in list(map(lambda f: f.function_name, self.funcitons))

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

def random_module(start_func, target_func,
                  no_functions = 5, callgraph_edges=10,\
                  max_cfg_width_depth=5, max_cfg_length_depth=5,\
                  embed_loop = False,\
                  shuffle_calls = False,\
                  chain_length=5) -> Module :
    module = Module(start_func, target_func)

    function_body_template = generate_complete_cfg_block(wd=max_cfg_width_depth, ld=max_cfg_length_depth, embed_loop=embed_loop)
    for _ in range(no_functions):
        new_function = random_funcion(random.randint(1, 6), module=module)
        module.add_function(new_function)

    calls = generate_random_connected_dag([module.start] + module.funcitons + [module.target], callgraph_edges)
    
    for func in [module.start, module.target] + module.funcitons:
        if shuffle_calls:
            func.set_module_call_list([call for call in calls if call[0] == func])
        func.set_def_chains(randim_binary_op_for_all_symbols(func.symbol_table, length=chain_length))\
            .set_body(function_body_template, end_block=shuffle_calls)
    
    if not shuffle_calls:
        calls = list(map(lambda pair: CallInstruction(pair[0], pair[1]), calls))
        for call in calls:
            call.caller.set_body(call, end_block=False)

        for func in [module.start, module.target] + module.funcitons:
            func.set_body(NoOp(), end_block=True)

    return module