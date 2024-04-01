import random

C_DATA_TYPES = {
    "int": lambda: random.randint(-100, 100),
    "float": lambda: random.uniform(-100.0, 100.0),
    # either this or hex(ord(random()) the following line
    "char": lambda: f'\'%c\'' % (random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")),
    "double": lambda: random.uniform(-1000.0, 1000.0),
    "short": lambda: random.randint(-32768, 32767),
    "long": lambda: random.randint(-2147483648, 2147483647)
}

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