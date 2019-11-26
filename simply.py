#!/usr/bin/python3
import sys
from simply_lex import SimplyLex
from simply_yacc import *
from graphviz import Digraph

html_page_template = """<!DOCTYPE html>
<html lang="en" dir="ltr">
  <head>
    <meta charset="utf-8">
    <style media="screen">
    .lineno {{
      color : grey;
      font-style: italic;
    }}
    .keyword {{
      color : blue;
    }}
    .operator {{
      color : darkslategray;
    }}
    .constant {{
      color : midnightblue;
    }}
    .comment {{
      color : darkgreen;
      font-style: italic;
    }}
    </style>
    <title>SimPly output</title>
  </head>
  <body>
  {}
  </body>
</html>"""

html_file_template = """<h1>{}</h1>
<h2>Code</h2>
<pre>{}</pre>
<h2>AST</h2>
<h3>Simple</h3>
<img src="{}"/>
<h3>Deep</h3>
<img src="{}"/>""" # filename, code, env, simple, deep

def create_graph():
  dot = Digraph(format='png')
  dot.graph_attr['splines'] = "polyline"
  dot.node_attr['fontname'] = "monospace"
  dot.edge_attr['fontname'] = "monospace"
  return dot

# inputs
if len(sys.argv) <2:
    sys.stderr.write("Usage : "+sys.argv[0]+" file1.py [file2.py ...] \n")
    exit(1)

html_body = ""
for py_filename in sys.argv[1:]:
  with open(py_filename,'r') as py_file:
    py_code = py_file.read()
    # YACC parser
    print("Parsing :",py_filename)
    lexer = SimplyLex()
    parser = yacc.yacc(outputdir="yacc.out")
    ast = parser.parse(py_code,lexer=lexer)
    # HTML w/ syntax highlighting
    gv_filename_simple = py_filename[:-3]+".s.gv"
    gv_filename_deep = py_filename[:-3]+".d.gv"
    environment = {}
    ast.checkType(environment)
    ast.local_environment = environment
    html_body += html_file_template.format(py_filename,
                                           lexer.toHtml(),
                                           gv_filename_simple+".png",
                                           gv_filename_deep+".png")
    # AST Graph (graphviz)
    dot = create_graph()
    ast.toGraph(dot)
    dot.render(gv_filename_simple)
    dot = create_graph()
    ast.toGraph(dot,is_deep=True)
    dot.render(gv_filename_deep)
    # Console execution
    # print(lexer.code)
    # ast.execute({})
    # RESET
    print()
    parser.restart()

html_file = open("output.html","wt")
html_file.write(html_page_template.format(html_body))
html_file.close()
