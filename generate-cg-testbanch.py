import os
import time
import subprocess as sp
from optparse import OptionParser

GREEN = "\033[32m"
RESET = "\033[0m"

generate_c_code_cmd = ['python3', 'codegen.py', '-f', '', '-e', '', '--ld',  '1', '--wd', '1', '-o', '', '-c']
NO_FUNC_CMD_INDEX = 3
NO_CALLS_CMD_INDEX = 5
TEST_NAME_INDEX = 11
WD_INDEX = 9
LD_INDEX = 7

parser = OptionParser()
parser.add_option('--min-f', dest='min_functions', default=1, help='Number of functions on the longest callgraph path')
parser.add_option('--max-f', dest='max_functions', default=50, help='Number of functions on the longest callgraph path')

parser.add_option('--edge-set', dest='edges', default=-1, help='Number of calls in module')
parser.add_option('-s', '--step', dest='step', default=1, help='Step from edge calculation. Default 1.')

parser.add_option('-t', '--tries', dest='tries', default=1, help='Generate for the same combination multiple samples. Default 1.')

parser.add_option('--min-wd', dest='func_if_depth_min', default=-1, help='Depth of the if statemnts of the cfg of a function')
parser.add_option('--wd', dest='func_if_depth', default=1, help='Depth of the if statemnts of the cfg of a function')
parser.add_option('--min-ld', dest='func_len_depth_min', default=-1, help='Length of the if statemnts of the cfg of a function')
parser.add_option('--ld', dest='func_len_depth', default=1, help='Length of the if statemnts of the cfg of a function')

parser.add_option('--target-dir', dest='target_dir', default='tests', help='Path to directory where samples are placed. Creates directory if does not exist.')
parser.add_option('-r', '--rm', dest='remove_c', action="store_true", default=False, help='Remove generated c file and leave only the .bc')
(options, args) = parser.parse_args()

generate_c_code_cmd[7] = options.func_len_depth
generate_c_code_cmd[9] = options.func_if_depth

os.makedirs(options.target_dir, exist_ok=True)

for no_functions in range(int(options.min_functions), int(options.max_functions)+1):
    generate_c_code_cmd[NO_FUNC_CMD_INDEX] = str(no_functions)
    for no_calls in range(no_functions+1, ((no_functions+2) * (no_functions+1) // 2), int(options.step)) if int(options.edges) == -1 else range(int(options.edges), int(options.edges)+1):
        generate_c_code_cmd[NO_CALLS_CMD_INDEX] = str(no_calls)

        for wd in range(int(options.func_if_depth) if int(options.func_if_depth_min) == -1 else int(options.func_if_depth_min), int(options.func_if_depth)+1):
            generate_c_code_cmd[WD_INDEX] = str(wd)

            for ld in range(int(options.func_len_depth) if int(options.func_len_depth_min) == -1 else int(options.func_len_depth_min), int(options.func_len_depth)+1):
                generate_c_code_cmd[LD_INDEX] = str(ld)

                for try_no in range(int(options.tries)):
                    generate_c_code_cmd[TEST_NAME_INDEX] = f"{options.target_dir}/sample-v{no_functions}-e{no_calls}-ld{ld}-wd{wd}-try{try_no}.c"
                    return_code = 1
                    while return_code != 0:
                        return_code = sp.call(generate_c_code_cmd, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
                    print(f"Generating: \'{generate_c_code_cmd[TEST_NAME_INDEX]}\'\t-- {GREEN}DONE{RESET}")
                    if options.remove_c:
                        os.unlink(generate_c_code_cmd[TEST_NAME_INDEX])
