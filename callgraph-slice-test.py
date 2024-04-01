import os
import time
import subprocess as sp

generate_c_code_cmd = ['python3', 'codegen.py', '-f', '20', '-e', '50', '-o', 'tests/sample.c', '-c']
NO_FUNC_CMD_INDEX = 3
NO_CALLS_CMD_INDEX = 5

# opt -S tests/sample.bc -passes=cg-first-test-pass >/dev/null
run_llvm_optimizer_pass = ['opt', '-S', 'tests/sample.bc', '-passes=cg-first-test-pass']

results_file = open('results/callgraph-slice-test.csv', 'w')

for no_functions in range(15, 40):
    generate_c_code_cmd[NO_FUNC_CMD_INDEX] = str(no_functions)
    for no_calls in range(no_functions-1, (no_functions * (no_functions - 1)) // 2):
        generate_c_code_cmd[NO_CALLS_CMD_INDEX] = str(no_calls)
        
        avg = 0
        for try_no in range(1, 6):
            print(f"[try {try_no}/5] Generating callgraph for {no_functions} functions and {no_calls} edges")
            # calling code generation may result in multiple variables having the same name as function or some other same sort of syntax problem
            # run until generates a good compile result
            return_code = 1
            while return_code != 0:
                return_code = sp.call(generate_c_code_cmd, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            print(f"[try {try_no}/5] DONE generating callgraph for {no_functions} functions and {no_calls} edges")
            print(f"[try {try_no}/5] Running optimizer for callgraph with {no_functions} functions and {no_calls} edges")
            start_tm = time.time()
            return_code = sp.call(run_llvm_optimizer_pass, stdout=sp.DEVNULL)
            if return_code != 0:
                exit(-1)
            end_tm = time.time()
            print(f"[try {try_no}/5] DONE running optimizer for callgraph with {no_functions} functions and {no_calls} edges")
            opt_run_time = end_tm-start_tm
            avg += opt_run_time
            print(f"[try {try_no}/5] {opt_run_time}")
        print()
        print()

        avg /= 5
        results_file.write(f"{no_functions},{no_calls},{avg}\n")
        results_file.flush()

        
results_file.close()