#!/usr/bin/python3
import sys
from simply_lex import SimplyLex
from simply_yacc import *

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
<h2>ASCII</h2>
<pre>{}</pre>
<h2>Graphviz</h2>
<h3>Simple</h3>
<img src="{}"/>
<h3>Deep</h3>
<img src="{}"/>""" # filename, code, env, simple, deep


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
    ast_root = parser.parse(py_code,lexer=lexer)
    # Compile...
    arm_filename = py_filename[:-3]+".S"
    arm_file = open(arm_filename,"wt")
    arm_file.write(ast_root.process())
    arm_file.close()


    # HTML w/ syntax highlighting
    gv_filename_simple = py_filename[:-3]+".s.gv"
    gv_filename_deep = py_filename[:-3]+".d.gv"
    html_body += html_file_template.format(py_filename,
                                           lexer.toHtml(),
                                           "<pre>"+str(ast_root)+"</pre>",
                                           gv_filename_simple+".png",
                                           gv_filename_deep+".png")
    ast_root.toGraph(gv_filename_simple,is_deep=False)
    ast_root.toGraph(gv_filename_deep,is_deep=True)
    print()
    parser.restart()

html_file = open("output.html","wt")
html_file.write(html_page_template.format(html_body))
html_file.close()
