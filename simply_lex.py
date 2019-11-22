#!/usr/bin/python3

import ply.lex as lex

class SimplyLex:
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
    'NEWLINE', 'COMMENT', 'INDENT','DEDENT'
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
  t_INTEGER_CONST = r'\d+'

  def t_ID(self,t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = SimplyLex.reserved.get(t.value,'ID')
    return t

  def t_NEWLINE(self,t):
    r'\n\t*'
    t.lexer.lineno += 1
    self.lineno += 1
    return t

  def t_COMMENT(self,t):
    r'\#.*\n'
    t.lexer.lineno += 1
    self.lineno += 1
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
        indent_level = len(tok.value)-1
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

  def toHtml(self):
    list_cuts = []
    for i in range(len(self.additional_tokens)):
      list_cuts.append(self.additional_tokens[i].lexpos)
    html = '<span class="lineno">1\t</span>'
    for i in range(len(list_cuts)-1):
      fragment = self.code[list_cuts[i]:list_cuts[i+1]]
      type = self.additional_tokens[i].type
      lineno = self.additional_tokens[i].lineno
      if type in ['IF', 'ELIF', 'ELSE', 'WHILE']:
        css_class = 'class = "keyword"'
      elif type in ['INTEGER_CONST', 'TRUE', 'FALSE']:
        css_class = 'class = "constant"'
      elif type in ['NOT', 'OR', 'AND',
                    'PLUS','MINUS','TIMES','DIVIDE','MODULO',
                    'LT','GT','LE','GE','EQ','NE']:
        css_class = 'class = "operator"'
      elif type=='COMMENT':
        fragment += '</span><span class="lineno">'+str(lineno+1)+'\t'
        css_class = 'class = "comment"'
      elif type=='NEWLINE':
        html += "\n"
        fragment = str(lineno+1)+"\t"+fragment[1:]
        css_class = 'class = "lineno"'
      else:
        css_class = ""
      html += '<span '+css_class+'title="'+type+'">'+fragment+"</span>"
    return html

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
