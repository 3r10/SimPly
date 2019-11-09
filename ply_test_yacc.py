#!/usr/bin/python3
# Yacc example

import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from ply_test_lex import tokens
from ply_test_syntax_tree import *

precedence = (
 ('left','NOT'),
 ('left','OR'),
 ('left','AND'),
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

def p_line_statement(p):
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
  'statement : ID EQUALS integer_expr'
  p[0] = ASTStatement(p[1],p[3])

def p_integer_expr(p):
  '''integer_expr : integer_expr PLUS integer_expr
                  | integer_expr MINUS integer_expr
                  | integer_expr TIMES integer_expr
                  | integer_expr DIVIDE integer_expr
                  | integer_expr MODULO integer_expr'''
  p[0] = ASTIntegerBinaryOperator(p[2],p[1],p[3])

def p_integer_expr_group(p):
  'integer_expr : LPAREN integer_expr RPAREN'
  p[0] = ASTIntegerGroup(p[2])

def p_integer_expr_constant(p):
  'integer_expr : INTEGER_CONST'
  p[0] = ASTIntegerConstant(p[1])

def p_integer_expr_value(p):
  'integer_expr : ID'
  p[0] = ASTIntegerVariable(p[1])

def p_boolean_comparison(p):
  '''boolean_expr : integer_expr LT integer_expr
                  | integer_expr GT integer_expr
                  | integer_expr LE integer_expr
                  | integer_expr GE integer_expr
                  | integer_expr EQ integer_expr
                  | integer_expr NE integer_expr'''
  p[0] = ASTComparison(p[2],p[1],p[3])

def p_boolean_expr(p):
  '''boolean_expr : boolean_expr OR boolean_expr
                  | boolean_expr AND boolean_expr'''
  p[0] = ASTBooleanBinaryOperator(p[2],p[1],p[3])

def p_boolean_not(p):
  'boolean_expr : NOT boolean_expr'
  p[0] = ASTBooleanNot(p[2])

def p_boolean_expr_group(p):
  'boolean_expr : LPAREN boolean_expr RPAREN'
  p[0] = ASTBooleanGroup(p[2])

def p_while(p):
  'while : WHILE boolean_expr COLON'
  p[0] = ASTWhile(p[2])

def p_if(p):
  'if : IF boolean_expr COLON'
  p[0] = ASTIf(p[2])

def p_elif(p):
  'elif : ELIF boolean_expr COLON'
  p[0] = ASTElif(p[2])

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
print(py_code)
result = parser.parse(py_code,tracking=True)
dot = Digraph()
result.toGraph(dot)
#dot.render('test_graph.gv', view=True)
print(result)
html_file = open("test_html.html","wt")
html_file.write("<pre>"+result.toHtml()+"</pre>")
html_file.close()
result.execute()
