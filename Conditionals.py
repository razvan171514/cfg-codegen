from string import Template
from typing import Dict, Tuple, List
import random

from util import C_DATA_TYPES
from Instructions import GoTo, InstructionBlock, random_simple_instruction_block

#...Condition...

class Condition:
    def __init__(self):
        self.lhs = None
        self.rhs = None
        self.sign = None

    def print_contextual(self, symbol_table: Dict[str, str]) -> str:
        var_name, var_type = random.choice(list(symbol_table.items()))
        sign = random.choice(['==', '>=', '!=', '<=', '>', '<'])
        rhs = C_DATA_TYPES[var_type]()
        return f"{var_name} {sign} {rhs}"

    def __str__(self):
        return f"{self.lhs} {self.sign} {self.rhs}"

def random_condition():
#     if var == None:
#         var_name, var_type = random.choice(list(symbol_table.items()))
#     else:
#         var_name, var_type = var, symbol_table[var]
#     sign = random.choice(['==', '>=', '!=', '<=', '>', '<'])
#     rhs = C_DATA_TYPES[var_type]()
    return Condition()

#..........

#...IfThen...

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

def random_ifthen(symbol_table: Dict[str, str], add_goto_statement = False, goto_label='end_of_function') -> IfThen:
    ift = IfThen(random_condition(symbol_table))
    bb = random_simple_instruction_block(symbol_table)

    if add_goto_statement:
        bb.add_block(GoTo(goto_label))

    return ift.set_then_block(bb)

#..........

#...IfThenElse...

class IfThenElse:
    TEMPLATE_FILE = 'snippets/if-then-else.template'

    def __init__(self):
        with open(self.TEMPLATE_FILE, 'r') as templ_file: 
            self.template_string = templ_file.read()

        self.condition = Condition()
        self.then_block = None
        self.else_block = None

    def set_condition(self, condition: Condition):
        self.condition = condition
        return self

    def set_then_block(self, then_block: InstructionBlock):
        self.then_block = then_block
        return self

    def set_else_block(self, else_block: InstructionBlock):
        self.else_block = else_block
        return self

    def clear():
        self.condition = None
        self.then_block = None
        self.else_block = None

    def print_contextual(self, symbol_table: Dict[str, str]) -> str:
        t = Template(self.template_string)
        if_statement = t.safe_substitute(condition = self.condition.print_contextual(symbol_table),\
                                         then_body = (self.then_block.print_contextual(symbol_table) if self.then_block is not None else ''),
                                         else_body = (self.else_block.print_contextual(symbol_table) if self.else_block is not None else ''))
        return if_statement

    def __str__(self):
        t = Template(self.template_string)
        if_statement = t.safe_substitute(condition = str(self.condition),\
                                         then_body = (str(self.then_block) if self.then_block is not None else ''),
                                         else_body = (str(self.else_block) if self.else_block is not None else ''))
        return if_statement

#..........
