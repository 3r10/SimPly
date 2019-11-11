
import ply.yacc as yacc
from simply_lex import tokens
from simply_ast import *

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
          | else
          | comment'''
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

def p_comment(p):
  'comment : COMMENT'
  p[0] = ASTComment(p[1])

# Error rule for syntax errors
def p_error(p):
  print("Syntax error in input!")

parser = yacc.yacc(outputdir="yacc.out")
