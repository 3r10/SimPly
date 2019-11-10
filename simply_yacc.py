#!/usr/bin/python3
# Yacc example

import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from ply_test_lex import tokens
from ply_test_syntax_tree import *

precedence = (
 ('left','OR'),
 ('left','AND'),
 ('left','NOT'),
 ('nonassoc','LT','GT','LE','GE','EQ','NE'),  # Nonassociative operators
 ('left','PLUS','MINUS'),
 ('left','TIMES','DIVIDE','MODULO'),
)

def p_code_simple(p):
  'code : line NEWLINE'
  p[0] = ASTSequence()
  p[0].addNode(p[1])

def p_code_multiple(p):
  'code : code line NEWLINE'
  p[1].addNode(p[2])
  p[0] = p[1]

def p_line(p):
  '''line : statement
          | while
          | if
          | elif
          | else'''
  p[1].setLine(p.lineno(1))
  p[0] = p[1]

def p_line_tab(p):
  'line : TAB line'
  p[2].doIndent()
  p[0] = p[2]

def p_statement(p):
  'statement : ID EQUALS expression'
  p[0] = ASTStatement(p[1],p[3])

def p_expression_variable(p):
  'expression : ID'
  p[0] = ASTVariable(p[1])

def p_integer_constant(p):
  'expression : INTEGER_CONST'
  p[0] = ASTIntegerConstant(int(p[1]))

def p_boolean_constant(p):
  '''expression : TRUE
                | FALSE'''
  p[0] = ASTBooleanConstant(p[1]=="True")

def p_expression_binary(p):
  '''expression : expression PLUS expression
                | expression MINUS expression
                | expression TIMES expression
                | expression DIVIDE expression
                | expression MODULO expression
                | expression LT expression
                | expression GT expression
                | expression LE expression
                | expression GE expression
                | expression EQ expression
                | expression NE expression
                | expression OR expression
                | expression AND expression'''
  p[0] = ASTBinaryOperator(p[2],p[1],p[3])

def p_boolean_not(p):
  'expression : NOT expression'
  p[0] = ASTBooleanNot(p[2])

def p_expression_group(p):
  'expression : LPAREN expression RPAREN'
  p[0] = ASTExpressionGroup(p[2])

def p_while(p):
  'while : WHILE expression COLON'
  p[0] = ASTWhile(p[2])

def p_if(p):
  'if : IF expression COLON'
  p[0] = ASTIf("if",p[2])

def p_elif(p):
  'elif : ELIF expression COLON'
  p[0] = ASTIf("elif",p[2])

def p_else(p):
  'else : ELSE COLON'
  p[0] = ASTElse()

# Error rule for syntax errors
def p_error(p):
  print("Syntax error in input!")

# Build the parser
parser = yacc.yacc()

py_code = ""
py_file = open('ply_test_example.py', 'r')
for line in py_file:
  i = 0
  while line[i]==' ':
    i += 1
  py_code += '\t'*(i//2)+line[i:]
py_file.close()
syntax_tree = parser.parse(py_code,tracking=True)
# str rendering
print(syntax_tree)
# HTML w/ syntax highlighting
html_file = open("test_html.html","wt")
html_file.write("<h1>Code</h1><pre>"+syntax_tree.toHtml()+"</pre>")
# Type check
html_file.write("<h1>Environment</h1><pre>"+str(syntax_tree.checkType())+"</pre>")
# AST Graph (graphviz)
dot = Digraph(format='png')
dot.graph_attr['rankdir'] = 'LR'
dot.graph_attr['splines'] = "polyline"
dot.node_attr['fontname'] = "monospace"
dot.edge_attr['fontname'] = "monospace"
syntax_tree.toGraph(dot,is_deep=True)
dot.render('test_graph.gv')
html_file.write("<h1>AST</h1><img width='100%' src='test_graph.gv.png'/>")

# Execution
syntax_tree.execute()
#
html_file.close()
