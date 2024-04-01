from string import Template
from typing import Dict, Tuple, List
import random

from util import C_DATA_TYPES
from Instructions import GoTo, random_simple_instruction_block

#...Condition...

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

    def set_else_block(self, else_block):
        t = Template(self.template_string)
        self.template_string = t.safe_substitute(else_body = else_block)
        return self

    def __str__(self):
        return self.template_string

#..........
