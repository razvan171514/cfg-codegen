from string import Template
from typing import Dict, Tuple, List
import random

from util import C_DATA_TYPES, ContextualTemplateObject
from Instructions import GoTo, InstructionBlock, random_simple_instruction_block

#...Condition...

class Condition(ContextualTemplateObject):
    def __init__(self):
        self.lhs = None
        self.rhs = None
        self.sign = None

    def print_contextual(self, symbol_table: Dict[str, str]) -> str:
        var_name, var_type = random.choice(list(symbol_table.items()))
        sign = random.choice(['==', '>=', '!=', '<=', '>', '<'])
        rhs = C_DATA_TYPES[var_type]()
        return f"{var_name} {sign} {rhs}"

#..........

#...IfThen...

class IfThen(ContextualTemplateObject):
    TEMPLATE_FILE = 'snippets/if-then.template'

    def __init__(self):
        with open(self.TEMPLATE_FILE, 'r') as templ_file: 
            self.template_string = templ_file.read()

        self.condition = Condition()
        self.then_block = None

    def set_condition(self, condition: Condition):
        self.condition = condition
        return self

    def set_then_block(self, then_block: InstructionBlock):
        self.then_block = then_block
        return self

    def clear():
        self.condition = None
        self.then_block = None

    def print_contextual(self, symbol_table: Dict[str, str]) -> str:
        t = Template(self.template_string)
        if_statement = t.safe_substitute(condition = self.condition.print_contextual(symbol_table),\
                                         then_body = (self.then_block.print_contextual(symbol_table) if self.then_block is not None else ''))
        return if_statement

#..........

#...IfThenElse...

class IfThenElse(ContextualTemplateObject):
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

#..........
