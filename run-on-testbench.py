import re
import os
import time
import subprocess as sp
from optparse import OptionParser

# opt -S tests/sample.bc -passes=cg-first-test-pass >/dev/null
run_llvm_optimizer_pass = ['opt', '-S', '', '-passes=']
PASS_INDEX = 3
BC_PATH_INDEX = 2

parser = OptionParser()
parser.add_option('--target-dir', dest='target_dir', default='tests', help='Path to directory where samples are placed.')
parser.add_option('-o', '--output-file', dest='output_file', default='results/output.csv', help='Path to the output file.')
parser.add_option('--pass', dest='pass_name', default='cg-first-test-pass', help='opt pass to be run and timed.')
(options, args) = parser.parse_args()

run_llvm_optimizer_pass[PASS_INDEX] = f"-passes={options.pass_name}"

def extract_variables(file_name):
    pattern = r'sample-v(\d+)-e(\d+)-ld(\d+)-wd(\d+)-bb(\d+)-try(\d+)\.c'
    match = re.match(pattern, file_name)
    
    if not match:
        return None, None, None, None, None, None
    
    vertices = int(match.group(1))
    edges = int(match.group(2))
    length_depth = int(match.group(3))
    width_depth = int(match.group(4))
    no_bb = int(match.group(5))
    tries = int(match.group(6))
    return vertices, edges, length_depth, width_depth, no_bb, tries

if not os.path.exists(options.target_dir):
    print(f"The specified directory '{options.target_dir}' does not exist.")
    exit(-1)

output_file = open(options.output_file, 'w')
output_file.write('test_file,vertices,edges,length_depth,width_depth,no_basic_blocks,tries,time\n')

periodic_flush = 0

bc_files = os.listdir(options.target_dir)    
for bc_file in bc_files:
    vertices, edges, length_depth, width_depth, basic_blocks, try_no = extract_variables(bc_file)

    bc_file_path = os.path.join(options.target_dir, bc_file)
    run_llvm_optimizer_pass[BC_PATH_INDEX] = bc_file_path

    print(f"Running opt:\t{bc_file}")
    start_tm = time.time_ns()
    return_code = sp.call(run_llvm_optimizer_pass, stdout=sp.DEVNULL)
    if return_code != 0:
        print('ERROR running opt')
        exit(-1)
    end_tm = time.time_ns()
    exec_time = end_tm - start_tm
    
    output_file.write(f"{bc_file},{vertices},{edges},{length_depth},{width_depth},{basic_blocks},{try_no},{exec_time}\n")

    periodic_flush += 1
    if periodic_flush == 5:
        output_file.flush()
        periodic_flush = 0

output_file.close()
