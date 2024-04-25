from string import Template
from typing import Dict, Tuple, List
import random
from wonderwords import RandomWord
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from util import C_DATA_TYPES, ContextualTemplateObject

#...DeclarationBlock...

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
    for i in range(length):
        c_data_type = random.choice(list(C_DATA_TYPES.keys()))
        variable_name = "var_" + str(i + 1)
        initial_value = C_DATA_TYPES[c_data_type]()
        data_tuples.append((c_data_type, variable_name, initial_value))
    return DeclarationBlock(data_tuples)

#..........

#...Function...

class Function:
    TEMPLATE_FILE = 'snippets/function.template'

    def __init__(self):
        with open(self.TEMPLATE_FILE, 'r') as templ_file: 
            self.template_string = templ_file.read()
        self.symbol_table = {}

        self.module_call_list = []

    def function_header(self):
        return self.template_string.split('\n')[0] + ';'

    def set_module_call_list(self, calls):
        self.module_call_list = calls
        return self

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

    # MUST happen after the module sets the call list otherwise the template will NOT get constructed correctly
    def set_body(self, body: ContextualTemplateObject, end_block = False):
        t = Template(self.template_string)
        body_str = '{block}\n{terminator}'.format(\
            block = body.print_contextual(self.symbol_table, call_list=self.module_call_list),\
            terminator = '${func_body}' if not end_block else '')
        self.template_string = t.safe_substitute(func_body = body_str)
        return self

    def __str__(self):
        return self.template_string

#..........

def random_funcion(header_arg_list_length) -> Function:
    word_validity_regex = '^(?!auto$|break$|case$|char$|const$|continue$|default$|do$|double$|else$|enum$|extern$|float$|for$|goto$|if$|int$|long$|register$|return$|short$|signed$|sizeof$|static$|struct$|switch$|typedef$|union$|unsigned$|void$|volatile$|while$)(?!.*-)[a-zA-Z]+$'
    word_generator = RandomWord()
    rand_arg_list = {}

    for _ in range(header_arg_list_length):
        random_var_name = word_generator.word(regex=word_validity_regex)
        random_var_type = random.choice(list(C_DATA_TYPES.keys()))
        rand_arg_list[random_var_name] = random_var_type


    func = Function()\
        .set_return_type(random.choice(list(C_DATA_TYPES.keys())))\
        .set_func_name(word_generator.word(regex=word_validity_regex))\
        .set_header_arg_list(rand_arg_list)\
        .set_declaration_block(random_declaration_block())

    return_val_candidates = [key for key, val in func.symbol_table.items() if val == func.return_type]
    if return_val_candidates:
        return_val = random.choice(return_val_candidates)
    else:
        return_val = C_DATA_TYPES[func.return_type]()

    return func.set_return_value(return_val)

from Conditionals import IfThenElse
from Loops import For, While
from Instructions import InstructionBlock, random_simple_instruction_block, CallInstruction

def generate_cfg_block(depth = 1) -> InstructionBlock:
    inst_blk = InstructionBlock()
    inst_blk.add_block(random_simple_instruction_block())

    if depth == 0:
        return inst_blk

    ifte = IfThenElse()\
        .set_then_block(generate_cfg_block(depth-1))\
        .set_else_block(generate_cfg_block(depth-1))
    inst_blk.add_block(ifte)
    
    inst_blk.add_block(random_simple_instruction_block())
    inst_blk.add_block(CallInstruction())
    return inst_blk

def generate_complete_cfg_block(wd = 1, ld = 1, embed_loop = False) -> InstructionBlock:
    inst_blk = InstructionBlock()

    if_template = generate_cfg_block(depth=wd)
    for_template = For().set_body(if_template)
    while_template = While().set_body(if_template)

    for _ in range(ld):
        inst_blk.add_block(if_template)

    if embed_loop:
        inst_blk.add_block(for_template)

    return inst_blk
