# cfg-codegen
C source code generation framework for large CFGs

```bash
python3 codegen.py -h
Usage: codegen.py [options]

Options:
  -h, --help            show this help message and exit
  -f NO_FUNCTIONS, --functions=NO_FUNCTIONS
                        Number of functions on the longest callgraph path
  -e CALLGRAPH_EDGES, --callgraph-edges=CALLGRAPH_EDGES
                        Number of nodes in the CFG of a function
  --wd=FUNC_IF_DEPTH    Maximum depth of the if statemnts of the cfg of a
                        function
  --ld=FUNC_LEN_DEPTH   Maximum length of the if statemnts of the cfg of a
                        function
  --embed-loop          Use loops in the function CFG.
  --shuffle-calls       If set the calls are going to be placed in the middle
                        of the CFG insted of the last basick block of the
                        funciton.
  -o OUTPUT_FILE, --output=OUTPUT_FILE
                        Output file name
  -c, --compile-output  Use clang to compile output source code
  --opt-callgraph       Generate callgraph of compiled sample source code.
                        Option is ignored if -c is not provided
  --opt-cfg             Generate cfg for each function compiled sample source
                        code. Option is ignored if -c is not provided
```

## Example usage
```bash
$ python3 codegen.py -f 10 -e 20 --ld 2 --wd 3 --embed-loop --shuffle-calls -o tests/sample.c -c --opt-callgraph --opt-cfg```