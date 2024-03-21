from optparse import OptionParser
from string import Template
from typing import Dict, Tuple, List
import random
import nltk
import subprocess
import os
from functools import partial

parser = OptionParser()
parser.add_option('-f', '--functions', dest='no_functions', default=3, help='Number of functions on the longest callgraph path')
parser.add_option('-e', '--callgraph-edges', dest='callgraph_edges', default=6, help='Number of nodes in the CFG of a function')
parser.add_option('-o', '--output', dest='output_file', default='sample.c', help='Output file name')
parser.add_option('-c', '--compile-output', dest='compile', action="store_true", default=False, help='Use clang to compile output source code')
parser.add_option('--opt-callgraph', dest='gen_callgraph', action="store_true", default=False, help='Generate callgraph of compiled sample source code. Option is ignored if -c is not provided')
parser.add_option('--opt-cfg', dest='gen_cfg', action="store_true", default=False, help='Generate cfg for each function compiled sample source code. Option is ignored if -c is not provided')

######################################DeclarationBlock##########################################################################
C_DATA_TYPES = {
    "int": lambda: random.randint(-100, 100),
    "float": lambda: random.uniform(-100.0, 100.0),
    # either this or hex(ord(random()) the following line
    "char": lambda: f'\'%c\'' % (random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")),
    "double": lambda: random.uniform(-1000.0, 1000.0),
    "short": lambda: random.randint(-32768, 32767),
    "long": lambda: random.randint(-2147483648, 2147483647)
}

class DeclarationBlock:

    def __init__(self, declaration_list: List[Tuple[str, str, object]]):
        self.decaration_table = declaration_list

    def get_symbol_table(self):
        return {variable_name : c_data_type for c_data_type, variable_name, _ in self.decaration_table}

    def __str__(self):
        def declaration_statement(item):
            (t, n, v) = item
            assign_statement = ''
            if v != None:
                assign_statement = f" = {v}"
            return f"{t} {n} {assign_statement};"
        
        return "\n".join(declaration_statement(item) for item in self.decaration_table)

def random_declaration_block(length = 5) -> DeclarationBlock:
    data_tuples = []
    for i in range(5):
        c_data_type = random.choice(list(C_DATA_TYPES.keys()))
        variable_name = "var_" + str(i + 1)
        initial_value = C_DATA_TYPES[c_data_type]()
        data_tuples.append((c_data_type, variable_name, initial_value))
    return DeclarationBlock(data_tuples)


#######################################################################################################################

class Function:
    TEMPLATE_FILE = 'snippets/function.template'

    def __init__(self):
        with open(self.TEMPLATE_FILE, 'r') as templ_file: 
            self.template_string = templ_file.read()
        self.symbol_table = {}

    def function_header(self):
        return self.template_string.split('\n')[0] + ';'

    def set_return_type(self, return_type):
        t = Template(self.template_string)
        self.template_string = t.safe_substitute(func_type = return_type)
        self.return_type = return_type
        if self.return_type == 'void':
            self.return_value = '';
            self.template_string = Template(self.template_string).safe_substitute(func_ret_val = '')
        return self

    def set_func_name(self, function_name):
        t = Template(self.template_string)
        self.template_string = t.safe_substitute(func_name = function_name)
        self.function_name = function_name
        return self

    def set_return_value(self, return_value):
        if self.return_type == 'void':
            return self

        t = Template(self.template_string)
        self.template_string = t.safe_substitute(func_ret_val = return_value)
        self.return_value = return_value
        return self
    
    def set_header_arg_list(self, arg_list: Dict[str, str]):
        self.function_arguments = arg_list
        self.symbol_table.update(arg_list)

        def arg_list_to_sting():
            return ", ".join(f"{var_type} {var_name}" for var_name, var_type in arg_list.items())

        t = Template(self.template_string)
        self.template_string = t.safe_substitute(func_header_arg_list = arg_list_to_sting())
        return self

    def set_declaration_block(self, declarations: DeclarationBlock):
        self.declaration_block = declarations
        self.symbol_table.update(declarations.get_symbol_table())

        t = Template(self.template_string)
        self.template_string = t.safe_substitute(declaration_block = declarations)
        return self

    def set_body(self, body, end_block = False):
        t = Template(self.template_string)
        body_str = '{block}\n{terminator}'.format(block = body, terminator = '${func_body}' if not end_block else '')
        self.template_string = t.safe_substitute(func_body = body_str)
        return self

    def __str__(self):
        return self.template_string

#######################################################################################################################

class NoOp:
    def __init__(self, var, label = ''):
        self.op = var
        self.label = label
    
    def __str__(self):
        if self.label != '':
            return f"{self.label}: {self.op};"
        return f"{self.op};"

def random_noop(symbol_table: Dict[str, str], label = ''):
    return NoOp(random.choice(list(symbol_table.keys())), label)

class GoTo:
    def __init__(self, label):
        self.label = label

    def __str__(self):
        return f"goto {self.label};"

class CallInstruction:
    def __init__(self, caller : Function, callee : Function):
        self.caller = caller
        self.callee = callee
        self.arg_list = CallInstruction.generate_callee_argument_list(caller, callee)

    def generate_callee_argument_list(caller : Function, callee : Function):
        call_arguments = {}

        def filter_symbol_table_by_var_type(var_type):
            return [key for key, val in caller.symbol_table.items() if val == var_type and key not in call_arguments.values()]

        for var_name, var_type in callee.function_arguments.items():
            argument_candidates = filter_symbol_table_by_var_type(var_type)
            try:
                call_arguments[var_name] = random.choice(argument_candidates)
            except IndexError:
                call_arguments[var_name] = str(C_DATA_TYPES[var_type]())
        
        return call_arguments

    def __str__(self):
        arguments = ", ".join(self.arg_list.values())
        return f"{self.callee.function_name}({arguments});"

class InstructionBlock:
    def __init__(self):
        self.block_array = []

    def add_block(self, block):
        self.block_array.append(block)
        return self

    def __str__(self):
        return "\n".join(str(instr) for instr in self.block_array)

def random_simple_instruction_block(func : Function) -> InstructionBlock:
    ins_block = InstructionBlock()
    for _ in range(random.randint(0, 5)):
        ins_block.add_block(random_noop(func.symbol_table))
    return ins_block

#######################################################################################################################

class Condition:
    def __init__(self, lhs, sign, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.sign = sign

    def __str__(self):
        return f"{self.lhs} {self.sign} {self.rhs}"

def random_condition(symbol_table: Dict[str, str], var = None):
    if var == None:
        var_name, var_type = random.choice(list(symbol_table.items()))
    else:
        var_name, var_type = var, symbol_table[var]
    sign = random.choice(['==', '>=', '!=', '<=', '>', '<'])
    rhs = C_DATA_TYPES[var_type]()
    return Condition(var_name, sign, rhs)

class IfThen:
    TEMPLATE_FILE = 'snippets/if-then.template'

    def __init__(self, cond : Condition):
        with open(self.TEMPLATE_FILE, 'r') as templ_file: 
            self.template_string = templ_file.read()
        self.condition = cond

        t = Template(self.template_string)
        self.template_string = t.safe_substitute(condition = cond)

    def set_then_block(self, then_block):
        t = Template(self.template_string)
        self.template_string = t.safe_substitute(then_body = then_block)
        return self

    def __str__(self):
        return self.template_string
        
def random_ifthen(func : Function, add_goto_statement = False, goto_label='end_of_function') -> IfThen:
    ift = IfThen(random_condition(func.symbol_table))
    bb = random_simple_instruction_block(func)

    if add_goto_statement:
        bb.add_block(GoTo(goto_label))

    return ift.set_then_block(bb)

class IfThenElse:
    TEMPLATE_FILE = 'snippets/if-then-else.template'

    def __init__(self, cond : Condition):
        with open(self.TEMPLATE_FILE, 'r') as templ_file: 
            self.template_string = templ_file.read()
        self.condition = cond

        t = Template(self.template_string)
        self.template_string = t.safe_substitute(condition = cond)

    def __str__(self):
        return self.template_string

#######################################################################################################################

def compex_function_body(func : Function, calls : List[CallInstruction], max_no_controll_blocks_per_func = 10):
    block_list = calls[:]
    
    block_generator = {
        InstructionBlock: partial(random_simple_instruction_block, func),
        IfThen: partial(random_ifthen, func)
    }

    for _ in range(random.randint(0, max_no_controll_blocks_per_func)):
        block_type, gen_funciton = random.choice(list(block_generator.items()))
        block_list.append(gen_funciton() if block_type == InstructionBlock else gen_funciton(random.choice([True, False])))

    random.shuffle(block_list)
    block_list.append(random_noop(func.symbol_table, label='end_of_function'))

    function_body = InstructionBlock()
    for blk in block_list:
        function_body.add_block(blk)
    
    return function_body

def random_funcion(header_arg_list_length, no_body_blocks = 0, complete_function = False, ignore_body=False) -> Function:
    words = nltk.corpus.words.words()
    rand_arg_list = {}

    for _ in range(header_arg_list_length):
        random_var_name = random.choice(words).lower()
        random_var_type = random.choice(list(C_DATA_TYPES.keys()))
        rand_arg_list[random_var_name] = random_var_type


    func = Function()\
        .set_return_type(random.choice(list(C_DATA_TYPES.keys())))\
        .set_func_name(random.choice(words).lower())\
        .set_header_arg_list(rand_arg_list)\
        .set_declaration_block(random_declaration_block())

    return_val_candidates = [key for key, val in func.symbol_table.items() if val == func.return_type]
    if return_val_candidates:
        return_val = random.choice(return_val_candidates)
    else:
        return_val = C_DATA_TYPES[func.return_type]()

    body_block_types = {
        NoOp: lambda : random_noop(func.symbol_table),
        IfThen: lambda : IfThen(random_condition(func.symbol_table)).set_then_block(InstructionBlock().add_block(random_noop(func.symbol_table)).add_block(GoTo('end_of_function')))
    }

    if not ignore_body:
        for _ in range(no_body_blocks):
            _, block = random.choice(list(body_block_types.items()))
            func.set_body(block())
        func.set_body(random_noop(func.symbol_table, label='end_of_function'), end_block=complete_function)

    return func.set_return_value(return_val)

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

def generate_random_graph(lsit_of_functions):
    parents = [lsit_of_functions[0]]
    calls = []

    for func in lsit_of_functions[1:]:
        calls.append((func, random.choice(parents)))
        parents.append(func)

    leafs = list(set(lsit_of_functions) - set([call[0] for call in calls]))
    roots = list(set(lsit_of_functions) - set([call[1] for call in calls]))

    return (roots, calls, leafs)

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
        func = random_funcion(random.randint(0, 4), ignore_body=True)
        # condition_variable = random.choice(list(func.symbol_table.keys()))
        # for _ in range(random.randint(0, max_no_controll_blocks_per_func)):
            # ift = IfThen(random_condition(func.symbol_table, var=condition_variable))\
            #     .set_then_block(InstructionBlock().add_block(random_noop(func.symbol_table)).add_block(GoTo('lastop')))
            # func.set_body(ift)
        # func.set_body(random_noop(func.symbol_table, 'lastop'))

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

#######################################################################################################################

start_test_func = Function().set_return_type('int')\
    .set_func_name('setsockopt_test')\
    .set_header_arg_list({"a": "int", "b": "int"})\
    .set_return_value('a')\
    .set_declaration_block(random_declaration_block())

for index in range(1, 5):
    ift = IfThen(random_condition(start_test_func.symbol_table, var='var_3'))\
        .set_then_block(InstructionBlock().add_block(random_noop(start_test_func.symbol_table)).add_block(GoTo('lastop')))
    start_test_func.set_body(ift)
start_test_func.set_body(random_noop(start_test_func.symbol_table, 'lastop'))

target_test_func = Function().set_return_type('int')\
    .set_func_name('ns_capable')\
    .set_header_arg_list({"cap": "int"})\
    .set_return_value('cap')\
    .set_declaration_block(random_declaration_block())
target_test_func.set_body(random_noop(target_test_func.symbol_table), end_block=True)

test_calls = [CallInstruction(start_test_func, target_test_func),CallInstruction(start_test_func, target_test_func), CallInstruction(start_test_func, target_test_func)]
compex_function_body(start_test_func, test_calls)

def indent_c_code(c_code):
    lines = c_code.split('\n')
    indent_level = 0
    indented_code = ''
    
    for line in lines:
        line = line.strip()
        if line.startswith('}') and indent_level > 0:
            indent_level -= 1
        
        indented_line = '\t' * indent_level + line
        
        if '{' in line and not line.startswith('#'):
            indent_level += 1
        
        indented_code += indented_line + '\n'
    
    return indented_code.strip()

(options, args) = parser.parse_args()

if __name__ == '__main__':
    mod = random_module(start_test_func,\
                        target_test_func,\
                        no_functions=int(options.no_functions),\
                        callgraph_edges=int(options.callgraph_edges))

    with open(options.output_file, 'w') as output_file:
        output_file.write(indent_c_code(str(mod)))

    if options.compile:
        output_dir = os.path.dirname(options.output_file)
        input_file_name = os.path.basename(options.output_file)
        output_file_name, _ = os.path.splitext(input_file_name)

        compile_cmd = f"clang {options.output_file} -emit-llvm -c -O0 -Xclang -disable-llvm-passes -o {output_dir}/{output_file_name}.bc"
        result = subprocess.run(compile_cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(result.stderr)

        if options.gen_callgraph:
            generate_callgraph_cmd = f"opt -S {output_dir}/{output_file_name}.bc -passes=dot-callgraph >/dev/null 2>&1"
            dot_png = f"dot -Tpng {output_dir}/{output_file_name}.bc.callgraph.dot -o {output_dir}/{output_file_name}.bc.callgraph.dot.png"
            
            result = subprocess.run(generate_callgraph_cmd, shell=True, check=True, stdout=subprocess.PIPE, text=True)
            result = subprocess.run(dot_png, shell=True, check=True, stdout=subprocess.PIPE, text=True)

            os.unlink(f"{output_dir}/{output_file_name}.bc.callgraph.dot")
        
        if options.gen_cfg:
            generate_cfg_cmd = f"opt -S {output_file_name}.bc -passes=dot-cfg >/dev/null 2>&1"
            result = subprocess.run(generate_cfg_cmd, shell=True, check=True, stdout=subprocess.PIPE, text=True, cwd=output_dir)
            
            index = 1
            total_no_convertable = len([file for file in os.listdir(output_dir) if file.endswith('.dot')])
            for dot_file in os.listdir(output_dir):
                if dot_file.endswith('.dot'):
                    print(f"Converting ({index}/{total_no_convertable}): {dot_file}")
                    index += 1

                    dot_png = f"dot -Tpng {dot_file} -o {dot_file}.png"
                    result = subprocess.run(dot_png, shell=True, check=True, stdout=subprocess.PIPE, text=True, cwd=output_dir)
                    os.unlink(f"{output_dir}/{dot_file}")
