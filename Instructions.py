from typing import Dict, List, Tuple
import random

from util import C_DATA_TYPES
from Functions import Function, random_declaration_block

#...NoOp...

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

#..........

#...GoTO...

class GoTo:
    def __init__(self, label):
        self.label = label

    def __str__(self):
        return f"goto {self.label};"

#..........

#...InstructionBlock...

class InstructionBlock:
    def __init__(self):
        self.block_array = []

    def add_block(self, block):
        self.block_array.append(block)
        return self

    def __str__(self):
        return "\n".join(str(instr) for instr in self.block_array)

def random_simple_instruction_block(symbol_table: Dict[str, str]) -> InstructionBlock:
    ins_block = InstructionBlock()
    for _ in range(random.randint(0, 5)):
        ins_block.add_block(random_noop(symbol_table))
    return ins_block

#..........

#...CallInstruction...

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

#..........
