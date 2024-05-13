from typing import Dict, List, Tuple
import random

from util import C_DATA_TYPES, ContextualTemplateObject
from Functions import Function, random_declaration_block

#...NoOp...

class NoOp(ContextualTemplateObject):
    def __init__(self, label = ''):
        self.label = label

    def print_contextual(self, symbol_table: Dict[str, str], call_list: List[Tuple] = []) -> str:
        op = random.choice(list(symbol_table.keys()))

        if self.label != '':
            return f"{self.label}: {op};"
        return f"{op};"

#..........

#...GoTO...

class GoTo:
    def __init__(self, label):
        self.label = label

    def __str__(self):
        return f"goto {self.label};"

#..........

#...InstructionBlock...

class InstructionBlock(ContextualTemplateObject):
    def __init__(self):
        self.block_array = []

    def add_block(self, block: ContextualTemplateObject):
        self.block_array.append(block)
        return self

    def print_contextual(self, symbol_table: Dict[str, str], call_list: List[Tuple] = []) -> str:
        return "\n".join(instr.print_contextual(symbol_table, call_list) for instr in self.block_array)

def random_simple_instruction_block() -> InstructionBlock:
    ins_block = InstructionBlock()
    for _ in range(random.randint(1, 5)):
        ins_block.add_block(NoOp())
    return ins_block

#..........

#...CallInstruction...

class CallInstruction(ContextualTemplateObject):
    def __init__(self, caller : Function = None, callee : Function = None):
        self.caller = caller
        self.callee = callee
        self.arg_list = CallInstruction.generate_callee_argument_list(caller, callee) if self.caller is not None and self.callee is not None else []

    def instantiate(self, caller : Function, callee : Function):
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

    def print_contextual(self, symbol_table: Dict[str, str] = None, call_list: List[Tuple] = []) -> str:
        if self.caller is not None or self.callee is not None:
            arguments = ", ".join(self.arg_list.values())
            return f"{self.callee.function_name}({arguments});"
        
        if call_list != []:
            caller, callee = call_list[0]
            del call_list[0]
            arguments = CallInstruction.generate_callee_argument_list(caller, callee)
        else:
            return ''

        arguments = ", ".join(arguments.values())
        return f"{callee.function_name}({arguments});"

    def __str__(self):
        if self.caller is None or self.callee is None:
            return ''
        arguments = ", ".join(self.arg_list.values())
        return f"{self.callee.function_name}({arguments});"

#..........

class BinaryOp(ContextualTemplateObject):

    def __init__(self, res_type, res_name, op, op1, op2):
        self.result_var = res_name
        self.result_type = res_type

        self.operand1_name = op1
        self.operand2_name = op2

        self.operation = op

    def __str__(self):
        return f"{self.result_var} = {self.operand1_name} {self.operation} {self.operand2_name};"

    def print_contextual(self, context: Dict[str, str], call_list: List[Tuple] = []) -> str:
        return f"{self.result_var} = {self.operand1_name} {self.operation} {self.operand2_name};"

def random_binary_op_list(symbol_table: Dict[str, str], var: Tuple[str, str] = None, length = 5) -> InstructionBlock:
    (var_name, var_type) = random.choice(list(symbol_table.items())) if var is None else var
    inst_blk = InstructionBlock()

    possible_operands = [key for key, ty in symbol_table.items() if ty == var_type and key != var_name]

    for _ in range(length):
        rand_op = random.choice(['+', '-', '*', '/'])
        rand_op1 = random.choice(possible_operands) if len(possible_operands) != 0 else C_DATA_TYPES[var_type]()
        rand_op2 = random.choice(possible_operands) if len(possible_operands) != 0 else C_DATA_TYPES[var_type]()
    
        inst_blk.add_block(BinaryOp(var_type, var_name, rand_op, rand_op1, rand_op2))

    return inst_blk

def randim_binary_op_for_all_symbols(symbol_table: Dict[str, str]) -> List[InstructionBlock]:
    res = []

    for var in symbol_table.items():
        res.append(random_binary_op_list(symbol_table, var))

    return res
