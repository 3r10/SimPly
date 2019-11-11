#!/usr/bin/python3
import sys
from simply_lex import lexer
from simply_yacc import parser
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
<h2>Environment</h2>
<pre>{}</pre>
<h2>AST</h2>
<h3>Simple</h3>
<img width="50%" src="{}"/>
<h3>Deep</h3>
<img width="50%" src="{}"/>""" # filename, code, env, simple, deep

def spaces2tab(code_in):
  code_out = ""
  first_indent = 0
  for line in code_in.split("\n"):
    line += "\n"
    i = 0
    while line[i]==' ':
      i += 1
    if i>0 and first_indent==0:
      first_indent = i
    if i==0:
      code_out += line[i:]
    else:
      code_out += '\t'*(i//first_indent)+line[i:]
  while code_out[-1]=="\n":
    code_out = code_out[:-1]
  return code_out+"\n"

def create_graph():
  dot = Digraph(format='png')
  dot.graph_attr['rankdir'] = 'LR'
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
    print("Parsing :",py_filename)
    # TAB are part of the Subset Grammar
    # spaces are ignored
    py_code = spaces2tab(py_file.read())
    # YACC parser
    ast = parser.parse(py_code,tracking=True)
    # HTML w/ syntax highlighting
    gv_filename_simple = py_filename[:-3]+".s.gv"
    gv_filename_deep = py_filename[:-3]+".d.gv"
    html_body += html_file_template.format(py_filename,
                                           ast.toHtml(),
                                           str(ast.checkType()),
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
    print(ast)
    ast.execute()
    # RESET
    lexer.lineno = 1
    parser.restart()

html_file = open("output.html","wt")
html_file.write(html_page_template.format(html_body))
html_file.close()
