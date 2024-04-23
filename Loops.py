from string import Template
import random
from wonderwords import RandomWord

from util import C_DATA_TYPES

#...For loop...
class For:
    TEMPLATE_FILE = 'snippets/for.template'

    def __init__(self):
        with open(self.TEMPLATE_FILE, 'r') as templ_file: 
            self.template_string = templ_file.read()
        
        self.counter_variable_name = RandomWord().word()
        self.counter_initial_val = C_DATA_TYPES['int']()
        self.counter_target_val = C_DATA_TYPES['int']()
        while self.counter_initial_val == self.counter_target_val:
            self.counter_target_val = C_DATA_TYPES['int']()
        self.couter_step_increment = '++' if self.counter_initial_val < self.counter_target_val else '--'
        self.couter_step_condition_sign = '<=' if self.counter_initial_val < self.counter_target_val else '>='

    def get_loop_symbol_table(self):
        return {self.counter_variable_name: 'int'}

    def set_body(self, body):
        t = Template(self.template_string)
        self.template_string = t.safe_substitute(loop_body = str(body))
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

    def __str__(self):
        return Template(self.template_string)\
            .safe_substitute(\
                loop_init = self.get_loop_initializer_instruction(),\
                loop_condition = self.get_loop_condition_instruction(),\
                loop_post_instr = self.get_loop_increment_instruction())

#...While loop...
class While:
    TEMPLATE_FILE = 'snippets/while.template'

    def __init__(self):
        with open(self.TEMPLATE_FILE, 'r') as templ_file: 
            self.template_string = templ_file.read()
        
    def set_body(self, body):
        t = Template(self.template_string)
        self.template_string = t.safe_substitute(while_body = str(body))
        return self

    #TODO

    def __str__(self):
        return self.template_string