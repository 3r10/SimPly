#!/usr/bin/python3
import sys
from simply_lex import SimplyLex
from simply_yacc import *

# inputs
if len(sys.argv) <3:
    sys.stderr.write("Usage : "+sys.argv[0]+" file.py file.S\n")
    exit(1)

py_filename = sys.argv[1]
with open(py_filename,'r') as py_file:
  py_code = py_file.read()

print("Parsing :",py_filename)
lexer = SimplyLex()
parser = yacc.yacc(outputdir="yacc.out")
ast_root = parser.parse(py_code,lexer=lexer)
print("  ... compiling")
ast_root.py_filename = py_filename
ast_root.py_code = py_code
arm_code = ast_root.process()
print("  ... writing")
arm_file = open(sys.argv[2],"wt")
arm_file.write(arm_code)
arm_file.close()
