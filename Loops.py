from string import Template
import random
from wonderwords import RandomWord
from typing import Dict

from util import C_DATA_TYPES, ContextualTemplateObject

class GenericLoop(ContextualTemplateObject):
    VALID_REGEX = '^(?!auto$|break$|case$|char$|const$|continue$|default$|do$|double$|else$|enum$|extern$|float$|for$|goto$|if$|int$|long$|register$|return$|short$|signed$|sizeof$|static$|struct$|switch$|typedef$|union$|unsigned$|void$|volatile$|while$)(?!.*-)[a-zA-Z]+$'

    def __init__(self, template_file_name):
        with open(template_file_name, 'r') as templ_file: 
            self.template_string = templ_file.read()
        
        self.counter_variable_name = RandomWord().word(regex=self.VALID_REGEX)
        self.counter_initial_val = C_DATA_TYPES['int']()
        self.counter_target_val = C_DATA_TYPES['int']()
        while self.counter_initial_val == self.counter_target_val:
            self.counter_target_val = C_DATA_TYPES['int']()
        self.couter_step_increment = '++' if self.counter_initial_val < self.counter_target_val else '--'
        self.couter_step_condition_sign = '<=' if self.counter_initial_val < self.counter_target_val else '>='
        self.loop_body = None

    def get_loop_symbol_table(self):
        return {self.counter_variable_name: 'int'}

    def set_body(self, body: ContextualTemplateObject):
        self.loop_body = body
        return self

    def change_loop_counter_name(self, name):
        self.counter_variable_name = name
        return self

    def get_loop_initializer_instruction(self):
        return 'int ' + self.counter_variable_name + '=' + str(self.counter_initial_val)

    def get_loop_condition_instruction(self):
        return self.counter_variable_name + self.couter_step_condition_sign + str(self.counter_target_val)

    def get_loop_increment_instruction(self):
        return self.counter_variable_name + self.couter_step_increment;

    def print_contextual(self, symbol_table: Dict[str, str] = None) -> str:
        return Template(self.template_string)\
            .safe_substitute(\
                loop_init = self.get_loop_initializer_instruction(),\
                loop_condition = self.get_loop_condition_instruction(),\
                loop_post_instr = self.get_loop_increment_instruction(),\
                loop_body = self.loop_body.print_contextual(symbol_table))


#...For loop...
class For(GenericLoop):
    TEMPLATE_FILE = 'snippets/for.template'

    def __init__(self):
        super().__init__(self.TEMPLATE_FILE)

#................

#...While loop...

class While(GenericLoop):
    TEMPLATE_FILE = 'snippets/while.template'

    def __init__(self):
        super().__init__(self.TEMPLATE_FILE)
    
#................