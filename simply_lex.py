#!/usr/bin/python3

import ply.lex as lex

class SimplyLex:
  reserved = {
    'if' : 'IF', 'elif' : 'ELIF', 'else' : 'ELSE',
    'while' : 'WHILE',
    'not' : 'NOT', 'or' : 'OR', 'and' : 'AND',
    'True' : 'TRUE', 'False' : 'FALSE',
    'print' : 'PRINT',
  }

  parser_tokens = [
    'INTEGER_CONST',
    'PLUS','MINUS','TIMES','DIVIDE','MODULO',
    'LT','GT','LE','GE','EQ','NE',
    'LPAREN','RPAREN',
    'ID','EQUALS',
    'COLON',
    'NEWLINE','INDENT','DEDENT',
    'EOF'
  ]+list(reserved.values())
  tokens = parser_tokens+['COMMENT']

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
  t_INTEGER_CONST = r'\d+'

  def t_ID(self,t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = SimplyLex.reserved.get(t.value,'ID')
    return t

  def t_NEWLINE(self,t):
    r'\n\t*'
    t.lexer.lineno += 1
    self.lineno += 1
    string = t.value
    t.value = 0
    while string[-1]=="\t":
      t.value += 1
      string = string[:-1]
    return t

  def t_COMMENT(self,t):
    r'\#.*\n\t*'
    t.lexer.lineno += 1
    self.lineno += 1
    t.type = 'NEWLINE'
    string = t.value
    t.value = 0
    while string[-1]=="\t":
      t.value += 1
      string = string[:-1]
    return t

  t_ignore = ' '

  def t_error(self,t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

  def __init__(self):
    self.lexer = lex.lex(module=self)

  def input(self,code):
    self.lexer.lineno = 1
    self.lineno = 1
    self.lexpos = 0
    self.indent_level = 0
    self.additional_tokens = []
    self.spaces2tab(code)
    self.lexer.input(self.code)
    tok = self.lexer.token()
    while tok:
      self.additional_tokens.append(tok)
      if tok.type=='NEWLINE':
        indent_level = tok.value
        while self.indent_level<indent_level:
          self.indent_level += 1
          tok2 = lex.LexToken()
          tok2.type = 'INDENT'
          tok2.value = self.indent_level
          tok2.lineno = tok.lineno
          tok2.lexpos = tok.lexpos+indent_level
          self.additional_tokens.append(tok2)
        while self.indent_level>indent_level:
          self.indent_level -= 1
          tok2 = lex.LexToken()
          tok2.type = 'DEDENT'
          tok2.value = self.indent_level
          tok2.lineno = tok.lineno
          tok2.lexpos = tok.lexpos+indent_level
          self.additional_tokens.append(tok2)
      tok = self.lexer.token()
    eof = lex.LexToken()
    eof.type = 'EOF'
    eof.value = ''
    eof.lineno = 0
    eof.lexpos = 0
    self.additional_tokens.append(eof)
    self.indent_level = 0
    self.i_token = 0

  def token(self):
    while self.i_token<len(self.additional_tokens) and self.additional_tokens[self.i_token].type=='COMMENT':
      self.i_token += 1
    if self.i_token>=len(self.additional_tokens):
      return
    tok = self.additional_tokens[self.i_token]
    if tok.type in ['INDENT','DEDENT']:
      self.indent_level = tok.value
    self.i_token += 1
    return tok

  def spaces2tab(self,code_in):
    # TAB are part of the Subset Grammar
    # spaces are ignored
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
    self.code = code_out+"\n"
