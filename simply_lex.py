import ply.lex as lex

reserved = {
  'if' : 'IF', 'elif' : 'ELIF', 'else' : 'ELSE',
  'while' : 'WHILE',
  'not' : 'NOT', 'or' : 'OR', 'and' : 'AND',
  'True' : 'TRUE', 'False' : 'FALSE',
}

tokens = [
  'INTEGER_CONST',
  'PLUS','MINUS','TIMES','DIVIDE','MODULO',
  'LT','GT','LE','GE','EQ','NE',
  'LPAREN','RPAREN',
  'ID','EQUALS',
  'COLON',
  'NEWLINE','TAB', 'COMMENT',
]+list(reserved.values())

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'//'
t_MODULO = r'%'
t_LT = r'<'
t_GT = r'>'
t_LE = r'<='
t_GE = r'>='
t_EQ = r'=='
t_NE = r'!='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQUALS = r'='
t_COLON = r':'
t_TAB = r'\t'
t_INTEGER_CONST = r'\d+'
t_COMMENT = r'\#.*'

def t_ID(t):
  r'[a-zA-Z_][a-zA-Z_0-9]*'
  t.type = reserved.get(t.value,'ID')
  return t

def t_NEWLINE(t):
  r'\n'
  t.lexer.lineno += 1
  return t

t_ignore = ' '

def t_error(t):
  print("Illegal character '%s'" % t.value[0])
  t.lexer.skip(1)

lexer = lex.lex()
