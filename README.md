# cfg-codegen
C source code generation framework for large CFGs

```bash
$ python3 codegen.py -h

Usage: codegen.py [options]

Options:
  -h, --help            show this help message and exit
  -f NO_FUNCTIONS, --functions=NO_FUNCTIONS
                        Number of functions on the longest callgraph path
  -e CALLGRAPH_EDGES, --callgraph-edges=CALLGRAPH_EDGES
                        Number of nodes in the CFG of a function
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
$ python3 codegen.py -f 30 -e 200 -o ./tests/sample.c -c --opt-callgraph --opt-cfg
```