
import ply.yacc as yacc
from simply_lex import SimplyLex
from simply_ast import *

tokens = SimplyLex.parser_tokens

precedence = (
 ('left','OR'),
 ('left','AND'),
 ('left','NOT'),
 ('nonassoc','LT','GT','LE','GE','EQ','NE'),  # Nonassociative operators
 ('left','PLUS','MINUS'),
 ('left','TIMES','DIVIDE','MODULO'),
)

def p_code(p):
  'code : sequence EOF'
  p[0] = ASTRoot(p[1])

def p_sequence(p):
  'sequence : statement sequence'
  p[0] = ASTSequence(p[1],p[2])

def p_sequence_single(p):
  'sequence : statement'
  p[0] = p[1]

def p_sequence_newline(p):
  'sequence : NEWLINE sequence'
  p[0] = p[2]

def p_statement(p):
  '''statement : assignment
               | while
               | if
               | print'''
  p[0] = p[1]

def p_assignment(p):
  'assignment : ID EQUALS expression NEWLINE'
  p[0] = ASTAssignment(p[1],p[3])

def p_print(p):
  'print : PRINT LPAREN expression RPAREN NEWLINE'
  p[0] = ASTPrint(p[3])

def p_while(p):
  'while : WHILE expression COLON NEWLINE INDENT sequence DEDENT'
  p[0] = ASTWhile(p[2],p[6])

def p_if(p):
  'if : IF expression COLON NEWLINE INDENT sequence DEDENT else'
  p[0] = ASTBranch(p[2],p[6],p[8])

def p_elif(p):
  'else : ELIF expression COLON NEWLINE INDENT sequence DEDENT else'
  p[0] = ASTBranch(p[2],p[6],p[8])

def p_else(p):
  'else : ELSE COLON NEWLINE INDENT sequence DEDENT'
  p[0] = p[5]

def p_nop(p):
  'else :'
  p[0] = ASTNop()

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
  p[0] = p[2]

# Error rule for syntax errors
def p_error(p):
  print(p)
  print("Syntax error in input!")
