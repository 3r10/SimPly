from graphviz import Digraph

ASTVariables = {}

class ASTIntegerBinaryOperator:
  def __init__(self,operator,operand1,operand2):
    self.operator = operator
    self.operand1 = operand1
    self.operand2 = operand2
  def __repr__(self):
    return str(self.operand1)+str(self.operator)+str(self.operand2)
  def evaluate(self):
    eval1 = self.operand1.evaluate()
    eval2 = self.operand2.evaluate()
    return eval(str(eval1)+self.operator+str(eval2))

class ASTIntegerGroup:
  def __init__(self,expression):
    self.expression = self.expression
  def __repr__(self):
    return "("+str(self.expression)+")"
  def evaluate(self):
    return self.expression.evaluate()

class ASTIntegerConstant:
  def __init__(self,value):
    self.value = value
  def __repr__(self):
    return str(self.value)
  def evaluate(self):
    return self.value

class ASTIntegerVariable:
  def __init__(self,name):
    self.name = name
  def __repr__(self):
    return self.name
  def evaluate(self):
    global ASTVariables
    assert self.name in ASTVariables, self.name+" referenced before assignment"
    return ASTVariables[self.name]

class ASTComparison:
  def __init__(self,operator,operand1,operand2):
    self.operator = operator
    self.operand1 = operand1
    self.operand2 = operand2
  def __repr__(self):
    return str(self.operand1)+str(self.operator)+str(self.operand2)
  def toHtml(self):
    return (str(self.operand1)
           +self.operator.replace(">","&gt;").replace("<","&lt;")
           +str(self.operand2))
  def evaluate(self):
    eval1 = self.operand1.evaluate()
    eval2 = self.operand2.evaluate()
    return eval(str(eval1)+self.operator+str(eval2))

class ASTBooleanBinaryOperator:
  def __init__(self,operator,operand1,operand2):
    self.operator = operator
    self.operand1 = operand1
    self.operand2 = operand2
  def __repr__(self):
    return str(self.operand1)+" "+self.operator+" "+str(self.operand2)
  def toHtml(self):
    return (self.operand1.toHtml()
           +' <span style="color:blue">'+self.operator+'</span> '
           +self.operand2.toHtml())
  def evaluate(self):
    eval1 = self.operand1.evaluate()
    eval2 = self.operand2.evaluate()
    return eval(str(eval1)+" "+self.operator+" "+str(eval2))

class ASTBooleanNot:
  def __init__(self,operand):
    self.operand = operand
  def __repr__(self):
    return "not "+str(self.operand)
  def toHtml(self):
    return '<span style="color:blue">not</span> '+self.expression.toHtml()
  def evaluate(self):
    return not self.operand.evaluate()

class ASTBooleanGroup:
  def __init__(self,expression):
    self.expression = self.expression
  def __repr__(self):
    return "("+str(self.expression)+")"
  def toHtml(self):
    return "("+self.expression.toHtml()+")"
  def evaluate(self):
    return self.expression.evaluate()

class ASTNode:
  def setLine(self,number):
    self.line_number = number
    self.indent = 0
  def doIndent(self):
    self.indent += 1
  def __repr__(self):
    return str(self.line_number)+"\t"*(self.indent+1)
  def toHtml(self):
    return '<span style="color:grey; font-style: italic">'+str(self.line_number)+"</span>\t"+"  "*self.indent
  def execute(self):
    print("Line ",self.line_number,": ",end="")


class ASTStatement(ASTNode):
  def __init__(self,id,expression):
    self.type = "statement"
    self.id = id
    self.expression = expression
  def __repr__(self):
    return ASTNode.__repr__(self)+self.id+" = "+str(self.expression)+"\n"
  def toHtml(self):
    return ASTNode.toHtml(self)+self.id+" = "+str(self.expression)+"\n"
  def toGraph(self,dot):
    name = "S"+str(self.line_number)
    dot.node(name,"Statement "+self.id+" = "+str(self.expression))
    return name
  def execute(self):
    ASTNode.execute(self)
    global ASTVariables
    value = self.expression.evaluate()
    ASTVariables[self.id] = value
    print(self.id,"<-",value)

class ASTWhile(ASTNode):
  def __init__(self,condition):
    self.type = "while"
    self.condition = condition
    self.sequence = ASTSequence()
  def addNode(self,node):
    self.sequence.addNode(node)
  def __repr__(self):
    return ASTNode.__repr__(self)+"while "+str(self.condition)+":\n"+str(self.sequence)
  def toHtml(self):
    return ASTNode.toHtml(self)+'<span style="color:blue">while</span> '+self.condition.toHtml()+":\n"+self.sequence.toHtml()
  def toGraph(self,dot):
    name = "W"+str(self.line_number)
    dot.node(name,"While")
    condition_name = "C"+str(self.line_number)
    dot.node(condition_name,str(self.condition))
    dot.edge(name,condition_name,"condition")
    sequence_name = self.sequence.toGraph(dot)
    dot.edge(name,sequence_name,"block")
    return name
  def execute(self):
    while self.condition.evaluate():
      ASTNode.execute(self)
      print("Condition : T")
      self.sequence.execute()
    ASTNode.execute(self)
    print("Condition : F")

class ASTIf(ASTNode):
  def __init__(self,condition):
    self.type = "if"
    self.condition = condition
    self.sequence = ASTSequence()
    self.next = None
  def addNode(self,node):
    if self.next:
      self.next.addNode(node)
    else:
      self.sequence.addNode(node)
  def __repr__(self):
    string = ASTNode.__repr__(self)+"if "+str(self.condition)+":\n"
    string += str(self.sequence)
    if self.next:
      string += str(self.next)
    return string
  def toHtml(self):
    string = ASTNode.toHtml(self)+'<span style="color:blue">if</span> '+self.condition.toHtml()+":\n"
    string += self.sequence.toHtml()
    if self.next:
      string += self.next.toHtml()
    return string
  def toGraph(self,dot):
    name = "B"+str(self.line_number)
    dot.node(name,"Branch")
    condition_name = "C"+str(self.line_number)
    dot.node(condition_name,str(self.condition))
    dot.edge(name,condition_name,"condition")
    if_name = self.sequence.toGraph(dot)
    dot.edge(name,if_name,"if")
    if self.next:
      else_name = self.next.toGraph(dot)
      dot.edge(name,else_name,"else")
    return name
  def execute(self):
    ASTNode.execute(self)
    condition = self.condition.evaluate()
    print("If",condition)
    if condition:
      self.sequence.execute()
    elif self.next:
      self.next.execute()

class ASTElif(ASTNode):
  def __init__(self,condition):
    self.type = "elif"
    self.condition = condition
    self.sequence = ASTSequence()
    self.next = None
  def addNode(self,node):
    if self.next:
      self.next.addNode(node)
    else:
      self.sequence.append(node)
  def __repr__(self):
    string = ASTNode.__repr__(self)+"elif "+str(self.condition)+":\n"
    string += str(self.sequence)
    if self.next:
      string += str(self.next)
    return string
  def toHtml(self):
    string = ASTNode.toHtml(self)+'<span style="color:blue">elif</span> '+self.condition.toHtml()+":\n"
    string += self.sequence.toHtml()
    if self.next:
      string += self.next.toHtml()
    return string
  def toGraph(self,dot):
    name = "B"+str(self.line_number)
    dot.node(name,"Branch")
    condition_name = "C"+str(self.line_number)
    dot.node(condition_name,str(self.condition))
    dot.edge(name,condition_name,"condition")
    if_name = self.sequence.toGraph(dot)
    dot.edge(name,if_name,"if")
    if self.next:
      else_name = self.next.toGraph(dot)
      dot.edge(name,else_name,"else")
    return name
  def execute(self):
    ASTNode.execute(self)
    condition = self.condition.evaluate()
    print("Elif",condition)
    if condition:
      self.sequence.execute()
    elif self.next:
      self.next.execute()

class ASTElse(ASTNode):
  def __init__(self):
    self.type = "else"
    self.sequence = ASTSequence()
  def addNode(self,node):
    self.sequence.addNode(node)
  def __repr__(self):
    return ASTNode.__repr__(self)+'else:\n'+str(self.sequence)
  def toHtml(self):
    string = ASTNode.toHtml(self)+'<span style="color:blue">else</span>:\n'
    string += self.sequence.toHtml()
    return string
  def toGraph(self,dot):
    sequence_name = self.sequence.toGraph(dot)
    return sequence_name
  def execute(self):
    ASTNode.execute(self)
    print("Else")
    self.sequence.execute()

class ASTSequence:
  def __init__(self):
    self.nodes = []
  def addNode(self,node):
    if self.nodes==[]:
      self.nodes.append(node)
    elif self.nodes[-1].indent==node.indent:
      if node.type in ["elif", "else"] and self.nodes[-1].type in ["if","elif"]:
        self.nodes[-1].next = node
      else:
        self.nodes.append(node)
    else:
      self.nodes[-1].addNode(node)
  def __repr__(self):
    repr = ""
    for node in self.nodes:
      repr += str(node)
    return repr
  def toHtml(self):
    string = ""
    for node in self.nodes:
      string += node.toHtml()
    return string
  def toGraph(self,dot):
    name = "Seq"+str(self.nodes[0].line_number)
    dot.node(name,"Sequence")
    for node in self.nodes:
      node_name = node.toGraph(dot)
      dot.edge(name,node_name)
    return name
  def execute(self):
    for node in self.nodes:
      node.execute()
