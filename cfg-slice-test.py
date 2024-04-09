import os
import time
import subprocess as sp
from typing import List

generate_c_code_cmd = ['python3', 'codegen.py', '-f', '20', '-e', '50', '--ld', '1', '--wd', '1', '-o', 'tests/sample.c', '-c']
NO_FUNC_CMD_INDEX = 3
NO_CALLS_CMD_INDEX = 5
FUNC_CFG_WD_INDEX = 9
FUNC_CFG_LD_INDEX = 7

# opt -S tests/sample.bc -passes=path-search-cfg >/dev/null
run_llvm_optimizer_pass = ['opt', '-S', 'tests/sample.bc', '-passes=path-search-cfg']

def print_cmd(cmd: List[str]):
    acc = ""
    for el in cmd:
        acc += (el + " ")
    return acc

results_file = open('results/cfg-slice-test.csv', 'w')

# for no_functions in range(15, 40):
#     generate_c_code_cmd[NO_FUNC_CMD_INDEX] = str(no_functions)
#     for no_calls in range(no_functions-1, (no_functions * (no_functions - 1)) // 2):
#         generate_c_code_cmd[NO_CALLS_CMD_INDEX] = str(no_calls)
        
for ld in range(1, 20):
    generate_c_code_cmd[FUNC_CFG_LD_INDEX] = str(ld)
    for wd in range(1, 40):
        generate_c_code_cmd[FUNC_CFG_WD_INDEX] = str(wd)

        avg = 0
        for try_no in range(1, 6):
            print(f"[try {try_no}/5] Generating CFG with ld={ld} and wd={wd}")
            cmd_string = print_cmd(generate_c_code_cmd)
            print(f"[try {try_no}/5] running: \"{cmd_string}\"")
            # calling code generation may result in multiple variables having the same name as function or some other same sort of syntax problem
            # run until generates a good compile result
            return_code = 1
            while return_code != 0:
                return_code = sp.call(generate_c_code_cmd, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            print(f"[try {try_no}/5] DONE generating CFG with ld={ld} and wd={wd}")
            print(f"[try {try_no}/5] Running optimizer pass")
            start_tm = time.time_ns()
            return_code = sp.call(run_llvm_optimizer_pass, stdout=sp.DEVNULL)
            if return_code != 0:
                exit(-1)
            end_tm = time.time_ns()
            print(f"[try {try_no}/5] DONE running optimizer pass")
            opt_run_time = end_tm-start_tm
            avg += opt_run_time
            print(f"[try {try_no}/5] {opt_run_time}")
        avg /= 5

        print(f"Batch avg time: {avg}")
        print()
        print()

        results_file.write(f"{ld},{wd},{avg}\n")
        results_file.flush()
    break


results_file.close()