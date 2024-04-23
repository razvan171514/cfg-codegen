from optparse import OptionParser
import random
import subprocess
import os

from Module import *
from Functions import *
from Instructions import *
from Conditionals import *
from Loops import *
from util import *

parser = OptionParser()
parser.add_option('-f', '--functions', dest='no_functions', default=3, help='Number of functions on the longest callgraph path')
parser.add_option('-e', '--callgraph-edges', dest='callgraph_edges', default=6, help='Number of nodes in the CFG of a function')
parser.add_option('--wd', dest='func_if_depth', default=5, help='Maximum depth of the if statemnts of the cfg of a function')
parser.add_option('--ld', dest='func_len_depth', default=5, help='Maximum length of the if statemnts of the cfg of a function')
parser.add_option('-o', '--output', dest='output_file', default='sample.c', help='Output file name')
parser.add_option('-c', '--compile-output', dest='compile', action="store_true", default=False, help='Use clang to compile output source code')
parser.add_option('--opt-callgraph', dest='gen_callgraph', action="store_true", default=False, help='Generate callgraph of compiled sample source code. Option is ignored if -c is not provided')
parser.add_option('--opt-cfg', dest='gen_cfg', action="store_true", default=False, help='Generate cfg for each function compiled sample source code. Option is ignored if -c is not provided')

(options, args) = parser.parse_args()

if __name__ == '__main__':
    source_func = Function().set_return_type('int')\
        .set_func_name('setsockopt_test')\
        .set_header_arg_list({"a": "int", "b": "int"})\
        .set_return_value('a')\
        .set_declaration_block(random_declaration_block())
    source_func.set_body(\
        generate_complete_cfg_block(\
                                    wd=int(options.func_if_depth),\
                                    ld=int(options.func_len_depth)\
                                    )\
    )

    target_func = Function().set_return_type('int')\
        .set_func_name('ns_capable')\
        .set_header_arg_list({"cap": "int"})\
        .set_return_value('cap')\
        .set_declaration_block(random_declaration_block())
    target_func.set_body(\
        generate_complete_cfg_block(\
                                    wd=int(options.func_if_depth),\
                                    ld=int(options.func_len_depth)\
                                    )\
    )

    mod = random_module(source_func, target_func,\
                        no_functions=int(options.no_functions),\
                        callgraph_edges=int(options.callgraph_edges),\
                        max_cfg_width_depth=int(options.func_if_depth),\
                        max_cfg_length_depth=int(options.func_len_depth))

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
